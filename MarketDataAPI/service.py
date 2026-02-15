import threading
import time
from flask_socketio import SocketIO
from repository import MarketRepository

class MarketDataService:
    """
    Service layer to coordinate data fetching and broadcasting.
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
        thread = threading.Thread(target=target, name=name, daemon=True)
        thread.start()
        self._threads.append(thread)

    def _run_market_data_loop(self):
        print("[INFO] => Started Market Data Loop")
        while self.running:
            data = self.repository.get_market_data(...)
            # socketio.emit(...)
            time.sleep(1)

    def _run_trades_loop(self):
        print("[INFO] => Started Trades Loop")
        while self.running:
            data = self.repository.get_active_trades()
            # socketio.emit(...)
            time.sleep(1)

    def _run_history_loop(self):
        print("[INFO] => Started History Loop")
        while self.running:
            data = self.repository.get_history_deals()
            # socketio.emit(...)
            time.sleep(2)
