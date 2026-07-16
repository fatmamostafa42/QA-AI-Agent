from app.automation.playwright.browser import BrowserManager

with BrowserManager(headless=False) as browser:

    browser.page.goto(
        "https://opensource-demo.orangehrmlive.com/web/index.php/auth/login"
    )

    input("Login manually then press ENTER...")

    browser.save_session()