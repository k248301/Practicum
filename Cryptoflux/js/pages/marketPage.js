import { socketService } from "../services/socketService.js";
import { SOCKET_EVENTS, DOM_IDS, CHART_COLORS } from "../core/constants.js";
import { showError, showSuccess, showToast } from "../ui/toast.js";

/**
 * Market Page Controller - Real-time market data with Socket.IO and fallback
 */
class MarketPage {
    constructor() {
        this.initialized = false;
        this.marketData = new Map(); // symbol -> current data
        this.priceHistory = new Map(); // symbol -> Array<{bid, ask, last, time, timestamp}>
        this.previousPrices = new Map(); // symbol -> {bid, ask} for color comparison
        this.currentSymbol = null;
        this.chartInstance = null;
        this.updateInterval = null;
        this.usingSocket = false;
        this.currentTimeframe = 0; // 0 = All, otherwise minutes
        this.MAX_HISTORY = 500; // Max history entries per symbol
    }

    /**
     * Initialize the market page
     */
    async initialize() {
        if (this.initialized) return;

        try {
            console.log("Initializing market page...");

            // Initialize UI
            this.setupEventListeners();
            this.initializeTabs();

            // Try socket first, fallback to simulation
            await this.connectSocket();

            this.initialized = true;
            console.log("Market page initialized successfully");
        } catch (error) {
            console.error("Failed to initialize market page:", error);
            showError("Failed to initialize market page. Please refresh.");
        }
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Close modal button
        const closeBtn = document.getElementById("closeGraphModal");
        if (closeBtn) {
            closeBtn.onclick = () => this.closeGraphModal();
        }

        // Click outside modal to close
        const modal = document.getElementById(DOM_IDS.GRAPH_MODAL);
        if (modal) {
            window.onclick = (e) => {
                if (e.target === modal) {
                    this.closeGraphModal();
                }
            };
        }

        // Timeframe buttons
        this.setupTimeframeButtons();
    }

    /**
     * Setup timeframe filter buttons
     */
    setupTimeframeButtons() {
        const timeframes = [
            { id: "marketTf1m", minutes: 1 },
            { id: "marketTf5m", minutes: 5 },
            { id: "marketTf15m", minutes: 15 },
            { id: "marketTfAll", minutes: 0 },
        ];

        timeframes.forEach(({ id, minutes }) => {
            const btn = document.getElementById(id);
            if (btn) {
                btn.onclick = () => this.setTimeframe(minutes);
            }
        });
    }

    /**
     * Connect to socket server with fallback
     */
    async connectSocket() {
        try {
            showToast("Connecting to live market data...", "info", 2000);

            // Create custom socket connection for market data
            const socket = io.connect("https://evolving-ghastly-rabbit.ngrok-free.app");

            socket.on("connect", () => {
                console.log("✅ Connected to market data socket");
                this.usingSocket = true;
                showSuccess("Connected to live market data");
            });

            socket.on("On_Market_Data_Update", (data) => {
                this.handleMarketUpdate(data);
            });

            socket.on("disconnect", () => {
                console.warn("Socket disconnected, falling back to simulation");
                this.usingSocket = false;
                this.startSimulation();
            });

            socket.on("connect_error", (error) => {
                console.warn("Socket connection error:", error);
                this.usingSocket = false;
                this.startSimulation();
            });

            // Wait 3 seconds, if no connection, start simulation
            setTimeout(() => {
                if (!this.usingSocket) {
                    console.log("Socket timeout, using simulation");
                    this.startSimulation();
                }
            }, 3000);
        } catch (error) {
            console.warn("Socket failed, using simulation:", error);
            this.startSimulation();
        }
    }

    /**
     * Start price simulation (fallback mode)
     */
    startSimulation() {
        if (this.updateInterval) return; // Already running

        showToast("Using simulated market data", "warning", 3000);

        const symbols = [
            { symbol: "BTC/USD", bid: 67125.45, ask: 67130.1, last: 67128.22, spread: 4.65 },
            { symbol: "ETH/USD", bid: 3521.18, ask: 3522.4, last: 3521.75, spread: 1.22 },
            { symbol: "XRP/USD", bid: 0.523, ask: 0.526, last: 0.525, spread: 0.003 },
            { symbol: "LTC/USD", bid: 84.65, ask: 84.92, last: 84.81, spread: 0.27 },
            { symbol: "BNB/USD", bid: 598.4, ask: 599.05, last: 598.7, spread: 0.65 },
        ];

        // Initialize
        symbols.forEach((data) => {
            this.handleMarketUpdate(data);
        });

        // Update every second
        this.updateInterval = setInterval(() => {
            symbols.forEach((data) => {
                // Separate random changes for bid and ask
                const bidChange = (Math.random() - 0.5) * 0.02; // ±1% for bid
                const askChange = (Math.random() - 0.5) * 0.02; // ±1% for ask

                data.bid += data.bid * bidChange;
                data.ask += data.ask * askChange;

                // Ensure ask is always higher than bid (maintain spread)
                if (data.ask <= data.bid) {
                    data.ask = data.bid + (data.bid * 0.0001); // 0.01% minimum spread
                }

                data.last = (data.bid + data.ask) / 2;
                data.spread = data.ask - data.bid;

                this.handleMarketUpdate(data);
            });
        }, 1000);

        console.log("✓ Price simulation started");
    }

