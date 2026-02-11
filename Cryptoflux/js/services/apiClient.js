import { NGROK_HEADERS, API_CONFIG } from "../core/constants.js";

/**
 * Generic API client for HTTP requests
 */
class ApiClient {
    constructor() {
        this.baseURL = API_CONFIG.BOT_API_URL;
    }

    /**
     * Make a GET request
     * @param {string} endpoint - API endpoint
     * @param {Object} headers - Additional headers
     * @returns {Promise<any>}
     */
    async get(endpoint, headers = {}) {
        return this.request(endpoint, {
            method: "GET",
            headers: { ...NGROK_HEADERS, ...headers },
        });
    }

    /**
     * Make a POST request
     * @param {string} endpoint - API endpoint
     * @param {Object} data - Request body
     * @param {Object} headers - Additional headers
     * @returns {Promise<any>}
     */
    async post(endpoint, data = null, headers = {}) {
        return this.request(endpoint, {
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
     * @param {string} endpoint - API endpoint
     * @param {Object} options - Fetch options
     * @returns {Promise<any>}
     */
    async request(endpoint, options) {
        const url = endpoint.startsWith("http")
            ? endpoint
            : `${this.baseURL}${endpoint}`;

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
            console.error(`API request failed: ${endpoint}`, error);
            throw error;
        }
    }
}

// Export singleton instance
export const apiClient = new ApiClient();
