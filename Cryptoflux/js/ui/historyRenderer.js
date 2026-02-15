import {
    DOM_IDS,
    TRADE_TYPE_NAMES,
    CLOSE_REASON,
    CHART_COLORS,
} from "../core/constants.js";
import { formatProfit, formatPrice } from "../utils/formatters.js";

/**
 * History Renderer - Renders history trades table
 */
class HistoryRenderer {
    constructor() {
        this.tableBody = null;
    }

    /**
     * Initialize the renderer
     */
    initialize() {
        const table = document.getElementById(DOM_IDS.HISTORY_TABLE);
        if (table) {
            this.tableBody = table.querySelector("tbody");
        } else {
            console.warn("History table not found");
        }
    }

    /**
     * Render or update a history row
     * @param {Object} data - History data
     */
    renderHistory(data) {
        if (!this.tableBody) {
            console.warn("Table body not initialized");
            return;
        }

        const rowId = "history-" + data.ticket;
        let row = document.getElementById(rowId);

        if (!row) {
            row = this.createHistoryRow(data, rowId);
            this.tableBody.appendChild(row);
        } else {
            this.updateHistoryRow(row, data);
        }
    }

    /**
     * Create a new history row
     * @param {Object} data - History data
     * @param {string} rowId - Row ID
     * @returns {HTMLTableRowElement}
     */
    createHistoryRow(data, rowId) {
        const row = document.createElement("tr");
        row.id = rowId;

        // Create cells
        const symbolCell = this.createCell(data.symbol);
        const ticketCell = this.createCell(data.ticket);
        const timeCell = this.createCell(data.time);
        const typeCell = this.createCell(TRADE_TYPE_NAMES[data.type] || "Unknown");
        const volumeCell = this.createCell(data.volume);
        const priceCell = this.createCell(formatPrice(data.price));
        const commissionCell = this.createCell(formatPrice(data.commission));
        const swapCell = this.createCell(formatPrice(data.swap));
        const profitCell = this.createCell(formatProfit(data.profit));
        const commentCell = this.createCell(data.comment);

        // Apply styling
        typeCell.style.background = data.type === 0 ? "orange" : "seagreen";

        // Apply reason colors to price cell
        this.applyReasonColors(priceCell, data.reason);

        // Apply profit colors
        if (data.profit !== 0) {
            profitCell.style.color =
                data.profit < 0 ? CHART_COLORS.NEGATIVE : CHART_COLORS.POSITIVE;
        }

        // Append cells
        row.appendChild(symbolCell);
        row.appendChild(ticketCell);
        row.appendChild(timeCell);
        row.appendChild(typeCell);
        row.appendChild(volumeCell);
        row.appendChild(priceCell);
        row.appendChild(commissionCell);
        row.appendChild(swapCell);
        row.appendChild(profitCell);
        row.appendChild(commentCell);

        return row;
    }

    /**
     * Update an existing history row
     * @param {HTMLTableRowElement} row - The row to update
     * @param {Object} data - History data
     */
    updateHistoryRow(row, data) {
        const cells = row.cells;
        cells[0].textContent = data.symbol;
        cells[1].textContent = data.ticket;
        cells[2].textContent = data.time;
        cells[3].textContent = TRADE_TYPE_NAMES[data.type] || "Unknown";
        cells[4].textContent = data.volume;
        cells[5].textContent = formatPrice(data.price, 6);
        cells[6].textContent = formatPrice(data.commission, 6);
        cells[7].textContent = formatPrice(data.swap, 6);
        cells[8].textContent = formatProfit(data.profit);
        cells[9].textContent = data.comment;
    }

    /**
     * Create a table cell
     * @param {*} content - Cell content
     * @returns {HTMLTableCellElement}
     */
    createCell(content) {
        const cell = document.createElement("td");
        cell.textContent = content;
        return cell;
    }

    /**
     * Apply colors based on close reason
     * @param {HTMLTableCellElement} cell - Price cell
     * @param {number} reason - Close reason
     */
    applyReasonColors(cell, reason) {
        if (reason === CLOSE_REASON.STOP_LOSS) {
            cell.style.background = "lightpink";
        } else if (reason === CLOSE_REASON.TAKE_PROFIT) {
            cell.style.background = "lightblue";
        }
    }
}

// Export singleton instance
export const historyRenderer = new HistoryRenderer();
