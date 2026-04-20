/**
 * Format a profit value with specified decimal places
 * @param {number} value - The value to format
 * @param {number} decimals - Number of decimal places (default: 6)
 * @returns {string}
 */
export function formatProfit(value, decimals = 6) {
    return value.toFixed(decimals);
}

/**
 * Format a percentage value
 * @param {number} value - The value to format
 * @param {number} decimals - Number of decimal places (default: 2)
 * @returns {string}
 */
export function formatPercent(value, decimals = 2) {
    return value.toFixed(decimals);
}

/**
 * Format a price value
 * @param {number} value - The value to format
 * @param {number} decimals - Number of decimal places (default: 2)
 * @returns {string}
 */
export function formatPrice(value, decimals = 2) {
    return value.toFixed(4);
}

/**
 * Format a date object to time string
 * @param {Date} date - The date to format
 * @returns {string}
 */
export function formatTime(date) {
    return date.toLocaleTimeString();
}

/**
 * Format a date object to date string
 * @param {Date} date - The date to format
 * @returns {string}
 */
export function formatDate(date) {
    return date.toLocaleDateString();
}

/**
 * Format a date object to full date-time string
 * @param {Date} date - The date to format
 * @returns {string}
 */
export function formatDateTime(date) {
    return date.toLocaleString();
}
