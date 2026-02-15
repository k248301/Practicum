import requests
from requests.adapters import HTTPAdapter, Retry
import random
from datetime import datetime, timedelta
import logging

class NewsService:
    def __init__(self, api_key):
        self.api_key = api_key
        self.logger = logging.getLogger("NewsAPI.Service")
        self._session = self._create_session()

    def _create_session(self):
        session = requests.Session()
        retries = Retry(
            total=5,
            backoff_factor=0.3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        session.mount("https://", HTTPAdapter(max_retries=retries))
        return session

    def _build_url(self):
        queries = ["cryptotrading", "cryptocurrency", "bitcoin", "ethereum"]
        query_string = random.choice(queries)
        
        days = 2
        sort_by = "relevance"
        language = "en"
        page_size = 20

        to_date = datetime.utcnow()
        to_str_date = to_date.strftime("%Y-%m-%d")
        from_date = to_date - timedelta(days=days)
        from_str_date = from_date.strftime("%Y-%m-%d")

        params = {
            "q": query_string,
            "from": from_str_date,
            "to": to_str_date,
            "language": language,
            "sortBy": sort_by,
            "pageSize": page_size,
            "apiKey": self.api_key
        }
        return "https://newsapi.org/v2/everything", params

    def get_news(self):
        base_url, params = self._build_url()
        log_params = params.copy()
        log_params["apiKey"] = "***"
        self.logger.info(f"Auto-fetching news | url={base_url} | params={log_params}")
        
        try:
            response = self._session.get(base_url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            if "articles" not in data:
                self.logger.error("Invalid response from News API: no articles field")
                return None, "Invalid response from news service"
            
            return data["articles"], None

        except requests.exceptions.Timeout:
            self.logger.error("News API request timed out")
            raise
        except requests.exceptions.RequestException as e:
            self.logger.error(f"News API request failed: {e}")
            raise
        except Exception as e:
            self.logger.exception("Unexpected error during news fetch")
            raise
