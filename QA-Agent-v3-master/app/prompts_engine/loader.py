"""
Prompt template engine.

Each prompt lives in `prompts/<name>.yaml` with this shape:

  name: requirement_analyst
  version: 1
  model: smart           # 'fast' or 'smart'
  output_schema: TextBlob  # one of the names in app.schemas, or 'TextBlob'
  template: |
    You are a senior QA requirement analyst.
    Retrieved context:
    {context}

The engine:
  - Loads YAML files lazily (cached after first load)
  - Provides a render(name, **vars) helper
  - Reports the prompt's metadata so node code can pick the right LLM tier
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from string import Template

import yaml


PROMPTS_DIR = Path("prompts")


@dataclass(frozen=True)
class PromptSpec:
    name: str
    version: int
    model: str
    output_schema: str
    template: str

    def render(self, **kwargs) -> str:
        """Render using Python's str.format() semantics, but tolerant of
        missing variables (renders as empty string)."""
        # Defensive: avoid str.format eating curly braces inside the prompt
        # body. We use string.Template instead with $-style substitution
        # mapped from {var}.
        body = self.template
        # Convert {var} placeholders → $var, but only for top-level ones.
        # Anything else stays literal.
        for key in kwargs:
            body = body.replace("{" + key + "}", "${" + key + "}")
        # Anything still wrapped in {…} stays as-is (LLMs are fine with it).
        return Template(body).safe_substitute(
            {k: (v if v is not None else "") for k, v in kwargs.items()}
        )


@lru_cache(maxsize=64)
def load(name: str) -> PromptSpec:
    path = PROMPTS_DIR / f"{name}.yaml"
    if not path.exists():
        raise FileNotFoundError(
            f"Prompt template not found: {path}. "
            f"Available: {sorted(p.stem for p in PROMPTS_DIR.glob('*.yaml'))}"
        )

    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return PromptSpec(
        name=data.get("name", name),
        version=int(data.get("version", 1)),
        model=str(data.get("model", "fast")).lower(),
        output_schema=str(data.get("output_schema", "TextBlob")),
        template=str(data.get("template", "")).strip(),
    )


def list_prompts() -> list[str]:
    return sorted(p.stem for p in PROMPTS_DIR.glob("*.yaml"))
