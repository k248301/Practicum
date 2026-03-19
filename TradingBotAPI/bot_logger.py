import logging
import os
from logging.handlers import TimedRotatingFileHandler

def setup_logger():
    if not os.path.exists('Logs'):
        os.makedirs('Logs')

    log_formatter = logging.Formatter('[%(asctime)s][%(levelname)s][%(message)s]', datefmt='%Y-%m-%d %H:%M:%S')

    file_handler = TimedRotatingFileHandler('Logs/trading_bot.log', when='midnight', interval=1, backupCount=30)
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    console_handler.setLevel(logging.INFO)

    bot_logger = logging.getLogger('TradingBot')
    
    # Check if handlers are already added to avoid duplicate logs in case of reloads
    if not bot_logger.handlers:
        bot_logger.setLevel(logging.INFO)
        bot_logger.addHandler(file_handler)
        bot_logger.addHandler(console_handler)
        
    return bot_logger

logger = setup_logger()
