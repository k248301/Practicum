import { apiClient } from "./apiClient.js";
import { API_CONFIG } from "../core/constants.js";

/**
 * News Service - Fetches cryptocurrency news
 */
class NewsService {
    /**
     * Fetch news articles
     * @returns {Promise<Array>}
     */
    async fetchNews() {
        try {
            const response = await apiClient.get(`${API_CONFIG.NEWS_API_URL}/fetch-news`);
            return response.articles || [];
        } catch (error) {
            console.error("Failed to fetch news:", error);
            throw new Error("Unable to fetch news");
        }
    }

    /**
     * Filter articles that have valid images and URLs
     * @param {Array} articles - Array of news articles
     * @returns {Array}
     */
    filterValidArticles(articles) {
        return articles.filter(
            (item) =>
                item.urlToImage &&
                item.urlToImage.trim() !== "" &&
                item.url &&
                item.url.trim() !== ""
        );
    }
}

// Export singleton instance
export const newsService = new NewsService();
