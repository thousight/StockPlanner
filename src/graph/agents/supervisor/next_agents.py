from src.graph.utils.prompt import convert_agents_to_prompt

def get_supervisor_next_agents_prompt():
    from src.graph.agents.research.agent import research_agent
    from src.graph.agents.analyst.agent import analyst_agent
    from src.graph.agents.off_topic.agent import off_topic_agent
    
    AVAILABLE_AGENTS = {
        "research": research_agent,
        "analyst": analyst_agent,
        "off_topic": off_topic_agent
    }
    return convert_agents_to_prompt(AVAILABLE_AGENTS)
