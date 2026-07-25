from __future__ import annotations

from typing import Any, Dict, Optional

from playwright.sync_api import Page, Locator, TimeoutError


class ExecutionEngine:
    """
    Generic Execution Engine

    Responsible for executing semantic actions produced by
    ActionEngine.

    It contains NO business logic.

    It only executes actions.

    Future:
        - Playwright
        - Appium
        - Selenium
    """

    def __init__(self, page: Page):
        self.page = page

    # =====================================================
    # Public API
    # =====================================================

    def execute(
        self,
        action: Dict[str, Any],
        value: Optional[str] = None,
    ) -> Dict[str, Any]:

        result = {
            "success": False,
            "action": action.get("action"),
            "locator": action.get("locator"),
            "message": "",
            "exception": None,
        }

        try:

            locator = self._resolve_locator(
                action["locator"]
            )

            action_name = (
                action["action"]
                .lower()
                .strip()
            )

            if action_name in (
                "navigate",
                "click",
                "submit",
                "create",
                "edit",
                "delete",
                "save",
                "cancel",
                "close",
                "next",
                "previous",
                "search",
                "filter",
                "refresh",
                "download",
                "upload",
            ):

                locator.click(timeout=5000)

            elif action_name in (
                "fill",
                "input",
            ):

                locator.fill(value or "")

            elif action_name == "select":

                locator.select_option(value or "")

            elif action_name == "check":

                locator.check()

            elif action_name == "uncheck":

                locator.uncheck()

            else:

                return {
                    **result,
                    "message": f"Unsupported action: {action_name}"
                }

            result["success"] = True
            result["message"] = "Executed successfully"

        except TimeoutError as ex:

            result["message"] = "Execution timeout"
            result["exception"] = str(ex)

        except Exception as ex:

            result["message"] = "Execution failed"
            result["exception"] = str(ex)

        return result

    # =====================================================
    # Locator Resolver
    # =====================================================

    def _resolve_locator(
        self,
        locator: Dict[str, Any],
    ) -> Locator:

        strategy = locator.get("strategy")
        value = locator.get("value")

        if strategy == "text":
            return self.page.get_by_text(
                value,
                exact=False,
            )

        if strategy == "id":
            return self.page.locator(
                f"#{value}"
            )

        if strategy == "name":
            return self.page.locator(
                f'[name="{value}"]'
            )

        if strategy == "placeholder":
            return self.page.get_by_placeholder(
                value
            )

        if strategy == "title":
            return self.page.locator(
                f'[title="{value}"]'
            )

        if strategy == "aria-label":
            return self.page.get_by_label(
                value
            )

        if strategy == "css":
            return self.page.locator(
                value
            )

        raise ValueError(
            f"Unknown locator strategy: {strategy}"
        )