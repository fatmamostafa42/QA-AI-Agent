class TemplateEngine:
    """
    Converts Scenario + Page Knowledge
    into real QA Test Steps.

    Supports:
        - Positive
        - Negative
        - Validation

    Generic Template Engine.
    """

    def build(
        self,
        scenario,
        page,
        knowledge=None,
        case_kind="Positive"
    ):

        scenario_lower = scenario.lower()

        # -------------------------------
        # Template Selection
        # -------------------------------

        if (
            "create" in scenario_lower
            or "add" in scenario_lower
            or "new" in scenario_lower
        ):

            result = self._create(page)


        elif (
            "edit" in scenario_lower
            or "update" in scenario_lower
        ):

            result = self._edit(page)


        elif (
            "delete" in scenario_lower
            or "remove" in scenario_lower
        ):

            result = self._delete(page)


        elif (
            "search" in scenario_lower
            or "filter" in scenario_lower
        ):

            result = self._search(page)


        elif "login" in scenario_lower:

            result = self._login(page)


        elif "upload" in scenario_lower:

            result = self._upload(page)


        elif "dashboard" in scenario_lower:

            result = self._dashboard(page)


        else:

            result = self._default(
                scenario
            )


        steps, expected = result


        # -------------------------------
        # Negative Test Case
        # -------------------------------

        if case_kind == "Negative":

            steps = [

                step.replace(
                    "valid",
                    "invalid"
                ).replace(
                    "Valid",
                    "Invalid"
                )

                for step in steps
            ]


            expected = (
                "Validation message is displayed "
                "and operation is rejected."
            )


        # -------------------------------
        # Validation Test Case
        # -------------------------------

        elif case_kind == "Validation":

            new_steps = []

            inserted = False


            for step in steps:

                if (
                    "Enter valid" in step
                    or
                    "Enter invalid" in step
                ):

                    if not inserted:

                        new_steps.append(
                            "Leave mandatory fields empty."
                        )

                        inserted = True

                else:

                    new_steps.append(step)


            if not inserted:

                new_steps.append(
                    "Leave mandatory fields empty."
                )


            steps = new_steps


            expected = (
                "Required field validation message "
                "is displayed."
            )


        return steps, expected



    # ==================================================
    # CREATE TEMPLATE
    # ==================================================

    def _create(self, page):

        fields = page.get(
            "form_fields",
            []
        )


        buttons = page.get(
            "button_texts",
            []
        )


        add_button = self._button(
            buttons,
            [
                "Add",
                "Create",
                "New"
            ]
        )


        save_button = self._button(
            buttons,
            [
                "Save",
                "Submit"
            ]
        )


        steps = [

            f"Open {page.get('title','Application')} page."

        ]


        if add_button:

            steps.append(
                f"Click '{add_button}'."
            )


        for field in fields:

            steps.append(
                f"Enter valid {field}."
            )


        if save_button:

            steps.append(
                f"Click '{save_button}'."
            )


        return (

            steps,

            "Record is created successfully."

        )



    # ==================================================
    # EDIT TEMPLATE
    # ==================================================

    def _edit(self, page):

        return (

            [

                f"Open {page.get('title','Application')} page.",
                "Search existing record.",
                "Click Edit.",
                "Update required fields.",
                "Click Save."

            ],

            "Changes are saved successfully."

        )



    # ==================================================
    # DELETE TEMPLATE
    # ==================================================

    def _delete(self, page):

        return (

            [

                f"Open {page.get('title','Application')} page.",
                "Search existing record.",
                "Click Delete.",
                "Confirm deletion."

            ],

            "Record is deleted successfully."

        )



    # ==================================================
    # SEARCH TEMPLATE
    # ==================================================

    def _search(self, page):

        placeholders = page.get(
            "input_placeholders",
            []
        )


        buttons = page.get(
            "button_texts",
            []
        )


        steps = [

            f"Open {page.get('title','Application')} page."

        ]


        if placeholders:

            steps.append(
                f"Enter valid {placeholders[0]}."
            )


        search_button = self._button(
            buttons,
            [
                "Search"
            ]
        )


        if search_button:

            steps.append(
                f"Click '{search_button}'."
            )


        return (

            steps,

            "Matching records are displayed."

        )



    # ==================================================
    # LOGIN TEMPLATE
    # ==================================================

    def _login(self, page):

        return (

            [

                "Open Login page.",
                "Enter valid Username.",
                "Enter valid Password.",
                "Click Login."

            ],

            "Dashboard opens successfully."

        )



    # ==================================================
    # UPLOAD TEMPLATE
    # ==================================================

    def _upload(self, page):

        return (

            [

                f"Open {page.get('title','Application')} page.",
                "Click Upload.",
                "Choose valid file.",
                "Click Save."

            ],

            "File uploaded successfully."

        )



    # ==================================================
    # DASHBOARD TEMPLATE
    # ==================================================

    def _dashboard(self, page):

        return (

            [

                "Open Dashboard."

            ],

            "Dashboard widgets are displayed."

        )



    # ==================================================
    # DEFAULT TEMPLATE
    # ==================================================

    def _default(self, scenario):

        return (

            [

                f"Execute scenario '{scenario}'."

            ],

            "Operation completed successfully."

        )



    # ==================================================
    # BUTTON FINDER
    # ==================================================

    def _button(
        self,
        buttons,
        names
    ):

        for name in names:

            for button in buttons:

                if button.lower() == name.lower():

                    return button


        return None