import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

class BaseTest:
    BASE_URL = "http://localhost:5000"  # Assuming Flask runs on 5000

    @pytest.fixture(autouse=True)
    def setup(self):
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless")  # Uncomment for headless execution
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        self.driver.maximize_window()
        self.driver.implicitly_wait(10)
        self.wait = WebDriverWait(self.driver, 10)
        yield
        self.driver.quit()

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
        self.driver.find_element(*LoginLocators.LOGIN_EMAIL).send_keys(email)
        self.driver.find_element(*LoginLocators.LOGIN_PASSWORD).send_keys(password)
        self.driver.find_element(*LoginLocators.LOGIN_SUBMIT).click()
        # Wait for redirection to home
        self.wait_for_element((By.ID, "header"))
