from playwright.sync_api import Page, expect
from locators import LoginLocators, HeaderLocators
from conftest import BASE_URL

def test_invalid_login_credentials(page: Page):
    """Test login failure with invalid credentials."""
    page.goto(f"{BASE_URL}/index.html")
    
    page.fill(LoginLocators.LOGIN_EMAIL, "wrong@example.com")
    page.fill(LoginLocators.LOGIN_PASSWORD, "WrongPass123")
    page.click(LoginLocators.LOGIN_SUBMIT)
    
    # Verify the error box pops up
    expect(page.locator(LoginLocators.ERROR_BOX)).to_be_visible()

def test_signup_password_mismatch(page: Page):
    """Test that mismatched passwords trigger an error on the signup form."""
    page.goto(f"{BASE_URL}/index.html")
    
    # Toggle to signup form
    page.click(LoginLocators.TOGGLE_LINK)
    expect(page.locator(LoginLocators.SIGNUP_FORM)).to_be_visible()
    
    # Fill signup with mismatched passwords
    page.fill(LoginLocators.SIGNUP_EMAIL, "new@example.com")
    page.fill(LoginLocators.SIGNUP_PASSWORD, "Secure123!")
    page.fill(LoginLocators.SIGNUP_CONFIRM, "Different123!")
    page.click(LoginLocators.SIGNUP_SUBMIT)
    
    # Verify the error box pops up
    expect(page.locator(LoginLocators.ERROR_BOX)).to_be_visible()

def test_logout_functionality(logged_in_page: Page):
    """Test that a logged-in user can successfully log out."""
    # Click Logout
    logged_in_page.click(HeaderLocators.LOGOUT_BUTTON)
    
    # Verify user is redirected back to the login page
    expect(logged_in_page.locator(LoginLocators.LOGIN_FORM)).to_be_visible()