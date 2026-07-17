from playwright.sync_api import Page


class AccessibilityScanner:
    """
    Scans accessibility-related information from the current page.
    """

    def __init__(self, page: Page):
        self.page = page

    def scan(self):

        elements = []

        locator = self.page.locator(
            "input, button, select, textarea, a"
        )

        count = locator.count()

        for i in range(count):

            try:

                element = locator.nth(i)

                tag = element.evaluate(
                    "el => el.tagName.toLowerCase()"
                )

                text = ""

                try:
                    text = element.inner_text().strip()
                except Exception:
                    pass

                elements.append({

                    "tag": tag,

                    "text": text,

                    "label": self._label(element),

                    "role": element.get_attribute("role"),

                    "aria_label": element.get_attribute("aria-label"),

                    "aria_required":
                        element.get_attribute("aria-required"),

                    "required":
                        element.get_attribute("required") is not None,

                    "disabled":
                        element.get_attribute("disabled") is not None,

                    "readonly":
                        element.get_attribute("readonly") is not None,

                    "hidden":
                        self._is_hidden(element)

                })

            except Exception as e:

                print(f"Accessibility Error: {e}")

        return elements

    def _label(self, element):

        try:

            element_id = element.get_attribute("id")

            if not element_id:
                return None

            label = self.page.locator(
                f"label[for='{element_id}']"
            )

            if label.count():

                return label.first.inner_text().strip()

        except Exception:

            pass

        return None

    def _is_hidden(self, element):

        try:

            return not element.is_visible()

        except Exception:

            return False