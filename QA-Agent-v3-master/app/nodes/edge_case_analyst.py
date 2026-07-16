"""
Edge Case Analyst.

PURPOSE
   Produce a dedicated list of EDGE CASES — subtle conditions that aren't
   happy path and aren't simple negative tests. The output is both a
   standalone report AND a feed into the test case generator.

INPUTS
   - state.requirement_analysis, risk_analysis, security_analysis, api_analysis
   - state.features (for tagging)

OUTPUT (in state)
   edge_cases: List[EdgeCase]
     Each item has: title, description, category (race/state/boundary/...),
     related_feature, expected_failure_mode, suggested_test.

   Also exported as `edge_cases.md` + `edge_cases.json` in the run output.

QA VALUE
   The most expensive bugs in production are edge cases (race conditions,
   state corruption, timezone surprises). Most QA processes don't have a
   dedicated step for hunting them — they get caught by accident. This
   node makes the hunt deliberate and reviewable.
"""
from app.state import QAState
from app.utils.logger import log_step, log_success, log_error, Timer
from app.utils.parser import parse_edge_cases
from app.nodes._common import run_template


def _feature_names_block(features: list[dict]) -> str:
    if not features:
        return "(no features detected)"
    return "\n".join(f"- {f.get('name', '?')}" for f in features)


def edge_case_analyst(state: QAState):
    try:
        with Timer("Edge Case Analysis"):
            log_step("Generating edge cases")

            response = run_template(
                "edge_case_analyst",
                features=_feature_names_block(state.get("features", [])),
                requirement_analysis=state.get("requirement_analysis", ""),
                risk_analysis=state.get("risk_analysis", ""),
                security_analysis=state.get("security_analysis", ""),
                api_analysis=state.get("api_analysis", ""),
            )

            edge_cases = parse_edge_cases(response)
            log_success(f"Identified {len(edge_cases)} edge case(s)")
            return {"edge_cases": [e.model_dump() for e in edge_cases]}

    except Exception as e:
        log_error("Edge Case Analysis", e)
        return {"edge_cases": []}
