import logging
from logging.handlers import RotatingFileHandler

def setup_logger(name="NewsAPI", log_file="news_api.log", level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        # File Handler (Rotating)
        try:
            file_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3)
            file_formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            print(f"Failed to setup file handler for logging: {e}")

        # Stream Handler (Console)
        stream_handler = logging.StreamHandler()
        stream_formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        stream_handler.setFormatter(stream_formatter)
        logger.addHandler(stream_handler)

    return logger
