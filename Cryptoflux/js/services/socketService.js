import { API_CONFIG, SOCKET_EVENTS } from "../core/constants.js";

/**
 * Socket Service - Manages WebSocket connection
 */
class SocketService {
    constructor() {
        this.socket = null;
        this.connected = false;
        this.eventHandlers = new Map();
        this._disconnectListeners = [];
        this._errorListeners = [];
    }

    /**
     * Connect to Socket.IO server
     * @param {string} url - Optional URL override
     * @returns {Promise<void>}
     */
    connect(url = API_CONFIG.SOCKET_URL) {
        return new Promise((resolve, reject) => {
            try {
                if (this.socket && this.connected) {
                    console.log("Socket already connected");
                    resolve();
                    return;
                }

                this.socket = io.connect(url, {
                    extraHeaders: {
                        "ngrok-skip-browser-warning": "true",
                    },
                    withCredentials: true,
                });

                this.socket.on("connect", () => {
                    console.log("Socket.IO connected");
                    this.connected = true;
                    resolve();
                });

                this.socket.on("disconnect", () => {
                    console.log("Socket.IO disconnected");
                    this.connected = false;
                    // Notify all registered disconnect listeners
                    this._disconnectListeners.forEach((cb) => cb());
                });

                this.socket.on("connect_error", (error) => {
                    console.warn("Socket.IO connection error:", error);
                    this.connected = false;
                    // Notify all registered error listeners
                    this._errorListeners.forEach((cb) => cb(error));
                    reject(error);
                });
            } catch (error) {
                console.error("Failed to create socket connection:", error);
                reject(error);
            }
        });
    }

    /**
     * Subscribe to a socket event
     * @param {string} event - Event name
     * @param {Function} handler - Event handler
     */
    on(event, handler) {
        if (!this.socket) {
            console.warn("Socket not initialized");
            return;
        }

        // Store handler for potential cleanup
        if (!this.eventHandlers.has(event)) {
            this.eventHandlers.set(event, []);
        }
        this.eventHandlers.get(event).push(handler);

        this.socket.on(event, handler);
    }

    /**
     * Unsubscribe from a socket event
     * @param {string} event - Event name
     * @param {Function} handler - Event handler
     */
    off(event, handler) {
        if (!this.socket) return;

        this.socket.off(event, handler);

        // Remove from stored handlers
        if (this.eventHandlers.has(event)) {
            const handlers = this.eventHandlers.get(event);
            const index = handlers.indexOf(handler);
            if (index > -1) {
                handlers.splice(index, 1);
            }
        }
    }

    /**
     * Emit an event to the server
     * @param {string} event - Event name
     * @param {*} data - Data to send
     */
    emit(event, data) {
        if (!this.socket || !this.connected) {
            console.warn("Socket not connected, cannot emit:", event);
            return;
        }

        this.socket.emit(event, data);
    }

    /**
     * Check if socket is connected
     * @returns {boolean}
     */
    isConnected() {
        return this.connected;
    }

    /**
     * Register a callback for socket disconnect events.
     * Useful for pages that need to fall back to simulation on connection loss.
     * @param {Function} callback
     */
    onDisconnect(callback) {
        this._disconnectListeners.push(callback);
    }

    /**
     * Register a callback for socket connection error events.
     * @param {Function} callback
     */
    onError(callback) {
        this._errorListeners.push(callback);
    }

    /**
     * Disconnect from socket
     */
    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
            this.connected = false;
            this._disconnectListeners = [];
            this._errorListeners = [];
        }
    }
}

// Export singleton instance
export const socketService = new SocketService();
