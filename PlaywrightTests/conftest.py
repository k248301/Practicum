import pytest
from playwright.sync_api import Page, expect
from locators import LoginLocators, HeaderLocators

# Updated to match your Live Server port and directory
BASE_URL = "http://127.0.0.1:5500/Cryptoflux" 

@pytest.fixture
def logged_in_page(page: Page) -> Page:
    """Fixture to automatically log in and return an authenticated page instance."""
    page.goto(f"{BASE_URL}/index.html")
    
    # Fill in the login credentials
    page.fill(LoginLocators.LOGIN_EMAIL, "testuser@example.com")
    page.fill(LoginLocators.LOGIN_PASSWORD, "TestPass123!")
    page.click(LoginLocators.LOGIN_SUBMIT)
    
    expect(page.locator(HeaderLocators.HEADER_CONTAINER)).to_be_visible()
    
    return page