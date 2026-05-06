import pytest
import allure
from base_test import BaseTest
from locators import HeaderLocators, TradeLocators
import time

@allure.feature("Data Persistence")
class TestPersistence(BaseTest):

    @pytest.fixture(autouse=True)
    def login_setup(self, setup_driver):
        self.login("k248301@nu.edu.pk", "cyyt7P__")
        self.driver.find_element(*HeaderLocators.TRADES_LINK).click()
        self.wait_for_element(TradeLocators.TRADES_TABLE)

    @allure.story("Config Persistence on Page Refresh")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_config_persistence_on_refresh(self):
        """Verify that bot configuration survives a page refresh"""
        # 1. Open Modal and set a unique value
        self.wait_for_clickable(TradeLocators.CONFIG_BUTTON).click()
        time.sleep(5) # Wait for save API call
        max_trades_input = self.wait_for_element(TradeLocators.MAX_TRADES)
        time.sleep(5) # Wait for save API call
        unique_value = "2"
        max_trades_input.clear()
        time.sleep(5) # Wait for save API call
        max_trades_input.send_keys(unique_value)
        time.sleep(5) # Wait for save API call
        # 2. Save
        self.driver.find_element(*TradeLocators.SAVE_CHANGES).click()
        time.sleep(5) # Wait for save API call
        
        # 3. Refresh Page
        self.driver.refresh()
        time.sleep(5)
        
        # 4. Open Modal again and check value
        self.wait_for_clickable(TradeLocators.CONFIG_BUTTON).click()
        # Refetch input from the new DOM
        time.sleep(5)
        max_trades_input_new = self.wait_for_element(TradeLocators.MAX_TRADES)
        
        # Give a small moment for values to populate from the fetch
        time.sleep(4)
        current_value = max_trades_input_new.get_attribute("value")
        assert current_value == unique_value, f"Expected {unique_value} but got {current_value} after refresh"
        
        self.take_screenshot("config_persistence_verified")
        
        # Cleanup
        self.driver.find_element(*TradeLocators.CANCEL_CHANGES).click()

    @allure.story("Bot Status Persistence on Page Refresh")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_bot_status_persistence(self):
        """Verify that bot 'Running' status persists after refresh"""
        bot_btn = self.wait_for_clickable(TradeLocators.BOT_BUTTON)
        
        # Start bot if not running (state 'stopped')
        if bot_btn.get_attribute("data-bot-state") == "stopped":
            bot_btn.click()
            # Bot startup flow in JS has 4+ seconds of timeouts
            time.sleep(7) 
            
        assert bot_btn.get_attribute("data-bot-state") == "running"
        
        # Refresh
        self.driver.refresh()
        # Give it plenty of time to initialize socket and fetch status
        time.sleep(8) 
        
        # Check again - must refetch after refresh
        bot_btn_after = self.wait_for_clickable(TradeLocators.BOT_BUTTON)
        current_state = bot_btn_after.get_attribute("data-bot-state")
        assert current_state == "running", f"Bot should be running after refresh, but was {current_state}"
        
        # Cleanup: Stop bot
        bot_btn_after.click()
        time.sleep(2)
        self.take_screenshot("bot_status_persistence_verified")
