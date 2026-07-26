class SmartStepBuilder:
    """
    Builds smart QA steps from page knowledge.

    Reads:

    - buttons
    - form fields
    - placeholders

    instead of hardcoded values.
    """

    def __init__(
        self,
        page,
        scenario=None
    ):

        self.page = page or {}
        self.scenario = scenario or {}
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
    
    def build(self):

        intent = self.scenario.get(
            "intent",
            "UNKNOWN"
        )

        if intent == "SEARCH":

            return {
            "steps": [
                self.open_page(),
                self.search_field(),
                self.click("Search")
            ],
            "expected_result":
                "Matching records are displayed."
            }

        if intent == "CREATE":

            return {
            "steps": [
                self.open_page(),
                *self.enter_fields(),
                self.click(
                    "Save",
                    "Add",
                    "Create"
                )
            ],
            "expected_result":
                "Record is created successfully."
            }

        if intent == "EDIT":

            return {
            "steps": [
                self.open_page(),
                self.click("Edit"),
                *self.enter_fields(),
                self.click(
                    "Save",
                    "Update"
                )
            ],
            "expected_result":
                "Changes are saved successfully."
        }

        if intent == "DELETE":

            return {
            "steps": [
                self.open_page(),
                self.click("Delete"),
                self.click("Confirm")
            ],
            "expected_result":
                "Record is deleted successfully."
            }

        if intent == "LOGIN":

            return {
            "steps": [
                self.open_page(),
                *self.enter_fields(),
                self.click("Login")
            ],
            "expected_result":
                "User is logged in successfully."
            }

        return {
        "steps": [
            self.open_page()
        ],
        "expected_result":
            "Operation completed successfully."
    }