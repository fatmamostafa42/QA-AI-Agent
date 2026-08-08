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

            try:
                before_dom = self.page.locator("body").inner_text()[:1000]
            except Exception:
               before_dom = ""

            before_state = {
                "url": before_url,
                "title": before_title,
                "dom": before_dom,
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
                print("=" * 60)
                print("CLICKING:", action["locator"])
                print("COUNT:", locator.count())
                print("URL BEFORE:", self.page.url)
                print("=" * 60)
                print("OUTER HTML:")
                print(locator.first.evaluate("e => e.outerHTML"))

                locator.click(
                    timeout=5000,
                    force=False,      
                )
                print("COUNT:", locator.count())

                for i in range(locator.count()):
                    print(f"\nCandidate {i}")
                    print(locator.nth(i).evaluate("e => e.outerHTML"))
                print("=" * 60)
                print("URL AFTER CLICK:", self.page.url)
                print("=" * 60)

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
                self.page.wait_for_timeout(300)
            except Exception:
                pass

            try:
                self.page.wait_for_load_state(
                "domcontentloaded",
                timeout=3000
                )
            except Exception:
                pass

            try:
                self.page.wait_for_load_state(
                "networkidle",
                timeout=3000
    )
            except Exception:
                pass

            after_url = self.page.url

            print("=" * 60)
            print("EXECUTION RESULT")
            print("BEFORE :", before_url)
            print("AFTER  :", after_url)
            print("=" * 60)

            try:
                after_title = self.page.title()
            except Exception:
                after_title = ""

            try:
                after_dom = self.page.locator("body").inner_text()[:1000]
            except Exception:
                after_dom = ""

            after_state = {
                "url": after_url,
                "title": after_title,
                "dom": after_dom,
            }

            same_page = (
                before_state["url"] ==
                after_state["url"]
            )

            title_changed = (
                before_state["title"] !=
                after_state["title"]
            )

            content_changed = (
                before_state["dom"] !=
                after_state["dom"]
            )

# يعتبر Navigation إذا تغير URL أو تغير محتوى الصفحة أو العنوان
            navigated = (
                (not same_page)
                or title_changed
                or content_changed
            )
            
            result.update({

                "success": True,

                "action": action.get("action"),
                "locator": action.get("locator"),

                "message": "Executed successfully",
                "exception": None,

                "old_state": before_state,
                "new_state": after_state,
                "same_page": same_page,
                "navigated": navigated,

                "title_changed": title_changed,

                "content_changed": content_changed,

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

            candidates = self.page.get_by_text(
                value,
                exact=True,
            )

            try:
                if candidates.count() == 1:
                    return candidates.first
            except Exception:
                pass

            try:
                link = self.page.get_by_role(
                    "link",
                    name=value,
                    exact=True,
                )

                if link.count():
                    return link.first
            except Exception:
                pass

            try:
                button = self.page.get_by_role(
                    "button",
                    name=value,
                    exact=True,
                )

                if button.count():
                    return button.first
            except Exception:
                pass

            return candidates.first

        if strategy == "id":
            return self.page.locator(f"#{value}")

        if strategy == "name":
            return self.page.locator(f'[name="{value}"]')

        if strategy == "placeholder":
            return self.page.get_by_placeholder(value)

        if strategy == "title":
            return self.page.locator(f'[title="{value}"]')

        if strategy == "aria-label":
            return self.page.get_by_label(value)

        if strategy == "css":
            return self.page.locator(value)

        raise ValueError(
            f"Unknown locator strategy: {strategy}"
        )