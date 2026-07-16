"""Quality Reviewer — uses the quality_reviewer.yaml template."""
import json

from app.state import QAState
from app.utils.logger import log_step, log_success, log_error, Timer
from app.nodes._common import run_template


def quality_reviewer(state: QAState):
    try:
        with Timer("Quality Review"):
            scenarios = state.get("scenarios", []) or []
            test_cases = state.get("test_cases", []) or []
            edge_cases = state.get("edge_cases", []) or []

            log_step(
                f"Reviewing {len(scenarios)} scenario(s), "
                f"{len(test_cases)} test case(s), "
                f"{len(edge_cases)} edge case(s)"
            )

            scenarios_text = "\n\n".join(scenarios)[:8000]
            test_cases_text = "\n\n".join(test_cases)[:10000]
            edge_cases_text = json.dumps(edge_cases, indent=2)[:4000]

            response = run_template(
                "quality_reviewer",
                scenarios=scenarios_text,
                test_cases=test_cases_text,
                edge_cases=edge_cases_text,
            )
            log_success(f"Quality review ({len(response)} chars)")
            return {"quality_review": response}

    except Exception as e:
        log_error("Quality Review", e)
        return {"quality_review": f"ERROR: {e}"}
