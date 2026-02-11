// Configuration and Constants for CryptoFlux

// API Endpoints
export const API_CONFIG = {
    SOCKET_URL: "https://evolving-ghastly-rabbit.ngrok-free.app",
    BOT_API_URL: "https://mouse-funky-tahr.ngrok-free.app",
};

// Socket Events
export const SOCKET_EVENTS = {
    TRADES_UPDATE: "On_Trades_Data_Update",
    HISTORY_UPDATE: "On_History_Data_Update",
    MARKET_DATA_UPDATE: "On_Market_Data_Update",
};

// Trade Types
export const TRADE_TYPE = {
    BUY: 0,
    SELL: 1,
};

export const TRADE_TYPE_NAMES = {
    [TRADE_TYPE.BUY]: "Buy",
    [TRADE_TYPE.SELL]: "Sell",
};

// Close Reasons
export const CLOSE_REASON = {
    STOP_LOSS: 4,
    TAKE_PROFIT: 5,
};

// Limits
export const LIMITS = {
    MAX_PROFIT_HISTORY_POINTS: 1000,
    MAX_MARKET_HISTORY_POINTS: 500,
};

// Timeframes (in minutes)
export const TIMEFRAME = {
    ONE_MINUTE: 1,
    FIVE_MINUTES: 5,
    FIFTEEN_MINUTES: 15,
    ALL: 0,
};

// API Headers
export const NGROK_HEADERS = {
    "ngrok-skip-browser-warning": "69420",
};

// Chart Colors
export const CHART_COLORS = {
    PROFIT: "cyan",
    BID: "blue",
    ASK: "red",
    POSITIVE: "blue",
    NEGATIVE: "red",
};

// DOM Element IDs
export const DOM_IDS = {
    HEADER: "header",
    FOOTER: "footer",
    TRADES_TABLE: "tradesDataTable",
    HISTORY_TABLE: "historyDataTable",
    MARKET_TABLE: "marketDataTable",
    CONFIG_MODAL: "configModal",
    PROFIT_MODAL: "profitModal",
    GRAPH_MODAL: "graphModal",
    BOT_BUTTON: "botButton",
    CONFIG_BUTTON: "configButton",
    LOGOUT_BUTTON: "logout-button",
    MENU_TOGGLE: "menuToggle",
};
