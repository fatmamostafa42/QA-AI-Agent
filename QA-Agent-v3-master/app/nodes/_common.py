"""
Shared helper used by every analyst node.

`run_template(name, **vars)` loads the YAML template, renders it with
the supplied variables, picks the right LLM tier, invokes the LLM, and
returns the raw text response.

Centralizes the boilerplate that used to be duplicated across all nodes.
"""
from app.llm import get_llm
from app.prompts_engine.loader import load
from app.utils.logger import log_warning


def run_template(prompt_name: str, **vars) -> str:
    spec = load(prompt_name)
    prompt = spec.render(**vars)
    llm = get_llm(spec.model)

    try:
        response = llm.invoke(prompt)
        return response.content if hasattr(response, "content") else str(response)
    except Exception as e:
        log_warning(f"LLM call failed for {prompt_name}: {e}")
        return ""
