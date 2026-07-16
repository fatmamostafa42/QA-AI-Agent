"""
Report Generator — final node.

Writes every artifact to `app/outputs/<run_id>/` and mirrors to
`app/outputs/latest/`. Emits `execution_summary.json` for CI.
"""
from datetime import datetime, timezone

from app.state import QAState
from app.schemas import ExecutionSummary
from app.utils.output_writer import (
    ensure_run_dir, write_markdown, write_json, mirror_to_latest,
)
from app.utils.logger import log_step, log_success, log_error, Timer


# =========================================================
# Markdown table helpers
# =========================================================

def _matrix_to_markdown(matrix: list[dict]) -> str:
    if not matrix:
        return "_No traceability data._\n"
    lines = [
        "| # | Feature | Epic | Requirement | Scenarios | Test Cases | Tasks |",
        "|---|---|---|---|---|---|---|",
    ]
    for index, row in enumerate(matrix, start=1):
        scenarios = "; ".join(row.get("scenario_titles", []) or [])
        tests = "; ".join(row.get("test_titles", []) or [])
        jira = ", ".join(row.get("jira_keys", []) or [])
        epic = row.get("epic_key", "") or ""
        feature = row.get("feature", "")
        req = (row.get("requirement") or "").replace("\n", " ").strip()[:80]
        lines.append(
            f"| {index} | {feature[:40]} | {epic} | {req or '_n/a_'} "
            f"| {scenarios[:60] or '_n/a_'} | {tests[:80] or '_n/a_'} "
            f"| {jira or '_n/a_'} |"
        )
    return "\n".join(lines) + "\n"


def _features_to_markdown(features: list[dict], epic_map: dict[str, str]) -> str:
    if not features:
        return "_No features detected._\n"
    lines = ["| # | Feature | Epic | Description |", "|---|---|---|---|"]
    for index, feature in enumerate(features, start=1):
        name = feature.get("name", "")
        desc = (feature.get("description") or "").replace("\n", " ")[:120]
        epic_key = epic_map.get(name, "") or "_pending_"
        lines.append(f"| {index} | {name} | {epic_key} | {desc} |")
    return "\n".join(lines) + "\n"


def _edge_cases_to_markdown(edges: list[dict]) -> str:
    if not edges:
        return "_No edge cases identified._\n"
    lines = [
        "| # | Title | Category | Related Feature | Expected Failure |",
        "|---|---|---|---|---|",
    ]
    for index, edge in enumerate(edges, start=1):
        title = edge.get("title", "")[:80]
        category = edge.get("category", "")
        feature = edge.get("related_feature", "")
        failure = (edge.get("expected_failure_mode") or "").replace("\n", " ")[:100]
        lines.append(
            f"| {index} | {title} | {category} | {feature} | {failure} |"
        )
    return "\n".join(lines) + "\n"


def _automation_to_markdown(rows: list[dict]) -> str:
    if not rows:
        return "_No automation scoring data._\n"
    lines = [
        "| # | Title | Score | Recommendation | Rationale |",
        "|---|---|---|---|---|",
    ]
    for index, row in enumerate(rows, start=1):
        rationale = "; ".join(row.get("rationale", []) or [])
        lines.append(
            f"| {index} | {row.get('title','')[:80]} | {row.get('score',0)} "
            f"| {row.get('recommendation','')} | {rationale} |"
        )
    return "\n".join(lines) + "\n"


# =========================================================
# Node
# =========================================================

