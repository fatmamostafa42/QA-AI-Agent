from typing import Dict, List


class ScenarioGenerator:
    """
    Converts Business Features into Test Scenarios.

    Pipeline

    Knowledge
        ↓
    Requirement Analyzer
        ↓
    Feature Splitter
        ↓
    Scenario Generator
        ↓
    Test Case Generator
    """

    FEATURE_SCENARIOS = {

        "Dashboard": [
            "View Dashboard",
            "Refresh Dashboard",
            "Validate Dashboard Widgets"
        ],

        "User Management": [
            "Create User",
            "Search User",
            "Edit User",
            "Delete User",
            "Filter Users"
        ],

        "Employee Management": [
            "Add Employee",
            "Edit Employee",
            "Delete Employee",
            "Search Employee",
            "Filter Employee"
        ],

        "Leave Management": [
            "Apply Leave",
            "Approve Leave",
            "Reject Leave",
            "Cancel Leave",
            "Search Leave"
        ],

        "Claim Management": [
            "Create Claim",
            "Assign Claim",
            "Search Claim"
        ],

        "Performance Management": [
            "Search Reviews",
            "Create Review",
            "Edit Review"
        ],

        "Buzz Feed": [
            "Create Post",
            "Edit Post",
            "Delete Post"
        ],

        "Post Management": [
            "Like Post",
            "Comment Post",
            "Share Post"
        ],

        "Employee Directory": [
            "Search Employee",
            "View Employee Profile"
        ],

        "Corporate Branding": [
            "Upload Logo",
            "Update Branding",
            "Restore Defaults"
        ],

        "Nationality Management": [
            "Add Nationality",
            "Edit Nationality",
            "Delete Nationality"
        ],

        "Photo Upload": [
            "Upload Photo",
            "Replace Photo",
            "Invalid Photo Upload"
        ],

        "Video Upload": [
            "Upload Video",
            "Replace Video",
            "Invalid Video Upload"
        ],

        "Search": [
            "Search Valid Data",
            "Search Invalid Data",
            "Search Empty"
        ],

        "Auto Complete": [
            "Select Suggested Value",
            "No Matching Result"
        ],

        "Create Records": [
            "Create Record"
        ],

        "Data Persistence": [
            "Save Changes",
            "Verify Saved Data"
        ],

        "Reset Forms": [
            "Reset Form"
        ],

        "Cancel Operation": [
            "Cancel Changes"
        ],

        "Form Management": [
            "Required Fields Validation",
            "Field Length Validation",
            "Invalid Data Validation"
        ],

        "Navigation": [
            "Open Module",
            "Navigate Between Pages"
        ],

        "Button Actions": [
            "Click Buttons"
        ],

        "Data Entry": [
            "Enter Valid Data",
            "Enter Invalid Data"
        ],

        "Accessibility": [
            "Keyboard Navigation",
            "Focus Order",
            "Screen Reader Labels"
        ]
    }

    def __init__(self, features: Dict):

        self.features = features

    def generate(self) -> Dict:

        pages = []

        for page in self.features.get("features", []):

            scenarios = self._generate_page(page)

            pages.append({

                "url": page["url"],

                "title": page["title"],

                "features": page["features"],

                "scenarios": scenarios

            })

        return {

            "application": self.features.get("application", {}),

            "summary": self.features.get("summary", {}),

            "scenarios": pages

        }

    def _generate_page(self, page: Dict) -> List[str]:

        scenarios = []

        for feature in page.get("features", []):

            feature_scenarios = self.FEATURE_SCENARIOS.get(feature, [])

            for scenario in feature_scenarios:

                if scenario not in scenarios:

                    scenarios.append(scenario)

        return sorted(scenarios)