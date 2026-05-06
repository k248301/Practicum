import random
import requests
import joblib
import threading
import numpy as np
import pandas as pd
import MetaTrader5 as mt5
import time
import json
import os
import hashlib
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from tensorflow.keras.models import load_model
from bot_logger import logger

CONFIG_FILE = "user_configs.json"
DEFAULT_CONFIG = {
    "stop_loss": 5.0,
    "take_profit": 2.0,
    "max_volume": 1.0,
    "min_volume": 0.01,
    "max_trades": 3
}

USER_DATA = {}
USER_DATA_LOCK = threading.Lock()

def load_configs():
    global USER_DATA
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                saved_configs = json.load(f)
                for uid, config in saved_configs.items():
                    USER_DATA[uid] = {
                        "config": config,
                        "running": False,
                        "thread": None
                    }
            logger.info(f"Loaded {len(saved_configs)} user configs.")
        except Exception as e:
            logger.error(f"Failed to load configs: {e}")

def save_configs():
    with USER_DATA_LOCK:
        configs_to_save = {uid: data["config"] for uid, data in USER_DATA.items()}
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(configs_to_save, f, indent=4)
    except Exception as e:
        logger.error(f"Failed to save configs: {e}")

def get_user_magic(uid):
    """Generate a unique integer magic number from UID string."""
    return int(hashlib.md5(uid.encode()).hexdigest(), 16) % 10000000

def initialize_mt5():
    logger.info("Initializing MetaTrader 5...")
    if not mt5.initialize():
        logger.error(f"initialize() failed, error code: {mt5.last_error()}")
        quit()
    logger.info("MetaTrader 5 initialized successfully.")

def get_account_info():
    account_info = mt5.account_info()
    if account_info is None:
        logger.error(f"account_info() failed, error code: {mt5.last_error()}")
        return None
    return account_info

def get_positions(magic=None):
    if magic is not None:
        return mt5.positions_get(magic=magic)
    return mt5.positions_get()

def get_symbol_info(symbol):
    logger.info(f"Getting symbol info for {symbol}...")
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        logger.error(f"symbol_info() failed, error code: {mt5.last_error()}")
        return None
    logger.info(f"Symbol info for {symbol} retrieved successfully.")
    return symbol_info

def calculate_sl_tp(price, order_type, stop_loss_percent, take_profit_percent):
    logger.info(f"Calculating SL/TP for price: {price}, order_type: {order_type}...")
    if order_type == mt5.ORDER_TYPE_BUY:
        sl = price - (price * stop_loss_percent) / 100
        tp = price + (price * take_profit_percent) / 100
    else:
        sl = price + (price * stop_loss_percent) / 100
        tp = price - (price * take_profit_percent) / 100
    logger.info(f"SL: {sl}, TP: {tp}")
    return sl, tp

def calculate_volume(current_price, uid):
    with USER_DATA_LOCK:
        if uid not in USER_DATA: return None
        config = USER_DATA[uid]["config"]
        magic = get_user_magic(uid)
    
    open_positions = get_positions(magic=magic)
    if open_positions is not None and len(open_positions) >= config["max_trades"]:
        logger.warning(f"[{uid}] Max trades reached.")
        return None

    account_info = get_account_info()
    if account_info is None: return None
    
    equity = account_info.equity
    volume = float(round(((equity / 20) / current_price), 2))
    volume = max(config["min_volume"], min(volume, config["max_volume"]))
    return volume

def send_order(symbol, volume, price, sl, tp, order_type, magic, comment):
    logger.info(f"Sending order | Symbol: {symbol}, Type: {order_type}, Vol: {volume}, Price: {price}, SL: {sl}, TP: {tp}")
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": order_type,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 10,
        "magic": magic,
        "comment": comment,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        logger.error(f"Order failed for {symbol}, retcode={result.retcode}")
    else:
        logger.info(f"Order placed successfully for {symbol} (Ticket: {result.order})")
    return result

# --- Bot Logic ---
def add_indicators(df):
    df = df.copy()
    # Rename MT5 columns to match model's expected feature names
    df.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'tick_volume': 'Volume'}, inplace=True)
    numeric_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss.replace(0, np.nan)
    df['RSI'] = 100 - (100 / (1 + rs.fillna(100)))
    
    df['BB_mid'] = df['Close'].rolling(window=20).mean()
    df['BB_std'] = df['Close'].rolling(window=20).std()
    df['BB_upper'] = df['BB_mid'] + (df['BB_std'] * 2)
    df['BB_lower'] = df['BB_mid'] - (df['BB_std'] * 2)
    
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['MACD_signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    
    df['vol_change'] = df['Volume'].pct_change().replace([np.inf, -np.inf], np.nan).fillna(0)
    
    df = df.replace([np.inf, -np.inf], np.nan).dropna()
    return df

def predict_signal(model, scaler, df, sequence_length=30):
    features = [
        'Open', 'High', 'Low', 'Close', 'Volume', 
        'SMA_20', 'SMA_50', 'RSI', 'vol_change',
        'BB_upper', 'BB_lower', 'MACD', 'MACD_signal'
    ]
    # Keep only the sequence length
    if len(df) < sequence_length:
        return 0 # Hold (not enough data)
    
    df_seq = df.tail(sequence_length)
    scaled_features = scaler.transform(df_seq[features].values)
    
    # Reshape to (1, sequence_length, num_features)
    X = np.array([scaled_features])
    
    pred_probs = model.predict(X, verbose=0)
    signal = np.argmax(pred_probs, axis=1)[0]
    return signal

def analyze_and_trade(uid, symbol, model, scaler):
    with USER_DATA_LOCK:
        if uid not in USER_DATA: return False
        config = USER_DATA[uid]["config"]
        magic = get_user_magic(uid)

    tick = mt5.symbol_info_tick(symbol)
    if not tick: return False
    logger.info(f"Current ask price for {symbol}: {tick.ask}, bid price: {tick.bid}")
    
    # Download 100 M1 candles to calculate SMA 50 and sequence 30
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 100)
    if rates is None or len(rates) < 50: return False

    df = add_indicators(pd.DataFrame(rates))
    signal = predict_signal(model, scaler, df)
    logger.info(f"Analysis Complete | Symbol: {symbol}, User: {uid[:8]}, Signal: {signal} (1=Buy, 2=Sell, 0=Hold)")

    if signal == 1: # Buy
        sl, tp = calculate_sl_tp(tick.ask, mt5.ORDER_TYPE_BUY, config["stop_loss"], config["take_profit"])
        vol = calculate_volume(tick.ask, uid)
        if vol: return send_order(symbol, vol, tick.ask, sl, tp, mt5.ORDER_TYPE_BUY, magic, f"bot-{uid[:5]}")
    elif signal == 2: # Sell
        sl, tp = calculate_sl_tp(tick.bid, mt5.ORDER_TYPE_SELL, config["stop_loss"], config["take_profit"])
        vol = calculate_volume(tick.bid, uid)
        if vol: return send_order(symbol, vol, tick.bid, sl, tp, mt5.ORDER_TYPE_SELL, magic, f"bot-{uid[:5]}")
    return False

