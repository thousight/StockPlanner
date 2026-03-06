from src.graph.utils.prompt import convert_agents_to_prompt

def get_supervisor_next_agents_prompt():
    from src.graph.agents.research.fundamental import fundamental_researcher
    from src.graph.agents.research.sentiment import sentiment_researcher
    from src.graph.agents.research.macro import macro_researcher
    from src.graph.agents.research.narrative import narrative_researcher
    from src.graph.agents.research.generic import generic_researcher
    from src.graph.agents.analyst.agent import analyst_agent
    from src.graph.agents.off_topic.agent import off_topic_agent
    
    AVAILABLE_AGENTS = {
        "fundamental_researcher": fundamental_researcher,
        "sentiment_researcher": sentiment_researcher,
        "macro_researcher": macro_researcher,
        "narrative_researcher": narrative_researcher,
        "generic_researcher": generic_researcher,
        "analyst": analyst_agent,
        "off_topic": off_topic_agent
    }
    return convert_agents_to_prompt(AVAILABLE_AGENTS)
