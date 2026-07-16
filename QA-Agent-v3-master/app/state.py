"""
LangGraph state — single source of truth for what flows between nodes.

v3 additions: features, edge_cases, epic_keys, dedup metadata, story_analysis.
"""
from typing import TypedDict, List, Dict, Any


class QAState(TypedDict, total=False):

    # ---------- Inputs ----------
    documents: List[Dict[str, Any]]
    selected_agents: List[str]
    story: str

    # ---------- Document metadata ----------
    document_count: int
    total_document_size: int
    chunks_indexed: int

    # ---------- Analysis outputs ----------
    requirement_analysis: str
    risk_analysis: str
    security_analysis: str
    api_analysis: str
    accessibility_analysis: str
    performance_analysis: str
    story_analysis: str

    # ---------- NEW: features ----------
    features: List[Dict[str, Any]]

    # ---------- Generated artifacts ----------
    scenarios: List[str]
    scenarios_structured: List[Dict[str, Any]]
    test_cases: List[str]
    test_cases_structured: List[Dict[str, Any]]
    test_cases_count_before_dedup: int
    test_cases_count_after_dedup: int
    quality_review: str

    # ---------- NEW: edge cases ----------
    edge_cases: List[Dict[str, Any]]

    # ---------- Automation scoring ----------
    automation_candidates: List[Dict[str, Any]]

    # ---------- Traceability ----------
    traceability: List[Dict[str, Any]]

    # ---------- Publication ----------
    epic_keys: List[str]                     # NEW
    epic_map: Dict[str, str]                 # NEW — feature_name -> epic_key
    jira_keys: List[str]
    xray_keys: List[str]

    # ---------- Run-level metadata ----------
    run_id: str
    run_started_at: str
    run_ended_at: str
    output_dir: str
