"""
Hybrid LLM-output parser.

Two phases:
  1. Try to parse the response as JSON matching the target model.
     (handles ```json fences, leading/trailing prose, etc.)
  2. Fall back to the tolerant text-block parser when JSON parsing fails.

Decision (a) ChatOllama.with_structured_output() is unreliable on the
recommended qwen2.5:3b model. This module gives us the same typed-output
contract while staying robust on small models.
"""
from __future__ import annotations

import json
import re
from typing import List, Dict, Any, Type, TypeVar

from pydantic import BaseModel, ValidationError

from app.schemas import TestCase, Scenario, EdgeCase, Feature
from app.utils.logger import log_warning


T = TypeVar("T", bound=BaseModel)


# =========================================================
# JSON extraction
# =========================================================

_JSON_FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)


def _extract_json_blob(text: str) -> str | None:
    """Return the first JSON-looking blob from `text`, or None."""
    if not text:
        return None

    # 1. ```json fenced block
    fence_match = _JSON_FENCE.search(text)
    if fence_match:
        candidate = fence_match.group(1).strip()
        if candidate:
            return candidate

    # 2. First {...} or [...] block by bracket balancing
    for start_char, end_char in [("[", "]"), ("{", "}")]:
        start = text.find(start_char)
        if start == -1:
            continue
        depth = 0
        for index in range(start, len(text)):
            char = text[index]
            if char == start_char:
                depth += 1
            elif char == end_char:
                depth -= 1
                if depth == 0:
                    return text[start:index + 1]
    return None


def parse_json_list(text: str, model_cls: Type[T]) -> List[T]:
    """Try to parse `text` as a JSON list of `model_cls` objects."""
    blob = _extract_json_blob(text)
    if not blob:
        return []
    try:
        data = json.loads(blob)
    except json.JSONDecodeError as e:
        log_warning(f"JSON parse failed for {model_cls.__name__}: {e}")
        return []

    if not isinstance(data, list):
        if isinstance(data, dict):
            data = [data]
        else:
            return []

    out: List[T] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        try:
            out.append(model_cls(**item))
        except ValidationError:
            continue
    return out


# =========================================================
# Tolerant text-block fallback
#
# Same shape as v2 — split into blocks at "Title:" lines, then
# pull "Field: value" lines into a dict.
# =========================================================

_FIELD_RE = re.compile(
    r"^\s*(title|feature|requirement|scenario|preconditions|test\s*data|steps|"
    r"expected\s*result|priority|severity|type|automation\s*candidate|"
    r"objective|test\s*flow|related\s*requirement|related\s*risk|"
    r"category|expected\s*failure\s*mode|suggested\s*test|description|"
    r"related\s*feature)\s*:\s*(.*)$",
    re.IGNORECASE,
)


def _split_blocks(raw: str) -> List[str]:
    blocks, current = [], []
    for line in raw.splitlines():
        if re.match(r"^\s*title\s*:", line, re.IGNORECASE):
            if current:
                blocks.append("\n".join(current).strip())
            current = [line]
        else:
            current.append(line)
    if current:
        blocks.append("\n".join(current).strip())
    return [b for b in blocks if b]


def _parse_block_to_dict(block: str) -> Dict[str, str]:
    fields, last_key = {}, None
    for raw_line in block.splitlines():
        line = raw_line.rstrip()
        match = _FIELD_RE.match(line)
        if match:
            key = re.sub(r"\s+", "_", match.group(1).strip().lower())
            value = match.group(2).strip()
            fields[key] = value
            last_key = key
        elif last_key and line.strip():
            fields[last_key] = (fields[last_key] + "\n" + line.strip()).strip()
    return fields


