import requests
import threading
import numpy as np
import pandas as pd
import MetaTrader5 as mt5
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from tensorflow.keras.models import load_model
from sklearn.preprocessing import StandardScaler, LabelEncoder

BOT_CONFIG = {
    "stop_loss": 5.0,
    "take_profit": 2.0,
    "max_volume": 1.0,
    "min_volume": 0.01,
    "max_trades": 10
}

def initialize_mt5():
    print("Initializing MetaTrader 5...")
    if not mt5.initialize():
        print(f"initialize() failed, error code: {mt5.last_error()}")
        quit()
    print("MetaTrader 5 initialized successfully.")

def get_account_info():
    account_info = mt5.account_info()
    if account_info is None:
        print(f"account_info() failed, error code: {mt5.last_error()}")
        return None
    return account_info

def get_positions():
    positions = mt5.positions_get()
    if positions is None:
        print(f"positions_get() failed, error code: {mt5.last_error()}")
        return None
    return positions

def get_symbol_info(symbol):
    print(f"Getting symbol info for {symbol}...")
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(f"symbol_info() failed, error code: {mt5.last_error()}")
        return None
    print(f"Symbol info for {symbol} retrieved successfully.")
    return symbol_info

def calculate_sl_tp(price, order_type, stop_loss_percent, take_profit_percent):
    print(f"Calculating SL/TP for price: {price}, order_type: {order_type}...")
    if order_type == mt5.ORDER_TYPE_BUY:
        sl = price - (price * stop_loss_percent) / 100
        tp = price + (price * take_profit_percent) / 100
    else:
        sl = price + (price * stop_loss_percent) / 100
        tp = price - (price * take_profit_percent) / 100
    print(f"SL: {sl}, TP: {tp}")
    return sl, tp

def calculate_volume(current_price):
    open_positions = get_positions()
    max_trades = BOT_CONFIG["max_trades"]
    if open_positions is not None and len(open_positions) >= max_trades:
        print(f"Max trades ({max_trades}) reached, Holding equity..")
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
    print(f"Sending buy order for {symbol} at price: {price}, volume: {volume}...")
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
        print(f"Buy order failed, retcode={result.retcode}")
    else:
        print("Buy order placed successfully.")
    return result

def send_sell_order(symbol, volume, price, sl, tp):
    print(f"Sending sell order for {symbol} at price: {price}, volume: {volume}...")
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
        print(f"Sell order failed, retcode={result.retcode}")
    else:
        print("Sell order placed successfully.")
    return result

def preprocess_new_data(tick_frame):
    tick_frame['tickDirection'] = LabelEncoder().fit_transform(tick_frame['tickDirection'])
    numerical_cols = ['bid', 'ask', 'volume', 'open', 'high', 'low', 'tick_volume']
    tick_frame[numerical_cols] = StandardScaler().fit_transform(tick_frame[numerical_cols])
    return tick_frame

def predict_next_price(model, tick_frame):
    tick_frame = preprocess_new_data(tick_frame)
    tick_sequence = np.array([tick_frame.values for _ in range(10)])
    tick_sequence = np.array(tick_sequence).reshape((1, 10, 8))
    print(tick_sequence.shape)
    predicted_price = model.predict(tick_sequence)
    return predicted_price[0][0]


def analyze_and_trade(symbol, stop_loss_percent, take_profit_percent, model):
    print(f"Analysing account equity and deciding to trade for {symbol}...")
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
            print(f"Active position for {symbol} is in loss. Skipping trade.")
            return
        else:
            print(f"Active position for {symbol} is in profit. Proceeding with analysis.")

    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        print(f"symbol_info_tick() failed, error code: {mt5.last_error()}")
        return

    print(f"Current ask price for {symbol}: {tick.ask}, bid price: {tick.bid}")
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 1)
    if rates is None or len(rates) == 0:
        print(f"copy_rates_from_pos() failed, error code: {mt5.last_error()}")
        return

    rates_frame = pd.DataFrame(rates)
    tick_frame = pd.DataFrame([{
        'bid': tick.bid,
        'ask': tick.ask,
        'volume': tick.volume,
        'open': rates_frame['open'].iloc[0],
        'high': rates_frame['high'].iloc[0],
        'low': rates_frame['low'].iloc[0],
        'tick_volume': rates_frame['tick_volume'].iloc[0],
        'tickDirection': 'ZeroPlusTick'
    }])

    predicted_price = predict_next_price(model, tick_frame)
    print(f"Predicted next price for {symbol}: {predicted_price}")
    if equity < account_info.balance * 0.3:
        print("Equity is less than 30% of the balance. Cannot trade.")
        return

    if predicted_price > tick.ask:
        print(f"Predicted price {predicted_price} is higher than ask price {tick.ask}. Considering buy order...")
        sl, tp = calculate_sl_tp(tick.ask, mt5.ORDER_TYPE_BUY, stop_loss_percent, take_profit_percent)
        volume = calculate_volume(tick.ask)
        if volume is not None:
            send_buy_order(symbol, volume, tick.ask, sl, tp)
    elif predicted_price < tick.bid:
        print(f"Predicted price {predicted_price} is lower than bid price {tick.bid}. Considering sell order...")
        sl, tp = calculate_sl_tp(tick.bid, mt5.ORDER_TYPE_SELL, stop_loss_percent, take_profit_percent)
        volume = calculate_volume(tick.bid)
        if volume is not None:
            send_sell_order(symbol, volume, tick.bid, sl, tp)

RUNNING = False
BOTTHREAD = None
BOT_LOCK = threading.Lock()

def main():
    initialize_mt5()
    model = load_model('crypto_predictor_2026_02_27_04_17_47.h5')
    symbols = ['BTCUSD', 'ETHUSD', 'SOLUSD']

    while RUNNING:
        stop_loss_percent = BOT_CONFIG["stop_loss"]
        take_profit_percent = BOT_CONFIG["take_profit"]
        for symbol in symbols:
            if not RUNNING:
                break
            analyze_and_trade(symbol, stop_loss_percent, take_profit_percent, model)

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
        print(BOT_CONFIG)
        return jsonify({"Message": "Config updated.", "Config": BOT_CONFIG})
    else:
        return jsonify({"Config": BOT_CONFIG})

if __name__ == '__main__':
    app.run(port=8082)