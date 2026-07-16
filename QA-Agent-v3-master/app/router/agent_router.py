"""
Router for the LangGraph conditional edges.

Resolves the user's selected_agents through the alias registry so both
short ("security") and long ("security_analyst") names work.
"""
from app.config.agents import resolve_alias
from app.utils.logger import log_agent_skip


def _normalized_selection(state) -> set[str]:
    selected = state.get("selected_agents") or []
    keys: set[str] = set()
    for name in selected:
        resolved = resolve_alias(name)
        if resolved:
            keys.add(resolved)
    return keys


def should_run_agent(state, node_key: str, next_node: str, skip_node: str) -> str:
    """
    If selected_agents is empty, run everything.
    Otherwise route only to nodes whose canonical key is in the user's selection.
    """
    selection = _normalized_selection(state)

    if not selection:
        return next_node

    if node_key in selection:
        return next_node

    log_agent_skip(node_key)
    return skip_node
