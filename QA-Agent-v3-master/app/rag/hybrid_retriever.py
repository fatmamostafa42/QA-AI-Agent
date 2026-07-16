"""
Hybrid retriever — vector search (Chroma) + BM25 reranking.

The vectorstore is lazy-initialised so importing this module doesn't
require Ollama to be running and doesn't trigger embeddings to be
loaded on cold start (the previous version created the vectorstore at
import time, which crashed when Ollama wasn't available yet).
"""
from typing import Optional

from rank_bm25 import BM25Okapi
from langchain_chroma import Chroma

from app.rag.embeddings import embeddings


CHROMA_DIR = "app/rag/vectorstore"


_vectorstore: Optional[Chroma] = None


def _get_vectorstore() -> Chroma:
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = Chroma(
            persist_directory=CHROMA_DIR,
            embedding_function=embeddings,
        )
    return _vectorstore


def hybrid_search(
    query: str,
    k: int = 5,
    filter_metadata: dict | None = None,
) -> str:
    # ---------- Vector search ----------
    try:
        vector_results = _get_vectorstore().similarity_search(
            query=query, k=k, filter=filter_metadata,
        )
    except Exception:
        return ""

    if not vector_results:
        return ""

    corpus = [doc.page_content for doc in vector_results]

    # ---------- BM25 rerank ----------
    tokenized_corpus = [doc.split() for doc in corpus]
    bm25 = BM25Okapi(tokenized_corpus)
    bm25_scores = bm25.get_scores(query.split())

    ranked = sorted(
        zip(vector_results, bm25_scores),
        key=lambda x: x[1],
        reverse=True,
    )

    return "\n\n".join(doc.page_content for doc, _ in ranked[:k])
