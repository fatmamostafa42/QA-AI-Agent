class SmartStepBuilder:
    """
    Builds smart QA steps from page knowledge.

    Reads:

    - buttons
    - form fields
    - placeholders

    instead of hardcoded values.
    """

    def __init__(self, page):

        self.page = page or {}

    # -------------------------------------------------

    def open_page(self):

        return f"Open {self.page.get('title', 'Application')} page."

    # -------------------------------------------------

    def click(self, *names):

        buttons = self.page.get("button_texts", [])

        for wanted in names:

            for button in buttons:

                if wanted.lower() == button.lower():

                    return f"Click '{button}'."

        return f"Click '{names[0]}'."

    # -------------------------------------------------

    def enter_fields(self):

        fields = self.page.get("form_fields", [])

        steps = []

        for field in fields:

            steps.append(
                f"Enter valid {field}."
            )

        return steps

    # -------------------------------------------------

    def search_field(self):

        placeholders = self.page.get(
            "input_placeholders",
            []
        )

        if placeholders:

            return f"Enter valid {placeholders[0]}."

        fields = self.page.get(
            "form_fields",
            []
        )

        if fields:

            return f"Enter valid {fields[0]}."

        return "Enter search value."

    # -------------------------------------------------

    def verify(self, message):

        return message