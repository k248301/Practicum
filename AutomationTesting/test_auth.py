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

    def test_invalid_login(self):
        self.driver.get(f"{self.BASE_URL}/index.html")
        
        # Input wrong credentials
        self.driver.find_element(*LoginLocators.LOGIN_EMAIL).send_keys("wrong@example.com")
        self.driver.find_element(*LoginLocators.LOGIN_PASSWORD).send_keys("WrongPass!")
        self.driver.find_element(*LoginLocators.LOGIN_SUBMIT).click()
        
        # Verify Error Box is visible
        error_box = self.wait_for_element(LoginLocators.ERROR_BOX)
        assert error_box.is_displayed()
        
        # Additional check to ensure message has content
        error_message = self.driver.find_element(*LoginLocators.ERROR_MESSAGE)
        assert len(error_message.text) > 0
        self.take_screenshot("invalid_login_error")

    def test_invalid_signup(self):
        self.driver.get(f"{self.BASE_URL}/index.html")
        
        # Toggle to Signup
        self.wait_for_clickable(LoginLocators.TOGGLE_LINK).click()
        self.wait_for_element(LoginLocators.SIGNUP_FORM)
        
        # Fill Signup Form with mismatched passwords
        self.driver.find_element(*LoginLocators.SIGNUP_EMAIL).send_keys("baduser@example.com")
        self.driver.find_element(*LoginLocators.SIGNUP_PASSWORD).send_keys("Pass123!")
        self.driver.find_element(*LoginLocators.SIGNUP_CONFIRM).send_keys("MismatchPass!")
        
        # Submit
        self.driver.find_element(*LoginLocators.SIGNUP_SUBMIT).click()
        
        # Verify Error Box handles the mismatched password 
        error_box = self.wait_for_element(LoginLocators.ERROR_BOX)
        assert error_box.is_displayed()
        self.take_screenshot("invalid_signup_error")
