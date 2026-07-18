from typing import Dict, List, Set


class FeatureSplitter:
    """
    Converts Requirements into Business Features.

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

    def __init__(self, requirements: Dict):

        self.requirements = requirements

    def split(self) -> Dict:

        pages = []

        knowledge_pages = {
            page["url"]: page
            for page in self.requirements.get("pages", [])
        }

        for requirement in self.requirements.get("requirements", []):

            page = knowledge_pages.get(
                requirement["url"],
                {}
            )

            pages.append({

                "url": requirement["url"],

                "title": requirement["title"],

                "features": self._detect_features(page)

            })

        return {

            "application":
                self.requirements.get("application", {}),

            "summary":
                self.requirements.get("summary", {}),

            "features":
                pages

        }

    def _detect_features(
        self,
        page: Dict
    ) -> List[str]:

        features: Set[str] = set()

        url = page.get("url", "").lower()

        title = page.get("title", "").lower()

        words = []

        words.extend(page.get("button_texts", []))
        words.extend(page.get("link_texts", []))
        words.extend(page.get("input_placeholders", []))
        words.extend(page.get("form_fields", []))
        words.extend(page.get("navigation", []))

        words = [
            str(word).lower().strip()
            for word in words
            if word
        ]

        # ------------------------------------------------
        # Generic Features
        # ------------------------------------------------

        if page.get("buttons", 0):

            features.add("Button Actions")

        if page.get("inputs", 0):

            features.add("Data Entry")

        if page.get("forms", 0):

            features.add("Form Management")

        if page.get("links", 0):

            features.add("Navigation")

        if page.get("accessibility", 0):

            features.add("Accessibility")

        if page.get("tables", 0):

            features.add("Table Management")

        # ------------------------------------------------
        # Common Actions
        # ------------------------------------------------

        if any("search" in word for word in words):

            features.add("Search")

        if any("reset" in word for word in words):

            features.add("Reset Forms")

        if any("save" in word for word in words):

            features.add("Data Persistence")

        if any("submit" in word for word in words):

            features.add("Data Persistence")

        if any("update" in word for word in words):

            features.add("Data Persistence")

        if any("apply" in word for word in words):

            features.add("Data Persistence")

        if any("add" in word for word in words):

            features.add("Create Records")

        if any("delete" in word for word in words):

            features.add("Delete Records")

        if any("edit" in word for word in words):

            features.add("Edit Records")

        if any("cancel" in word for word in words):

            features.add("Cancel Operation")

        if any("download" in word for word in words):

            features.add("Download")

        if any("upload" in word for word in words):

            features.add("Upload")

        if any("export" in word for word in words):

            features.add("Export")

        if any("import" in word for word in words):

            features.add("Import")

        if any("hint" in word for word in words):

            features.add("Auto Complete")

        # ------------------------------------------------
        # Smart Business Detection
        # ------------------------------------------------

        if "dashboard" in url:

            features.add("Dashboard")

        if "admin" in url:

            features.add("User Management")

        if "pim" in url:

            features.add("Employee Management")

        if "leave" in url:

            features.add("Leave Management")

        if "claim" in url:

            features.add("Claim Management")

        if "performance" in url:

            features.add("Performance Management")

        if "directory" in url:

            features.add("Employee Directory")

        if "buzz" in url:

            features.add("Buzz Feed")

        if "maintenance" in url:

            features.add("Maintenance")

        if "recruitment" in url:

            features.add("Recruitment")

        if "time" in url:

            features.add("Time Management")

        # ------------------------------------------------
        # Smart Text Detection
        # ------------------------------------------------

        if any("branding" in word for word in words):

            features.add("Corporate Branding")

        if any("nationalit" in word for word in words):

            features.add("Nationality Management")

        if any("photo" in word for word in words):

            features.add("Photo Upload")

        if any("video" in word for word in words):

            features.add("Video Upload")

        if any("post" in word for word in words):

            features.add("Post Management")

        return sorted(features)