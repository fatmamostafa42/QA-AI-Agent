from app.generators.template_engine import TemplateEngine
from app.generators.priorities import PriorityResolver
from app.generators.testcase_utils import TestCaseUtils


class TestCaseGenerator:

    """
    Generates Dynamic Test Cases from:

        Knowledge
            +
        Scenarios

    Produces:
        Positive
        Negative
        Validation

    Generic for any web application.
    """

    def __init__(self, knowledge, scenarios):

        self.knowledge = knowledge
        self.scenarios = scenarios

        self.engine = TemplateEngine()

        self.counter = 1

    # ----------------------------------------------------

    def generate(self):

        knowledge_pages = self.knowledge.get(
            "pages",
            []
        )

        scenario_pages = self.scenarios.get(
            "scenarios",
            []
        )

        result = {

            "application":
                self.knowledge.get(
                    "application",
                    {}
                ),

            "summary": {

                "pages": 0,
                "test_cases": 0

            },

            "pages": []

        }

        total_cases = 0

        for scenario_page in scenario_pages:

            knowledge_page = self._find_page_knowledge(

                scenario_page.get("url"),

                knowledge_pages

            )

            page_cases = self._generate_page_cases(

                scenario_page,

                knowledge_page

            )

            result["pages"].append({

                "url":
                    scenario_page.get("url"),

                "title":
                    scenario_page.get("title"),

                "test_cases":
                    page_cases

            })

            total_cases += len(page_cases)

        result["summary"]["pages"] = len(
            result["pages"]
        )

        result["summary"]["test_cases"] = total_cases

        return result

    # ----------------------------------------------------

    def _generate_page_cases(

        self,

        scenario_page,

        knowledge_page

    ):

        cases = []

        features = scenario_page.get(
            "features",
            []
        )

        scenarios = scenario_page.get(
            "scenarios",
            []
        )

        for scenario in scenarios:

            feature = TestCaseUtils.detect_feature(

                scenario,

                features

            )

            # Positive
            cases.append(

                self._build_test_case(

                    scenario=scenario,

                    feature=feature,

                    page=knowledge_page,

                    case_kind="Positive"

                )

            )

            # Negative
            cases.append(

                self._build_test_case(

                    scenario=scenario,

                    feature=feature,

                    page=knowledge_page,

                    case_kind="Negative"

                )

            )

            # Validation
            cases.append(

                self._build_test_case(

                    scenario=scenario,

                    feature=feature,

                    page=knowledge_page,

                    case_kind="Validation"

                )

            )

        return cases
        # ----------------------------------------------------

    def _build_test_case(

        self,

        scenario,

        feature,

        page,

        case_kind="Positive"

    ):

        page_title = page.get(
            "title",
            ""
        )

        page_url = page.get(
            "url",
            ""
        )

        steps, expected = self.engine.build(

            scenario=scenario,

            page=page,

            case_kind=case_kind

        )

        testcase = {

            "id":
                f"TC-{self.counter:04}",

            "feature":
                feature,

            "scenario":
                scenario,

            "title":
                f"{case_kind} - {scenario}",

            "priority":
                PriorityResolver.resolve(

                    scenario,

                    feature

                ),

            "type":
                case_kind,

            "page":
                page_title,

            "url":
                page_url,

            "preconditions": [

                "Application is running",

                "User is logged in"

            ],

            "steps":
                steps,

            "expected_result":
                expected

        }

        self.counter += 1

        return testcase

    # ----------------------------------------------------
    # Helpers
    # ----------------------------------------------------

    def _find_page_knowledge(

        self,

        url,

        knowledge_pages

    ):

        for page in knowledge_pages:

            if page.get("url") == url:

                return page

        return {}

    # ----------------------------------------------------

    def _find_button(

        self,

        page,

        scenario

    ):

        buttons = page.get(
            "button_texts",
            []
        )

        scenario = scenario.lower()

        for button in buttons:

            if button.lower() in scenario:

                return button

        preferred = [

            "Save",

            "Add",

            "Create",

            "Search",

            "Submit",

            "Delete",

            "Update",

            "Edit",

            "Reset"

        ]

        for name in preferred:

            for button in buttons:

                if button.lower() == name.lower():

                    return button

        return None

    # ----------------------------------------------------

    def _find_input(

        self,

        page,

        scenario

    ):

        fields = page.get(
            "form_fields",
            []
        )

        placeholders = page.get(
            "input_placeholders",
            []
        )

        all_fields = fields + placeholders

        scenario = scenario.lower()

        for field in all_fields:

            if field.lower() in scenario:

                return field

        if all_fields:

            return all_fields[0]

        return None
        # ----------------------------------------------------

    def _determine_type(

        self,

        scenario,

        feature

    ):

        scenario = scenario.lower()

        feature = feature.lower()

        if "login" in scenario:
            return "Authentication"

        if "search" in scenario:
            return "Search"

        if "create" in scenario or "add" in scenario:
            return "CRUD"

        if "edit" in scenario or "update" in scenario:
            return "CRUD"

        if "delete" in scenario or "remove" in scenario:
            return "CRUD"

        if "upload" in scenario:
            return "Upload"

        if "dashboard" in scenario:
            return "Dashboard"

        if "navigation" in feature:
            return "Navigation"

        if "validation" in feature:
            return "Validation"

        return "Functional"

    # ----------------------------------------------------

    def _find_grid_action(

        self,

        page,

        scenario

    ):

        actions = page.get(
            "grid_actions",
            []
        )

        scenario = scenario.lower()

        for action in actions:

            if action.lower() in scenario:

                return action

        if actions:

            return actions[0]

        return None

    # ----------------------------------------------------

    def _find_card(

        self,

        page

    ):

        cards = page.get(
            "card_titles",
            []
        )

        if cards:

            return cards[0]

        return None

    # ----------------------------------------------------

    def _find_tab(

        self,

        page

    ):

        tabs = page.get(
            "tabs",
            []
        )

        if tabs:

            return tabs[0]

        return None

    # ----------------------------------------------------

    def _find_dropdown(

        self,

        page

    ):

        dropdowns = page.get(
            "dropdowns",
            {}
        )

        if dropdowns.get("custom_dropdowns", 0):
            return "Custom Dropdown"

        if dropdowns.get("aria_combobox", 0):
            return "Combobox"

        if dropdowns.get("native_selects", 0):
            return "Select"

        return None