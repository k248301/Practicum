import { socketService } from "./socketService.js";
import { SOCKET_EVENTS } from "../core/constants.js";

/**
 * Trade Service - Manages trade-related socket events
 */
class TradeService {
    constructor() {
        this.tradeUpdateCallbacks = [];
        this.historyUpdateCallbacks = [];
    }

    /**
     * Initialize trade service and subscribe to socket events
     */
    initialize() {
        // Subscribe to trade updates
        socketService.on(SOCKET_EVENTS.TRADES_UPDATE, (data) => {
            this.handleTradeUpdate(data);
        });

        // Subscribe to history updates
        socketService.on(SOCKET_EVENTS.HISTORY_UPDATE, (data) => {
            this.handleHistoryUpdate(data);
        });
    }

    /**
     * Handle incoming trade update
     * @param {Array|Object} data - Trade data from socket (array of trades)
     */
    handleTradeUpdate(data) {
        const trades = Array.isArray(data) ? data : [data];
        trades.forEach((trade) => {
            this.tradeUpdateCallbacks.forEach((callback) => callback(trade));
        });
    }

    /**
     * Handle incoming history update
     * @param {Array|Object} data - History data from socket (array of deals)
     */
    handleHistoryUpdate(data) {
        const deals = Array.isArray(data) ? data : [data];
        deals.forEach((deal) => {
            // Skip invalid data (empty symbol indicates placeholder)
            if (!deal.symbol || deal.symbol === "") {
                return;
            }
            this.historyUpdateCallbacks.forEach((callback) => callback(deal));
        });
    }

    /**
     * Subscribe to trade updates
     * @param {Function} callback - Callback function
     */
    onTradeUpdate(callback) {
        this.tradeUpdateCallbacks.push(callback);
    }

    /**
     * Subscribe to history updates
     * @param {Function} callback - Callback function
     */
    onHistoryUpdate(callback) {
        this.historyUpdateCallbacks.push(callback);
    }

    /**
     * Unsubscribe from trade updates
     * @param {Function} callback - Callback function
     */
    offTradeUpdate(callback) {
        const index = this.tradeUpdateCallbacks.indexOf(callback);
        if (index > -1) {
            this.tradeUpdateCallbacks.splice(index, 1);
        }
    }

    /**
     * Unsubscribe from history updates
     * @param {Function} callback - Callback function
     */
    offHistoryUpdate(callback) {
        const index = this.historyUpdateCallbacks.indexOf(callback);
        if (index > -1) {
            this.historyUpdateCallbacks.splice(index, 1);
        }
    }
}

// Export singleton instance
export const tradeService = new TradeService();
