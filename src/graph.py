from langgraph.graph import StateGraph, END
from src.state import AgentState
from src.agents.supervisor.agent import supervisor_agent
from src.agents.research.agent import research_agent
from src.agents.analyst.agent import analyst_agent
from src.agents.off_topic.agent import off_topic_agent
from src.agents.summarizer.agent import summarizer_agent

def mesh_router(state: AgentState):
    interactions = state.get("agent_interactions", [])
    if not interactions:
        return "summarizer"
    
    last_interaction = interactions[-1]
    return last_interaction.get("next_agent", "summarizer").lower()

def create_graph():
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("supervisor", supervisor_agent)
    workflow.add_node("research", research_agent)
    workflow.add_node("analyst", analyst_agent)
    workflow.add_node("off_topic", off_topic_agent)
    workflow.add_node("summarizer", summarizer_agent)
    
    # Set entry point
    workflow.set_entry_point("supervisor")

    workflow.add_conditional_edges(
        "supervisor",
        mesh_router,
        {
            "research": "research",
            "analyst": "analyst",
            "off_topic": "off_topic",
            "summarizer": "summarizer"
        }
    )
    
    workflow.add_conditional_edges(
        "research",
        mesh_router,
        {
            "analyst": "analyst",
            "supervisor": "supervisor",
            "summarizer": "summarizer"
        }
    )
    
    workflow.add_conditional_edges(
        "analyst",
        mesh_router,
        {
            "supervisor": "supervisor",
            "summarizer": "summarizer"
        }
    )
    
    workflow.add_conditional_edges(
        "off_topic",
        mesh_router,
        {
            "research": "research",
            "supervisor": "supervisor",
            "summarizer": "summarizer"
        }
    )

    workflow.add_edge("summarizer", END)
    
    return workflow.compile()