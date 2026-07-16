import json

from app.automation.playwright.browser import BrowserManager
from app.automation.playwright.login import LoginManager
from app.automation.playwright.explorer import Explorer


LOGIN_URL = (
    "https://opensource-demo.orangehrmlive.com/web/index.php/auth/login"
)


with BrowserManager(headless=False) as browser:

    login = LoginManager(browser, LOGIN_URL)

    login.ensure_login()

    explorer = Explorer(browser.page)

    result = explorer.explore()

    print(json.dumps(result, indent=4, ensure_ascii=False))

    input("\nPress ENTER to close...")