from pathlib import Path

from playwright.sync_api import (
    sync_playwright,
    Browser,
    BrowserContext,
    Page,
)


class BrowserManager:
    def __init__(
        self,
        headless: bool = False,
        slow_mo: int = 0,
        session_file: str = "storage/session.json",
    ):
        self.headless = headless
        self.slow_mo = slow_mo
        self.session_file = Path(session_file)

        self.playwright = None
        self.browser: Browser | None = None
        self.context: BrowserContext | None = None
        self.page: Page | None = None

    def start(self):
        self.playwright = sync_playwright().start()

        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            slow_mo=self.slow_mo,
        )

        if self.session_file.exists():
            self.context = self.browser.new_context(
                storage_state=str(self.session_file)
            )
            print(f"Loaded session: {self.session_file}")
        else:
            self.context = self.browser.new_context()
            print("No saved session found.")

        self.page = self.context.new_page()

        return self.page

    def save_session(self):
        if self.context:
            self.context.storage_state(path=str(self.session_file))
            print(f"Session saved to {self.session_file}")

    def stop(self):
        if self.context:
            self.context.close()

        if self.browser:
            self.browser.close()

        if self.playwright:
            self.playwright.stop()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()