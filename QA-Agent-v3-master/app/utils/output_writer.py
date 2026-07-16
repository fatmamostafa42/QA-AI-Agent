"""
Output writer.

Persists every agent's result to `app/outputs/<run_id>/` AND copies it
to `app/outputs/latest/` so external tooling always knows where to look.
"""
import json
import shutil
from pathlib import Path
from typing import Any


OUTPUTS_ROOT = Path("app/outputs")
LATEST_DIR = OUTPUTS_ROOT / "latest"


def ensure_run_dir(run_id: str) -> Path:
    run_dir = OUTPUTS_ROOT / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def write_markdown(run_dir: Path, name: str, content: str) -> Path:
    path = run_dir / f"{name}.md"
    path.write_text(content or "", encoding="utf-8")
    return path


def write_json(run_dir: Path, name: str, payload: Any) -> Path:
    path = run_dir / f"{name}.json"
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    return path


def mirror_to_latest(run_dir: Path) -> None:
    if LATEST_DIR.exists():
        shutil.rmtree(LATEST_DIR)
    shutil.copytree(run_dir, LATEST_DIR)
