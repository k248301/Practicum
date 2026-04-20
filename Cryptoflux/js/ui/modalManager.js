import { DOM_IDS } from "../core/constants.js";
import { showError } from "./toast.js";

/**
 * Modal Manager - Centralized modal handling
 */
class ModalManager {
    constructor() {
        this.modals = {};
        this.onConfigSave = null;
        this.onConfigOpen = null;
    }

    /**
     * Initialize modal manager
     */
    initialize() {
        // Find modals
        this.modals.config = document.getElementById(DOM_IDS.CONFIG_MODAL);
        this.modals.profit = document.getElementById(DOM_IDS.PROFIT_MODAL);
        this.modals.graph = document.getElementById(DOM_IDS.GRAPH_MODAL);

        // Setup config modal buttons
        this.setupConfigModal();

        // Setup profit modal close button
        this.setupProfitModal();

        // Close modals when clicking outside
        this.setupOutsideClickHandlers();
    }

    /**
     * Setup configuration modal
     */
    setupConfigModal() {
        if (!this.modals.config) return;

        const configButton = document.getElementById(DOM_IDS.CONFIG_BUTTON);
        const cancelBtn = this.modals.config.querySelector(".btn-cancel");
        const doneBtn = this.modals.config.querySelector(".btn-done");

        if (configButton) {
            configButton.onclick = () => this.openConfigModal();
        }

        if (cancelBtn) {
            cancelBtn.onclick = () => this.closeConfigModal();
        }

        if (doneBtn) {
            doneBtn.onclick = () => {
                const success = this.saveConfig();
                if (success) {
                    this.closeConfigModal();
                }
            };
        }

        // Live check for SL/TP changes
        const checkRisk = () => {
            const warningBox = document.getElementById("riskWarning");
            if (!warningBox) return;
            
            const stopLossInput = document.getElementById("stopLoss");
            const takeProfitInput = document.getElementById("takeProfit");
            
            const currSL = parseFloat(stopLossInput?.value || 0);
            const currTP = parseFloat(takeProfitInput?.value || 0);
            
            const origSL = parseFloat(stopLossInput?.dataset.original || 0);
            const origTP = parseFloat(takeProfitInput?.dataset.original || 0);
            
            if (currSL !== origSL || currTP !== origTP) {
                warningBox.classList.remove("hidden");
            } else {
                warningBox.classList.add("hidden");
            }
        };

        const stopLossInput = document.getElementById("stopLoss");
        const takeProfitInput = document.getElementById("takeProfit");
        if (stopLossInput) stopLossInput.addEventListener("input", checkRisk);
        if (takeProfitInput) takeProfitInput.addEventListener("input", checkRisk);
    }

    /**
     * Setup profit modal
     */
    setupProfitModal() {
        if (!this.modals.profit) return;

        const closeBtn = this.modals.profit.querySelector(".close");
        if (closeBtn) {
            closeBtn.onclick = () => this.closeProfitModal();
        }
    }

    /**
     * Setup outside click handlers
     */
    setupOutsideClickHandlers() {
        window.onclick = (event) => {
            if (event.target === this.modals.profit) {
                this.closeProfitModal();
            }
            if (event.target === this.modals.config) {
                this.closeConfigModal();
            }
            if (event.target === this.modals.graph) {
                this.closeGraphModal();
            }
        };
    }

    /**
     * Open configuration modal.
     * Fires the onConfigOpen callback (if set) first so the form can be
     * pre-populated with live data before the user sees it.
     */
    async openConfigModal() {
        if (!this.modals.config) return;

        // Pre-populate the form if a callback is registered
        if (this.onConfigOpen) {
            try {
                await this.onConfigOpen();
            } catch (error) {
                console.warn("Could not load config before opening modal:", error);
            }
        }

        this.modals.config.style.display = "flex";
    }

    /**
     * Close configuration modal
     */
    closeConfigModal() {
        if (this.modals.config) {
            this.modals.config.style.display = "none";
        }
    }

