from playwright.sync_api import Locator


class LocatorBuilder:
    """
    Builds stable Playwright locators for page elements.
    """

    def __init__(self, page):
        self.page = page


    def build(self, element: Locator):

        try:

            element_id = element.get_attribute("id")

            if element_id:
                return f"#{element_id}"


        except Exception:
            pass


        try:

            name = element.get_attribute("name")

            if name:
                return f"[name='{name}']"


        except Exception:
            pass


        try:

            placeholder = element.get_attribute("placeholder")

            if placeholder:
                return f"[placeholder='{placeholder}']"


        except Exception:
            pass


        try:

            tag = element.evaluate(
                "el => el.tagName.toLowerCase()"
            )

            return tag


        except Exception:

            return "unknown"