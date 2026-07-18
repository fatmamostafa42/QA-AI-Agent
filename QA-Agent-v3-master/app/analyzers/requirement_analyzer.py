from typing import Dict, List


class RequirementAnalyzer:
    """
    Converts Knowledge into Business Requirements.

    Explorer
        ↓
    Knowledge Builder
        ↓
    Requirement Analyzer
        ↓
    Feature Splitter
        ↓
    Scenario Generator
    """

    def __init__(self, knowledge: Dict):

        self.knowledge = knowledge

    def analyze(self) -> Dict:

        pages = self.knowledge.get("pages", [])

        requirements = []

        for page in pages:

            requirements.append(
                self._analyze_page(page)
            )

        return {

            "application":
                self.knowledge.get("application", {}),

            "summary":
                self.knowledge.get("summary", {}),

            # مهم جداً للـ Feature Splitter V2
            "pages":
                pages,

            "requirements":
                requirements

        }

    def _analyze_page(self, page: Dict) -> Dict:

        capabilities = []

        if page.get("buttons", 0):

            capabilities.append(
                "Button Interaction"
            )

        if page.get("inputs", 0):

            capabilities.append(
                "Data Entry"
            )

        if page.get("forms", 0):

            capabilities.append(
                "Form Submission"
            )

        if page.get("tables", 0):

            capabilities.append(
                "Data Table"
            )

        if page.get("links", 0):

            capabilities.append(
                "Navigation"
            )

        if page.get("accessibility", 0):

            capabilities.append(
                "Accessibility"
            )

        return {

            "url":
                page.get("url"),

            "title":
                page.get("title"),

            "capabilities":
                capabilities

        }