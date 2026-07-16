"""
Test Case Generator.

- Feature-aware (every test case has `feature` set).
- Produces structured TestCase output (Pydantic-validated).
- Runs dedup at the end.
- For every edge_case found upstream, also generates a test case
  tagged `test_type: EdgeCase`.
"""
from app.state import QAState
from app.rag.hybrid_retriever import hybrid_search
from app.utils.logger import log_step, log_success, log_error, Timer
from app.utils.parser import parse_test_cases
from app.utils.dedup import dedup_test_cases
from app.nodes._common import run_template
from app.schemas import TestCase


def _feature_names_block(features: list[dict]) -> str:
    if not features:
        return "(no features detected)"
    return "\n".join(f"- {f.get('name', '?')}" for f in features)


def _edge_cases_to_test_cases(edge_cases: list[dict]) -> list[dict]:
    """One test case per edge case so they end up in Jira too."""
    cases = []
    for edge in edge_cases or []:
        try:
            tc = TestCase(
                title=f"[EDGE] {edge.get('title', 'untitled edge case')[:200]}",
                feature=edge.get("related_feature", ""),
                requirement="",
                scenario=edge.get("description", ""),
                preconditions=edge.get("description", ""),
                test_data=f"Category: {edge.get('category', '')}",
                steps=[edge.get("suggested_test", "")] if edge.get("suggested_test") else [],
                expected_result=edge.get("expected_failure_mode", ""),
                priority="High",
                severity="Major",
                test_type="EdgeCase",
                automation_candidate=True,
                tags=["edge_case", edge.get("category", "")],
            )
            cases.append(tc.model_dump())
        except Exception:
            continue
    return cases


def generate_testcases(state: QAState):
    try:
        with Timer("Test Case Generation"):
            scenarios = "\n\n".join(state.get("scenarios", []) or [])
            log_step(
                f"Generating test cases from "
                f"{len(state.get('scenarios', []) or [])} scenario(s)"
            )

            context = hybrid_search(
                query=(
                    "validations workflows APIs boundaries "
                    "integrations security business rules "
                    "negative flows concurrency usability"
                ),
            )
            log_success(f"Retrieved testcase context ({len(context)} chars)")

            response = run_template(
                "generate_testcases",
                features=_feature_names_block(state.get("features", [])),
                context=context,
                requirement_analysis=state.get("requirement_analysis", ""),
                risk_analysis=state.get("risk_analysis", ""),
                security_analysis=state.get("security_analysis", ""),
                api_analysis=state.get("api_analysis", ""),
                accessibility_analysis=state.get("accessibility_analysis", ""),
                performance_analysis=state.get("performance_analysis", ""),
                scenarios=scenarios,
            )

            structured = [tc.model_dump() for tc in parse_test_cases(response)]

            # Append one test case per edge case
            edge_case_tests = _edge_cases_to_test_cases(state.get("edge_cases", []))
            structured.extend(edge_case_tests)
            log_step(
                f"Generated {len(structured) - len(edge_case_tests)} from LLM "
                f"+ {len(edge_case_tests)} from edge cases"
            )

            # Dedup
            count_before = len(structured)
            kept, dropped = dedup_test_cases(structured)
            log_success(
                f"Dedup: kept {len(kept)}, dropped {len(dropped)} "
                f"(of {count_before})"
            )

            # Build raw form too (back-compat for nodes that still expect strings)
            raw_blocks = []
            for tc in kept:
                steps_text = "\n".join(f"{index + 1}. {step}"
                                       for index, step in enumerate(tc.get("steps") or []))
                raw_blocks.append(
                    f"Title: {tc['title']}\n"
                    f"Feature: {tc.get('feature', '')}\n"
                    f"Requirement: {tc.get('requirement', '')}\n"
                    f"Scenario: {tc.get('scenario', '')}\n"
                    f"Preconditions: {tc.get('preconditions', '')}\n"
                    f"Test Data: {tc.get('test_data', '')}\n"
                    f"Steps:\n{steps_text}\n"
                    f"Expected Result: {tc.get('expected_result', '')}\n"
                    f"Priority: {tc.get('priority', 'Medium')}\n"
                    f"Severity: {tc.get('severity', 'Major')}\n"
                    f"Type: {tc.get('test_type', 'Functional')}\n"
                    f"Automation Candidate: "
                    f"{'Yes' if tc.get('automation_candidate') else 'No'}"
                )

            return {
                "test_cases": raw_blocks,
                "test_cases_structured": kept,
                "test_cases_count_before_dedup": count_before,
                "test_cases_count_after_dedup": len(kept),
            }

    except Exception as e:
        log_error("Test Case Generation", e)
        return {"test_cases": [], "test_cases_structured": []}