def report_generator(state: QAState):
    try:
        with Timer("Report Generation"):
            run_id = state.get(
                "run_id",
                datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S"),
            )
            run_dir = ensure_run_dir(run_id)
            log_step(f"Writing outputs to {run_dir}")

            # ---- Markdown analyses ----
            for field, name in [
                ("requirement_analysis",   "requirement_analysis"),
                ("risk_analysis",          "risk_analysis"),
                ("security_analysis",      "security_analysis"),
                ("api_analysis",           "api_analysis"),
                ("accessibility_analysis", "accessibility_analysis"),
                ("performance_analysis",   "performance_analysis"),
                ("story_analysis",         "story_analysis"),
                ("quality_review",         "quality_review"),
            ]:
                value = state.get(field) or ""
                if value:
                    write_markdown(run_dir, name, value)

            # ---- Features ----
            features = state.get("features", []) or []
            epic_map = state.get("epic_map", {}) or {}
            if features:
                write_markdown(
                    run_dir, "features",
                    "# Features\n\n" + _features_to_markdown(features, epic_map),
                )
                write_json(run_dir, "features", features)

            # ---- Scenarios ----
            scenarios = state.get("scenarios", []) or []
            if scenarios:
                write_markdown(run_dir, "scenarios", "\n\n---\n\n".join(scenarios))
            scenarios_struct = state.get("scenarios_structured", []) or []
            if scenarios_struct:
                write_json(run_dir, "scenarios_structured", scenarios_struct)

            # ---- Test cases ----
            test_cases = state.get("test_cases", []) or []
            if test_cases:
                write_markdown(run_dir, "testcases", "\n\n---\n\n".join(test_cases))
            structured = state.get("test_cases_structured", []) or []
            if structured:
                write_json(run_dir, "testcases_structured", structured)

            # ---- Edge cases ----
            edge_cases = state.get("edge_cases", []) or []
            if edge_cases:
                write_markdown(
                    run_dir, "edge_cases",
                    "# Edge Cases\n\n" + _edge_cases_to_markdown(edge_cases),
                )
                write_json(run_dir, "edge_cases", edge_cases)

            # ---- Traceability ----
            matrix = state.get("traceability", []) or []
            if matrix:
                write_markdown(
                    run_dir, "traceability_matrix",
                    "# Traceability Matrix\n\n" + _matrix_to_markdown(matrix),
                )
                write_json(run_dir, "traceability_matrix", matrix)

            # ---- Automation ----
            automation = state.get("automation_candidates", []) or []
            if automation:
                write_markdown(
                    run_dir, "automation_candidates",
                    "# Automation Candidate Scoring\n\n"
                    + _automation_to_markdown(automation),
                )
                write_json(run_dir, "automation_candidates", automation)

            # ---- Execution summary ----
            started_at = state.get("run_started_at") or datetime.now(timezone.utc).isoformat()
            ended_at = datetime.now(timezone.utc).isoformat()

            try:
                elapsed = (
                    datetime.fromisoformat(ended_at)
                    - datetime.fromisoformat(started_at)
                ).total_seconds()
            except Exception:
                elapsed = 0.0

            summary = ExecutionSummary(
                run_id=run_id,
                started_at=started_at,
                ended_at=ended_at,
                elapsed_seconds=round(elapsed, 2),
                document_count=state.get("document_count", 0),
                chunks_indexed=state.get("chunks_indexed", 0),
                feature_count=len(features),
                requirement_analysis_chars=len(state.get("requirement_analysis", "") or ""),
                risk_analysis_chars=len(state.get("risk_analysis", "") or ""),
                security_analysis_chars=len(state.get("security_analysis", "") or ""),
                api_analysis_chars=len(state.get("api_analysis", "") or ""),
                accessibility_analysis_chars=len(state.get("accessibility_analysis", "") or ""),
                performance_analysis_chars=len(state.get("performance_analysis", "") or ""),
                scenario_count=len(state.get("scenarios", []) or []),
                test_case_count=state.get("test_cases_count_before_dedup")
                                or len(state.get("test_cases", []) or []),
                test_case_count_after_dedup=state.get("test_cases_count_after_dedup")
                                            or len(structured),
                edge_case_count=len(edge_cases),
                automation_candidates=sum(
                    1 for r in (state.get("automation_candidates") or [])
                    if r.get("score", 0) >= 0.55
                ),
                epic_keys=state.get("epic_keys", []) or [],
                jira_keys=state.get("jira_keys", []) or [],
                xray_keys=state.get("xray_keys", []) or [],
            )
            write_json(run_dir, "execution_summary", summary.model_dump())

            mirror_to_latest(run_dir)
            log_success(f"Reports written to {run_dir} (+ mirrored to outputs/latest)")
            return {"output_dir": str(run_dir), "run_ended_at": ended_at}

    except Exception as e:
        log_error("Report Generation", e)
        return {}
