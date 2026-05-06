import pytest
import allure
from base_test import BaseTest
from locators import LoginLocators, HeaderLocators
import time
import random

@allure.feature("Authentication")
class TestAuth(BaseTest):

    @allure.story("User Registration")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_registration_flow(self):
        print("test_registration_flow")
        self.driver.get(f"{self.BASE_URL}/index.html")
        
        # Toggle to Signup
        self.wait_for_clickable(LoginLocators.TOGGLE_LINK).click()
        assert self.driver.find_element(*LoginLocators.SIGNUP_FORM).is_displayed()
        
        # Fill Signup Form
        num = random.randint(0,1000)
        email = f"testuser{num}@example.com"
        self.driver.find_element(*LoginLocators.SIGNUP_EMAIL).send_keys(email)
        self.driver.find_element(*LoginLocators.SIGNUP_PASSWORD).send_keys("TestPass123!")
        self.driver.find_element(*LoginLocators.SIGNUP_CONFIRM).send_keys("TestPass123!")
        
        # Submit
        self.driver.find_element(*LoginLocators.SIGNUP_SUBMIT).click()
        
        # In a real scenario, we'd check for a success message or redirection
        # Since this uses Firebase, it might take a moment
        time.sleep(2) 
        self.take_screenshot("registration_attempt")

    @allure.story("Login and Logout Flow")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_login_logout_flow(self):
        # Login
        print("test_login_logout_flow")
        self.login("k248301@nu.edu.pk", "cyyt7P__")
        
        # Verify Home Page
        assert "Home" in self.driver.title
        assert self.wait_for_element(HeaderLocators.HOME_LINK).is_displayed()
        
        # Logout
        self.wait_for_clickable(HeaderLocators.LOGOUT_BUTTON).click()
        
        # Verify Redirection to Login
        self.wait_for_element(LoginLocators.LOGIN_FORM)
        assert "Login" in self.driver.title

    @allure.story("Invalid Login Attempt")
    @allure.severity(allure.severity_level.NORMAL)
    def test_invalid_login(self):
        print("test_invalid_login")
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

    @allure.story("Invalid Signup Attempt")
    @allure.severity(allure.severity_level.NORMAL)
    def test_invalid_signup(self):
        print("test_invalid_signup")
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

    @allure.story("Empty Form Submission")
    @allure.severity(allure.severity_level.NORMAL)
    def test_empty_form_submission(self):
        print("test_empty_form_submission")
        self.driver.get(f"{self.BASE_URL}/index.html")
        
        # Submit empty login form
        self.driver.find_element(*LoginLocators.LOGIN_SUBMIT).click()
        
        # Verify Error Box handles empty fields
        error_box = self.wait_for_element(LoginLocators.ERROR_BOX)
        assert error_box.is_displayed()
        self.take_screenshot("empty_login_error")

    @allure.story("Invalid Email Format")
    @allure.severity(allure.severity_level.NORMAL)
    def test_invalid_email_format(self):
        print("test_invalid_email_format")
        self.driver.get(f"{self.BASE_URL}/index.html")
        
        # Input improperly formatted email
        self.driver.find_element(*LoginLocators.LOGIN_EMAIL).send_keys("user@domain") # Missing .com
        self.driver.find_element(*LoginLocators.LOGIN_PASSWORD).send_keys("ValidPass123!")
        self.driver.find_element(*LoginLocators.LOGIN_SUBMIT).click()
        
        # Verify Error Box or HTML5 validation catches it
        # Depending on implementation, HTML5 'required' or 'type=email' might prevent submission,
        # or custom JS handles it. If custom JS, the error box will show.
        error_box = self.wait_for_element(LoginLocators.ERROR_BOX)
        assert error_box.is_displayed()
        self.take_screenshot("invalid_email_format_error")
