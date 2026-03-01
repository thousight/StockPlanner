from langgraph.graph import StateGraph, END
from src.graph.state import AgentState
from src.graph.nodes import commit_node
from src.graph.agents.supervisor.agent import supervisor_agent
from src.graph.agents.research.agent import research_agent
from src.graph.agents.analyst.agent import analyst_agent
from src.graph.agents.off_topic.agent import off_topic_agent
from src.graph.agents.summarizer.agent import summarizer_agent

def create_mesh_router(allowed_destinations: list):
    def router(state: AgentState):
        interactions = state.get("agent_interactions", [])
        if not interactions:
            return "summarizer"
        
        last_interaction = interactions[-1]
        next_agent = last_interaction.get("next_agent", "summarizer").lower()
        if next_agent not in allowed_destinations:
            print(f"WARNING: Invalid next_agent '{next_agent}'. Falling back.")
            return "summarizer" if "summarizer" in allowed_destinations else allowed_destinations[0]
        return next_agent
    return router

def create_graph():
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("supervisor", supervisor_agent)
    workflow.add_node("research", research_agent)
    workflow.add_node("analyst", analyst_agent)
    workflow.add_node("off_topic", off_topic_agent)
    workflow.add_node("summarizer", summarizer_agent)
    workflow.add_node("commit", commit_node)
    
    # Set entry point
    workflow.set_entry_point("supervisor")

    workflow.add_conditional_edges(
        "supervisor",
        create_mesh_router(["research", "analyst", "off_topic", "summarizer"]),
        {
            "research": "research",
            "analyst": "analyst",
            "off_topic": "off_topic",
            "summarizer": "summarizer"
        }
    )
    
    workflow.add_conditional_edges(
        "research",
        create_mesh_router(["analyst", "supervisor", "summarizer"]),
        {
            "analyst": "analyst",
            "summarizer": "summarizer"
        }
    )
    
    workflow.add_conditional_edges(
        "analyst",
        create_mesh_router(["supervisor", "summarizer"]),
        {
            "summarizer": "summarizer"
        }
    )
    
    workflow.add_conditional_edges(
        "off_topic",
        create_mesh_router(["research", "supervisor", "summarizer"]),
        {
            "research": "research",
            "summarizer": "summarizer"
        }
    )

    workflow.add_edge("summarizer", "commit")
    workflow.add_edge("commit", END)
    
    return workflow.compile()