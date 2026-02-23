from src.utils.prompt import convert_agents_to_prompt
from langgraph.graph import END

def get_off_topic_next_agents_prompt():
    from src.agents.summarizer.agent import summarizer_agent
    from src.agents.supervisor.agent import supervisor_agent
    from src.agents.research.agent import research_agent

    AVAILABLE_AGENTS = {
        "supervisor": supervisor_agent,
        "research": research_agent,
        "summarizer": summarizer_agent
    }

    return convert_agents_to_prompt(AVAILABLE_AGENTS)
