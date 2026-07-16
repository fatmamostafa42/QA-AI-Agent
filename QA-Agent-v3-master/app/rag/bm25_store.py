"""
Standalone BM25 store over the converted markdown files.

Lazy-initialised so importing this module never crashes when the
markdown folder is empty (the previous eager version raised
ZeroDivisionError on empty corpus).
"""
from pathlib import Path
from typing import List, Optional

from rank_bm25 import BM25Okapi


MARKDOWN_DIR = Path("app/markdown")


_documents: List[str] = []
_bm25: Optional[BM25Okapi] = None


def _build() -> None:
    global _documents, _bm25

    _documents = []
    tokenized: List[List[str]] = []

    if not MARKDOWN_DIR.exists():
        _bm25 = None
        return

    for file in MARKDOWN_DIR.glob("*.md"):
        text = file.read_text(encoding="utf-8", errors="ignore")
        if not text.strip():
            continue
        _documents.append(text)
        tokenized.append(text.lower().split())

    _bm25 = BM25Okapi(tokenized) if tokenized else None


def bm25_search(query: str, top_k: int = 3) -> List[str]:
    """Lazy-init on first use; safe to call when no docs exist."""
    global _bm25
    if _bm25 is None:
        _build()
    if _bm25 is None or not _documents:
        return []

    scores = _bm25.get_scores(query.lower().split())
    ranked = sorted(zip(_documents, scores), key=lambda x: x[1], reverse=True)
    return [doc for doc, _ in ranked[:top_k]]
