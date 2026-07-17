from playwright.sync_api import Locator


class LocatorBuilder:
    """
    Builds stable Playwright locators.

    Priority:

    1. data-testid
    2. id
    3. name
    4. aria-label
    5. placeholder
    6. role
    7. visible text
    8. CSS fallback
    """

    def __init__(self, page):
        self.page = page

    def build(self, element: Locator):

        # -----------------------------
        # data-testid
        # -----------------------------
        try:
            value = (
                element.get_attribute("data-testid")
                or element.get_attribute("data-test")
                or element.get_attribute("data-cy")
            )

            if value:
                return f"[data-testid='{value}']"

        except Exception:
            pass

        # -----------------------------
        # id
        # -----------------------------
        try:
            value = element.get_attribute("id")

            if value:
                return f"#{value}"

        except Exception:
            pass

        # -----------------------------
        # name
        # -----------------------------
        try:
            value = element.get_attribute("name")

            if value:
                return f"[name='{value}']"

        except Exception:
            pass

        # -----------------------------
        # aria-label
        # -----------------------------
        try:
            value = element.get_attribute("aria-label")

            if value:
                return f"[aria-label='{value}']"

        except Exception:
            pass

        # -----------------------------
        # placeholder
        # -----------------------------
        try:
            value = element.get_attribute("placeholder")

            if value:
                return f"[placeholder='{value}']"

        except Exception:
            pass

        # -----------------------------
        # role
        # Ignore meaningless roles
        # -----------------------------
        try:

            role = element.get_attribute("role")

            ignored_roles = {
                "none",
                "presentation",
                ""
            }

            if role and role not in ignored_roles:
                return f"[role='{role}']"

        except Exception:
            pass

        # -----------------------------
        # text locator
        # -----------------------------
        try:

            text = element.inner_text().strip()

            if (
                text
                and len(text) <= 40
            ):
                return f"text={text}"

        except Exception:
            pass

        # -----------------------------
        # CSS fallback
        # -----------------------------
        try:

            tag = element.evaluate(
                "el => el.tagName.toLowerCase()"
            )

            classes = element.get_attribute("class")

            if classes:

                class_list = [
                    c
                    for c in classes.split()
                    if c.strip()
                ]

                if class_list:

                    # أول كلاس فقط لتقليل طول الـ locator
                    return f"{tag}.{class_list[0]}"

            return tag

        except Exception:

            return "unknown"