"""Story Analyst — analyzes a single Jira story via the analyze_story.yaml template."""
from app.state import QAState
from app.rag.hybrid_retriever import hybrid_search
from app.utils.logger import log_step, log_success, log_error, Timer
from app.nodes._common import run_template


def analyze_story(state: QAState):
    try:
        with Timer("Story Analysis"):
            story = state.get("story", "")
            if not story:
                return {"story_analysis": "ERROR: no story provided"}

            log_step("Retrieving SRS context for story")
            context = hybrid_search(
                query=story + " functional requirements validations workflows "
                              "APIs authentication integrations edge cases",
            )
            log_success(f"Retrieved context ({len(context)} chars)")

            response = run_template(
                "analyze_story",
                context=context,
                story=story,
            )
            log_success(f"Story analysis ({len(response)} chars)")

            # Also set requirement_analysis so downstream nodes can consume it
            return {
                "story_analysis": response,
                "requirement_analysis": response,
            }

    except Exception as e:
        log_error("Story Analysis", e)
        return {"story_analysis": f"ERROR: {e}"}
