from src.utils.prompt import convert_agents_to_prompt

def get_analyst_next_agents_prompt():
    from src.agents.summarizer.agent import summarizer_agent
    from src.agents.supervisor.agent import supervisor_agent

    AVAILABLE_AGENTS = {
        "supervisor": supervisor_agent,
        "summarizer": summarizer_agent
    }

    return convert_agents_to_prompt(AVAILABLE_AGENTS)
