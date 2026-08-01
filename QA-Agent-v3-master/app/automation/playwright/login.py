from app.automation.playwright.browser import BrowserManager


class LoginManager:

    def __init__(
        self,
        browser: BrowserManager,
        login_url: str,
    ):
        self.browser = browser
        self.login_url = login_url


    @property
    def session_exists(self) -> bool:
        return (
            self.browser.session_file.exists()
            and self.browser.session_file.stat().st_size > 0
        )


    def login_manually(self):
        """
        Manual login flow
        """

        self.browser.page.goto(self.login_url)

        print("=" * 60)
        print("Please login manually.")
        print("After successful login press ENTER.")
        print("=" * 60)

        input()

        self.browser.save_session()


    def is_authenticated(self):
        """
        Temporary authentication check.
        """

        current_url = self.browser.page.url

        print("Current URL:", current_url)

        if "/auth/login" not in current_url.lower():
            print("Login verification passed.")
            return True

        print("Login verification failed.")
        return False


    def ensure_login(self):

        if self.session_exists:
            print("Existing session found.")

            self.browser.page.goto(self.login_url)

            if self.is_authenticated():
                return

            print("Session expired.")
            self.login_manually()

        else:
            print("No valid session found.")
            self.login_manually()