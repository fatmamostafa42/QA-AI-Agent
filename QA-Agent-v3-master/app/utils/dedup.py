"""
Embedding-based test case deduplicator.

Uses the same Ollama embeddings already in the project to compute a
similarity signature for each test case (title + first step), then
greedily removes near-duplicates above the configured cosine threshold.

Threshold default: 0.90 (configurable via TC_DEDUP_THRESHOLD env var).
"""
from __future__ import annotations

import math
import os
from typing import List, Dict, Any, Tuple

from app.rag.embeddings import embeddings
from app.utils.logger import log_info, log_warning


THRESHOLD = float(os.getenv("TC_DEDUP_THRESHOLD", "0.90"))


def _signature(tc: Dict[str, Any]) -> str:
    """Title + first step = the dedup signature (Decision (b))."""
    title = (tc.get("title") or "").strip()
    steps = tc.get("steps") or []
    first_step = steps[0] if steps else ""
    if isinstance(first_step, dict):
        first_step = first_step.get("action") or first_step.get("text", "")
    return f"{title} || {first_step}".strip()


def _cosine(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def dedup_test_cases(
    test_cases: List[Dict[str, Any]],
    threshold: float = THRESHOLD,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Returns (kept, dropped). `kept` preserves input order; `dropped`
    is annotated with `_dropped_because = 'similar to: <kept_title>'`.
    """
    if len(test_cases) < 2:
        return list(test_cases), []

    signatures = [_signature(tc) for tc in test_cases]

    try:
        vectors = embeddings.embed_documents(signatures)
    except Exception as e:
        log_warning(f"Embeddings unavailable for dedup ({e}); skipping")
        return list(test_cases), []

    kept: List[Dict[str, Any]] = []
    kept_vectors: List[List[float]] = []
    dropped: List[Dict[str, Any]] = []

    for index, tc in enumerate(test_cases):
        vector = vectors[index]
        is_duplicate = False
        for kept_index, kv in enumerate(kept_vectors):
            sim = _cosine(vector, kv)
            if sim >= threshold:
                annotated = dict(tc)
                annotated["_dropped_because"] = (
                    f"similar to: {kept[kept_index].get('title', '?')} "
                    f"(cosine={sim:.3f})"
                )
                dropped.append(annotated)
                is_duplicate = True
                break
        if not is_duplicate:
            kept.append(tc)
            kept_vectors.append(vector)

    log_info(
        f"Dedup: kept {len(kept)} / dropped {len(dropped)} "
        f"(threshold {threshold:.2f})"
    )
    return kept, dropped
