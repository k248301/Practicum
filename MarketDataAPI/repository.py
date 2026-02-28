from abc import ABC, abstractmethod
import MetaTrader5 as mt5
from config import Config
from datetime import datetime, timedelta

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
            login=Config.ACC_ID,
            password=Config.ACC_KEY,
            server=Config.ACC_ORG
        )
        if not authorized:
            print(f"[ERROR] => Failed to connect to trade account, error code = {mt5.last_error()}")
            return False
        print("[INFO] => Logged in successfully")
        return True

    def getTimeSinceEpoch(self, seconds):
        epoch = datetime(1970, 1, 1)
        seconds = int(seconds)
        delta = timedelta(seconds=seconds)
        result = epoch + delta
        return result

    def get_market_data(self, tickers):
        """Fetches real-time price info for provided tickers."""
        tickerQuotes = []
        for ticker in tickers:
            try:
                symbol_tick_raw = mt5.symbol_info_tick(ticker)
                if symbol_tick_raw is None:
                    print(f"[WARNING] => Symbol info tick for {ticker} is None")
                    continue
                
                symbol_tick = symbol_tick_raw._asdict()
                
                rates_frame_raw = mt5.copy_rates_from(ticker, mt5.TIMEFRAME_D1, datetime.now(), 1)
                if rates_frame_raw is None or len(rates_frame_raw) == 0:
                    print(f"[WARNING] => Rates frame for {ticker} is None or empty")
                    continue
                
                rates_frame = rates_frame_raw[0]

                tickerQuote = {
                    'symbol': ticker,
                    'time': self.getTimeSinceEpoch(symbol_tick["time"]).strftime('%Y-%m-%d %H:%M:%S'),
                    'bid': float(symbol_tick["bid"]),
                    'ask': float(symbol_tick["ask"]),
                    'last': float(symbol_tick["last"]),
                    'volume': float(rates_frame["tick_volume"]),
                    'tick_volume': float(rates_frame["tick_volume"]),
                    'open': float(rates_frame["open"]),
                    'close': float(rates_frame["close"]),
                    'high': float(rates_frame["high"]),
                    'low': float(rates_frame["low"]),
                    'spread': float(rates_frame["spread"])
                }
                tickerQuotes.append(tickerQuote)
            except Exception as e:
                print(f"[ERROR] => Failed to fetch data for {ticker}: {e}")
                continue
        return tickerQuotes

    def get_history_deals(self):
        """Fetches account deal history for the last 24 hours."""
        from_date = datetime.now() - timedelta(days=1)
        historyDeals = mt5.history_deals_get(from_date, datetime.now())
        arrHistoryDeals = []
        if historyDeals is not None:
            for deal in historyDeals:
                deal_dict = deal._asdict()
                historyDeal = {
                    'symbol': deal_dict['symbol'],
                    'ticket': int(deal_dict['ticket']),
                    'time': datetime.fromtimestamp(deal_dict['time']).strftime('%Y-%m-%d %H:%M:%S'),
                    'type': deal_dict['type'],
                    'volume': float(deal_dict['volume']),
                    'price': float(deal_dict['price']),
                    'commission': float(deal_dict['commission']),
                    'swap': float(deal_dict['swap']),
                    'profit': float(deal_dict['profit']),
                    'comment': deal_dict['comment'],
                    'reason': int(deal_dict['reason']),
                }
                arrHistoryDeals.append(historyDeal)
        return arrHistoryDeals

    def get_active_trades(self):
        """Fetches currently open positions."""
        positions = mt5.positions_get()
        tradesData = []
        if positions is not None:
            for trade in positions:
                trade_dict = trade._asdict()
                current_price = float(trade_dict['price_current'])
                open_price = float(trade_dict['price_open'])
                change = float((current_price - open_price) / current_price * 100) if current_price != 0 else 0.0
                tradeData = {
                    'symbol': trade_dict['symbol'],
                    'ticket': trade_dict['ticket'],
                    'time': datetime.fromtimestamp(trade_dict['time']).strftime('%Y-%m-%d %H:%M:%S'),
                    'type': trade_dict['type'],
                    'volume': float(trade_dict['volume']),
                    'tradePrice': open_price,
                    'stopLoss': float(trade_dict['sl']),
                    'takeProfit': float(trade_dict['tp']),
                    'price': current_price,
                    'profit': float(trade_dict['profit']),
                    'change': change,
                    'identity': trade_dict['comment'],
                }
                tradesData.append(tradeData)
        return tradesData

    def shutdown(self):
        print("[INFO] => Shutting down MetaTrader5")
        mt5.shutdown()
