import { DOM_IDS, TRADE_TYPE_NAMES, CHART_COLORS } from "../core/constants.js";
import { formatProfit } from "../utils/formatters.js";

/**
 * Trade Renderer - Renders active trades table
 */
class TradeRenderer {
    constructor() {
        this.tableBody = null;
        this.previousProfits = new Map(); // Store previous profit for arrows
    }

    /**
     * Initialize the renderer
     */
    initialize() {
        const table = document.getElementById(DOM_IDS.TRADES_TABLE);
        if (table) {
            this.tableBody = table.querySelector("tbody");
        } else {
            console.warn("Trades table not found");
        }
    }

    /**
     * Render or update a trade row
     * @param {Object} data - Trade data
     */
    renderTrade(data) {
        if (!this.tableBody) {
            console.warn("Table body not initialized");
            return;
        }

        let row = document.getElementById(data.ticket);

        if (!row) {
            row = this.createTradeRow(data);
            this.tableBody.appendChild(row);
        } else {
            this.updateTradeRow(row, data);
        }
    }

    /**
     * Create a new trade row
     * @param {Object} data - Trade data
     * @returns {HTMLTableRowElement}
     */
    createTradeRow(data) {
        const row = document.createElement("tr");
        row.id = data.ticket;

        const fields = [
            { key: "symbol", value: data.symbol },
            { key: "ticket", value: data.ticket },
            { key: "time", value: data.time },
            { key: "type", value: TRADE_TYPE_NAMES[data.type] || "Unknown" },
            { key: "volume", value: data.volume },
            { key: "tradePrice", value: data.tradePrice },
            { key: "stopLoss", value: data.stopLoss },
            { key: "takeProfit", value: data.takeProfit },
            { key: "price", value: data.price },
            { key: "profit", value: formatProfit(data.profit) },
            { key: "change", value: data.change.toFixed(2) },
            { key: "identity", value: data.identity },
        ];

        fields.forEach((field) => {
            const td = document.createElement("td");
            td.textContent = field.value;
            if (field.key === "profit") {
                td.classList.add("profit-cell");
            }
            row.appendChild(td);
        });

        // Add action button
        const actionCell = document.createElement("td");
        const viewBtn = document.createElement("button");
        viewBtn.className = "viewBtn";
        viewBtn.textContent = "View";
        viewBtn.onclick = () => this.onViewChart(data.ticket);
        actionCell.appendChild(viewBtn);
        row.appendChild(actionCell);

        // Store initial profit
        this.previousProfits.set(data.ticket, data.profit);

        return row;
    }

    /**
     * Update an existing trade row
     * @param {HTMLTableRowElement} row - The row to update
     * @param {Object} data - Trade data
     */
    updateTradeRow(row, data) {
        const cells = row.cells;

        // Update fields
        cells[2].textContent = data.time; // time
        cells[3].textContent = TRADE_TYPE_NAMES[data.type] || "Unknown"; // type
        cells[4].textContent = data.volume; // volume
        cells[5].textContent = data.tradePrice; // tradePrice
        cells[6].textContent = data.stopLoss; // stopLoss
        cells[7].textContent = data.takeProfit; // takeProfit
        // price column NOT updated (as per original code)

        // Update profit with arrows and colors
        const profitCell = cells[9];
        const prevProfit = this.previousProfits.get(data.ticket) || data.profit;

        if (data.profit > prevProfit) {
            profitCell.style.color = CHART_COLORS.POSITIVE;
            profitCell.innerHTML = `&#9650; ${formatProfit(data.profit)}`;
        } else if (data.profit < prevProfit) {
            profitCell.style.color = CHART_COLORS.NEGATIVE;
            profitCell.innerHTML = `&#9660; ${formatProfit(data.profit)}`;
        } else {
            profitCell.style.color = "black";
            profitCell.innerHTML = formatProfit(data.profit);
        }

        this.previousProfits.set(data.ticket, data.profit);

        // Update change
        cells[10].textContent = data.change.toFixed(2);

        // Update identity
        cells[11].textContent = data.identity;
    }

    /**
     * Set the callback for view chart button
     * @param {Function} callback - Callback function(ticket)
     */
    setViewChartCallback(callback) {
        this.onViewChart = callback;
    }
}

// Export singleton instance
export const tradeRenderer = new TradeRenderer();