def bot_worker(uid):
    logger.info(f"Starting bot worker for user: {uid}")
    model_path = r'..\\CryptoTradingModel\\Artifacts\\crypto_predictor_2026_02_27_04_17_47.keras'
    scaler_path = r'..\\CryptoTradingModel\\Artifacts\\data_scaler_2026_02_27_04_17_47.pkl'
    
    model = load_model(model_path)
    scaler = joblib.load(scaler_path)

    symbols = ['BTCUSD!', 'ETHUSD!', 'XRPUSD!', 'LTCUSD!', 'SOLUSD!', 'BNBUSD!', 'DOTUSD!', 'DOGUSD!', 'TETUSD!', 'ADAUSD!', 'AAVUSD!']

    while True:
        with USER_DATA_LOCK:
            if uid not in USER_DATA or not USER_DATA[uid]["running"]:
                break
        
        random.shuffle(symbols)
        for symbol in symbols:
            with USER_DATA_LOCK:
                if not USER_DATA[uid]["running"]: break
            if analyze_and_trade(uid, symbol, model, scaler):
                time.sleep(300)
            time.sleep(1)
    logger.info(f"Bot worker for user {uid} stopped.")

# --- Flask App ---
app = Flask(__name__)
CORS(app)
@app.route('/start-bot', methods=['POST'])
def start_bot():
    uid = request.json.get("uid")
    if not uid: return jsonify({"Message": "Missing UID", "Status": -1}), 400
    
    with USER_DATA_LOCK:
        if uid not in USER_DATA:
            USER_DATA[uid] = {"config": DEFAULT_CONFIG.copy(), "running": False, "thread": None}
        
        if USER_DATA[uid]["running"]:
            return jsonify({"Message": "Bot already running", "Status": 1})
        
        USER_DATA[uid]["running"] = True
        thread = threading.Thread(target=bot_worker, args=(uid,), daemon=True)
        USER_DATA[uid]["thread"] = thread
        thread.start()
        
    return jsonify({"Message": "Bot started", "Status": 1})

@app.route('/stop-bot', methods=['POST'])
def stop_bot():
    uid = request.json.get("uid")
    if not uid: return jsonify({"Message": "Missing UID", "Status": -1}), 400
    
    with USER_DATA_LOCK:
        if uid in USER_DATA and USER_DATA[uid]["running"]:
            USER_DATA[uid]["running"] = False
            return jsonify({"Message": "Bot stopping", "Status": 0})
    return jsonify({"Message": "Bot not running", "Status": -2})

@app.route('/bot-config', methods=['GET', 'POST'])
def bot_config():
    uid = request.args.get("uid") if request.method == 'GET' else request.json.get("uid")
    if not uid: return jsonify({"Message": "Missing UID"}), 400

    if request.method == 'POST':
        data = request.json
        with USER_DATA_LOCK:
            if uid not in USER_DATA:
                USER_DATA[uid] = {"config": DEFAULT_CONFIG.copy(), "running": False, "thread": None}
            
            for key in ["stop_loss", "take_profit", "max_volume", "min_volume", "max_trades"]:
                if key in data:
                    USER_DATA[uid]["config"][key] = float(data[key]) if key != "max_trades" else int(data[key])
        
        save_configs()
        return jsonify({"Message": "Config updated", "Config": USER_DATA[uid]["config"]})
    else:
        with USER_DATA_LOCK:
            config = USER_DATA.get(uid, {}).get("config", DEFAULT_CONFIG)
        return jsonify({"Config": config})

@app.route('/bot-status', methods=['GET'])
def bot_status():
    uid = request.args.get("uid")
    if not uid: return jsonify({"Message": "Missing UID"}), 400
    with USER_DATA_LOCK:
        running = USER_DATA.get(uid, {}).get("running", False)
    return jsonify({"RUNNING": running, "Status": 1 if running else 0})

if __name__ == '__main__':
    initialize_mt5()
    load_configs()
    app.run(port=8082)