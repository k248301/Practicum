import { socketService } from "../services/socketService.js";
import { tradeService } from "../services/tradeService.js";
import { botService } from "../services/botService.js";
import { tradeStore } from "../store/tradeStore.js";
import { historyStore } from "../store/historyStore.js";
import { profitHistoryStore } from "../store/profitHistoryStore.js";
import { tradeRenderer } from "../ui/tradeRenderer.js";
import { historyRenderer } from "../ui/historyRenderer.js";
import { modalManager } from "../ui/modalManager.js";
import { profitChart } from "../charts/profitChart.js";
import { showToast, showError, showSuccess } from "../ui/toast.js";
import { DOM_IDS, TIMEFRAME } from "../core/constants.js";

/**
 * Trades Page Controller - Orchestrates all components for the trades page
 */
class TradesPage {
    constructor() {
        this.initialized = false;
        this.currentProfitTicket = null;
        this.dummyInterval = null;
        this.socketConnected = false;
    }

    /**
     * Initialize the trades page
     */
    async initialize() {
        if (this.initialized) return;

        try {
            console.log("Initializing trades page...");

            // Initialize UI components
            this.initializeUI();

            // Setup event listeners
            this.setupEventListeners();

            // Setup data flow (before connecting so handlers are ready)
            this.setupDataFlow();

            // Connect to socket
            await this.connectSocket();

            // Initialize tabs
            this.initializeTabs();

            // Only load dummy data if socket connection failed
            if (!this.socketConnected) {
                this.loadDummyData();
            }

            this.initialized = true;
            console.log("Trades page initialized successfully");
        } catch (error) {
            console.error("Failed to initialize trades page:", error);
            showError("Failed to initialize trades page. Please refresh.");
        }
    }

    /**
     * Initialize UI components
     */
    initializeUI() {
        tradeRenderer.initialize();
        historyRenderer.initialize();
        modalManager.initialize();
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Bot button
        const botButton = document.getElementById(DOM_IDS.BOT_BUTTON);
        if (botButton) {
            botButton.onclick = () => this.handleBotToggle();
        }

        // Modal config save
        modalManager.setConfigSaveCallback((config) => this.handleBotConfig(config));

        // Trade renderer view chart callback
        tradeRenderer.setViewChartCallback((ticket) => this.openProfitModal(ticket));

        // Profit modal timeframe buttons
        this.setupTimeframeButtons();
    }

    /**
     * Setup timeframe buttons
     */
    setupTimeframeButtons() {
        const timeframes = [
            { id: "tf1", value: TIMEFRAME.ONE_MINUTE },
            { id: "tf5", value: TIMEFRAME.FIVE_MINUTES },
            { id: "tf15", value: TIMEFRAME.FIFTEEN_MINUTES },
            { id: "tfAll", value: TIMEFRAME.ALL },
        ];

        timeframes.forEach(({ id, value }) => {
            const btn = document.getElementById(id);
            if (btn) {
                btn.onclick = () => this.setTimeframe(value);
            }
        });
    }

    /**
     * Connect to socket server
     */
    async connectSocket() {
        try {
            showToast("Connecting to server...", "info");
            await socketService.connect();
            tradeService.initialize();
            this.socketConnected = true;
            showSuccess("Connected to server");

            // Stop dummy data if it was running
            if (this.dummyInterval) {
                clearInterval(this.dummyInterval);
                this.dummyInterval = null;
            }
        } catch (error) {
            console.warn("Socket connection failed, using dummy data:", error);
            showError("Could not connect to server. Using demo data.");
        }
    }

    /**
     * Setup data flow between services, stores, and UI
     */
    setupDataFlow() {
        // Trade updates: Service → Store → UI
        tradeService.onTradeUpdate((data) => {
            try {
                tradeStore.upsertTrade(data);
                tradeRenderer.renderTrade(data);

                // Add to profit history
                profitHistoryStore.addProfitPoint(data.ticket, data.profit);
            } catch (error) {
                console.error("Error handling trade update:", error);
            }
        });

        // History updates: Service → Store → UI
        tradeService.onHistoryUpdate((data) => {
            try {
                historyStore.upsertHistory(data);
                historyRenderer.renderHistory(data);
            } catch (error) {
                console.error("Error handling history update:", error);
            }
        });
    }

    /**
     * Initialize tabs
     */
    initializeTabs() {
        // Click first tab
        const firstTab = document.querySelector(".tablinks");
        if (firstTab) {
            firstTab.click();
        }
    }

