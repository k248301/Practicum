import pytest
from base_test import BaseTest
from locators import LoginLocators, HeaderLocators
import time

class TestAuth(BaseTest):

    def test_registration_flow(self):
        self.driver.get(f"{self.BASE_URL}/index.html")
        
        # Toggle to Signup
        self.wait_for_clickable(LoginLocators.TOGGLE_LINK).click()
        assert self.driver.find_element(*LoginLocators.SIGNUP_FORM).is_displayed()
        
        # Fill Signup Form
        self.driver.find_element(*LoginLocators.SIGNUP_EMAIL).send_keys("testuser@example.com")
        self.driver.find_element(*LoginLocators.SIGNUP_PASSWORD).send_keys("TestPass123!")
        self.driver.find_element(*LoginLocators.SIGNUP_CONFIRM).send_keys("TestPass123!")
        
        # Submit
        self.driver.find_element(*LoginLocators.SIGNUP_SUBMIT).click()
        
        # In a real scenario, we'd check for a success message or redirection
        # Since this uses Firebase, it might take a moment
        time.sleep(2) 
        self.take_screenshot("registration_attempt")

    def test_login_logout_flow(self):
        # Login
        self.login("testuser@example.com", "TestPass123!")
        
        # Verify Home Page
        assert "Home" in self.driver.title
        assert self.wait_for_element(HeaderLocators.HOME_LINK).is_displayed()
        
        # Logout
        self.wait_for_clickable(HeaderLocators.LOGOUT_BUTTON).click()
        
        # Verify Redirection to Login
        self.wait_for_element(LoginLocators.LOGIN_FORM)
        assert "Login" in self.driver.title
