import pytest
from base_test import BaseTest
from locators import HeaderLocators, TradeLocators
import time

class TestBot(BaseTest):

    @pytest.fixture(autouse=True)
    def login_setup(self, setup_driver):
        self.login("testuser@example.com", "TestPass123!")
        self.driver.find_element(*HeaderLocators.TRADES_LINK).click()
        self.wait_for_element(TradeLocators.TRADES_TABLE)

    def test_bot_configuration(self):
        print("test_bot_configuration")
        # Open Modal
        self.wait_for_clickable(TradeLocators.CONFIG_BUTTON).click()
        assert self.wait_for_element(TradeLocators.CONFIG_MODAL).is_displayed()
        
        # Change Values
        sl_input = self.driver.find_element(*TradeLocators.STOP_LOSS)
        sl_input.clear()
        sl_input.send_keys("5.0")
        
        tp_input = self.driver.find_element(*TradeLocators.TAKE_PROFIT)
        tp_input.clear()
        tp_input.send_keys("10.0")
        
        # Save Changes
        self.driver.find_element(*TradeLocators.SAVE_CHANGES).click()
        
        # Verify modal is closed
        time.sleep(5)
        assert not self.driver.find_element(*TradeLocators.CONFIG_MODAL).is_displayed()
        self.take_screenshot("bot_config_saved")

    def test_bot_control(self):
        print("test_bot_control")
        bot_btn = self.wait_for_clickable(TradeLocators.BOT_BUTTON)
        initial_state = bot_btn.get_attribute("data-bot-state")
        
        # Start Bot
        bot_btn.click()
        time.sleep(5)
        assert bot_btn.get_attribute("data-bot-state") != initial_state
        
        # Verify text change (Assuming it changes to "Stop Bot")
        # assert "Stop" in bot_btn.text
        
        # Stop Bot
        bot_btn.click()
        time.sleep(2)
        assert bot_btn.get_attribute("data-bot-state") == initial_state
        self.take_screenshot("bot_control_cycle")

    def test_bot_config_negative_values(self):
        print("test_bot_config_negative_values")
        # Open Modal
        self.wait_for_clickable(TradeLocators.CONFIG_BUTTON).click()
        self.wait_for_element(TradeLocators.CONFIG_MODAL)

        # Negative Volumes
        min_vol_input = self.driver.find_element(*TradeLocators.MIN_VOLUME)
        min_vol_input.clear()
        min_vol_input.send_keys("-1.0")

        sl_input = self.driver.find_element(*TradeLocators.STOP_LOSS)
        sl_input.clear()
        sl_input.send_keys("10.0")

        tp_input = self.driver.find_element(*TradeLocators.TAKE_PROFIT)
        tp_input.clear()
        tp_input.send_keys("5.0") # TP is less than SL, should be rejected ideally

        # Save Changes
        self.driver.find_element(*TradeLocators.SAVE_CHANGES).click()

        # Assuming the UI should prevent this and NOT close the modal
        # Check that the modal is still displayed
        time.sleep(1)
        assert self.driver.find_element(*TradeLocators.CONFIG_MODAL).is_displayed()
        
        # Take screenshot of the state
        self.take_screenshot("bot_config_negative_rejected")

        # Cleanup: close modal
        self.driver.find_element(*TradeLocators.CANCEL_CHANGES).click()

