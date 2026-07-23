from typing import Any, Dict, List
from playwright.sync_api import Page


class ActionEngine:
    """
    Generic Action Engine

    Responsible for discovering every possible user action
    on the current page.

    It is completely generic and works with any website.
    """

    def __init__(self, page: Page):
        self.page = page

    # =====================================================
    # Public API
    # =====================================================

    def discover_actions(self) -> List[Dict[str, Any]]:

        actions = []

        actions.extend(self._discover_buttons())
        actions.extend(self._discover_links())
        actions.extend(self._discover_inputs())

        return actions

    # =====================================================
    # Buttons
    # =====================================================

    def _discover_buttons(self):

        actions = []

        buttons = self.page.locator("button")

        count = buttons.count()

        for i in range(count):

            button = buttons.nth(i)

            action = self._build_action(button, "button")

            if action:
                actions.append(action)

        return actions

    # =====================================================
    # Links
    # =====================================================

    def _discover_links(self):

        actions = []

        links = self.page.locator("a[href]")

        count = links.count()

        for i in range(count):

            link = links.nth(i)

            action = self._build_action(link, "link")

            if action:
                actions.append(action)

        return actions

    # =====================================================
    # Inputs
    # =====================================================

    def _discover_inputs(self):

        actions = []

        inputs = self.page.locator("input, textarea, select")

        count = inputs.count()

        for i in range(count):

            element = inputs.nth(i)

            action = self._build_action(element, "input")

            if action:
                actions.append(action)

        return actions

    # =====================================================
    # Generic Builder
    # =====================================================

    def _build_action(self, element, element_type):

        try:
            text = (element.inner_text() or "").strip()
        except Exception:
            text = ""

        try:
            aria = element.get_attribute("aria-label") or ""
        except Exception:
            aria = ""

        try:
            title = element.get_attribute("title") or ""
        except Exception:
            title = ""

        try:
            placeholder = element.get_attribute("placeholder") or ""
        except Exception:
            placeholder = ""

        try:
            input_type = element.get_attribute("type") or ""
        except Exception:
            input_type = ""

        semantic = " ".join([
            text,
            aria,
            title,
            placeholder
        ]).lower()

        action = self._detect_action(
            semantic,
            element_type,
            input_type
        )

        return {
            "element": element_type,
            "action": action["action"],
            "confidence": action["confidence"],
            "requires_input": action["requires_input"],
            "may_navigate": action["may_navigate"],
            "may_open_dialog": action["may_open_dialog"],
            "risk": action["risk"],
            "locator": self._build_locator(element)
        }

    # =====================================================
    # Action Detection
    # =====================================================

    def _detect_action(
        self,
        text,
        element_type,
        input_type
    ):

        action = "unknown"

        confidence = 0.50

        requires_input = False

        may_navigate = False

        may_open_dialog = False

        risk = "low"

        if element_type == "link":

            action = "navigate"

            confidence = 0.95

            may_navigate = True

        elif element_type == "input":

            action = "fill"

            confidence = 0.95

            requires_input = True

        else:

            keywords = {

                "search": "search",
                "find": "search",

                "save": "save",

                "submit": "submit",

                "continue": "submit",

                "login": "submit",

                "sign in": "submit",

                "add": "create",

                "new": "create",

                "create": "create",

                "edit": "edit",

                "update": "edit",

                "delete": "delete",

                "remove": "delete",

                "reset": "reset",

                "cancel": "cancel",

                "close": "close",

                "back": "back",

                "next": "next",

                "previous": "previous",

                "download": "download",

                "upload": "upload",

                "filter": "filter",

                "sort": "sort",

                "view": "view"

            }

            for keyword, detected in keywords.items():

                if keyword in text:

                    action = detected

                    confidence = 0.95

                    break

            if action == "delete":
                risk = "high"

            if action in [
                "create",
                "edit",
                "submit"
            ]:
                requires_input = True

        return {

            "action": action,

            "confidence": confidence,

            "requires_input": requires_input,

            "may_navigate": may_navigate,

            "may_open_dialog": may_open_dialog,

            "risk": risk

        }

    # =====================================================
    # Generic Locator
    # =====================================================

    def _build_locator(self, element):

        try:
            text = (element.inner_text() or "").strip()

            if text:
                return {
                    "strategy": "text",
                    "value": text
                }

        except Exception:
            pass

        for attr in [
            "aria-label",
            "placeholder",
            "name",
            "id",
            "title"
        ]:

            try:

                value = element.get_attribute(attr)

                if value:

                    return {
                        "strategy": attr,
                        "value": value
                    }

            except Exception:
                pass

        return {
            "strategy": "css",
            "value": "unknown"
        }