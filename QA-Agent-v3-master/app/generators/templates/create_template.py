from app.generators.smart_step_builder import SmartStepBuilder


class CreateTemplate:

    def build(self, page, analysis):

        builder = SmartStepBuilder(page)

        steps = [
            builder.open_page(),
            builder.click("Add", "Create", "New")
        ]

        steps.extend(builder.enter_fields())

        steps.append(
            builder.click("Save", "Submit")
        )

        return (
            steps,
            f"{analysis['entity']} created successfully."
        )