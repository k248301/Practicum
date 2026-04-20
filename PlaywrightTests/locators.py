
class LoginLocators:
    TOGGLE_LINK = "#toggle-link"
    LOGIN_FORM = "#login-form"
    LOGIN_EMAIL = ".in-email"
    LOGIN_PASSWORD = ".in-password"
    LOGIN_SUBMIT = "#login-form input[type='submit']"
    
    SIGNUP_FORM = "#signup-form"
    SIGNUP_EMAIL = ".up-email"
    SIGNUP_PASSWORD = ".up-password"
    SIGNUP_CONFIRM = ".up-confirm-password"
    SIGNUP_SUBMIT = "#signup-form input[type='submit']"
    
    ERROR_BOX = "#error-box"
    ERROR_MESSAGE = "#error-message"

class HeaderLocators:
    HEADER_CONTAINER = "#header"  # Adjust if your header has a different ID or tag
    HOME_LINK = "text=Home"
    MARKET_LINK = "text=Market"
    NEWS_LINK = "text=News"
    TRADES_LINK = "text=Trades"
    LOGOUT_BUTTON = "#logout-button"

class NewsLocators:
    MAIN_ARTICLE = "#mainArticle"
    SIDE_ARTICLES = "#sideArticles"
    SLIDER = "#slider"
    NEXT_BTN = ".next"
    PREV_BTN = ".prev"

class TradeLocators:
    TRADES_TABLE = "#tradesDataTable"
    CONFIG_BUTTON = "#configButton"
    BOT_BUTTON = "#botButton"
    CONFIG_MODAL = "#configModal"
    STOP_LOSS = "#stopLoss"
    TAKE_PROFIT = "#takeProfit"
    MAX_VOLUME = "#maxVolume"
    MIN_VOLUME = "#minVolume"
    MAX_TRADES = "#maxTrades"
    SAVE_CHANGES = ".btn-done"
    CANCEL_CHANGES = ".btn-cancel"