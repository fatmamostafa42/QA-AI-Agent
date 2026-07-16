"""
Pydantic schemas — validate LLM output and serialize cleanly.

Adds Feature, EdgeCase, structured Analysis blobs.
"""
from typing import List, Optional, Literal

from pydantic import BaseModel, Field, ConfigDict


Priority = Literal["Lowest", "Low", "Medium", "High", "Highest"]
Severity = Literal["Trivial", "Minor", "Major", "Critical", "Blocker"]
TestType = Literal[
    "Functional", "Negative", "Boundary", "Validation",
    "Integration", "API", "Security", "Performance",
    "Accessibility", "Usability", "Regression", "EdgeCase",
]


# =========================================================
# Features  (NEW — used for Jira Epic grouping)
# =========================================================

class Feature(BaseModel):
    """One feature detected in the SRS — becomes a Jira Epic."""
    model_config = ConfigDict(extra="allow")

    name: str
    description: str = ""
    related_requirements: List[str] = Field(default_factory=list)


# =========================================================
# Edge cases  (NEW — separate artifact)
# =========================================================

class EdgeCase(BaseModel):
    """One edge case identified by the edge_case analyst."""
    model_config = ConfigDict(extra="allow")

    title: str
    description: str = ""
    category: str = ""                       # race / boundary / state / data / etc.
    related_feature: Optional[str] = ""
    expected_failure_mode: str = ""
    suggested_test: str = ""


# =========================================================
# Test artifacts
# =========================================================

class TestCase(BaseModel):
    model_config = ConfigDict(extra="allow")

    title: str
    feature: Optional[str] = ""              # NEW — for Epic grouping
    requirement: Optional[str] = ""
    scenario: Optional[str] = ""
    preconditions: Optional[str] = ""
    test_data: Optional[str] = ""
    steps: List[str] = Field(default_factory=list)
    expected_result: Optional[str] = ""
    priority: Priority = "Medium"
    severity: Severity = "Major"
    test_type: TestType = "Functional"
    automation_candidate: bool = True
    automation_score: float = Field(0.0, ge=0.0, le=1.0)
    tags: List[str] = Field(default_factory=list)


class Scenario(BaseModel):
    title: str
    feature: Optional[str] = ""              # NEW
    objective: Optional[str] = ""
    preconditions: Optional[str] = ""
    test_flow: List[str] = Field(default_factory=list)
    expected_result: Optional[str] = ""
    priority: Priority = "Medium"
    scenario_type: TestType = "Functional"
    related_requirement: Optional[str] = ""
    related_risk: Optional[str] = ""


class TraceabilityRow(BaseModel):
    feature: str = ""
    requirement: str
    scenario_titles: List[str]
    test_titles: List[str]
    jira_keys: List[str] = Field(default_factory=list)
    epic_key: str = ""


# =========================================================
# Run summary
# =========================================================

class ExecutionSummary(BaseModel):
    run_id: str
    started_at: str
    ended_at: str
    elapsed_seconds: float

    document_count: int = 0
    chunks_indexed: int = 0
    feature_count: int = 0

    requirement_analysis_chars: int = 0
    risk_analysis_chars: int = 0
    security_analysis_chars: int = 0
    api_analysis_chars: int = 0
    accessibility_analysis_chars: int = 0
    performance_analysis_chars: int = 0

    scenario_count: int = 0
    test_case_count: int = 0
    test_case_count_after_dedup: int = 0
    edge_case_count: int = 0
    automation_candidates: int = 0

    epic_keys: List[str] = Field(default_factory=list)
    jira_keys: List[str] = Field(default_factory=list)
    xray_keys: List[str] = Field(default_factory=list)
