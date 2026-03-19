import requests
import joblib
import threading
import numpy as np
import pandas as pd
import MetaTrader5 as mt5
from datetime import datetime, time, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from tensorflow.keras.models import load_model
from bot_logger import logger

BOT_CONFIG = {
    "stop_loss": 5.0,
    "take_profit": 2.0,
    "max_volume": 1.0,
    "min_volume": 0.01,
    "max_trades": 3
}

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

def get_positions():
    positions = mt5.positions_get()
    if positions is None:
        logger.error(f"positions_get() failed, error code: {mt5.last_error()}")
        return None
    return positions

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

def calculate_volume(current_price):
    open_positions = get_positions()
    max_trades = BOT_CONFIG["max_trades"]
    if open_positions is not None and len(open_positions) >= max_trades:
        logger.warning(f"Max trades ({max_trades}) reached, Holding equity..")
        return None

    account_info = get_account_info()
    if account_info is None:
        return None
    
    equity = account_info.equity
    volume = float(round(((equity / 20) / current_price), 2))

    min_vol = BOT_CONFIG["min_volume"]
    max_vol = BOT_CONFIG["max_volume"]
    volume = max(min_vol, min(volume, max_vol))

    return volume

def send_buy_order(symbol, volume, price, sl, tp):
    logger.info(f"Sending buy order for {symbol} at price: {price}, volume: {volume}...")
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": mt5.ORDER_TYPE_BUY,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 10,
        "magic": 123456,
        "comment": "py-bot-buy",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        logger.error(f"Buy order failed, retcode={result.retcode}")
    else:
        logger.info("Buy order placed successfully.")
    return result

def send_sell_order(symbol, volume, price, sl, tp):
    logger.info(f"Sending sell order for {symbol} at price: {price}, volume: {volume}...")
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": mt5.ORDER_TYPE_SELL,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 10,
        "magic": 123456,
        "comment": "py-bot-sell",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        logger.error(f"Sell order failed, retcode={result.retcode}")
    else:
        logger.info("Sell order placed successfully.")
    return result

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

def analyze_and_trade(symbol, stop_loss_percent, take_profit_percent, model, scaler):
    logger.info(f"Analysing account equity and deciding to trade for {symbol}...")
    account_info = get_account_info()
    if account_info is None:
        return

    equity = account_info.equity
    positions = get_positions()
    if positions is None:
        return

    active_position = next((pos for pos in positions if pos.symbol == symbol), None)
    if active_position:
        profit = active_position.profit
        if profit < 0:
            logger.warning(f"Active position for {symbol} is in loss. Skipping trade.")
            return
        else:
            logger.info(f"Active position for {symbol} is in profit. Proceeding with analysis.")

    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        logger.error(f"symbol_info_tick() failed, error code: {mt5.last_error()}")
        return

    logger.info(f"Current ask price for {symbol}: {tick.ask}, bid price: {tick.bid}")
    
    # Download 100 M1 candles to calculate SMA 50 and sequence 30
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 100)
    if rates is None or len(rates) == 0:
        logger.error(f"copy_rates_from_pos() failed, error code: {mt5.last_error()}")
        return

    rates_frame = pd.DataFrame(rates)
    rates_frame['time'] = pd.to_datetime(rates_frame['time'], unit='s')
    
    # Calculate indicators
    engineered_df = add_indicators(rates_frame)
    if len(engineered_df) < 30:
        logger.error(f"Not enough data after engineering indicators for {symbol}. Rows: {len(engineered_df)}")
        return
        
    signal = predict_signal(model, scaler, engineered_df)
    logger.info(f"Predicted signal for {symbol}: {signal} (0: Hold, 1: Buy, 2: Sell)")
    
    if equity < account_info.balance * 0.3:
        logger.error("Equity is less than 30% of the balance. Cannot trade.")
        return

    if signal == 1:
        logger.info(f"Model signaled BUY. Considering buy order...")
        sl, tp = calculate_sl_tp(tick.ask, mt5.ORDER_TYPE_BUY, stop_loss_percent, take_profit_percent)
        volume = calculate_volume(tick.ask)
        if volume is not None:
            send_buy_order(symbol, volume, tick.ask, sl, tp)
    elif signal == 2:
        logger.info(f"Model signaled SELL. Considering sell order...")
        sl, tp = calculate_sl_tp(tick.bid, mt5.ORDER_TYPE_SELL, stop_loss_percent, take_profit_percent)
        volume = calculate_volume(tick.bid)
        if volume is not None:
            send_sell_order(symbol, volume, tick.bid, sl, tp)
    
