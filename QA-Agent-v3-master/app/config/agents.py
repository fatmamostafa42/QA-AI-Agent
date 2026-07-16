"""
Agent registry — listing for --help and alias resolution.

v3 adds: feature_extractor, edge_case_analyst.
"""
from typing import List, Dict


AGENTS: List[Dict[str, object]] = [
    {"node_key": "requirement",           "aliases": ["requirement", "requirement_analyst", "requirements"],            "phase": "analyze"},
    {"node_key": "risk",                  "aliases": ["risk", "risk_analyst", "risks"],                                  "phase": "analyze"},
    {"node_key": "security",              "aliases": ["security", "security_analyst"],                                   "phase": "analyze"},
    {"node_key": "api",                   "aliases": ["api", "api_analyst"],                                             "phase": "analyze"},
    {"node_key": "accessibility",         "aliases": ["accessibility", "accessibility_analyst", "a11y"],                 "phase": "analyze"},
    {"node_key": "performance",           "aliases": ["performance", "performance_analyst", "perf"],                     "phase": "analyze"},
    {"node_key": "features",              "aliases": ["features", "feature_extractor"],                                  "phase": "structure"},
    {"node_key": "scenarios",             "aliases": ["scenarios", "generate_scenarios"],                                "phase": "generate"},
    {"node_key": "edge_cases",            "aliases": ["edge_cases", "edge_case_analyst", "edge"],                        "phase": "generate"},
    {"node_key": "testcases",             "aliases": ["testcases", "generate_testcases", "tests"],                       "phase": "generate"},
    {"node_key": "automation_candidates", "aliases": ["automation", "automation_candidates", "automation_candidate_detector"], "phase": "review"},
    {"node_key": "quality_review",        "aliases": ["quality", "quality_review", "quality_reviewer"],                  "phase": "review"},
    {"node_key": "traceability",          "aliases": ["traceability", "traceability_matrix"],                            "phase": "review"},
    {"node_key": "jira",                  "aliases": ["jira", "publish_jira"],                                           "phase": "publish"},
    {"node_key": "report",                "aliases": ["report", "report_generator"],                                     "phase": "report"},
]


_ALIAS_TO_KEY: Dict[str, str] = {
    alias.lower(): agent["node_key"]
    for agent in AGENTS
    for alias in agent["aliases"]
}


def resolve_alias(name: str) -> str | None:
    return _ALIAS_TO_KEY.get(name.lower().strip())


def all_node_keys() -> List[str]:
    return [agent["node_key"] for agent in AGENTS]
