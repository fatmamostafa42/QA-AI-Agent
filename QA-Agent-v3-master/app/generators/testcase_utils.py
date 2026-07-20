class TestCaseUtils:
    """
    Helper methods for Test Case Generator.
    """

    @staticmethod
    def detect_feature(scenario, features):

        if not scenario:
            return "General"

        scenario = scenario.lower()

        for feature in features:

            feature_lower = feature.lower()

            if "search" in scenario and "search" in feature_lower:
                return feature

            if "create" in scenario and (
                "create" in feature_lower
                or "management" in feature_lower
            ):
                return feature

            if "add" in scenario and (
                "create" in feature_lower
                or "management" in feature_lower
            ):
                return feature

            if "edit" in scenario and (
                "management" in feature_lower
                or "edit" in feature_lower
            ):
                return feature

            if "update" in scenario and (
                "management" in feature_lower
                or "edit" in feature_lower
            ):
                return feature

            if "delete" in scenario and (
                "management" in feature_lower
                or "delete" in feature_lower
            ):
                return feature

            if "dashboard" in scenario and "dashboard" in feature_lower:
                return feature

            if "upload" in scenario and "upload" in feature_lower:
                return feature

            if "login" in scenario and "login" in feature_lower:
                return feature

        if features:
            return features[0]

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