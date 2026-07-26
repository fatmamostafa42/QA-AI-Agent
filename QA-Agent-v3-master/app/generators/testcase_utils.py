class TestCaseUtils:
    """
    Helper methods for Test Case Generator.
    """

    @staticmethod
    def detect_feature(scenario, features):

        if not scenario:
            return "General"

        if isinstance(scenario, dict):
            scenario = scenario.get("name", "")
        elif not isinstance(scenario, str):
            scenario = str(scenario)

            scenario = scenario.lower()

        for feature in features:

            if isinstance(feature, dict):
                feature_name = (
                feature.get("name")
                or feature.get("title")
                or ""
            )
            else:
                feature_name = str(feature)

            feature_lower = feature_name.lower()

            if "search" in scenario and "search" in feature_lower:
                return feature_name

            if "create" in scenario and (
                "create" in feature_lower
                or "management" in feature_lower
            ):
                return feature_name

            if "add" in scenario and (
                "create" in feature_lower
                or "management" in feature_lower
            ):
                return feature_name

            if "edit" in scenario and (
                "management" in feature_lower
                or "edit" in feature_lower
            ):
               return feature_name

            if "update" in scenario and (
                "management" in feature_lower
                or "edit" in feature_lower
            ):
                return feature_name

            if "delete" in scenario and (
                "management" in feature_lower
                or "delete" in feature_lower
            ):
                return feature_name

            if "dashboard" in scenario and "dashboard" in feature_lower:
                return feature_name

            if "upload" in scenario and "upload" in feature_lower:
                return feature_name

            if "login" in scenario and "login" in feature_lower:
                return feature_name

        if features:
            first = features[0]

            if isinstance(first, dict):
                return (
                first.get("name")
                or first.get("title")
                or "General"
                )

            return str(first)

        return "General"

       
    @staticmethod
    def unique(items):

        result = []

        seen = set()

        for item in items:

            if item not in seen:

                result.append(item)

                seen.add(item)

        return result