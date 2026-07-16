import time

from pathlib import Path

from app.state import QAState

from app.utils.logger import (
    log_agent_start,
    log_agent_end,
    log_error,
    log_step,
    log_success
)


MARKDOWN_DIR = Path("app/markdown")


def load_documents(state: QAState):

    agent = "Document Loader"

    start = time.time()

    try:

        log_agent_start(agent)

        # ---------------------------------
        # Validate Directory
        # ---------------------------------

        log_step("Checking markdown directory...")

        if not MARKDOWN_DIR.exists():

            raise FileNotFoundError(
                f"Markdown directory not found: "
                f"{MARKDOWN_DIR}"
            )

        # ---------------------------------
        # Load Documents
        # ---------------------------------

        documents = []

        markdown_files = list(
            MARKDOWN_DIR.glob("*.md")
        )

        log_success(
            f"Found {len(markdown_files)} markdown files"
        )

        for file in markdown_files:

            log_step(f"Loading file: {file.name}")

            content = file.read_text(
                encoding="utf-8",
                errors="ignore"
            )

            document = {
                "filename": file.name,
                "path": str(file),
                "content": content,
                "size": len(content)
            }

            documents.append(document)

            log_success(
                f"Loaded {file.name} "
                f"({len(content)} chars)"
            )

        # ---------------------------------
        # Final Summary
        # ---------------------------------

        total_chars = sum(
            doc["size"]
            for doc in documents
        )

        log_success(
            f"Total documents loaded: "
            f"{len(documents)}"
        )

        log_success(
            f"Total content size: "
            f"{total_chars} chars"
        )

        log_agent_end(agent, start)

        return {

            # Main Output
            "documents": documents,

            # Metadata
            "document_count": len(documents),

            "total_document_size": total_chars
        }

    except Exception as e:

        log_error(agent, e)

        raise e