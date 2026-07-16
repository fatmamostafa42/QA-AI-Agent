"""
Performance Analyst.

PURPOSE
   Identify load / stress / spike / soak / scalability risks before they
   hit production.

INPUTS
   - state.requirement_analysis  (markdown blob from requirement_analyst)
   - RAG-retrieved chunks filtered to section_type='performance'

OUTPUT (in state)
   performance_analysis: structured markdown with sections:
     - Performance Hot Paths
     - Load Test Scenarios
     - Stress Test Scenarios
     - Spike Test Scenarios
     - Soak Test Scenarios
     - Scalability Risks
     - Suggested KPIs and Thresholds

   Each finding includes: hot path, risk, suggested workload, suggested
   tool (k6/JMeter/Gatling/Locust), suggested KPI/threshold.

QA VALUE
   Functional testing rarely catches performance issues. This node makes
   performance risks first-class:
     - flags database hot paths and cache-invalidation traps
     - surfaces third-party API timeout / retry chains
     - calls out queue back-pressure and async worker bottlenecks
     - turns abstract NFRs (e.g., "fast") into concrete KPIs (p95 < 500ms)
   Prevents the classic "it worked in QA, exploded under real load" outcome.

COST
   1 LLM call on FAST_MODEL (~20–40s on qwen2.5:3b).
"""
from app.state import QAState
from app.rag.hybrid_retriever import hybrid_search
from app.utils.logger import log_step, log_success, log_error, Timer
from app.nodes._common import run_template


def performance_analyst(state: QAState):
    try:
        with Timer("Performance Analysis"):
            log_step("Retrieving performance context")
            context = hybrid_search(
                query=(
                    "performance load throughput latency response time "
                    "scalability concurrent users database query "
                    "caching rate limit timeout"
                ),
                filter_metadata={"section_type": "performance"},
            )
            log_success(f"Retrieved context ({len(context)} chars)")

            response = run_template(
                "performance_analyst",
                context=context,
                requirement_analysis=state.get("requirement_analysis", ""),
            )
            log_success(f"Performance analysis ({len(response)} chars)")
            return {"performance_analysis": response}

    except Exception as e:
        log_error("Performance Analysis", e)
        return {"performance_analysis": f"ERROR: {e}"}
