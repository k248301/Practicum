from selenium.webdriver.common.by import By

class LoginLocators:
    TOGGLE_LINK = (By.ID, "toggle-link")
    LOGIN_FORM = (By.ID, "login-form")
    LOGIN_EMAIL = (By.CLASS_NAME, "in-email")
    LOGIN_PASSWORD = (By.CLASS_NAME, "in-password")
    LOGIN_SUBMIT = (By.CSS_SELECTOR, "#login-form input[type='submit']")
    
    SIGNUP_FORM = (By.ID, "signup-form")
    SIGNUP_EMAIL = (By.CLASS_NAME, "up-email")
    SIGNUP_PASSWORD = (By.CLASS_NAME, "up-password")
    SIGNUP_CONFIRM = (By.CLASS_NAME, "up-confirm-password")
    SIGNUP_SUBMIT = (By.CSS_SELECTOR, "#signup-form input[type='submit']")
    ERROR_BOX = (By.ID, "error-box")
    ERROR_MESSAGE = (By.ID, "error-message")

class HeaderLocators:
    HOME_LINK = (By.LINK_TEXT, "Home")
    MARKET_LINK = (By.LINK_TEXT, "Market")
    NEWS_LINK = (By.LINK_TEXT, "News")
    TRADES_LINK = (By.LINK_TEXT, "Trades")
    LOGOUT_BUTTON = (By.ID, "logout-button")

class HomeLocators:
    HERO_SECTION = (By.CLASS_NAME, "hero-section")
    GET_STARTED_BTN = (By.CLASS_NAME, "hero-btn")
    VISION_SECTION = (By.CLASS_NAME, "vision-mission")

class MarketLocators:
    MARKET_TABLE = (By.ID, "marketDataTable")
    TABLE_ROWS = (By.CSS_SELECTOR, "#marketDataTable tbody tr")
    GRAPH_MODAL = (By.ID, "graphModal")
    CLOSE_MODAL = (By.ID, "closeGraphModal")

class NewsLocators:
    MAIN_ARTICLE = (By.ID, "mainArticle")
    SIDE_ARTICLES = (By.ID, "sideArticles")
    SLIDER = (By.ID, "slider")
    NEXT_BTN = (By.CLASS_NAME, "next")
    PREV_BTN = (By.CLASS_NAME, "prev")

class TradeLocators:
    TRADES_TABLE = (By.ID, "tradesDataTable")
    CONFIG_BUTTON = (By.ID, "configButton")
    BOT_BUTTON = (By.ID, "botButton")
    CONFIG_MODAL = (By.ID, "configModal")
    STOP_LOSS = (By.ID, "stopLoss")
    TAKE_PROFIT = (By.ID, "takeProfit")
    MAX_VOLUME = (By.ID, "maxVolume")
    MIN_VOLUME = (By.ID, "minVolume")
    MAX_TRADES = (By.ID, "maxTrades")
    SAVE_CHANGES = (By.CLASS_NAME, "btn-done")
    CANCEL_CHANGES = (By.CLASS_NAME, "btn-cancel")
