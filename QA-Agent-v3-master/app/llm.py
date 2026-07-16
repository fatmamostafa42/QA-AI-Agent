"""
Ollama LLM clients with FAST / SMART selection.

Two named models:
  - FAST_MODEL  → cheap, used for the 6 analyst nodes
  - SMART_MODEL → strong, used for scenario / testcase / quality nodes

If only one model is configured, both names point to it.

Each prompt YAML can declare `model: fast` or `model: smart` to override
the default for that prompt.
"""
import os
from functools import lru_cache

from dotenv import load_dotenv
from langchain_ollama import ChatOllama


load_dotenv()


from app.config.config_loader import load_models

cfg = load_models()

FAST_MODEL = cfg["models"]["fast"]
SMART_MODEL = cfg["models"]["smart"]

OLLAMA_BASE_URL = cfg["ollama"]["url"]
OLLAMA_TEMPERATURE = cfg["ollama"]["temperature"]


@lru_cache(maxsize=4)
def _build(model_name: str) -> ChatOllama:
    return ChatOllama(
        model=model_name,
        base_url=OLLAMA_BASE_URL,
        temperature=OLLAMA_TEMPERATURE,
    )


def get_llm(tier: str = "fast") -> ChatOllama:
    """
    Return a ChatOllama instance for the requested tier.

    tier: 'fast' | 'smart' (anything else → 'fast')
    """
    tier = (tier or "fast").lower().strip()
    if tier == "smart":
        return _build(SMART_MODEL)
    return _build(FAST_MODEL)


# Back-compat alias — `from app.llm import llm` still works.
llm = get_llm("smart")
