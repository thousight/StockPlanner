from langgraph.graph import StateGraph, END
from src.agents.state import AgentState
from src.agents.nodes import research_node, analyst_node

def create_graph():
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("research", research_node)
    workflow.add_node("analyst", analyst_node)
    
    # Define edges
    # Start -> Research -> Analyst -> END
    workflow.set_entry_point("research")
    workflow.add_edge("research", "analyst")
    workflow.add_edge("analyst", END)
    
    return workflow.compile()
