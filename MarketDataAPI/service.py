from datetime import datetime
import threading
import sys
import hashlib
from flask_socketio import SocketIO
from repository import MarketRepository
from config import Config

ADMIN_UID = "O8pOUpjPMwRM4eH9CmF1JYTmub53"
def get_user_magic(uid):
    return int(hashlib.md5(uid.encode()).hexdigest(), 16) % 10000000

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
        self.active_users = set()
        self.user_lock = threading.Lock()

    def add_user(self, uid):
        with self.user_lock:
            self.active_users.add(uid)

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
                all_trades = self.repository.get_active_trades()
                
                with self.user_lock:
                    users = list(self.active_users)
                
                for uid in users:
                    if uid == ADMIN_UID:
                        # Admin sees everything
                        user_trades = all_trades
                    else:
                        magic = get_user_magic(uid)
                        # Regular filtering: magic or UID-specific comment
                        user_trades = [t for t in all_trades if t.get('magic') == magic or t.get('identity') == f"bot-{uid[:5]}"]
                    
                    self.socketio.emit('On_Trades_Data_Update', user_trades, room=uid)
                    
            except Exception as e:
                print(f"[ERROR] => Trades Loop error: {e}", flush=True)
            self.socketio.sleep(1.0)

    def _run_history_loop(self):
        print("[INFO] => Started History Loop", flush=True)
        self.socketio.sleep(2)
        while self.running:
            try:
                all_history = self.repository.get_history_deals()
                
                with self.user_lock:
                    users = list(self.active_users)
                
                for uid in users:
                    if uid == ADMIN_UID:
                        # Admin sees everything
                        user_history = all_history
                    else:
                        magic = get_user_magic(uid)
                        user_history = [h for h in all_history if h.get('magic') == magic or h.get('comment') == f"bot-{uid[:5]}"]
                    
                    self.socketio.emit('On_History_Data_Update', user_history, room=uid)
            except Exception as e:
                print(f"[ERROR] => History Loop error: {e}", flush=True)
            self.socketio.sleep(5.0)
