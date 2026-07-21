from app.generators.smart_step_builder import SmartStepBuilder


class SearchTemplate:

    def build(self, page, analysis):

        builder = SmartStepBuilder(page)

        return (
            [
                builder.open_page(),
                builder.search_field(),
                builder.click("Search")
            ],
            "Matching records are displayed."
        )