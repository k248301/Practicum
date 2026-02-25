from abc import ABC, abstractmethod
import MetaTrader5 as mt5
from config import Config

class MarketRepository(ABC):
    """
    Interface for Market Data Repository.
    Abstracts the data source (MT5) from the application logic.
    """
    @abstractmethod
    def initialize(self): pass
    @abstractmethod
    def login(self): pass
    @abstractmethod
    def get_market_data(self, tickers): pass
    @abstractmethod
    def get_history_deals(self): pass
    @abstractmethod
    def get_active_trades(self): pass
    @abstractmethod
    def shutdown(self): pass

class MT5Repository(MarketRepository):
    """
    Implements Singleton pattern to ensure only one connection instance.
    Uses MetaTrader5 for real-time and historical data.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MT5Repository, cls).__new__(cls)
        return cls._instance

    def initialize(self):
        print("[INFO] => Initializing MetaTrader5")
        if not mt5.initialize():
            print(f"[ERROR] => initialize() failed, error code = {mt5.last_error()}")
            return False
        return True

    def login(self):
        print("[INFO] => Logging into MT5 Account")
        authorized = mt5.login(
            login=Config.MT5_LOGIN,
            password=Config.MT5_PASSWORD,
            server=Config.MT5_SERVER
        )
        if not authorized:
            print(f"[ERROR] => Failed to connect to trade account, error code = {mt5.last_error()}")
            return False
        print("[INFO] => Logged in successfully")
        return True

    def get_market_data(self, tickers):
        """Fetches real-time price info for provided tickers."""
        data = {}
        for ticker in tickers:
            symbol_info = mt5.symbol_info_tick(ticker)
            if symbol_info:
                data[ticker] = {
                    "bid": symbol_info.bid,
                    "ask": symbol_info.ask,
                    "last": symbol_info.last,
                    "time": symbol_info.time
                }
        return data

    def get_history_deals(self):
        """Fetches account deal history for the last 24 hours."""
        from datetime import datetime, timedelta
        from_date = datetime.now() - timedelta(days=1)
        deals = mt5.history_deals_get(from_date, datetime.now())
        if deals is None: return []
        return [deal._asdict() for deal in deals]

    def get_active_trades(self):
        """Fetches currently open positions."""
        positions = mt5.positions_get()
        if positions is None: return []
        return [pos._asdict() for pos in positions]

    def shutdown(self):
        print("[INFO] => Shutting down MetaTrader5")
        mt5.shutdown()
