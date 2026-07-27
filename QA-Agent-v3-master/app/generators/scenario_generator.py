from typing import Dict, List, Any

from app.generators.scenario_intelligence import ScenarioIntelligence
import re


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

        for page in self.features:

            page_features = page.get("features", [])

            for feature_name in page_features:

                feature_name = feature_name.strip()

                if not feature_name:
                    continue

            analysis = self.ai.analyze(feature_name)

            scenarios.append({

                "name": feature_name,

                "source": "feature",

                "intent": analysis["intent"],

                "entity": analysis["entity"],

                "category": analysis["category"],

                "page": page.get("title", ""),

                "url": page.get("url", ""),

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
            print("FlowDiscovery is None")
            return scenarios

        try:
            flows = self.flow.extract_flows()
            print("\n========== FLOW DEBUG ==========")
            print("Flows:", len(flows))
            for f in flows[:5]:
                print(f)
            print("================================\n")

        except Exception as e:
             print("FLOW ERROR:", e)
             return scenarios



        for flow in flows:

            print("Processing flow:", flow)
            pages = flow.get("pages", [])
            actions = flow.get("actions", [])

            if len(pages) < 2:
               continue

            for i in range(len(pages) - 1):

                from_page = pages[i]
                to_page = pages[i + 1]

                scenario_name = self._build_flow_name(
                    pages=[from_page, to_page],
                    actions=actions
                    )

                analysis = self.ai.analyze(scenario_name)

                scenarios.append({

                   "name": scenario_name,

                   "source": "flow",

                   "intent": analysis["intent"],

                   "entity": to_page,

                   "category": analysis["category"],

                   "pages": [from_page, to_page],

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

    def _normalize_name(self, name):

        name = name.lower()

        name = re.sub(
        r"[^a-z0-9 ]",
        "",
        name
        )

        replacements = {
        "add": "create",
        "new": "create",
        "remove": "delete",
        "modify": "edit",
        "update": "edit"
        }

        words = name.split()

        words = [
        replacements.get(w, w)
        for w in words
        ]

        return " ".join(words)

    def _remove_duplicates(
        self,
        scenarios
    ):

        unique = []

        seen = set()

        for scenario in scenarios:

            key = (

            self._normalize_name(
            scenario.get("name","")
            ),

            scenario.get("entity","").lower()

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
    