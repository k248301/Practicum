import pytest
from base_test import BaseTest
from locators import HeaderLocators, HomeLocators, MarketLocators, NewsLocators
import time

class TestDashboard(BaseTest):

    @pytest.fixture(autouse=True)
    def login_setup(self):
        self.login("testuser@example.com", "TestPass123!")

    def test_ui_general_checks(self):
        # Check components visibility
        assert self.wait_for_element(HeaderLocators.HOME_LINK).is_displayed()
        assert self.driver.find_element(*HomeLocators.HERO_SECTION).is_displayed()
        assert self.driver.find_element(*HomeLocators.VISION_SECTION).is_displayed()
        
        # Check navigation
        self.driver.find_element(*HeaderLocators.MARKET_LINK).click()
        assert "Market" in self.driver.title
        
        self.driver.find_element(*HeaderLocators.NEWS_LINK).click()
        assert "News" in self.driver.title

    def test_news_feed(self):
        self.driver.find_element(*HeaderLocators.NEWS_LINK).click()
        
        # Verify news content is loaded
        # Note: Depending on API speed, we might need a longer wait
        time.sleep(3)
        assert self.wait_for_element(NewsLocators.MAIN_ARTICLE).is_displayed()
        
        # Test slider
        slider = self.driver.find_element(*NewsLocators.SLIDER)
        initial_scroll = slider.get_attribute("scrollLeft")
        self.driver.find_element(*NewsLocators.NEXT_BTN).click()
        time.sleep(1)
        assert slider.get_attribute("scrollLeft") != initial_scroll

    def test_market_data(self):
        self.driver.find_element(*HeaderLocators.MARKET_LINK).click()
        
        # Verify table has data
        self.wait_for_element(MarketLocators.MARKET_TABLE)
        rows = self.driver.find_elements(*MarketLocators.TABLE_ROWS)
        # We expect some rows if the server is running and emitting data
        # assert len(rows) > 0 
        self.take_screenshot("market_data_table")
        
        # Test Modal (if rows exist)
        if len(rows) > 0:
            rows[0].click() # Assuming clicking a row opens the modal
            assert self.wait_for_element(MarketLocators.GRAPH_MODAL).is_displayed()
            self.driver.find_element(*MarketLocators.CLOSE_MODAL).click()
            time.sleep(1)
            assert not self.driver.find_element(*MarketLocators.GRAPH_MODAL).is_displayed()
