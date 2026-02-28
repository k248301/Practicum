from datetime import datetime
import threading
import sys
from flask_socketio import SocketIO
from repository import MarketRepository
from config import Config

class MarketDataService:
    """
    Service layer to coordinate data fetching and broadcasting.
    Acts as a Facade to the underlying repository and socket handling.
    """
    def __init__(self, repository: MarketRepository, socketio: SocketIO):
        self.repository = repository
        self.socketio = socketio
        self.running = False
        self._threads = []

    def start(self):
        print("[INFO] => Starting MarketDataService")
        self.running = True
        self.repository.initialize()
        self.repository.login()
        
        # Start background threads for data updates
        self._start_thread(self._run_market_data_loop, "MarketData")
        self._start_thread(self._run_trades_loop, "Trades")
        self._start_thread(self._run_history_loop, "History")

    def stop(self):
        self.running = False
        self.repository.shutdown()

    def _start_thread(self, target, name):
        thread = self.socketio.start_background_task(target=target)
        self._threads.append(thread)

    def _run_market_data_loop(self):
        print("[INFO] => Started Market Data Loop", flush=True)
        symbols = Config.TICKERS
        self.socketio.sleep(2)  # Wait for server to be ready
        while self.running:
            try:
                data = self.repository.get_market_data(symbols)
                for quote in data:
                    self.socketio.emit('On_Market_Data_Update', quote)
            except Exception as e:
                print(f"[ERROR] => Market Data Loop error: {e}", flush=True)
            self.socketio.sleep(0.5)

    def _run_trades_loop(self):
        print("[INFO] => Started Trades Loop", flush=True)
        self.socketio.sleep(2)  # Wait for server to be ready
        while self.running:
            try:
                data = self.repository.get_active_trades()
                self.socketio.emit('On_Trades_Data_Update', data)
            except Exception as e:
                print(f"[ERROR] => Trades Loop error: {e}", flush=True)
            self.socketio.sleep(3)

    def _run_history_loop(self):
        print("[INFO] => Started History Loop", flush=True)
        self.socketio.sleep(2)  # Wait for server to be ready
        while self.running:
            try:
                data = self.repository.get_history_deals()
                self.socketio.emit('On_History_Data_Update', data)
            except Exception as e:
                print(f"[ERROR] => History Loop error: {e}", flush=True)
            self.socketio.sleep(10)  # History doesn't need to be as frequent

