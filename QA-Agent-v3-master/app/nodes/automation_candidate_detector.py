"""
Automation Candidate Detector.

PURPOSE
   Tell the QA team which generated test cases are worth automating now,
   which should be stabilised first, and which should stay manual.

INPUTS
   - state.test_cases_structured (preferred)
   - state.test_cases (fallback for raw text)

OUTPUT (in state)
   automation_candidates: list of
     {
       "title": "...",
       "score": 0.95,
       "recommendation": "Automate" | "Automate after stabilization" |
                         "Manual first; revisit" | "Keep manual",
       "rationale": ["+ api", "+ status code", "- captcha", ...]
     }

   Also exported as `automation_candidates.md` and `automation_candidates.json`.

QA VALUE
   Prevents wasted automation effort. Without this node, teams often:
     - try to automate captcha / 2FA / visual review tests (low ROI)
     - skip automating high-value API regression tests (high ROI)
     - blindly mark every test "automation candidate = Yes"
   This node uses domain heuristics to surface the real candidates:
     + API tests, boundary tests, regression tests → high score
     - captcha, manual inspection, physical device, real payment → low score

   Recommendation thresholds:
     ≥ 0.75 → Automate
     0.55–0.75 → Automate after stabilization
     0.35–0.55 → Manual first; revisit
     < 0.35   → Keep manual

COST
   FREE. Rule-based scoring, no LLM call. Runs in < 1 second for hundreds
   of test cases.
"""
from typing import Dict, List, Any

from app.state import QAState
from app.utils.logger import log_step, log_success, log_error, Timer


_POSITIVE_SIGNALS = {
    "api":            0.20,
    "endpoint":       0.15,
    "status code":    0.10,
    "request":        0.05,
    "response":       0.05,
    "schema":         0.10,
    "boundary":       0.15,
    "validation":     0.10,
    "regression":     0.15,
    "json":           0.05,
    "database":       0.05,
    "calculation":    0.10,
    "rate limit":     0.10,
}

_NEGATIVE_SIGNALS = {
    "look and feel":           -0.20,
    "subjective":              -0.20,
    "manual inspection":       -0.20,
    "exploratory":             -0.15,
    "visual review":           -0.15,
    "captcha":                 -0.25,
    "two factor":              -0.15,
    "2fa":                     -0.15,
    "third party email":       -0.10,
    "physical device":         -0.30,
    "real payment":            -0.20,
    "human verification":      -0.25,
    "screen reader":           -0.10,
    "accessibility audit":     -0.10,
}


def _score(text: str) -> float:
    lower = text.lower()
    score = 0.5
    for signal, weight in _POSITIVE_SIGNALS.items():
        if signal in lower:
            score += weight
    for signal, weight in _NEGATIVE_SIGNALS.items():
        if signal in lower:
            score += weight
    return max(0.0, min(1.0, score))


def _recommendation(score: float) -> str:
    if score >= 0.75:
        return "Automate"
    if score >= 0.55:
        return "Automate after stabilization"
    if score >= 0.35:
        return "Manual first; revisit"
    return "Keep manual"


def _rationale(text: str) -> List[str]:
    lower = text.lower()
    reasons: List[str] = []
    for signal in _POSITIVE_SIGNALS:
        if signal in lower:
            reasons.append(f"+ {signal}")
    for signal in _NEGATIVE_SIGNALS:
        if signal in lower:
            reasons.append(f"- {signal}")
    return reasons[:6]


def _flatten_structured(tc: Dict[str, Any]) -> str:
    """Compose a single string from a structured TestCase for scoring."""
    parts = [
        tc.get("title", ""),
        tc.get("scenario", ""),
        " ".join(tc.get("steps") or []),
        tc.get("expected_result", ""),
        tc.get("test_data", ""),
        tc.get("test_type", ""),
    ]
    return " ".join(p for p in parts if p)


def automation_candidate_detector(state: QAState):
    try:
        with Timer("Automation Candidate Detection"):
            structured: List[Dict] = state.get("test_cases_structured") or []
            raw: List[str] = state.get("test_cases") or []

            items: List[tuple[str, str]] = []   # (title, scoring_text)

            if structured:
                for tc in structured:
                    items.append((tc.get("title", "untitled"),
                                  _flatten_structured(tc)))
            else:
                for text in raw:
                    title_line = text.splitlines()[0] if text else ""
                    title = title_line.replace("Title:", "").strip()[:120] or "untitled"
                    items.append((title, text))

            log_step(f"Scoring {len(items)} test case(s)")

            scored: List[Dict] = []
            for title, text in items:
                score = _score(text)
                scored.append({
                    "title": title,
                    "score": round(score, 2),
                    "recommendation": _recommendation(score),
                    "rationale": _rationale(text),
                })

            scored.sort(key=lambda r: r["score"], reverse=True)
            automatable = sum(1 for r in scored if r["score"] >= 0.55)
            log_success(
                f"Scored {len(scored)} cases — {automatable} good "
                f"automation candidate(s)"
            )
            return {"automation_candidates": scored}

    except Exception as e:
        log_error("Automation Candidate Detection", e)
        return {"automation_candidates": []}
