from src.utils.prompt import convert_agents_to_prompt
from langgraph.graph import END

def get_supervisor_next_agents_prompt():
    from src.agents.summarizer.agent import summarizer_agent
    from src.agents.research.agent import research_agent
    from src.agents.analyst.agent import analyst_agent
    from src.agents.off_topic.agent import off_topic_agent
    
    AVAILABLE_AGENTS = {
        "research": research_agent,
        "analyst": analyst_agent,
        "off_topic": off_topic_agent,
        "summarizer": summarizer_agent
    }
    return convert_agents_to_prompt(AVAILABLE_AGENTS)