    /**
     * Handle bot toggle (start/stop)
     */
    async handleBotToggle() {
        const botButton = document.getElementById(DOM_IDS.BOT_BUTTON);
        if (!botButton) return;

        const isRunning = botButton.dataset.botState === "running";

        try {
            botButton.disabled = true;
            const response = isRunning
                ? await botService.stopBot()
                : await botService.startBot();

            showSuccess(response.Message || "Bot status updated");

            // Update button state
            if (response.Status === 1) {
                botButton.textContent = "Stop Bot";
                botButton.dataset.botState = "running";
            } else {
                botButton.textContent = "Start Bot";
                botButton.dataset.botState = "stopped";
            }
        } catch (error) {
            showError(error.message || "Failed to update bot status");
        } finally {
            botButton.disabled = false;
        }
    }

    /**
     * Handle bot configuration
     */
    async handleBotConfig(config) {
        try {
            await botService.configureBot(config);
            showSuccess("Bot configuration saved");
        } catch (error) {
            showError("Failed to save configuration");
            console.error("Bot config error:", error);
        }
    }

    /**
     * Open profit modal for a ticket
     */
    openProfitModal(ticket) {
        this.currentProfitTicket = ticket;

        // Update modal title
        const title = document.getElementById("profitModalTitle");
        if (title) {
            title.textContent = `Profit Graph - Ticket ${ticket}`;
        }

        // Open modal
        modalManager.openProfitModal();

        // Create chart
        profitChart.createChart("profitGraphCanvas", ticket);

        // Set default timeframe to All
        this.setTimeframe(TIMEFRAME.ALL);
    }

    /**
     * Set timeframe for profit chart
     */
    setTimeframe(minutes) {
        // Update active button
        document.querySelectorAll(".time-buttons button").forEach((btn) => {
            btn.classList.remove("active");
        });

        const btnId =
            minutes === TIMEFRAME.ALL
                ? "tfAll"
                : `tf${minutes}`;
        const activeBtn = document.getElementById(btnId);
        if (activeBtn) {
            activeBtn.classList.add("active");
        }

        // Update chart
        profitChart.setTimeframe(minutes);
    }

    /**
     * Load dummy data for demonstration
     */
    loadDummyData() {
        const dummyTrades = [
            {
                ticket: "1001",
                symbol: "BTCUSD",
                time: "12:01:15",
                type: 0,
                volume: 0.5,
                tradePrice: 34000,
                stopLoss: 33800,
                takeProfit: 34500,
                price: 34050,
                profit: 25.0,
                change: 0.15,
                identity: "Manual",
            },
            {
                ticket: "1002",
                symbol: "ETHUSD",
                time: "12:01:16",
                type: 1,
                volume: 1,
                tradePrice: 2100,
                stopLoss: 2080,
                takeProfit: 2150,
                price: 2090,
                profit: 10.0,
                change: -0.48,
                identity: "Manual",
            },
            {
                ticket: "1003",
                symbol: "LTCUSD",
                time: "12:01:17",
                type: 0,
                volume: 2,
                tradePrice: 85,
                stopLoss: 82,
                takeProfit: 88,
                price: 84.5,
                profit: -1.0,
                change: -0.59,
                identity: "Manual",
            },
        ];

        // Initial render
        dummyTrades.forEach((trade) => {
            tradeStore.upsertTrade(trade);
            tradeRenderer.renderTrade(trade);
            profitHistoryStore.addProfitPoint(trade.ticket, trade.profit);
        });

        // Simulate live updates
        this.dummyInterval = setInterval(() => {
            dummyTrades.forEach((trade) => {
                trade.profit += (Math.random() - 0.5) * 2;
                trade.change =
                    ((trade.price - trade.tradePrice) / trade.tradePrice) * 100;

                tradeStore.upsertTrade(trade);
                tradeRenderer.renderTrade(trade);
                profitHistoryStore.addProfitPoint(trade.ticket, trade.profit);
            });
        }, 1000);
    }

    /**
     * Cleanup when leaving page
     */
    destroy() {
        if (this.dummyInterval) {
            clearInterval(this.dummyInterval);
        }
        profitChart.destroy();
        socketService.disconnect();
    }
}

// Tab switching function (keeping for inline onclick)
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

// Initialize page
const tradesPage = new TradesPage();
tradesPage.initialize();

// Cleanup on page unload
window.addEventListener("beforeunload", () => {
    tradesPage.destroy();
});
