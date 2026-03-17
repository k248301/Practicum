import { apiClient } from "./apiClient.js";
import { API_CONFIG } from "../core/constants.js";

/**
 * Bot Service - Manages trading bot API calls.
 */
class BotService {
    /**
     * Start the trading bot
     * @returns {Promise<Object>}
     */
    async startBot() {
        try {
            const response = await apiClient.get(`${API_CONFIG.BOT_API_URL}/start-bot`);
            return response;
        } catch (error) {
            console.error("Failed to start bot:", error);
            throw new Error("Unable to start bot. Network unstable.");
        }
    }

    /**
     * Stop the trading bot
     * @returns {Promise<Object>}
     */
    async stopBot() {
        try {
            const response = await apiClient.get(`${API_CONFIG.BOT_API_URL}/stop-bot`);
            return response;
        } catch (error) {
            console.error("Failed to stop bot:", error);
            throw new Error("Unable to stop bot. Network unstable.");
        }
    }

    /**
     * Get the current bot configuration from the API
     * @returns {Promise<Object>} Config object with snake_case keys
     */
    async getConfig() {
        try {
            const response = await apiClient.get(`${API_CONFIG.BOT_API_URL}/bot-config`);
            return response.Config; // { stop_loss, take_profit, max_volume, min_volume, max_trades }
        } catch (error) {
            console.error("Failed to get bot config:", error);
            throw new Error("Unable to fetch bot configuration.");
        }
    }

    /**
     * Save bot configuration to the API
     * @param {Object} config - Config with camelCase keys from the UI
     * @param {number} config.stopLoss
     * @param {number} config.takeProfit
     * @param {number} config.maxVolume
     * @param {number} config.minVolume
     * @param {number} config.maxTrades
     * @returns {Promise<Object>}
     */
    async configureBot(config) {
        try {
            // Map camelCase UI fields → snake_case API fields
            const payload = {
                stop_loss: config.stopLoss,
                take_profit: config.takeProfit,
                max_volume: config.maxVolume,
                min_volume: config.minVolume,
                max_trades: config.maxTrades,
            };
            const response = await apiClient.post(
                `${API_CONFIG.BOT_API_URL}/bot-config`,
                payload
            );
            return response;
        } catch (error) {
            console.error("Failed to configure bot:", error);
            throw new Error("Unable to configure bot. Network unstable.");
        }
    }

    /**
     * Get bot status
     * @returns {Promise<Object>}
     */
    async getBotStatus() {
        try {
            const response = await apiClient.get(`${API_CONFIG.BOT_API_URL}/bot-status`);
            return response;
        } catch (error) {
            console.error("Failed to get bot status:", error);
            throw error;
        }
    }
}

// Export singleton instance
export const botService = new BotService();
