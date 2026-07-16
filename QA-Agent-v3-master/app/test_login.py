from app.automation.playwright.browser import BrowserManager
from app.automation.playwright.login import LoginManager


LOGIN_URL = (
    "https://opensource-demo.orangehrmlive.com/web/index.php/auth/login"
)


with BrowserManager(headless=False) as browser:

    login = LoginManager(browser, LOGIN_URL)

    login.ensure_login()

    print("Current URL:")
    print(browser.page.url)

    print("Page title:")
    print(browser.page.title())

    input("Press ENTER to close...")