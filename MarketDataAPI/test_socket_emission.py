"""
Socket Emission Test Client
----------------------------
Connects to the MarketDataAPI SocketIO server and listens for data events.
Reports which events were received and validates the data structure.

Usage:
  1. Start MarketDataAPI.py in another terminal (requires MT5 running)
  2. Run: python test_socket_emission.py
"""

import socketio
import time
import sys
import json

# Configuration
SERVER_URL = " http://127.0.0.1:8081"
TIMEOUT_SECONDS = 15

# Track received events
received_events = {
    "On_Market_Data_Update": [],
    "On_Trades_Data_Update": [],
    "On_History_Data_Update": [],
}

# Expected fields for validation
EXPECTED_MARKET_FIELDS = {'symbol', 'time', 'bid', 'ask', 'last', 'volume', 'tick_volume', 'open', 'close', 'high', 'low', 'spread'}
EXPECTED_TRADES_FIELDS = {'symbol', 'ticket', 'time', 'type', 'volume', 'tradePrice', 'stopLoss', 'takeProfit', 'price', 'profit', 'change', 'identity'}
EXPECTED_HISTORY_FIELDS = {'symbol', 'ticket', 'time', 'type', 'volume', 'price', 'commission', 'swap', 'profit', 'comment', 'reason'}

sio = socketio.Client(logger=True, engineio_logger=True)

@sio.event
def connect():
    print(f"[OK] Connected to server at {SERVER_URL}")

@sio.event
def disconnect():
    print("[FAIL] Disconnected from server")

@sio.event
def connect_error(data):
    print(f"[FAIL] Connection error: {data}")

@sio.on("On_Market_Data_Update")
def on_market_data(data):
    received_events["On_Market_Data_Update"].append(data)
    count = len(data) if isinstance(data, list) else 1
    print(f"  [RECV] On_Market_Data_Update -- {count} ticker(s)")

@sio.on("On_Trades_Data_Update")
def on_trades_data(data):
    received_events["On_Trades_Data_Update"].append(data)
    count = len(data) if isinstance(data, list) else 1
    print(f"  [RECV] On_Trades_Data_Update -- {count} trade(s)")

@sio.on("On_History_Data_Update")
def on_history_data(data):
    received_events["On_History_Data_Update"].append(data)
    count = len(data) if isinstance(data, list) else 1
    print(f"  [RECV] On_History_Data_Update -- {count} deal(s)")


def validate_fields(data_list, expected_fields, event_name):
    """Validate that received data has the expected fields."""
    if not data_list:
        return False, "No data received"
    
    # Take the first emission
    first_emission = data_list[0]
    if isinstance(first_emission, list) and len(first_emission) > 0:
        sample = first_emission[0]
    elif isinstance(first_emission, dict):
        sample = first_emission
    else:
        return True, f"Received but empty (type: {type(first_emission).__name__})"

    actual_fields = set(sample.keys())
    missing = expected_fields - actual_fields
    extra = actual_fields - expected_fields

    if missing:
        return False, f"Missing fields: {missing}"
    if extra:
        return True, f"OK (extra fields: {extra})"
    return True, "OK -- all fields present"


def run_test():
    print("=" * 60)
    print("  MarketDataAPI Socket Emission Test")
    print("=" * 60)
    print(f"\nConnecting to {SERVER_URL}...")
    
    try:
        sio.connect(SERVER_URL, wait_timeout=10, transports=['polling'], headers={'ngrok-skip-browser-warning': 'true'})
    except Exception as e:
        print(f"\n[FAIL] Could not connect to server: {e}")
        print("       Make sure MarketDataAPI.py is running first!")
        sys.exit(1)

    print(f"Listening for events for {TIMEOUT_SECONDS} seconds...\n")
    time.sleep(TIMEOUT_SECONDS)

    # Disconnect
    sio.disconnect()

    # Results
    print("\n" + "=" * 60)
    print("  TEST RESULTS")
    print("=" * 60)

    all_passed = True

    # Check Market Data
    event = "On_Market_Data_Update"
    count = len(received_events[event])
    if count > 0:
        valid, msg = validate_fields(received_events[event], EXPECTED_MARKET_FIELDS, event)
        status = "[PASS]" if valid else "[WARN]"
        print(f"  {status} {event}: received {count} emission(s) -- {msg}")
        if not valid:
            all_passed = False
    else:
        print(f"  [FAIL] {event}: no data received")
        all_passed = False

    # Check Trades Data
    event = "On_Trades_Data_Update"
    count = len(received_events[event])
    if count > 0:
        valid, msg = validate_fields(received_events[event], EXPECTED_TRADES_FIELDS, event)
        status = "[PASS]" if valid else "[WARN]"
        print(f"  {status} {event}: received {count} emission(s) -- {msg}")
        if not valid:
            all_passed = False
    else:
        print(f"  [WARN] {event}: no data received (may have no open trades)")

    # Check History Data  
    event = "On_History_Data_Update"
    count = len(received_events[event])
    if count > 0:
        valid, msg = validate_fields(received_events[event], EXPECTED_HISTORY_FIELDS, event)
        status = "[PASS]" if valid else "[WARN]"
        print(f"  {status} {event}: received {count} emission(s) -- {msg}")
        if not valid:
            all_passed = False
    else:
        print(f"  [WARN] {event}: no data received (may have no recent deals)")

    # Print a sample of market data if available
    if received_events["On_Market_Data_Update"]:
        first = received_events["On_Market_Data_Update"][0]
        if isinstance(first, list) and len(first) > 0:
            print(f"\n  Sample market data (first ticker):")
            print(f"  {json.dumps(first[0], indent=4)}")

    print("\n" + "=" * 60)
    if all_passed:
        print("  >> All critical tests passed!")
    else:
        print("  >> Some tests failed -- see above")
    print("=" * 60)


if __name__ == "__main__":
    run_test()
