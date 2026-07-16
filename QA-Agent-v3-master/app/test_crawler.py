import json

from app.automation.playwright.browser import BrowserManager
from app.automation.playwright.login import LoginManager
from app.automation.playwright.crawler import Crawler


LOGIN_URL = (
    "https://opensource-demo.orangehrmlive.com/web/index.php/auth/login"
)


with BrowserManager(headless=False) as browser:

    login = LoginManager(browser, LOGIN_URL)

    login.ensure_login()

    crawler = Crawler(browser.page)

    pages = crawler.crawl(max_pages=10)

    print(json.dumps(pages, indent=4, ensure_ascii=False))

    input("\nPress ENTER to close...")