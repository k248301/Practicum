/**
 * Trade Store - Manages active trades state
 */
class TradeStore {
    constructor() {
        this.trades = new Map(); // ticket -> trade data
        this.subscribers = new Set();
    }

    /**
     * Add or update a trade
     * @param {Object} tradeData - Trade data
     */
    upsertTrade(tradeData) {
        const ticket = tradeData.ticket;
        this.trades.set(ticket, tradeData);
        this.notifySubscribers();
    }

    /**
     * Remove a trade
     * @param {string} ticket - Trade ticket
     */
    removeTrade(ticket) {
        this.trades.delete(ticket);
        this.notifySubscribers();
    }

    /**
     * Get a single trade
     * @param {string} ticket - Trade ticket
     * @returns {Object|undefined}
     */
    getTrade(ticket) {
        return this.trades.get(ticket);
    }

    /**
     * Get all trades
     * @returns {Array<Object>}
     */
    getAllTrades() {
        return Array.from(this.trades.values());
    }

    /**
     * Get all trade tickets
     * @returns {Array<string>}
     */
    getAllTickets() {
        return Array.from(this.trades.keys());
    }

    /**
     * Check if trade exists
     * @param {string} ticket - Trade ticket
     * @returns {boolean}
     */
    hasTrade(ticket) {
        return this.trades.has(ticket);
    }

    /**
     * Clear all trades
     */
    clear() {
        this.trades.clear();
        this.notifySubscribers();
    }

    /**
     * Subscribe to store changes
     * @param {Function} callback - Callback function
     */
    subscribe(callback) {
        this.subscribers.add(callback);
    }

    /**
     * Unsubscribe from store changes
     * @param {Function} callback - Callback function
     */
    unsubscribe(callback) {
        this.subscribers.delete(callback);
    }

    /**
     * Notify all subscribers of changes
     */
    notifySubscribers() {
        this.subscribers.forEach((callback) => callback());
    }
}

// Export singleton instance
export const tradeStore = new TradeStore();
