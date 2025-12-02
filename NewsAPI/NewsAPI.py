import os
import logging
import random
import requests
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_compress import Compress
from flask_caching import Cache
from requests.adapters import HTTPAdapter, Retry

# App Initialization
app = Flask(__name__)
CORS(app)
Compress(app)

app.config["CACHE_TYPE"] = "simple"       
app.config["CACHE_DEFAULT_TIMEOUT"] = 120  # 2 minutes cache
cache = Cache(app)

# Logging 
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# External API Key
NEWS_API_KEY = "eec815cd8dbf484b9ad21f9426612a87"

# HTTP Session with Retry Logic
session = requests.Session()
retries = Retry(
    total=5,
    backoff_factor=0.3,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"]
)
session.mount("https://", HTTPAdapter(max_retries=retries))

# Helper Function
def build_news_url():
    queries = ["cryptotrading", "cryptocurrency", "bitcoin", "ethereum"]
    query_string = random.choice(queries)
    
    days = 2
    sort_by = "relevance"
    language = "en"
    page_size = 20

    # DATE RANGE
    to_date = datetime.utcnow()
    from_date = to_date - timedelta(days=days)
    from_str = from_date.strftime("%Y-%m-%d")
    to_str = to_date.strftime("%Y-%m-%d")

    # BUILD NEWS API URL
    api_url = (
        f"https://newsapi.org/v2/everything?"
        f"q={query_string}"
        f"&from={from_str}"
        f"&to={to_str}"
        f"&language={language}"
        f"&sortBy={sort_by}"
        f"&pageSize={page_size}"
        f"&apiKey={NEWS_API_KEY}"
    )
    return api_url


# News Route (Cached)
@app.route("/fetch-news", methods=["GET"])
#@cache.cached(query_string=True)  # Cache per unique request parameters
def fetch_news():
    try:
        # BUILD NEWS API URL
        api_url = build_news_url()
        logging.info(f"Auto-fetching news | api_url={api_url}")
    
        # API Request
        response = session.get(api_url, timeout=5)
        response.raise_for_status()
        data = response.json()

        if "articles" not in data:
            logging.error("Invalid response from News API: no articles field")
            return jsonify({"error": "Invalid response from news service"}), 502

        # Success
        return jsonify({
            "status": "success",
            "count": len(data["articles"]),
            "articles": data["articles"]
        }), 200

    except ValueError:
        return jsonify({"error": "Invalid query parameters"}), 400

    except requests.exceptions.Timeout:
        logging.error("News API request timed out")
        return jsonify({"error": "Request timed out"}), 504

    except requests.exceptions.RequestException as e:
        logging.error(f"News API request failed: {e}")
        return jsonify({"error": "External API error"}), 502

    except Exception as e:
        logging.exception("Unexpected server error")
        return jsonify({"error": "Internal server error"}), 500


# Run Application
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081, debug=False)
