import pytest
import os
import allure
from datetime import datetime

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()

    # set a report attribute for each phase of a call, which can
    # be "setup", "call", "teardown"
    setattr(item, "rep_" + rep.when, rep)

    # check if a test failed
    if rep.when == "call" and rep.failed:
        # Get the driver from the class instance
        driver = getattr(item.instance, "driver", None)
        if driver:
            if not os.path.exists("screenshots"):
                os.makedirs("screenshots")
            
            timestamp = datetime.now().strftime("%H-%M-%S")
            screenshot_name = f"screenshots/failure_{item.name}_{timestamp}.png"
            driver.save_screenshot(screenshot_name)
            
            # Use extra attribute of pytest-html to add screenshot to report
            if hasattr(rep, "extra"):
                import pytest_html
                extra = getattr(rep, "extra", [])
                html = '<div><img src="%s" alt="screenshot" style="width:304px;height:228px;" ' \
                       'onclick="window.open(this.src)" align="right"/></div>' % screenshot_name
                extra.append(pytest_html.extras.html(html))
                rep.extra = extra
            
            # Attach screenshot to Allure report
            with open(screenshot_name, "rb") as f:
                allure.attach(f.read(), name=f"failure_{item.name}", attachment_type=allure.attachment_type.PNG)
