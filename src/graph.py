from langgraph.graph import StateGraph, END
from src.state import AgentState
from src.agents.supervisor.agent import supervisor_agent
from src.agents.research.agent import research_agent
from src.agents.analyst.agent import analyst_agent
from src.agents.cache_maintenance.agent import cache_maintenance_agent

def mesh_router(state: AgentState):
    dest = state.get("next_agent", "cache_maintenance").lower()
    if dest in ["end", "cache_maintenance"]:
        return "cache_maintenance"
    return dest

def create_graph():
    workflow = StateGraph(AgentState)
    
    # Add nodes (we keep the string names the same, but use the new function names)
    workflow.add_node("supervisor", supervisor_agent)
    workflow.add_node("research", research_agent)
    workflow.add_node("analyst", analyst_agent)
    workflow.add_node("cache_maintenance", cache_maintenance_agent)
    
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
    
    workflow.add_conditional_edges(
        "research",
        mesh_router,
        {
            "analyst": "analyst",
            "supervisor": "supervisor",
            "cache_maintenance": "cache_maintenance"
        }
    )
    
    workflow.add_conditional_edges(
        "analyst",
        mesh_router,
        {
            "research": "research",
            "supervisor": "supervisor",
            "cache_maintenance": "cache_maintenance"
        }
    )
    
    # Final cleanup node leads to the actual END
    workflow.add_edge("cache_maintenance", END)
    
    return workflow.compile()