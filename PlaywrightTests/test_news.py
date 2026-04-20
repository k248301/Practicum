from playwright.sync_api import Page, expect
from locators import HeaderLocators, NewsLocators

def test_news_page_layout_visibility(logged_in_page: Page):
    """Test that all major news sections render correctly."""
    logged_in_page.click(HeaderLocators.NEWS_LINK)
    
    # Verify components
    expect(logged_in_page.locator(NewsLocators.MAIN_ARTICLE)).to_be_visible()
    expect(logged_in_page.locator(NewsLocators.SIDE_ARTICLES)).to_be_visible()
    expect(logged_in_page.locator(NewsLocators.SLIDER)).to_be_visible()

def test_news_slider_navigation(logged_in_page: Page):
    """Test the carousel Next and Prev button scrolling."""
    logged_in_page.click(HeaderLocators.NEWS_LINK)
    slider = logged_in_page.locator(NewsLocators.SLIDER)
    
    # Give the page a moment to fetch news data from the API
    logged_in_page.wait_for_timeout(2000)
    
    # Get initial scroll position using JavaScript
    initial_scroll = slider.evaluate("el => el.scrollLeft")
    
    # Click Next
    logged_in_page.click(NewsLocators.NEXT_BTN)
    logged_in_page.wait_for_timeout(1000) # Wait for CSS scroll animation
    
    scrolled_right = slider.evaluate("el => el.scrollLeft")
    assert scrolled_right > initial_scroll, "Slider did not scroll to the right!"
    
    # Click Prev
    logged_in_page.click(NewsLocators.PREV_BTN)
    logged_in_page.wait_for_timeout(1000)
    
    scrolled_left = slider.evaluate("el => el.scrollLeft")
    assert scrolled_left < scrolled_right, "Slider did not scroll back to the left!"