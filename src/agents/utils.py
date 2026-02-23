from typing import Dict, Any

def get_next_interaction_id(state: Dict[str, Any]) -> int:
    """Returns the next sequential interaction ID."""
    return len(state.get("agent_interactions", [])) + 1

def get_current_question(state: Dict[str, Any], default_label: str = "Decompose request") -> str:
    """
    Returns the task instruction for the current agent.
    Priority:
    1. next_question from the previous agent's interaction.
    2. user_input from the state.
    3. default_label.
    """
    interactions = state.get("agent_interactions", [])
    if interactions:
        return interactions[-1].get("next_question", default_label)
    return state.get("user_input", default_label)

def format_interactions_as_text(state: Dict[str, Any]) -> str:
    """Standardizes the text representation of agent interactions for prompts."""
    interactions_text = ""
    for idx, interaction in enumerate(state.get("agent_interactions", [])):
        agent = interaction.get('agent', 'unknown')
        interactions_text += f"--- Interaction {idx + 1} ({agent} agent) ---\n"
        interactions_text += f"Current Task (from previous agent): {interaction.get('question', '')}\n"
        interactions_text += f"Answer/Output from {agent}: {interaction.get('answer', '')}\n"
        interactions_text += f"Instruction for Next Agent: {interaction.get('next_question', 'N/A')}\n\n"
    return interactions_text