    /**
     * Handle market data update (from socket or simulation)
     * @param {Object} data - Market data
     */
    handleMarketUpdate(data) {
        try {
            const symbol = data.symbol;

            // Initialize history if new symbol
            if (!this.priceHistory.has(symbol)) {
                this.priceHistory.set(symbol, []);
            }

            // Add to history with timestamp
            const history = this.priceHistory.get(symbol);
            const timestamp = Date.now();
            history.push({
                bid: data.bid,
                ask: data.ask,
                last: data.last || (data.bid + data.ask) / 2,
                time: new Date(),
                timestamp: timestamp,
            });

            // Keep only last 500 entries
            if (history.length > this.MAX_HISTORY) {
                history.shift();
            }

            // Store current data
            this.marketData.set(symbol, data);

            // Update table row (with color changes)
            this.updateOrCreateRow(data);

            // Update chart if this symbol is displayed
            if (this.currentSymbol === symbol && this.chartInstance) {
                this.updateChart();
            }
        } catch (error) {
            console.error("Error handling market update:", error);
        }
    }

    /**
     * Update or create table row with color indicators
     * @param {Object} data - Market data
     */
    updateOrCreateRow(data) {
        const table = document.getElementById("marketDataTable");
        if (!table) return;

        const tbody = table.querySelector("tbody");
        if (!tbody) return;

        const symbol = data.symbol;
        let row = null;

        // Find existing row
        for (let r of tbody.rows) {
            if (r.cells[0].textContent === symbol) {
                row = r;
                break;
            }
        }

        // Create new row if doesn't exist
        if (!row) {
            row = this.createNewRow(data);
            tbody.appendChild(row);
            return;
        }

        // Get previous prices for comparison
        const prev = this.previousPrices.get(symbol) || { bid: data.bid, ask: data.ask };

        // Update ONLY bid and ask columns (cells 2 and 3)
        const bidCell = row.cells[2];
        this.updatePriceCell(bidCell, data.bid, prev.bid, "bid");

        const askCell = row.cells[3];
        this.updatePriceCell(askCell, data.ask, prev.ask, "ask");

        // Store current as previous
        this.previousPrices.set(symbol, { bid: data.bid, ask: data.ask });
    }

    /**
     * Update price cell with color and flash
     * @param {HTMLElement} cell - Table cell
     * @param {number} newPrice - New price
     * @param {number} oldPrice - Previous price
     * @param {string} type - 'bid' or 'ask'
     */
    updatePriceCell(cell, newPrice, oldPrice, type) {
        // Remove existing classes
        cell.classList.remove("price-up", "price-down");

        // Add color and arrow based on direction
        if (newPrice > oldPrice) {
            cell.classList.add("price-up"); // Blue
            cell.innerHTML = `&#9650; ${newPrice.toFixed(2)}`; // ▲ arrow up
        } else if (newPrice < oldPrice) {
            cell.classList.add("price-down"); // Red
            cell.innerHTML = `&#9660; ${newPrice.toFixed(2)}`; // ▼ arrow down
        } else {
            // No change - just update value
            cell.textContent = newPrice.toFixed(2);
        }
    }

    /**
     * Create new table row for a symbol
     * @param {Object} data - Market data
     * @returns {HTMLTableRowElement}
     */
    createNewRow(data) {
        const row = document.createElement("tr");

        const cells = [
            data.symbol,
            new Date().toLocaleTimeString(),
            data.bid.toFixed(2),
            data.ask.toFixed(2),
            (data.last || (data.bid + data.ask) / 2).toFixed(2),
            (data.open || 0).toFixed(2),
            (data.close || 0).toFixed(2),
            (data.high || 0).toFixed(2),
            (data.low || 0).toFixed(2),
            (data.spread || data.ask - data.bid).toFixed(4),
            data.volume || 0,
            data.tickVolume || 0,
        ];

        cells.forEach((text, i) => {
            const cell = document.createElement("td");
            cell.textContent = text;

            // Add class to bid/ask cells
            if (i === 2) cell.className = "bid";
            if (i === 3) cell.className = "ask";

            row.appendChild(cell);
        });

        // Add action button
        const actionCell = document.createElement("td");
        const viewBtn = document.createElement("button");
        viewBtn.className = "viewBtn";
        viewBtn.textContent = "View";
        viewBtn.onclick = () => this.openGraphModal(data.symbol);
        actionCell.appendChild(viewBtn);
        row.appendChild(actionCell);

        return row;
    }

    /**
     * Initialize tabs
     */
    initializeTabs() {
        const firstTab = document.querySelector(".tablinks");
        if (firstTab) {
            firstTab.click();
        }
    }

