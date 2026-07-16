"""
LangGraph workflow (v3).

Default flow:

  load_documents
    → requirement_analyst              (gate node — must finish first)
    → [PARALLEL FAN-OUT]                (Decision 5: conservative parallel)
        ├─ risk_analyst
        ├─ security_analyst
        ├─ api_analyst
        ├─ accessibility_analyst
        └─ performance_analyst
    → [PARALLEL JOIN at feature_extractor]
    → feature_extractor                 (one Epic per feature later)
    → generate_scenarios
    → edge_case_analyst
    → generate_testcases                (consumes scenarios + edge cases, dedups)
    → automation_candidate_detector
    → quality_reviewer
    → traceability_matrix
    → publish_jira                      (Epics first, then Tasks under parents)
    → report_generator
    → END

If the user passes `--story "..."`, a smaller graph runs:

  analyze_story → feature_extractor → generate_scenarios → edge_case_analyst
    → generate_testcases → automation_candidate_detector → traceability
    → publish_jira → report_generator
"""
from langgraph.graph import StateGraph, END

from app.state import QAState

from app.nodes.load_documents import load_documents
from app.nodes.requirement_analyst import requirement_analyst
from app.nodes.risk_analyst import risk_analyst
from app.nodes.security_analyst import security_analyst
from app.nodes.api_analyst import api_analyst
from app.nodes.accessibility_analyst import accessibility_analyst
from app.nodes.performance_analyst import performance_analyst
from app.nodes.feature_extractor import feature_extractor
from app.nodes.generate_scenarios import generate_scenarios
from app.nodes.edge_case_analyst import edge_case_analyst
from app.nodes.generate_testcases import generate_testcases
from app.nodes.automation_candidate_detector import automation_candidate_detector
from app.nodes.quality_reviewer import quality_reviewer
from app.nodes.traceability_matrix import traceability_matrix
from app.nodes.publish_jira import publish_jira
from app.nodes.report_generator import report_generator
from app.nodes.analyze_story import analyze_story


# =========================================================
# Full graph
# =========================================================

def _build_full_graph():
    builder = StateGraph(QAState)

    # Nodes
    builder.add_node("load_documents",          load_documents)
    builder.add_node("requirement",             requirement_analyst)
    builder.add_node("risk",                    risk_analyst)
    builder.add_node("security",                security_analyst)
    builder.add_node("api",                     api_analyst)
    builder.add_node("accessibility",           accessibility_analyst)
    builder.add_node("performance",             performance_analyst)
    builder.add_node("features",                feature_extractor)
    builder.add_node("scenarios",               generate_scenarios)
    builder.add_node("edge_cases",              edge_case_analyst)
    builder.add_node("testcases",               generate_testcases)
    builder.add_node("automation_candidates",   automation_candidate_detector)
    builder.add_node("quality_review",          quality_reviewer)
    builder.add_node("traceability",            traceability_matrix)
    builder.add_node("jira",                    publish_jira)
    builder.add_node("report",                  report_generator)

    builder.set_entry_point("load_documents")

    # Pipeline
    builder.add_edge("load_documents", "requirement")

    # ===== Fan-out from requirement → 5 parallel analysts =====
    for parallel_node in ["risk", "security", "api", "accessibility", "performance"]:
        builder.add_edge("requirement", parallel_node)

    # ===== Fan-in: all 5 must complete before features =====
    # LangGraph automatically joins when multiple edges target the same node.
    for parallel_node in ["risk", "security", "api", "accessibility", "performance"]:
        builder.add_edge(parallel_node, "features")

    # Linear from there
    builder.add_edge("features",              "scenarios")
    builder.add_edge("scenarios",             "edge_cases")
    builder.add_edge("edge_cases",            "testcases")
    builder.add_edge("testcases",             "automation_candidates")
    builder.add_edge("automation_candidates", "quality_review")
    builder.add_edge("quality_review",        "traceability")
    builder.add_edge("traceability",          "jira")
    builder.add_edge("jira",                  "report")
    builder.add_edge("report",                END)

    return builder.compile()


graph = _build_full_graph()


# =========================================================
# Story flow
# =========================================================

def _build_story_graph():
    builder = StateGraph(QAState)
    builder.add_node("analyze_story", analyze_story)
    builder.add_node("features",      feature_extractor)
    builder.add_node("scenarios",     generate_scenarios)
    builder.add_node("edge_cases",    edge_case_analyst)
    builder.add_node("testcases",     generate_testcases)
    builder.add_node("automation",    automation_candidate_detector)
    builder.add_node("traceability",  traceability_matrix)
    builder.add_node("jira",          publish_jira)
    builder.add_node("report",        report_generator)

    builder.set_entry_point("analyze_story")
    builder.add_edge("analyze_story", "features")
    builder.add_edge("features",      "scenarios")
    builder.add_edge("scenarios",     "edge_cases")
    builder.add_edge("edge_cases",    "testcases")
    builder.add_edge("testcases",     "automation")
    builder.add_edge("automation",    "traceability")
    builder.add_edge("traceability",  "jira")
    builder.add_edge("jira",          "report")
    builder.add_edge("report",        END)
    return builder.compile()


story_graph = _build_story_graph()
