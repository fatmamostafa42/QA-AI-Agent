"""API Analyst — uses the api_analyst.yaml template."""
from app.state import QAState
from app.rag.hybrid_retriever import hybrid_search
from app.utils.logger import log_step, log_success, log_error, Timer
from app.nodes._common import run_template


def api_analyst(state: QAState):
    try:
        with Timer("API Analysis"):
            log_step("Retrieving API context")
            context = hybrid_search(
                query=(
                    "API endpoints request response validation status codes "
                    "authentication headers tokens integrations payloads "
                    "error handling rate limiting retries schema validation"
                ),
                filter_metadata={"section_type": "api"},
            )
            log_success(f"Retrieved context ({len(context)} chars)")

            response = run_template(
                "api_analyst",
                context=context,
                requirement_analysis=state.get("requirement_analysis", ""),
            )
            log_success(f"API analysis ({len(response)} chars)")
            return {"api_analysis": response}

    except Exception as e:
        log_error("API Analysis", e)
        return {"api_analysis": f"ERROR: {e}"}
