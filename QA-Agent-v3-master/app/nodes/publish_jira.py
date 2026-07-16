"""
Jira / Xray Publisher (v3).

Two-phase publish:

  PHASE 1 — Create one Epic per feature (uses Epic issue type)
  PHASE 2 — Create one Task (or Xray Test) per test case, linked to its
            Feature's Epic via the `parent` field

If `parent` is rejected by the Jira instance (some classic projects),
falls back to creating an issue link of type 'Relates'.

Environment:
  JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN, JIRA_PROJECT  (required to publish)
  JIRA_USE_XRAY=1                                     (use Test issue type)
  JIRA_EPIC_ISSUETYPE=Epic                            (override if your project uses another)
"""
import os
import re
from typing import Dict, Any, List, Optional

from app.state import QAState
from app.jira.client import get_jira
from app.utils.logger import log_step, log_success, log_warning, log_error, Timer


PROJECT = os.getenv("JIRA_PROJECT", "")
USE_XRAY = os.getenv("JIRA_USE_XRAY", "0") in {"1", "true", "yes"}
EPIC_ISSUETYPE = os.getenv("JIRA_EPIC_ISSUETYPE", "Epic")
TEST_ISSUETYPE = "Test" if USE_XRAY else "Task"


# =========================================================
# Helpers
# =========================================================

def _clean(text: str, limit: int = 100) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    return text[:limit]


def _build_epic_fields(feature: Dict[str, Any]) -> Dict[str, Any]:
    name = _clean(feature.get("name", "Untitled Feature"))
    desc = feature.get("description", "")
    reqs = feature.get("related_requirements") or []

    body = [f"*Feature:* {name}", "", desc or "_no description_"]
    if reqs:
        body.append("")
        body.append("*Related requirements:*")
        for req in reqs:
            body.append(f"- {req}")

    return {
        "project": {"key": PROJECT},
        "summary": name,
        "description": "\n".join(body),
        "issuetype": {"name": EPIC_ISSUETYPE},
        "labels": ["AI_QA", "Generated", "Epic_Feature"],
    }


def _build_test_fields(tc: Dict[str, Any], parent_key: Optional[str]) -> Dict[str, Any]:
    summary = _clean(tc.get("title", "Untitled"))
    priority = tc.get("priority") or "Medium"

    body_lines = [
        f"*Feature:* {tc.get('feature') or '_n/a_'}",
        f"*Requirement:* {tc.get('requirement') or '_n/a_'}",
        f"*Scenario:* {tc.get('scenario') or '_n/a_'}",
        f"*Preconditions:* {tc.get('preconditions') or '_n/a_'}",
        f"*Test Data:* {tc.get('test_data') or '_n/a_'}",
        "",
        "*Steps:*",
    ]
    for step in tc.get("steps") or []:
        body_lines.append(f"# {step}")
    body_lines += [
        "",
        f"*Expected Result:* {tc.get('expected_result') or '_n/a_'}",
        f"*Severity:* {tc.get('severity') or 'Major'}",
        f"*Type:* {tc.get('test_type') or 'Functional'}",
        f"*Automation Candidate:* {'Yes' if tc.get('automation_candidate') else 'No'}",
    ]

    labels = ["AI_QA", "Generated"]
    if tc.get("automation_candidate"):
        labels.append("AutomationCandidate")
    if tc.get("test_type"):
        labels.append(f"Type_{tc['test_type']}")

    fields: Dict[str, Any] = {
        "project": {"key": PROJECT},
        "summary": summary,
        "description": "\n".join(body_lines),
        "issuetype": {"name": TEST_ISSUETYPE},
        "priority": {"name": priority},
        "labels": labels,
    }
    if parent_key:
        fields["parent"] = {"key": parent_key}
    return fields


def _try_create(jira, fields: Dict[str, Any]) -> Optional[object]:
    """Try to create the issue; on parent-rejection, retry without parent."""
    try:
        return jira.create_issue(fields=fields)
    except Exception as e:
        message = str(e).lower()
        if "parent" in message and "parent" in fields:
            log_warning(f"Parent field rejected, retrying without it: {e}")
            without_parent = {k: v for k, v in fields.items() if k != "parent"}
            try:
                issue = jira.create_issue(fields=without_parent)
                return issue
            except Exception as inner:
                log_error("Create-issue (fallback)", inner)
                return None
        log_error("Create-issue", e)
        return None


def _link_relates(jira, from_key: str, to_key: str) -> None:
    """Fallback when `parent` doesn't work — create a 'Relates' link."""
    try:
        jira.create_issue_link("Relates", from_key, to_key)
    except Exception as e:
        log_warning(f"Could not create Relates link {from_key}->{to_key}: {e}")


# =========================================================
# Publisher
# =========================================================

def publish_jira(state: QAState):
    try:
        with Timer("Jira Publishing"):
            jira = get_jira()
            if jira is None or not PROJECT:
                log_step("Jira not configured — skipping publish")
                return {"jira_keys": [], "xray_keys": [], "epic_keys": [], "epic_map": {}}

            features = state.get("features", []) or []
            test_cases = state.get("test_cases_structured", []) or []

            # =========================================================
            # PHASE 1 — Epics
            # =========================================================
            epic_map: Dict[str, str] = {}
            epic_keys: List[str] = []

            if features:
                log_step(f"PHASE 1 — Creating {len(features)} Epic(s)")
                for feature in features:
                    fields = _build_epic_fields(feature)
                    issue = _try_create(jira, fields)
                    if issue is not None:
                        epic_map[feature.get("name", "")] = issue.key
                        epic_keys.append(issue.key)
                        log_success(f"Epic {issue.key} ← {feature.get('name', '?')}")
                    else:
                        log_warning(f"Epic creation failed for: {feature.get('name', '?')}")
            else:
                log_warning("No features to create Epics from")

            # =========================================================
            # PHASE 2 — Test cases linked to their Epic
            # =========================================================
            log_step(
                f"PHASE 2 — Creating {len(test_cases)} {TEST_ISSUETYPE}(s)"
            )

            jira_keys: List[str] = []
            relate_fallbacks: List[tuple[str, str]] = []

            for index, tc in enumerate(test_cases, start=1):
                feature_name = tc.get("feature") or ""
                parent_key = epic_map.get(feature_name)

                fields = _build_test_fields(tc, parent_key)
                issue = _try_create(jira, fields)
                if issue is None:
                    continue

                created_with_parent = "parent" in fields
                # If the issue was created but the parent silently didn't take,
                # add a Relates link as a fallback (visible in Jira).
                if parent_key and not created_with_parent:
                    relate_fallbacks.append((issue.key, parent_key))

                jira_keys.append(issue.key)
                log_success(
                    f"[{index}/{len(test_cases)}] Created {issue.key} "
                    f"(epic: {parent_key or '—'})"
                )

            # =========================================================
            # PHASE 3 — Add fallback Relates links if `parent` was rejected
            # =========================================================
            if relate_fallbacks:
                log_step(f"Creating {len(relate_fallbacks)} Relates link(s) as fallback")
                for from_key, to_key in relate_fallbacks:
                    _link_relates(jira, from_key, to_key)

            log_success(
                f"Done — {len(epic_keys)} Epic(s), {len(jira_keys)} test issue(s)"
            )
            return {
                "epic_keys": epic_keys,
                "epic_map": epic_map,
                "jira_keys": jira_keys,
                "xray_keys": jira_keys if USE_XRAY else [],
            }

    except Exception as e:
        log_error("Jira Publishing", e)
        return {"jira_keys": [], "xray_keys": [], "epic_keys": [], "epic_map": {}}
