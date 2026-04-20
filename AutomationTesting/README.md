# CryptoFlux UI Automation Suite

This folder contains UI automation scripts for the CryptoFlux trading bot application using Selenium WebDriver and Pytest.

## Prerequisites

1.  **Python 3.x**: Ensure Python is installed.
2.  **Chrome Browser**: The scripts are configured to use Google Chrome.
3.  **ChromeDriver**: The scripts use `webdriver-manager` to handle driver installation automatically.

## Setup

Install the required dependencies:

```bash
pip install -r requirements-test.txt
```

## Running Tests

Before running the tests, ensure the CryptoFlux application is running locally (default: `http://localhost:5000`).

To run all tests:

```bash
pytest
```

To run specific test files:

```bash
pytest test_auth.py
pytest test_dashboard.py
pytest test_bot.py
```

## Project Structure

- `base_test.py`: Base configuration for Selenium WebDriver.
- `locators.py`: Centralized storage for CSS selectors and element IDs.
- `test_auth.py`: Tests for Registration, Login, and Logout.
- `test_dashboard.py`: Tests for UI General Checks, News Feed, and Market Data.
- `test_bot.py`: Tests for Bot Configuration and Bot Control.
- `screenshots/`: (Generated) Folder containing screenshots of failed tests or verification points.
