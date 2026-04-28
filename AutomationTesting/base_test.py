import pytest
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os
import time

class BaseTest:
    BASE_URL = "http://127.0.0.1:5500/Cryptoflux"  # Frontend recommended port

    @pytest.fixture(autouse=True)
    def setup_driver(self, request):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        driver = webdriver.Chrome(options=options)
        driver.maximize_window()
        driver.implicitly_wait(15)
        
        # Set on instance and class if applicable
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)
        if request.cls:
            request.cls.driver = driver
            request.cls.wait = self.wait
            
        yield driver
        driver.quit()

    def wait_for_element(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def wait_for_clickable(self, locator):
        return self.wait.until(EC.element_to_be_clickable(locator))

    def take_screenshot(self, name):
        if not os.path.exists("screenshots"):
            os.makedirs("screenshots")
        self.driver.save_screenshot(f"screenshots/{name}.png")

    def login(self, email, password):
        self.driver.get(f"{self.BASE_URL}/index.html")
        from locators import LoginLocators
        # Wait for the login form specifically
        self.wait_for_element(LoginLocators.LOGIN_FORM)
        self.driver.find_element(*LoginLocators.LOGIN_EMAIL).send_keys(email)
        self.driver.find_element(*LoginLocators.LOGIN_PASSWORD).send_keys(password)
        self.driver.find_element(*LoginLocators.LOGIN_SUBMIT).click()
        # Wait for redirection to home (header is in all pages except index)
        self.wait_for_element((By.ID, "header"))
        # Ensure header components (Home link) are loaded
        from locators import HeaderLocators
        self.wait_for_element(HeaderLocators.HOME_LINK)
        time.sleep(0.5)
