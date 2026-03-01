from src.graph.utils.prompt import convert_agents_to_prompt

def get_research_next_agents_prompt():
    from src.graph.agents.summarizer.agent import summarizer_agent
    from src.graph.agents.analyst.agent import analyst_agent

    AVAILABLE_AGENTS = {
        "analyst": analyst_agent,
        "summarizer": summarizer_agent
    }

    return convert_agents_to_prompt(AVAILABLE_AGENTS)
