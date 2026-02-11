/**
 * History Store - Manages closed trades state
 */
class HistoryStore {
    constructor() {
        this.history = new Map(); // ticket -> history data
        this.subscribers = new Set();
    }

    /**
     * Add or update a history record
     * @param {Object} historyData - History data
     */
    upsertHistory(historyData) {
        const ticket = historyData.ticket;
        this.history.set(ticket, historyData);
        this.notifySubscribers();
    }

    /**
     * Get a single history record
     * @param {string} ticket - Trade ticket
     * @returns {Object|undefined}
     */
    getHistory(ticket) {
        return this.history.get(ticket);
    }

    /**
     * Get all history records
     * @returns {Array<Object>}
     */
    getAllHistory() {
        return Array.from(this.history.values());
    }

    /**
     * Check if history exists
     * @param {string} ticket - Trade ticket
     * @returns {boolean}
     */
    hasHistory(ticket) {
        return this.history.has(ticket);
    }

    /**
     * Clear all history
     */
    clear() {
        this.history.clear();
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
export const historyStore = new HistoryStore();
