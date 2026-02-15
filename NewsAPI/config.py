import os

class Config:
    NEWS_API_KEY = os.environ.get("NEWS_API_KEY", "eec815cd8dbf484b9ad21f9426612a87")
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 120
    DEBUG = False
    PORT = 8081
    HOST = "0.0.0.0"
