from pathlib import Path


VECTOR_DB_PATH = Path("app/rag/vectorstore")


def vectorstore_exists():

    return VECTOR_DB_PATH.exists() and any(
        VECTOR_DB_PATH.iterdir()
    )