from typing import Dict, List, Any

from app.generators.scenario_intelligence import ScenarioIntelligence


class ScenarioGenerator:
    """
    Generic Scenario Generator

    Builds QA scenarios from discovered application flows.

    Inputs
    ------
    - Features
    - FlowDiscovery Graph
    - SmartExplorer Actions

    Output
    ------
    List of normalized scenarios ready for
    TestCaseGenerator.
    """

    def __init__(
        self,
        features: List[Dict[str, Any]] | None = None,
        flow_discovery=None
    ):

        self.features = features or []
        self.flow = flow_discovery

        self.ai = ScenarioIntelligence()

    # =====================================================
    # Public API
    # =====================================================

    def generate(self) -> List[Dict[str, Any]]:

        scenarios = []

        scenarios.extend(
            self._generate_from_features()
        )

        scenarios.extend(
            self._generate_from_flows()
        )

        scenarios = self._remove_duplicates(
            scenarios
        )

        return scenarios
        # =====================================================
    # Feature-Based Scenarios
    # =====================================================

    def _generate_from_features(self):

        scenarios = []

        for feature in self.features:

            feature_name = (
                feature.get("name")
                or feature.get("title")
                or ""
            ).strip()

            if not feature_name:
                continue

            analysis = self.ai.analyze(feature_name)

            scenarios.append({

                "name": feature_name,

                "source": "feature",

                "intent": analysis["intent"],

                "entity": analysis["entity"],

                "category": analysis["category"],

                "steps": [],

                "expected_result": "",

                "actions": []

            })

        return scenarios

    # =====================================================
    # Flow-Based Scenarios
    # =====================================================

    def _generate_from_flows(self):

        scenarios = []

        if self.flow is None:
            return scenarios

        try:

            flows = self.flow.extract_flows()

        except Exception:

            return scenarios

        for flow in flows:

            pages = flow.get("pages", [])

            actions = flow.get("actions", [])

            if not pages:
                continue

            scenario_name = self._build_flow_name(
                pages,
                actions
            )

            analysis = self.ai.analyze(
                scenario_name
            )

            scenarios.append({

                "name": scenario_name,

                "source": "flow",

                "intent": analysis["intent"],

                "entity": analysis["entity"],

                "category": analysis["category"],

                "pages": pages,

                "actions": actions,

                "steps": [],

                "expected_result": ""

            })

        return scenarios
        # =====================================================
    # Flow Name Builder
    # =====================================================

    def _build_flow_name(
        self,
        pages,
        actions
    ):

        if actions:

            first = actions[0]

            if isinstance(first, dict):

                action = first.get(
                    "action",
                    ""
                ).strip()

                element = first.get(
                    "element",
                    ""
                ).strip()

                if action and element:

                    return (
                        f"{action.title()} "
                        f"{element.title()}"
                    )

                if action:

                    return action.title()

        if len(pages) >= 2:

            return (
                f"{pages[0]} -> "
                f"{pages[-1]}"
            )

        if pages:

            return pages[0]

        return "Unknown Scenario"

    # =====================================================
    # Duplicate Removal
    # =====================================================

    def _remove_duplicates(
        self,
        scenarios
    ):

        unique = []

        seen = set()

        for scenario in scenarios:

            key = (

                scenario.get("name", "").lower(),

                scenario.get("intent", "").lower(),

                scenario.get("entity", "").lower()

            )

            if key in seen:
                continue

            seen.add(key)

            unique.append(scenario)

        return self._sort(unique)

    # =====================================================
    # Sorting
    # =====================================================

    def _sort(
        self,
        scenarios
    ):

        priority = {

            "LOGIN": 1,

            "CREATE": 2,

            "SEARCH": 3,

            "VIEW": 4,

            "EDIT": 5,

            "DELETE": 6,

            "UPLOAD": 7,

            "DOWNLOAD": 8,

            "APPROVE": 9,

            "REJECT": 10,

            "UNKNOWN": 99

        }

        scenarios.sort(

            key=lambda s: (

                priority.get(

                    s.get(
                        "intent",
                        "UNKNOWN"
                    ),

                    99

                ),

                s.get(
                    "name",
                    ""
                )

            )

        )

        return scenarios