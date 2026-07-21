from app.generators.scenario_intelligence import ScenarioIntelligence
from app.generators.template_registry import TemplateRegistry


class TemplateEngine:
    """
    Converts Scenario + Knowledge
    into QA Test Steps using:

    Scenario
        ↓
    Scenario Intelligence
        ↓
    Template Registry
        ↓
    Smart Template
    """

    def __init__(self):

        self.intelligence = ScenarioIntelligence()
        self.registry = TemplateRegistry()

    # -------------------------------------------------

    def build(
        self,
        scenario,
        page,
        knowledge=None,
        case_kind="Positive"
    ):

        analysis = self.intelligence.analyze(scenario)

        template = self.registry.get(
            analysis["intent"]
        )

        if template:

            steps, expected = template.build(
                page,
                analysis
            )

        else:

            steps = [
                f"Execute scenario '{scenario}'."
            ]

            expected = "Operation completed successfully."

        # --------------------------------------------
        # Negative
        # --------------------------------------------

        if case_kind == "Negative":

            negative_steps = []

            for step in steps:

                step = step.replace(
                    "valid",
                    "invalid"
                ).replace(
                    "Valid",
                    "Invalid"
                )

                negative_steps.append(step)

            steps = negative_steps

            expected = (
                "Validation message is displayed "
                "and operation is rejected."
            )

        # --------------------------------------------
        # Validation
        # --------------------------------------------

        elif case_kind == "Validation":

            validation_steps = []

            inserted = False

            for step in steps:

                if (
                    "Enter valid" in step
                    or
                    "Enter invalid" in step
                ) and not inserted:

                    validation_steps.append(
                        "Leave all mandatory fields empty."
                    )

                    inserted = True

                else:

                    validation_steps.append(step)

            if not inserted:

                validation_steps.append(
                    "Leave mandatory fields empty."
                )

            steps = validation_steps

            expected = (
                "Required field validation message is displayed."
            )

        return steps, expected