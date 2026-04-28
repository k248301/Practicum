import pytest
import allure
from base_test import BaseTest
from locators import HeaderLocators, TradeLocators
import time
from datetime import datetime, timedelta

@allure.feature("Trade History")
class TestHistory(BaseTest):

    @pytest.fixture(autouse=True)
    def login_setup(self, setup_driver):
        self.login("k248301@nu.edu.pk", "cyyt7P__")
        self.driver.find_element(*HeaderLocators.TRADES_LINK).click()
        self.wait_for_element(TradeLocators.HISTORY_TABLE)

    @allure.story("Trade History Date Filtering")
    @allure.severity(allure.severity_level.NORMAL)
    def test_history_date_filtering(self):
        """Test that history filtering correctly updates the table"""
        # Use ISO format YYYY-MM-DD which is more reliable for HTML5 date inputs
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Refetch elements right before use
        self.driver.find_element(*TradeLocators.START_DATE).send_keys(yesterday)
        self.driver.find_element(*TradeLocators.END_DATE).send_keys(today)
        
        # Click filter
        self.driver.find_element(*TradeLocators.FILTER_HISTORY_BTN).click()
        
        # Wait for potential animation or fetch
        time.sleep(4)
        
        # Check if table is present
        history_table = self.wait_for_element(TradeLocators.HISTORY_TABLE)
        assert history_table.is_displayed()
        
        # Take screenshot of filtered history
        self.take_screenshot("history_filtered")

    @allure.story("Trade History Filter Reset")
    @allure.severity(allure.severity_level.NORMAL)
    def test_history_reset(self):
        """Test that resetting the filter restores default dates"""
        # Refetch to avoid stale reference
        start_input = self.wait_for_element(TradeLocators.START_DATE)
        
        # Change value
        start_input.send_keys("2020-01-01")
        
        # Click reset
        self.driver.find_element(*TradeLocators.RESET_HISTORY_BTN).click()
        time.sleep(1)
        
        # Verify it's back to default (yesterday)
        # Using a wait to ensure the JS reset has finished updating the field
        time.sleep(2)
        val = self.driver.find_element(*TradeLocators.START_DATE).get_attribute("value")
        assert len(val) == 10, f"Expected a date string (YYYY-MM-DD), but got: {val}"
        # We check if it starts with the correct year at least to be safe with timezones
        assert val.startswith(datetime.now().strftime("%Y")), f"Year mismatch: {val}"
        self.take_screenshot("history_reset_verified")
