class PriorityResolver:
    """
    Determines Test Case priority based on
    Scenario + Feature.

    Generic for any web application.
    """

    PRIORITIES = {

        # Authentication
        "login": "Critical",
        "logout": "High",
        "password": "High",

        # CRUD
        "create": "High",
        "add": "High",
        "save": "High",
        "edit": "High",
        "update": "High",
        "delete": "High",
        "remove": "High",

        # Approval
        "approve": "High",
        "reject": "High",

        # Upload / Download
        "upload": "High",
        "import": "High",
        "download": "Medium",
        "export": "Medium",

        # Search
        "search": "Medium",
        "filter": "Medium",
        "sort": "Medium",
        "reset": "Low",

        # Navigation
        "navigation": "Low",
        "navigate": "Low",
        "open": "Low",

        # Dashboard
        "dashboard": "Medium",
        "refresh": "Low",

        # Validation
        "required": "High",
        "invalid": "High",
        "validation": "High",
        "field length": "Medium",
        "valid": "Medium",

        # Generic
        "view": "Low"
    }

    @classmethod
    def resolve(
        cls,
        scenario: str,
        feature: str = ""
    ) -> str:

        text = f"{scenario} {feature}".lower()

        for keyword, priority in cls.PRIORITIES.items():

            if keyword in text:
                return priority

        return "Medium"