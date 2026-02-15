from abc import ABC, abstractmethod
# import MetaTrader5 as mt5 # Keep as comment for now
from config import Config

class MarketRepository(ABC):
    """
    Interface for Market Data Repository.
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
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MT5Repository, cls).__new__(cls)
        return cls._instance

    def initialize(self):
        print("[INFO] => Initializing MT5 Repository (Base Structure)")
        pass

    def login(self):
        print("[INFO] => Logging into MT5 Repository (Base Structure)")
        pass

    def get_market_data(self, tickers):
        return []

    def get_history_deals(self):
        return []

    def get_active_trades(self):
        return []

    def shutdown(self):
        print("[INFO] => Shutting down MT5 Repository")
        # mt5.shutdown()
        pass
