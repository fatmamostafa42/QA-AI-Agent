from app.utils.logger import log_agent_skip


def should_run(state, agent_name):

    selected = state.get("selected_agents", [])

    # ---------------------------------
    # Run all agents if nothing selected
    # ---------------------------------

    if not selected:
        return True

    # ---------------------------------
    # Normalize values
    # ---------------------------------

    normalized_selected = [
        agent.lower().strip()
        for agent in selected
    ]

    normalized_agent = agent_name.lower().strip()

    # ---------------------------------
    # Check selection
    # ---------------------------------

    if normalized_agent in normalized_selected:
        return True

    log_agent_skip(agent_name)

    return False