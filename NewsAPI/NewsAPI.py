from flask import Flask, jsonify
from flask_cors import CORS
from flask_compress import Compress
from flask_caching import Cache
from config import Config
from logger import setup_logger
from news_service import NewsService
import requests

app = Flask(__name__)
app.config.from_object(Config)

CORS(app)
Compress(app)
cache = Cache(app)
logger = setup_logger()
news_service = NewsService(Config.NEWS_API_KEY)

@app.route("/fetch-news", methods=["GET"])
@cache.cached(timeout=Config.CACHE_DEFAULT_TIMEOUT)
def fetch_news():
    try:
        articles, error = news_service.get_news()
        
        if error:
            logger.error(f"Service returned error: {error}")
            return jsonify({"error": error}), 502

        logger.info(f"Successfully fetched {len(articles)} articles.")
        return jsonify({
            "status": "success",
            "count": len(articles),
            "articles": articles
        }), 200

    except requests.exceptions.Timeout:
        logger.error("Request timed out in route handler")
        return jsonify({"error": "Request timed out"}), 504
    except requests.exceptions.RequestException:
        logger.error("External API error in route handler")
        return jsonify({"error": "External API error"}), 502
    except Exception as e:
        logger.exception(f"Internal server error: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    logger.info(f"Starting NewsAPI on {Config.HOST}:{Config.PORT}")
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
