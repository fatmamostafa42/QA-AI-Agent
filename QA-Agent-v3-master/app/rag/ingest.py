"""
Vector database ingestion.

Splits markdown files into chunks (default 1500 chars per user guide,
override via RAG_CHUNK_SIZE / RAG_CHUNK_OVERLAP env vars), tags each
chunk with a section_type for metadata filtering, and persists to
ChromaDB.
"""
import os
import re
import uuid
import shutil

from pathlib import Path

from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.documents import Document

from app.rag.embeddings import embeddings
from app.rag.cache import vectorstore_exists
from app.utils.logger import log_info, log_success, log_warning


load_dotenv()


MARKDOWN_DIR = Path("app/markdown")
CHROMA_DIR = Path("app/rag/vectorstore")

CHUNK_SIZE = int(os.getenv("RAG_CHUNK_SIZE", "1500"))
CHUNK_OVERLAP = int(os.getenv("RAG_CHUNK_OVERLAP", "200"))


# =========================================================
# Section detection — expanded vocabulary
#
# The guide promises 7 categories; we add 3 more useful ones:
# accessibility, mobile, integration, data, ui.
# =========================================================

SECTION_RULES = [
    ("security",      ["jwt", "oauth", "token", "password", "authentication",
                       "authorization", "login", "permission", "owasp",
                       "encryption", "vulnerability", "csrf", "xss",
                       "sql injection", "session", "audit", "privilege"]),
    ("api",           ["endpoint", "request", "response", "rest", "graphql",
                       "status code", "payload", "header", "rate limit",
                       "api", "http", "json"]),
    ("payment",       ["payment", "transaction", "checkout", "invoice",
                       "billing", "refund", "stripe", "paypal"]),
    ("performance",   ["load", "stress", "throughput", "latency",
                       "performance", "scalability", "concurrent",
                       "soak", "spike"]),
    ("accessibility", ["accessibility", "wcag", "screen reader", "aria",
                       "keyboard navigation", "color contrast"]),
    ("mobile",        ["ios", "android", "mobile", "responsive", "appium",
                       "tablet", "touch"]),
    ("integration",   ["integration", "webhook", "third party", "external",
                       "sync", "import", "export"]),
    ("data",          ["database", "schema", "migration", "model", "table",
                       "constraint"]),
    ("ui",            ["page", "screen", "button", "form", "modal",
                       "dropdown", "frontend"]),
]


def detect_section_type(text: str) -> str:
    lower = text.lower()
    for category, keywords in SECTION_RULES:
        for keyword in keywords:
            if keyword in lower:
                return category
    return "functional"


# =========================================================
# Header-aware chunking
# =========================================================

def _build_splitter() -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n## ", "\n### ", "\n#### ", "\n\n", "\n", ". ", " ", ""],
        keep_separator=True,
    )


def _detect_heading(chunk: str) -> str | None:
    match = re.match(r"^\s*#{1,6}\s+(.+)", chunk)
    return match.group(1).strip() if match else None


# =========================================================
# Ingestion
# =========================================================

def ingest_documents(force_rebuild: bool = False) -> int:
    """Build (or reuse) the vector store. Returns the number of chunks indexed."""

    if vectorstore_exists() and not force_rebuild:
        log_info("Using cached vector database")
        return 0

    if force_rebuild and CHROMA_DIR.exists():
        shutil.rmtree(CHROMA_DIR)
        log_info("Removed old vector database")

    if not MARKDOWN_DIR.exists() or not any(MARKDOWN_DIR.glob("*.md")):
        log_warning(f"No markdown files found in {MARKDOWN_DIR}")
        return 0

    splitter = _build_splitter()
    docs: list[Document] = []

    for file in sorted(MARKDOWN_DIR.glob("*.md")):
        content = file.read_text(encoding="utf-8", errors="ignore")
        if not content.strip():
            log_warning(f"Empty file skipped: {file.name}")
            continue

        chunks = splitter.split_text(content)
        for index, chunk in enumerate(chunks):
            docs.append(
                Document(
                    page_content=chunk,
                    metadata={
                        "source": file.name,
                        "chunk_id": str(uuid.uuid4()),
                        "section_type": detect_section_type(chunk),
                        "chunk_index": index,
                        "heading": _detect_heading(chunk) or "",
                    },
                )
            )

        log_info(f"Embedded {len(chunks)} chunks from {file.name}")

    if not docs:
        log_warning("Nothing to ingest")
        return 0

    Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory=str(CHROMA_DIR),
    )
    log_success(f"Ingested {len(docs)} chunks into vector store")
    return len(docs)
