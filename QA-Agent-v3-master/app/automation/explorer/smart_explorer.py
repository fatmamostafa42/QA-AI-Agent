# smart_explorer.py

from typing import Dict, Any
from playwright.sync_api import Page

from app.automation.explorer.action_engine import ActionEngine



class SmartExplorer:
    """
    Intelligent Explorer

    Responsible for understanding the current page
    and discovering the possible user actions.
    """

    def __init__(self, page: Page):
        self.page = page

        # Initialize Action Engine
        self.action_engine = ActionEngine(page)

    # =====================================================
    # Analyze Current Page
    # =====================================================

    def analyze_page(self) -> Dict[str, Any]:
        """
        Analyze current page and return high-level information.
        """

        try:
            title = self.page.title()
        except Exception:
            title = ""

        url = self.page.url

        try:
            body = self.page.locator("body").inner_text()
        except Exception:
            body = ""

        body = body.lower()

        # Discover available actions
        actions = self.action_engine.discover_actions()
        print("\n========== ACTIONS ==========")

        for action in actions:
           print(action)

        print("=============================\n")

        return {

            "url": url,

            "title": title,

            "is_login": "login" in url.lower(),

            "has_table": "records found" in body,

            "has_form": (
                self.page.locator("input").count() > 0
                or self.page.locator("textarea").count() > 0
            ),

            "has_menu": self.page.locator("nav").count() > 0,

            "buttons": self.page.locator("button").count(),

            "inputs": self.page.locator("input").count(),

            "links": self.page.locator("a").count(),

            # Smart semantic actions
            "actions": actions
        }