_PRIORITY = {
    "p0": "Highest", "p1": "High", "p2": "Medium", "p3": "Low", "p4": "Lowest",
    "highest": "Highest", "critical": "Highest", "high": "High",
    "medium": "Medium", "med": "Medium", "low": "Low", "lowest": "Lowest",
}
_SEVERITY = {
    "blocker": "Blocker", "critical": "Critical", "major": "Major",
    "minor": "Minor", "trivial": "Trivial",
}
_TYPE = {
    "functional": "Functional", "negative": "Negative", "boundary": "Boundary",
    "validation": "Validation", "integration": "Integration", "api": "API",
    "security": "Security", "performance": "Performance",
    "accessibility": "Accessibility", "usability": "Usability",
    "regression": "Regression", "edgecase": "EdgeCase", "edge_case": "EdgeCase",
    "edge case": "EdgeCase", "edge": "EdgeCase",
}


def _to_steps(value: str) -> List[str]:
    if not value:
        return []
    lines = [line.strip(" -*0123456789.\t") for line in value.splitlines()]
    return [line for line in lines if line]


def _to_bool(value: str) -> bool:
    return value.strip().lower() in {"yes", "true", "y", "1"}


# =========================================================
# Hybrid public API
# =========================================================

def parse_test_cases(raw: str) -> List[TestCase]:
    """JSON first, then text-block fallback."""
    cases = parse_json_list(raw, TestCase)
    if cases:
        return cases

    cases = []
    for block in _split_blocks(raw):
        d = _parse_block_to_dict(block)
        if "title" not in d:
            continue
        try:
            cases.append(
                TestCase(
                    title=d.get("title", "").strip()[:255],
                    feature=d.get("feature", ""),
                    requirement=d.get("requirement", ""),
                    scenario=d.get("scenario", ""),
                    preconditions=d.get("preconditions", ""),
                    test_data=d.get("test_data", ""),
                    steps=_to_steps(d.get("steps", "")),
                    expected_result=d.get("expected_result", ""),
                    priority=_PRIORITY.get(d.get("priority", "").lower(), "Medium"),
                    severity=_SEVERITY.get(d.get("severity", "").lower(), "Major"),
                    test_type=_TYPE.get(d.get("type", "").lower(), "Functional"),
                    automation_candidate=_to_bool(d.get("automation_candidate", "yes")),
                )
            )
        except Exception:
            continue
    return cases


def parse_scenarios(raw: str) -> List[Scenario]:
    scenarios = parse_json_list(raw, Scenario)
    if scenarios:
        return scenarios

    scenarios = []
    for block in _split_blocks(raw):
        d = _parse_block_to_dict(block)
        if "title" not in d:
            continue
        try:
            scenarios.append(
                Scenario(
                    title=d.get("title", "").strip()[:255],
                    feature=d.get("feature", ""),
                    objective=d.get("objective", ""),
                    preconditions=d.get("preconditions", ""),
                    test_flow=_to_steps(d.get("test_flow", "")),
                    expected_result=d.get("expected_result", ""),
                    priority=_PRIORITY.get(d.get("priority", "").lower(), "Medium"),
                    scenario_type=_TYPE.get(d.get("type", "").lower(), "Functional"),
                    related_requirement=d.get("related_requirement", ""),
                    related_risk=d.get("related_risk", ""),
                )
            )
        except Exception:
            continue
    return scenarios


def parse_features(raw: str) -> List[Feature]:
    features = parse_json_list(raw, Feature)
    if features:
        return features

    features = []
    for block in _split_blocks(raw):
        d = _parse_block_to_dict(block)
        if "title" not in d:
            continue
        try:
            features.append(
                Feature(
                    name=d.get("title", "").strip()[:120],
                    description=d.get("description", ""),
                    related_requirements=_to_steps(d.get("requirement", "")),
                )
            )
        except Exception:
            continue
    return features


def parse_edge_cases(raw: str) -> List[EdgeCase]:
    edges = parse_json_list(raw, EdgeCase)
    if edges:
        return edges

    edges = []
    for block in _split_blocks(raw):
        d = _parse_block_to_dict(block)
        if "title" not in d:
            continue
        try:
            edges.append(
                EdgeCase(
                    title=d.get("title", "").strip()[:255],
                    description=d.get("description", ""),
                    category=d.get("category", ""),
                    related_feature=d.get("related_feature", ""),
                    expected_failure_mode=d.get("expected_failure_mode", ""),
                    suggested_test=d.get("suggested_test", ""),
                )
            )
        except Exception:
            continue
    return edges
