from langchain_core.runnables import RunnableConfig
from src.state import AgentState
from src.agents.analyst.subgraph import create_debate_graph
from src.agents.utils import with_logging

@with_logging
def analyst_agent(state: AgentState, config: RunnableConfig):
    """
    Adversarial Analyst: Orchestrates a 'Bull vs. Bear' debate and synthesizes a final investment report.
    """
    user_input = state.get("user_input", "Analyze the current portfolio and provide recommendations.")
    
    # Retrieve research data from interactions
    research_interaction = next((i for i in reversed(state.get("agent_interactions", [])) if i.get("agent") == "research"), None)
    research_context = research_interaction.get("answer", "") if research_interaction else ""

    # Analysis is now always computed fresh
    debate_graph = create_debate_graph()
    debate_input = {
        "research_data": research_context,
        "user_input": user_input,
        "session_context": state.get("session_context", {}),
        "agent_interactions": state.get("agent_interactions", [])
    }
    
    debate_results = debate_graph.invoke(debate_input, config=config)
    
    # Get the newly generated interactions from subgraph
    initial_interactions_count = len(state.get("agent_interactions", []))
    new_interactions = debate_results.get("agent_interactions", [])[initial_interactions_count:]
    
    # Add the Analyst's own final output interaction
    analyst_interaction = {
        "id": initial_interactions_count + len(new_interactions) + 1,
        "agent": "analyst",
        "answer": debate_results.get("final_report", ""),
        "next_agent": "summarizer"
    }
    new_interactions.append(analyst_interaction)
    
    return {
        "agent_interactions": new_interactions
    }