    /**
     * Open graph modal for a symbol
     * @param {string} symbol - Symbol to display
     */
    openGraphModal(symbol) {
        this.currentSymbol = symbol;
        this.currentTimeframe = 0; // Reset to All

        const modalTitle = document.getElementById("graphModalTitle");
        if (modalTitle) {
            modalTitle.textContent = `${symbol} Price Chart`;
        }

        const modal = document.getElementById(DOM_IDS.GRAPH_MODAL);
        if (modal) {
            modal.style.display = "flex";
        }

        // Set default active button
        this.setTimeframe(0);
    }

    /**
     * Close graph modal
     */
    closeGraphModal() {
        const modal = document.getElementById(DOM_IDS.GRAPH_MODAL);
        if (modal) {
            modal.style.display = "none";
        }

        if (this.chartInstance) {
            this.chartInstance.destroy();
            this.chartInstance = null;
        }

        this.currentSymbol = null;
    }

    /**
     * Set timeframe and update chart
     * @param {number} minutes - Timeframe in minutes (0 = All)
     */
    setTimeframe(minutes) {
        this.currentTimeframe = minutes;

        // Update active button
        document.querySelectorAll(".time-buttons button").forEach((btn) => {
            btn.classList.remove("active");
        });

        const btnId =
            minutes === 0 ? "marketTfAll" : `marketTf${minutes}m`;
        const activeBtn = document.getElementById(btnId);
        if (activeBtn) {
            activeBtn.classList.add("active");
        }

        // Create or update chart
        if (this.currentSymbol) {
            this.createChart(this.currentSymbol);
        }
    }

    /**
     * Filter history by timeframe
     * @param {Array} history - Full price history
     * @param {number} minutes - Timeframe in minutes (0 = All)
     * @returns {Array} Filtered history
     */
    filterHistoryByTimeframe(history, minutes) {
        if (minutes === 0) return history; // All data

        const cutoff = Date.now() - minutes * 60000;
        return history.filter((point) => point.timestamp >= cutoff);
    }

    /**
     * Create price chart with timeframe filtering
     * @param {string} symbol - Symbol to chart
     */
    createChart(symbol) {
        const canvas = document.getElementById("graphCanvas");
        if (!canvas) {
            console.error("Chart canvas not found");
            return;
        }

        const ctx = canvas.getContext("2d");

        // Destroy existing chart
        if (this.chartInstance) {
            this.chartInstance.destroy();
        }

        // Get filtered history
        const fullHistory = this.priceHistory.get(symbol) || [];
        const history = this.filterHistoryByTimeframe(fullHistory, this.currentTimeframe);

        this.chartInstance = new Chart(ctx, {
            type: "line",
            data: {
                labels: history.map((p) => p.time.toLocaleTimeString()),
                datasets: [
                    {
                        label: "Bid",
                        data: history.map((p) => p.bid),
                        borderColor: "#2196f3", // Blue
                        borderWidth: 2,
                        fill: false,
                        tension: 0.1,
                        pointRadius: 0,
                    },
                    {
                        label: "Ask",
                        data: history.map((p) => p.ask),
                        borderColor: "#f44336", // Red
                        borderWidth: 2,
                        fill: false,
                        tension: 0.1,
                        pointRadius: 0,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: false,
                plugins: {
                    legend: {
                        display: true,
                        position: "top",
                    },
                    tooltip: {
                        enabled: true,
                        mode: "index",
                        intersect: false,
                    },
                    zoom: {
                        pan: {
                            enabled: true,
                            mode: "x",
                        },
                        zoom: {
                            wheel: {
                                enabled: true,
                            },
                            pinch: {
                                enabled: true,
                            },
                            mode: "x",
                        },
                    },
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: "Time",
                        },
                        ticks: {
                            maxRotation: 45,
                            minRotation: 0,
                        },
                    },
                    y: {
                        title: {
                            display: true,
                            text: "Price",
                        },
                    },
                },
            },
        });
    }

    /**
     * Update chart with new data
     */
    updateChart() {
        if (!this.chartInstance || !this.currentSymbol) return;

        const fullHistory = this.priceHistory.get(this.currentSymbol) || [];
        const history = this.filterHistoryByTimeframe(fullHistory, this.currentTimeframe);

        this.chartInstance.data.labels = history.map((p) =>
            p.time.toLocaleTimeString()
        );
        this.chartInstance.data.datasets[0].data = history.map((p) => p.bid);
        this.chartInstance.data.datasets[1].data = history.map((p) => p.ask);

        this.chartInstance.update("none");
    }

    /**
     * Cleanup when leaving page
     */
    destroy() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
        if (this.chartInstance) {
            this.chartInstance.destroy();
        }
    }
}

// Tab switching function
window.openTab = function (evt, tabName) {
    document
        .querySelectorAll(".tabcontent")
        .forEach((t) => (t.style.display = "none"));
    document
        .querySelectorAll(".tablinks")
        .forEach((b) => b.classList.remove("active"));
    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.classList.add("active");
};

// Open graph modal function
window.openGraphModal = function (symbol) {
    marketPage.openGraphModal(symbol);
};

// Initialize page
const marketPage = new MarketPage();
marketPage.initialize();

// Cleanup on page unload
window.addEventListener("beforeunload", () => {
    marketPage.destroy();
});
