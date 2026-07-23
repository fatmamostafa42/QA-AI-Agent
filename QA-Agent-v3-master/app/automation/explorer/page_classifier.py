class PageClassifier:
    """
    Responsible for identifying the logical type of a page.
    """

    def classify(
        self,
        url: str,
        title: str,
        elements: dict,
        forms: list,
        tables: list,
    ) -> str:

        url = (url or "").lower()
        title = (title or "").lower()

        inputs = elements.get("inputs", [])
        buttons = elements.get("buttons", [])

        # Login Page
        if (
            "login" in url
            or "signin" in url
            or "password" in str(inputs).lower()
        ):
            return "login"

        # Dashboard
        if (
            "dashboard" in url
            or "dashboard" in title
        ):
            return "dashboard"

        # List Page
        if tables:
            return "list"

        # Form
        if len(inputs) and len(buttons):
            return "form"

        # Details
        if (
            "details" in url
            or "view" in url
        ):
            return "details"

        return "unknown"