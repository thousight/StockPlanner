from langgraph.graph import StateGraph, END
from src.graph.state import AgentState
from src.graph.agents.supervisor.agent import supervisor_agent
from src.graph.agents.research.agent import research_agent
from src.graph.agents.analyst.agent import analyst_agent
from src.graph.agents.off_topic.agent import off_topic_agent
from src.graph.agents.summarizer.agent import summarizer_agent
from typing import List

class MeshRouter:
    """
    Router for the multi-agent mesh.
    Determines the next agent based on the last agent interaction.
    """
    def __init__(self, allowed_destinations: List[str]):
        self.allowed_destinations = allowed_destinations

    def __call__(self, state: AgentState) -> str:
        interactions = state.get("agent_interactions", [])
        if not interactions:
            return "summarizer"
        
        last_interaction = interactions[-1]
        next_agent = last_interaction.get("next_agent", "summarizer").lower()
        if next_agent not in self.allowed_destinations:
            print(f"WARNING: Invalid next_agent '{next_agent}'. Falling back.")
            return "summarizer" if "summarizer" in self.allowed_destinations else self.allowed_destinations[0]
        return next_agent

def create_graph(checkpointer=None):
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
        MeshRouter(["research", "analyst", "off_topic", "summarizer"]),
        {
            "research": "research",
            "analyst": "analyst",
            "off_topic": "off_topic",
            "summarizer": "summarizer"
        }
    )
    
    workflow.add_conditional_edges(
        "research",
        MeshRouter(["analyst", "supervisor", "summarizer"]),
        {
            "analyst": "analyst",
            "summarizer": "summarizer"
        }
    )
    
    workflow.add_conditional_edges(
        "analyst",
        MeshRouter(["supervisor", "summarizer"]),
        {
            "summarizer": "summarizer"
        }
    )
    
    workflow.add_conditional_edges(
        "off_topic",
        MeshRouter(["research", "supervisor", "summarizer"]),
        {
            "research": "research",
            "summarizer": "summarizer"
        }
    )

    workflow.add_edge("summarizer", END)
    
    return workflow.compile(checkpointer=checkpointer)