    /**
     * Save configuration
     * @returns {boolean} True if successful, false if validations failed
     */
    saveConfig() {
        if (!this.modals.config) return false;

        const stopLossInput = document.getElementById("stopLoss");
        const takeProfitInput = document.getElementById("takeProfit");

        const config = {
            stopLoss: parseFloat(
                stopLossInput?.value || 0
            ),
            takeProfit: parseFloat(
                takeProfitInput?.value || 0
            ),
            maxVolume: parseFloat(
                document.getElementById("maxVolume")?.value || 0
            ),
            minVolume: parseFloat(
                document.getElementById("minVolume")?.value || 0
            ),
            maxTrades: parseInt(
                document.getElementById("maxTrades")?.value || 0,
                10
            ),
        };

        // Validations
        if (config.stopLoss < 1 || config.stopLoss > 100) {
            showError("Stop Loss must be between 1% and 100%.");
            return false;
        }

        if (config.takeProfit < 1 || config.takeProfit > 100) {
            showError("Take Profit must be between 1% and 100%.");
            return false;
        }

        if (config.maxTrades < 1 || config.maxTrades > 20) {
            showError("Max Trades must be between 1 and 20.");
            return false;
        }

        if (config.minVolume < 0.01 || config.minVolume > 1) {
            showError("Min Volume must be between 0.01 and 1.");
            return false;
        }

        if (config.maxVolume < 1 || config.maxVolume > 5) {
            showError("Max Volume must be between 1 and 5.");
            return false;
        }

        if (config.minVolume > config.maxVolume) {
            showError("Min Volume cannot be greater than Max Volume.");
            return false;
        }

        // Ensure warning resets on close/reopen or when successfully saved
        document.getElementById("riskWarning")?.classList.add("hidden");

        if (this.onConfigSave) {
            this.onConfigSave(config);
        }

        return true;
    }

    /**
     * Set callback for config save
     * @param {Function} callback - Called with the config object when user clicks Done
     */
    setConfigSaveCallback(callback) {
        this.onConfigSave = callback;
    }

    /**
     * Set async callback invoked before the config modal opens.
     * Useful for fetching the current config and pre-filling the form.
     * @param {Function} callback - async function, no arguments
     */
    setOnConfigOpenCallback(callback) {
        this.onConfigOpen = callback;
    }

    /**
     * Pre-populate the config form with values from the API.
     * @param {Object} config - Config with snake_case keys from the API
     * @param {number} config.stop_loss
     * @param {number} config.take_profit
     * @param {number} config.max_volume
     * @param {number} config.min_volume
     * @param {number} config.max_trades
     */
    populateConfigForm(config) {
        const set = (id, val, storeOriginal = false) => {
            const el = document.getElementById(id);
            if (el && val !== undefined) {
                el.value = val;
                if (storeOriginal) {
                    el.dataset.original = val;
                }
            } // end if
        };
        set("stopLoss",   config.stop_loss, true);
        set("takeProfit", config.take_profit, true);
        set("maxVolume",  config.max_volume);
        set("minVolume",  config.min_volume);
        set("maxTrades",  config.max_trades);
    }

    /**
     * Open profit modal
     */
    openProfitModal() {
        if (this.modals.profit) {
            this.modals.profit.style.display = "flex";
        }
    }

    /**
     * Close profit modal
     */
    closeProfitModal() {
        if (this.modals.profit) {
            this.modals.profit.style.display = "none";
        }
    }

    /**
     * Open graph modal (for market page)
     */
    openGraphModal() {
        if (this.modals.graph) {
            this.modals.graph.style.display = "block";
        }
    }

    /**
     * Close graph modal
     */
    closeGraphModal() {
        if (this.modals.graph) {
            this.modals.graph.style.display = "none";
        }
    }
}

// Export singleton instance
export const modalManager = new ModalManager();
