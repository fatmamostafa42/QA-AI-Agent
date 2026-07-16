from app.automation.playwright.browser import BrowserManager
from app.automation.playwright.login import LoginManager
from app.automation.playwright.crawler import Crawler
from app.exporters.json_exporter import JsonExporter


LOGIN_URL = (
    "https://opensource-demo.orangehrmlive.com/web/index.php/auth/login"
)


def main():

    with BrowserManager(headless=False) as browser:

        login = LoginManager(
            browser=browser,
            login_url=LOGIN_URL,
        )

        login.ensure_login()

        crawler = Crawler(browser.page)

        exploration_data = crawler.crawl()

        exporter = JsonExporter()

        exporter.export(exploration_data)

        print("\n" + "=" * 60)
        print("QA Web Agent finished successfully.")
        print("=" * 60)

        input("\nPress ENTER to close...")


if __name__ == "__main__":
    main()