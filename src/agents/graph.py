from langgraph.graph import StateGraph, END
from src.agents.state import AgentState
from src.agents.nodes.supervisor.node import supervisor_node
from src.agents.nodes.research.node import research_node
from src.agents.nodes.analyst.node import analyst_node
from src.agents.nodes.nodes import cache_maintenance_node

def mesh_router(state: AgentState):
    dest = state.get("next_node", "cache_maintenance").lower()
    if dest in ["end", "cache_maintenance"]:
        return "cache_maintenance"
    return dest

def create_graph():
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("research", research_node)
    workflow.add_node("analyst", analyst_node)
    workflow.add_node("cache_maintenance", cache_maintenance_node)
    
    # Set entry point
    workflow.set_entry_point("supervisor")

    # Supervisor decides the initial or next logical path
    workflow.add_conditional_edges(
        "supervisor",
        mesh_router,
        {
            "research": "research",
            "analyst": "analyst",
            "cache_maintenance": "cache_maintenance"
        }
    )
    
    # Research can go back to Supervisor, hand off to Analyst, or finish
    workflow.add_conditional_edges(
        "research",
        mesh_router,
        {
            "analyst": "analyst",
        }
    )
    
    # Analyst can loop back for more research or finish
    workflow.add_conditional_edges(
        "analyst",
        mesh_router,
        {
            "research": "research",
        }
    )
    
    # Final cleanup node leads to the actual END
    workflow.add_edge("cache_maintenance", END)
    
    return workflow.compile()