import { DOM_IDS } from "../core/constants.js";

/**
 * Modal Manager - Centralized modal handling
 */
class ModalManager {
    constructor() {
        this.modals = {};
        this.onConfigSave = null;
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
                this.saveConfig();
                this.closeConfigModal();
            };
        }
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
     * Open configuration modal
     */
    openConfigModal() {
        if (this.modals.config) {
            this.modals.config.style.display = "flex";
        }
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
     */
    saveConfig() {
        if (!this.modals.config) return;

        const config = {
            stopLoss: parseFloat(
                document.getElementById("stopLoss")?.value || 0
            ),
            takeProfit: parseFloat(
                document.getElementById("takeProfit")?.value || 0
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

        if (this.onConfigSave) {
            this.onConfigSave(config);
        }
    }

    /**
     * Set callback for config save
     * @param {Function} callback - Callback function
     */
    setConfigSaveCallback(callback) {
        this.onConfigSave = callback;
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