RUNNING = False
BOTTHREAD = None
BOT_LOCK = threading.Lock()

def main():
    initialize_mt5()
    model_path = r'..\\CryptoTradingModel\\Artifacts\\crypto_predictor_2026_02_27_04_17_47.keras'
    scaler_path = r'..\\CryptoTradingModel\\Artifacts\\data_scaler_2026_02_27_04_17_47.pkl'
    
    logger.info(f"Loading model from {model_path}...")
    model = load_model(model_path)
    
    logger.info(f"Loading scaler from {scaler_path}...")
    scaler = joblib.load(scaler_path)
    
    symbols = ['BTCUSD!', 'ETHUSD!', 'SOLUSD!']

    while RUNNING:
        stop_loss_percent = BOT_CONFIG["stop_loss"]
        take_profit_percent = BOT_CONFIG["take_profit"]
        for symbol in symbols:
            if not RUNNING:
                break
            analyze_and_trade(symbol, stop_loss_percent, take_profit_percent, model, scaler)

app = Flask(__name__)
CORS(app)
@app.route('/start-bot', methods=['GET', 'POST'])
def start_bot():
    global RUNNING, BOTTHREAD
    with BOT_LOCK:
        if not RUNNING:
            RUNNING = True
            BOTTHREAD = threading.Thread(target=main)
            BOTTHREAD.start()
            return jsonify({
                "Message": "Bot started.",
                "Status": 1
            })
        else:
            return jsonify({
                "Message": "Bot is already running.",
                "Status": 1
            })

@app.route('/stop-bot', methods=['GET', 'POST'])
def stop_bot():
    global RUNNING, BOTTHREAD
    with BOT_LOCK:
        if RUNNING:
            RUNNING = False
            if BOTTHREAD and BOTTHREAD.is_alive():
                BOTTHREAD.join(timeout=2.0)
            return jsonify({
                "Message": "Bot stopping...",
                "Status": 0
            })
        else:
            return jsonify({
                "Message": "Bot is not running.",
                "Status": -2
            })

@app.route('/bot-config', methods=['GET', 'POST'])
def bot_config():
    global BOT_CONFIG
    if request.method == 'POST':
        data = request.get_json()
        if data is None:
            return jsonify({"Message": "Invalid JSON body."}), 400

        required_keys = ["stop_loss", "take_profit", "max_volume", "min_volume", "max_trades"]
        missing = [k for k in required_keys if k not in data]
        if missing:
            return jsonify({"Message": f"Missing fields: {', '.join(missing)}"}), 400

        for key in required_keys:
            if not isinstance(data[key], (int, float)):
                return jsonify({"Message": f"Field '{key}' must be a number."}), 400

        BOT_CONFIG["stop_loss"] = float(data["stop_loss"])
        BOT_CONFIG["take_profit"] = float(data["take_profit"])
        BOT_CONFIG["max_volume"] = float(data["max_volume"])
        BOT_CONFIG["min_volume"] = float(data["min_volume"])
        BOT_CONFIG["max_trades"] = int(data["max_trades"])
        logger.info(BOT_CONFIG)
        return jsonify({"Message": "Config updated.", "Config": BOT_CONFIG})
    else:
        return jsonify({"Config": BOT_CONFIG})

if __name__ == '__main__':
    app.run(port=8082)