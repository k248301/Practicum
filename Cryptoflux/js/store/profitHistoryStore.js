import { LIMITS } from "../core/constants.js";

/**
 * Profit History Store - Manages profit history for charts
 */
class ProfitHistoryStore {
    constructor() {
        this.profitHistory = new Map(); // ticket -> Array of {profit, time}
        this.subscribers = new Map(); // ticket -> Set of callbacks
    }

    /**
     * Add a profit point
     * @param {string} ticket - Trade ticket
     * @param {number} profit - Profit value
     * @param {Date} time - Timestamp
     */
    addProfitPoint(ticket, profit, time = new Date()) {
        if (!this.profitHistory.has(ticket)) {
            this.profitHistory.set(ticket, []);
        }

        const history = this.profitHistory.get(ticket);
        history.push({ profit, time });

        // Keep only last N points to prevent memory issues
        if (history.length > LIMITS.MAX_PROFIT_HISTORY_POINTS) {
            history.shift();
        }

        this.notifySubscribers(ticket);
    }

    /**
     * Get profit history for a ticket
     * @param {string} ticket - Trade ticket
     * @param {number} minutes - Filter by timeframe (0 = all)
     * @returns {Array<{profit: number, time: Date}>}
     */
    getHistory(ticket, minutes = 0) {
        const history = this.profitHistory.get(ticket) || [];

        if (minutes === 0) {
            return history;
        }

        const now = new Date();
        const cutoff = now.getTime() - minutes * 60 * 1000;
        return history.filter((point) => point.time.getTime() >= cutoff);
    }

    /**
     * Get all ticket history
     * @param {string} ticket - Trade ticket
     * @returns {Array<{profit: number, time: Date}>}
     */
    getAllHistory(ticket) {
        return this.profitHistory.get(ticket) || [];
    }

    /**
     * Clear history for a ticket
     * @param {string} ticket - Trade ticket
     */
    clearHistory(ticket) {
        this.profitHistory.delete(ticket);
        this.notifySubscribers(ticket);
    }

    /**
     * Clear all history
     */
    clearAll() {
        this.profitHistory.clear();
        // Notify all subscribers
        this.subscribers.forEach((callbacks, ticket) => {
            this.notifySubscribers(ticket);
        });
    }

    /**
     * Subscribe to profit updates for a specific ticket
     * @param {string} ticket - Trade ticket
     * @param {Function} callback - Callback function
     */
    subscribe(ticket, callback) {
        if (!this.subscribers.has(ticket)) {
            this.subscribers.set(ticket, new Set());
        }
        this.subscribers.get(ticket).add(callback);
    }

    /**
     * Unsubscribe from profit updates
     * @param {string} ticket - Trade ticket
     * @param {Function} callback - Callback function
     */
    unsubscribe(ticket, callback) {
        if (this.subscribers.has(ticket)) {
            this.subscribers.get(ticket).delete(callback);
        }
    }

    /**
     * Notify subscribers for a specific ticket
     * @param {string} ticket - Trade ticket
     */
    notifySubscribers(ticket) {
        if (this.subscribers.has(ticket)) {
            this.subscribers.get(ticket).forEach((callback) => callback());
        }
    }
}

// Export singleton instance
export const profitHistoryStore = new ProfitHistoryStore();
