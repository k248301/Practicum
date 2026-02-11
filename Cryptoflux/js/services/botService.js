import { apiClient } from "./apiClient.js";

/**
 * Bot Service - Manages trading bot API calls
 */
class BotService {
    /**
     * Start the trading bot
     * @returns {Promise<Object>}
     */
    async startBot() {
        try {
            const response = await apiClient.get("/start-bot");
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
            const response = await apiClient.get("/stop-bot");
            return response;
        } catch (error) {
            console.error("Failed to stop bot:", error);
            throw new Error("Unable to stop bot. Network unstable.");
        }
    }

    /**
     * Configure the trading bot
     * @param {Object} config - Bot configuration
     * @param {number} config.stopLoss - Stop loss value
     * @param {number} config.take Profit - Take profit value
     * @param {number} config.maxVolume - Maximum volume
     * @param {number} config.minVolume - Minimum volume
     * @param {number} config.maxTrades - Maximum trades
     * @returns {Promise<Object>}
     */
    async configureBot(config) {
        try {
            const response = await apiClient.post("/configure-bot", config);
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
            const response = await apiClient.get("/bot-status");
            return response;
        } catch (error) {
            console.error("Failed to get bot status:", error);
            throw error;
        }
    }
}

// Export singleton instance
export const botService = new BotService();
