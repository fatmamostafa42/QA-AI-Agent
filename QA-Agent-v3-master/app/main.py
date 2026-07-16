"""
CLI entry point for AI QA Agent v3.

Usage:
    python -m app.main                          # full default flow
    python -m app.main --rebuild                # rebuild vector DB
    python -m app.main --story "Login via OAuth"  # story flow
    python -m app.main --help                   # help

NOTE: v3 graph runs the analyst stage in parallel, so the `agents`
positional argument is mostly informational — the flow runs end-to-end.
To skip an analyst, leave its prompt unchanged and just inspect the
output (or remove its edge from `graph.py`).
"""
import sys
import time
import argparse
from datetime import datetime, timezone

from app.converters.convert_to_md import process_resources
from app.rag.ingest import ingest_documents
from app.graph import graph, story_graph
from app.config.agents import AGENTS
from app.utils.logger import log_step, log_error, log_success, log_info


HELP_EPILOG = """
Examples:
  python -m app.main
  python -m app.main --rebuild
  python -m app.main --story "As a user I want OAuth login"

Available agents (v3 flow runs all of them in the parallel/sequential order
defined in app/graph.py):
""" + "\n".join(
    f"  - {' | '.join(a['aliases'])}  ({a['phase']})" for a in AGENTS
)


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="qa-agent",
        description="Multi-agent QA analysis from SRS/BRD/API documents.",
        epilog=HELP_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "agents", nargs="*",
        help="(Informational) Agents you want to focus on. v3 runs the full flow.",
    )
    parser.add_argument(
        "--rebuild", action="store_true",
        help="Force a fresh vector database build.",
    )
    parser.add_argument(
        "--story", type=str, default="",
        help="Run the story-analysis flow on a single Jira story text.",
    )
    return parser.parse_args(argv)


def _new_run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def main():
    args = _parse_args(sys.argv[1:])
    run_id = _new_run_id()
    started = time.time()
    started_iso = datetime.now(timezone.utc).isoformat()

    print("=" * 60)
    print(f"AI QA AGENT v3 — run {run_id}")
    print("=" * 60)

    log_step("STEP 1 — Converting resources")
    process_resources()

    log_step("STEP 2 — Preparing vector database")
    chunks_indexed = ingest_documents(force_rebuild=args.rebuild)

    log_step("STEP 3 — Running QA workflow")
    log_info(f"Selected agents (informational): {args.agents if args.agents else 'ALL'}")

    initial_state = {
        "selected_agents": args.agents,
        "run_id": run_id,
        "run_started_at": started_iso,
        "chunks_indexed": chunks_indexed,
    }

    if args.story:
        log_info(f"Story flow with story ({len(args.story)} chars)")
        initial_state["story"] = args.story
        result = story_graph.invoke(initial_state)
    else:
        result = graph.invoke(initial_state)

    log_step("QA WORKFLOW COMPLETED")
    epic_keys = result.get("epic_keys", [])
    jira_keys = result.get("jira_keys", [])
    output_dir = result.get("output_dir", "app/outputs/latest")

    log_success(f"Outputs: {output_dir}")
    log_success(f"Created Epics: {len(epic_keys)}")
    for key in epic_keys:
        print(f"  • {key}")
    log_success(f"Created Test issues: {len(jira_keys)}")

    elapsed = round(time.time() - started, 2)
    print(f"\nExecution time: {elapsed} sec")
    print("DONE")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExecution interrupted by user.")
    except Exception as e:
        log_error("MAIN", e)
        raise
