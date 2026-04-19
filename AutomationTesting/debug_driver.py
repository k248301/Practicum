from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import os

try:
    path = ChromeDriverManager().install()
    print(f"Driver Path: {path}")
    print(f"File exists: {os.path.exists(path)}")
    service = ChromeService(path)
    driver = webdriver.Chrome(service=service)
    print("Driver started successfully")
    driver.quit()
except Exception as e:
    print(f"Error: {e}")
