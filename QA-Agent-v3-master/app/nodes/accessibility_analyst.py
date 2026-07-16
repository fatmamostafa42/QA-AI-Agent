"""Accessibility Analyst — uses the accessibility_analyst.yaml template."""
from app.state import QAState
from app.rag.hybrid_retriever import hybrid_search
from app.utils.logger import log_step, log_success, log_error, Timer
from app.nodes._common import run_template


def accessibility_analyst(state: QAState):
    try:
        with Timer("Accessibility Analysis"):
            log_step("Retrieving accessibility context")
            context = hybrid_search(
                query=(
                    "accessibility wcag aria screen reader keyboard navigation "
                    "color contrast focus order alt text semantic html"
                ),
                filter_metadata={"section_type": "accessibility"},
            )
            log_success(f"Retrieved context ({len(context)} chars)")

            response = run_template(
                "accessibility_analyst",
                context=context,
                requirement_analysis=state.get("requirement_analysis", ""),
            )
            log_success(f"Accessibility analysis ({len(response)} chars)")
            return {"accessibility_analysis": response}

    except Exception as e:
        log_error("Accessibility Analysis", e)
        return {"accessibility_analysis": f"ERROR: {e}"}
