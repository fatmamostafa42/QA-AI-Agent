"""Risk Analyst — uses the risk_analyst.yaml template."""
from app.state import QAState
from app.rag.hybrid_retriever import hybrid_search
from app.utils.logger import log_step, log_success, log_error, Timer
from app.nodes._common import run_template


def risk_analyst(state: QAState):
    try:
        with Timer("Risk Analysis"):
            log_step("Retrieving risk context")
            context = hybrid_search(
                query=(
                    "business risks validation failures concurrency regression "
                    "edge cases APIs integrations transactions authentication "
                    "authorization performance scalability"
                ),
                filter_metadata={"section_type": "functional"},
            )
            log_success(f"Retrieved context ({len(context)} chars)")

            response = run_template(
                "risk_analyst",
                context=context,
                requirement_analysis=state.get("requirement_analysis", ""),
            )
            log_success(f"Risk analysis ({len(response)} chars)")
            return {"risk_analysis": response}

    except Exception as e:
        log_error("Risk Analysis", e)
        return {"risk_analysis": f"ERROR: {e}"}
