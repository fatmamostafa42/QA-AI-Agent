"""Scenario Generator — feature-aware, template-driven."""
from app.state import QAState
from app.rag.hybrid_retriever import hybrid_search
from app.utils.logger import log_step, log_success, log_error, Timer
from app.utils.parser import parse_scenarios
from app.nodes._common import run_template


def _feature_names_block(features: list[dict]) -> str:
    if not features:
        return "(no features detected)"
    return "\n".join(f"- {f.get('name', '?')}" for f in features)


def generate_scenarios(state: QAState):
    try:
        with Timer("Scenario Generation"):
            log_step("Retrieving scenario context")
            context = hybrid_search(
                query=(
                    "business workflows validations user journeys "
                    "edge cases APIs integrations security "
                    "concurrency usability negative flows"
                ),
            )
            log_success(f"Retrieved scenario context ({len(context)} chars)")

            response = run_template(
                "generate_scenarios",
                features=_feature_names_block(state.get("features", [])),
                context=context,
                requirement_analysis=state.get("requirement_analysis", ""),
                risk_analysis=state.get("risk_analysis", ""),
                security_analysis=state.get("security_analysis", ""),
                api_analysis=state.get("api_analysis", ""),
            )

            structured = parse_scenarios(response)

            # Keep both forms — raw blocks (back-compat) + structured JSON
            scenarios_raw = [
                block.strip()
                for block in response.split("\n\n")
                if block.strip() and "title" in block.lower()
            ]

            log_success(f"Generated {len(structured)} scenario(s)")
            return {
                "scenarios": scenarios_raw,
                "scenarios_structured": [s.model_dump() for s in structured],
            }

    except Exception as e:
        log_error("Scenario Generation", e)
        return {"scenarios": [], "scenarios_structured": []}
