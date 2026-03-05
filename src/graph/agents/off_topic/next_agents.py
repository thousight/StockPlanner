from src.graph.utils.prompt import convert_agents_to_prompt

def get_off_topic_next_agents_prompt():
    from src.graph.agents.summarizer.agent import summarizer_agent
    from src.graph.agents.supervisor.agent import supervisor_agent
    from src.graph.agents.research.fundamental import fundamental_researcher
    from src.graph.agents.research.sentiment import sentiment_researcher
    from src.graph.agents.research.macro import macro_researcher

    AVAILABLE_AGENTS = {
        "supervisor": supervisor_agent,
        "fundamental_researcher": fundamental_researcher,
        "sentiment_researcher": sentiment_researcher,
        "macro_researcher": macro_researcher,
        "summarizer": summarizer_agent
    }

    return convert_agents_to_prompt(AVAILABLE_AGENTS)
