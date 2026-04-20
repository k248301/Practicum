from playwright.sync_api import Page, expect
from locators import HeaderLocators, TradeLocators

def test_bot_configuration(logged_in_page: Page):
    """Test modifying bot configuration parameters."""
    # Navigate to trades
    logged_in_page.click(HeaderLocators.TRADES_LINK)
    expect(logged_in_page.locator(TradeLocators.TRADES_TABLE)).to_be_visible()
    
    # Open Configuration Modal
    logged_in_page.click(TradeLocators.CONFIG_BUTTON)
    modal = logged_in_page.locator(TradeLocators.CONFIG_MODAL)
    expect(modal).to_be_visible()
    
    # Update Stop Loss and Take Profit
    logged_in_page.fill(TradeLocators.STOP_LOSS, "5.0")
    logged_in_page.fill(TradeLocators.TAKE_PROFIT, "10.0")
    
    # Save Changes
    logged_in_page.click(TradeLocators.SAVE_CHANGES)
    
    # Verify modal closes automatically
    expect(modal).to_be_hidden()

def test_bot_start_stop_controls(logged_in_page: Page):
    """Test starting and stopping the trading bot."""
    logged_in_page.click(HeaderLocators.TRADES_LINK)
    
    bot_btn = logged_in_page.locator(TradeLocators.BOT_BUTTON)
    initial_text = bot_btn.inner_text()
    
    # Start the Bot
    bot_btn.click()
    
    # Ensure text changes (e.g., from "Start Bot" to "Stop Bot")
    expect(bot_btn).not_to_have_text(initial_text)
    
    # Stop the Bot
    bot_btn.click()
    
    # Verify it returns to initial state
    expect(bot_btn).to_have_text(initial_text)