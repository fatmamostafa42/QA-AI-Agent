import re


class ScenarioIntelligence:
    """
    Understands a scenario and extracts:

    - intent
    - entity
    - category

    Example:

    Create User
        ->
        intent = CREATE
        entity = USER
        category = CRUD
    """

    INTENTS = {

        "CREATE": [
            "create",
            "add",
            "new",
            "register"
        ],

        "EDIT": [
            "edit",
            "update",
            "modify"
        ],

        "DELETE": [
            "delete",
            "remove"
        ],

        "SEARCH": [
            "search",
            "find",
            "filter"
        ],

        "LOGIN": [
            "login",
            "log in",
            "sign in"
        ],

        "LOGOUT": [
            "logout",
            "log out",
            "sign out"
        ],

        "UPLOAD": [
            "upload",
            "import"
        ],

        "DOWNLOAD": [
            "download",
            "export"
        ],

        "APPROVE": [
            "approve",
            "accept"
        ],

        "REJECT": [
            "reject",
            "decline"
        ],

        "ASSIGN": [
            "assign"
        ],

        "RESET": [
            "reset",
            "clear"
        ],

        "VIEW": [
            "view",
            "open"
        ]
    }


    CRUD = {
        "CREATE",
        "EDIT",
        "DELETE",
        "SEARCH"
    }


    def analyze(self, scenario: str):

        text = scenario.lower()

        intent = "UNKNOWN"

        matched_word = ""

        for intent_name, keywords in self.INTENTS.items():

            for keyword in keywords:

                if keyword in text:

                    intent = intent_name
                    matched_word = keyword
                    break

            if intent != "UNKNOWN":
                break


        entity = scenario

        if matched_word:

            entity = re.sub(
                matched_word,
                "",
                scenario,
                flags=re.IGNORECASE
            ).strip()


        category = (

            "CRUD"

            if intent in self.CRUD

            else intent

        )


        return {

            "intent": intent,

            "entity": entity,

            "category": category

        }