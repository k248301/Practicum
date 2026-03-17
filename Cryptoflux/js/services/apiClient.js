import { NGROK_HEADERS } from "../core/constants.js";

/**
 * Generic API client for HTTP requests
 */
class ApiClient {
    /**
     * Make a GET request
     * @param {string} url - Full API URL
     * @param {Object} headers - Additional headers
     * @returns {Promise<any>}
     */
    async get(url, headers = {}) {
        return this.request(url, {
            method: "GET",
            headers: { ...NGROK_HEADERS, ...headers },
        });
    }

    /**
     * Make a POST request
     * @param {string} url - Full API URL
     * @param {Object} data - Request body
     * @param {Object} headers - Additional headers
     * @returns {Promise<any>}
     */
    async post(url, data = null, headers = {}) {
        return this.request(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                ...NGROK_HEADERS,
                ...headers,
            },
            body: data ? JSON.stringify(data) : null,
        });
    }

    /**
     * Make a generic HTTP request
     * @param {string} url - Full URL to fetch
     * @param {Object} options - Fetch options
     * @returns {Promise<any>}
     */
    async request(url, options) {
        try {
            const response = await fetch(url, options);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            // Try to parse as JSON, fallback to text
            const contentType = response.headers.get("content-type");
            if (contentType && contentType.includes("application/json")) {
                return await response.json();
            }
            return await response.text();
        } catch (error) {
            console.error(`API request failed: ${url}`, error);
            throw error;
        }
    }
}

// Export singleton instance
export const apiClient = new ApiClient();
