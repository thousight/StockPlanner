from src.graph.utils.prompt import convert_agents_to_prompt

def get_off_topic_next_agents_prompt():
    from src.graph.agents.summarizer.agent import summarizer_agent
    from src.graph.agents.research.agent import research_agent

    AVAILABLE_AGENTS = {
        "research": research_agent,
        "summarizer": summarizer_agent
    }

    return convert_agents_to_prompt(AVAILABLE_AGENTS)
