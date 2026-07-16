"""
Feature Extractor.

PURPOSE
   Detect the top-level product FEATURES described in the requirements.
   Each feature becomes one Jira Epic; downstream test cases are tagged
   with their parent feature and linked under that Epic.

INPUTS
   - state.requirement_analysis
   - RAG context (functional chunks)

OUTPUT (in state)
   features: List[Feature]  (Pydantic-validated)
     [
       {
         "name": "Account Registration & Login",
         "description": "...",
         "related_requirements": ["REQ-1", "REQ-2"]
       },
       ...
     ]

QA VALUE
   Without features, generated test cases are a flat list of 50–200 items
   no one wants to triage. With features:
     - Jira shows one Epic per capability — reviewers scan 8 Epics not 200 tasks
     - Each test case has a parent context, making prioritization realistic
     - Coverage gaps surface ("we have 0 tests for Notifications")
     - Future Xray test-set creation has a natural grouping

COST
   1 LLM call on SMART_MODEL (~30–60s on qwen2.5:7b). Asks for JSON; if
   JSON fails, falls back to the tolerant text-block parser.
"""
from app.state import QAState
from app.rag.hybrid_retriever import hybrid_search
from app.utils.logger import log_step, log_success, log_error, Timer
from app.utils.parser import parse_features
from app.nodes._common import run_template


def feature_extractor(state: QAState):
    try:
        with Timer("Feature Extraction"):
            log_step("Retrieving feature-extraction context")
            context = hybrid_search(
                query=(
                    "features capabilities user stories modules subsystems "
                    "workflows main use cases"
                ),
            )
            log_success(f"Retrieved context ({len(context)} chars)")

            response = run_template(
                "feature_extractor",
                context=context,
                requirement_analysis=state.get("requirement_analysis", ""),
            )

            features = parse_features(response)
            if not features:
                # Defensive fallback — synthesize a single feature so
                # downstream nodes don't crash on an empty list.
                from app.schemas import Feature
                features = [Feature(name="Core Functionality",
                                    description="Auto-fallback feature.")]

            log_success(f"Detected {len(features)} feature(s)")
            for feature in features[:10]:
                log_step(f"  • {feature.name}")

            return {"features": [f.model_dump() for f in features]}

    except Exception as e:
        log_error("Feature Extraction", e)
        return {"features": []}
