import pytest
from base_test import BaseTest
from locators import HeaderLocators, HomeLocators, MarketLocators, NewsLocators
import time

class TestDashboard(BaseTest):

    @pytest.fixture(autouse=True)
    def login_setup(self, setup_driver):
        self.login("testuser@example.com", "TestPass123!")

    def test_ui_general_checks(self):
        print("test_ui_general_checks")
        # Check components visibility
        time.sleep(1) # Allow page initialization
        assert self.wait_for_element(HeaderLocators.HOME_LINK).is_displayed()
        assert self.driver.find_element(*HomeLocators.HERO_SECTION).is_displayed()
        assert self.driver.find_element(*HomeLocators.VISION_SECTION).is_displayed()
        time.sleep(5)
        
        # Check navigation
        self.driver.find_element(*HeaderLocators.MARKET_LINK).click()
        time.sleep(5)
        assert "Market" in self.driver.title
        time.sleep(5)

        self.driver.find_element(*HeaderLocators.NEWS_LINK).click()
        time.sleep(5)
        assert "News" in self.driver.title

    def test_news_feed(self):
        print("test_news_feed")
        self.driver.find_element(*HeaderLocators.NEWS_LINK).click()
        
        # Verify news content is loaded
        # Note: Depending on API speed, we might need a longer wait
        time.sleep(5)
        assert self.wait_for_element(NewsLocators.MAIN_ARTICLE).is_displayed()
        time.sleep(5)
        # Test slider
        slider = self.driver.find_element(*NewsLocators.SLIDER)
        initial_scroll = slider.get_attribute("scrollLeft")
        self.driver.find_element(*NewsLocators.NEXT_BTN).click()
        time.sleep(5)
        assert slider.get_attribute("scrollLeft") != initial_scroll

    def test_market_data(self):
        print("test_market_data")
        self.driver.find_element(*HeaderLocators.MARKET_LINK).click()
        
        # Wait for toast "Connected to live market data"
        from selenium.webdriver.support import expected_conditions as EC
        self.wait.until(EC.text_to_be_present_in_element(MarketLocators.TOAST_MESSAGE, "Connected to live market data"))
        
        # Verify table has data
        self.wait_for_element(MarketLocators.MARKET_TABLE)
        rows = self.driver.find_elements(*MarketLocators.TABLE_ROWS)
        
        assert len(rows) > 0, "Market data rows should be populated after connection"
        self.take_screenshot("market_data_table_verified")

    def test_market_graph_view(self):
        print("test_market_graph_view")
        self.driver.find_element(*HeaderLocators.MARKET_LINK).click()
        
        # Wait for rows to be populated and click the first "View" button
        # Using wait_for_clickable directly on the view button locator handles potential table updates
        view_btn = self.wait_for_clickable(MarketLocators.VIEW_BTN)
        view_btn.click()
        
        # Verify graph modal is displayed
        modal = self.wait_for_element(MarketLocators.GRAPH_MODAL)
        assert modal.is_displayed(), "Graph modal should be visible"
        self.take_screenshot("market_graph_modal_open")
        
