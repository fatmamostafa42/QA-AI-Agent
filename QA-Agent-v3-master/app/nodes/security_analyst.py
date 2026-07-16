"""Security Analyst — uses the security_analyst.yaml template."""
from app.state import QAState
from app.rag.hybrid_retriever import hybrid_search
from app.utils.logger import log_step, log_success, log_error, Timer
from app.nodes._common import run_template


def security_analyst(state: QAState):
    try:
        with Timer("Security Analysis"):
            log_step("Retrieving security context")
            context = hybrid_search(
                query=(
                    "authentication authorization JWT session OWASP password "
                    "brute force tokens rate limiting encryption APIs"
                ),
                filter_metadata={"section_type": "security"},
            )
            log_success(f"Retrieved context ({len(context)} chars)")

            response = run_template(
                "security_analyst",
                context=context,
                requirement_analysis=state.get("requirement_analysis", ""),
            )
            log_success(f"Security analysis ({len(response)} chars)")
            return {"security_analysis": response}

    except Exception as e:
        log_error("Security Analysis", e)
        return {"security_analysis": f"ERROR: {e}"}
