"""Requirement Analyst — uses the requirement_analyst.yaml template."""
from app.state import QAState
from app.rag.hybrid_retriever import hybrid_search
from app.utils.logger import log_step, log_success, log_error, Timer
from app.nodes._common import run_template


def requirement_analyst(state: QAState):
    try:
        with Timer("Requirement Analysis"):
            log_step("Retrieving requirement context")
            context = hybrid_search(
                query=(
                    "functional requirements validations business rules "
                    "edge cases risks authentication APIs workflows "
                    "integrations authorization concurrency data consistency"
                ),
                filter_metadata={"section_type": "functional"},
            )
            log_success(f"Retrieved context ({len(context)} chars)")

            response = run_template("requirement_analyst", context=context)
            log_success(f"Requirement analysis ({len(response)} chars)")
            return {"requirement_analysis": response}

    except Exception as e:
        log_error("Requirement Analysis", e)
        return {"requirement_analysis": f"ERROR: {e}"}
