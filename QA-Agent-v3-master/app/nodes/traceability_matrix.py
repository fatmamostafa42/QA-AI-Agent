"""
Traceability Matrix.

Builds Feature → Requirement → Scenario → Test Case → Jira mappings
from the structured artifacts in state.
"""
from typing import Any, Dict, List

from app.state import QAState
from app.utils.logger import log_step, log_success, log_error, Timer


def _norm(text: str) -> str:
    return (text or "").strip().lower()


def traceability_matrix(state: QAState):
    try:
        with Timer("Traceability Matrix"):
            structured: List[Dict[str, Any]] = (
                state.get("test_cases_structured", []) or []
            )
            test_cases_raw = state.get("test_cases", []) or []
            jira_keys = state.get("jira_keys", []) or []
            epic_map = state.get("epic_map", {}) or {}

            log_step(
                f"Building matrix from "
                f"{len(structured) or len(test_cases_raw)} test case(s)"
            )

            matrix: List[Dict[str, Any]] = []

            if structured:
                groups: Dict[str, Dict[str, List[str]]] = {}
                for tc in structured:
                    feature = tc.get("feature") or "Unmapped"
                    req = tc.get("requirement") or "—"
                    key = f"{feature} || {req}"
                    bucket = groups.setdefault(key, {
                        "feature": feature,
                        "requirement": req,
                        "scenarios": [],
                        "tests": [],
                    })
                    title = tc.get("title", "untitled")
                    bucket["tests"].append(title)
                    scenario = tc.get("scenario") or ""
                    if scenario and scenario not in bucket["scenarios"]:
                        bucket["scenarios"].append(scenario)

                for index, payload in enumerate(groups.values()):
                    matrix.append({
                        "feature": payload["feature"],
                        "requirement": payload["requirement"],
                        "scenario_titles": payload["scenarios"],
                        "test_titles": payload["tests"],
                        "jira_keys": jira_keys[index:index + 1],
                        "epic_key": epic_map.get(payload["feature"], ""),
                    })

            log_success(f"Traceability matrix has {len(matrix)} row(s)")
            return {"traceability": matrix}

    except Exception as e:
        log_error("Traceability Matrix", e)
        return {"traceability": []}
