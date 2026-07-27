from __future__ import annotations

from typing import Any, Dict, Optional

from playwright.sync_api import Page, Locator, TimeoutError
import time


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

            before_url = self.page.url

            try:
                before_title = self.page.title()
            except Exception:
                before_title = ""

            before_state = {
                "url": before_url,
                "title": before_title
            }

            start_time = time.time()

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

            try:
                self.page.wait_for_load_state(
                "networkidle",
                timeout=3000
                )
            except Exception:
                pass

            after_url = self.page.url

            try:
                after_title = self.page.title()
            except Exception:
                after_title = ""

            after_state = {
                "url": after_url,
                "title": after_title
            }

            result.update({

            "success": True,

            "message": "Executed successfully",

            "old_url": before_url,
            "new_url": after_url,

            "old_title": before_title,
            "new_title": after_title,

            "old_state": before_state,
            "old_state": after_state,

            "navigated": before_url != after_url,

            "execution_time": round(
                time.time() - start_time,
                3
            )

        })

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