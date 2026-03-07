import logging
from langgraph.graph import StateGraph, END
from langgraph.types import Send
from src.graph.state import AgentState
from src.graph.agents.supervisor.agent import supervisor_agent
from src.graph.agents.research.fundamental import fundamental_researcher
from src.graph.agents.research.sentiment import sentiment_researcher
from src.graph.agents.research.macro import macro_researcher
from src.graph.agents.research.narrative import narrative_researcher
from src.graph.agents.research.generic import generic_researcher
from src.graph.agents.research.code_gen import code_generator_agent
from src.graph.agents.analyst.agent import analyst_agent
from src.graph.agents.off_topic.agent import off_topic_agent
from src.graph.agents.summarizer.agent import summarizer_agent
from typing import List, Union

logger = logging.getLogger(__name__)

class MeshRouter:
    """
    Router for the multi-agent mesh.
    Determines the next agent based on the last agent interaction.
    Supports parallel fan-out if next_agent contains a comma.
    """
    def __init__(self, allowed_destinations: List[str]):
        self.allowed_destinations = allowed_destinations

    def __call__(self, state: AgentState) -> Union[str, List[Send]]:
        interactions = state.get("agent_interactions", [])
        if not interactions:
            return "summarizer"
        
        last_interaction = interactions[-1]
        next_agent_raw = last_interaction.get("next_agent", "summarizer").lower()
        
        # Handle parallel fan-out
        if "," in next_agent_raw:
            agents = [a.strip() for a in next_agent_raw.split(",")]
            valid_agents = [a for a in agents if a in self.allowed_destinations]
            if valid_agents:
                # Return a list of Send objects for parallel execution
                return [Send(a, state) for a in valid_agents]
        
        # Single destination
        if next_agent_raw in self.allowed_destinations:
            # Special check for Analyst -> CodeGenerator loop
            if last_interaction.get("agent") == "analyst" and next_agent_raw == "code_generator":
                revision_count = state.get("code_revision_count", 0)
                if revision_count >= 2:
                    logger.warning("ANALYST LOOP: Max revisions (2) reached. Routing to summarizer.")
                    return "summarizer"
            
            return next_agent_raw
            
        logger.warning(f"Invalid next_agent '{next_agent_raw}'. Falling back.")
        return "summarizer"

def create_graph(checkpointer=None):
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("supervisor", supervisor_agent)
    workflow.add_node("fundamental_researcher", fundamental_researcher)
    workflow.add_node("sentiment_researcher", sentiment_researcher)
    workflow.add_node("macro_researcher", macro_researcher)
    workflow.add_node("narrative_researcher", narrative_researcher)
    workflow.add_node("generic_researcher", generic_researcher)
    workflow.add_node("code_generator", code_generator_agent)
    workflow.add_node("analyst", analyst_agent)
    workflow.add_node("off_topic", off_topic_agent)
    workflow.add_node("summarizer", summarizer_agent)
    
    # Set entry point
    workflow.set_entry_point("supervisor")

    # Routing from Supervisor (Supports Parallel Research)
    workflow.add_conditional_edges(
        "supervisor",
        MeshRouter([
            "fundamental_researcher", 
            "sentiment_researcher", 
            "macro_researcher", 
            "narrative_researcher",
            "generic_researcher",
            "code_generator",
            "analyst", 
            "off_topic", 
            "summarizer"
        ])
    )
    
    # Research nodes all flow into Analyst (Fan-in Join)
    workflow.add_edge("fundamental_researcher", "analyst")
    workflow.add_edge("sentiment_researcher", "analyst")
    workflow.add_edge("macro_researcher", "analyst")
    workflow.add_edge("narrative_researcher", "analyst")
    workflow.add_edge("generic_researcher", "analyst")
    workflow.add_edge("code_generator", "analyst")
    
    # Analyst routes to Supervisor (for follow-ups) or Summarizer
    workflow.add_conditional_edges(
        "analyst",
        MeshRouter(["supervisor", "fundamental_researcher", "sentiment_researcher", "macro_researcher", "narrative_researcher", "generic_researcher", "code_generator", "summarizer"])
    )
    
    workflow.add_conditional_edges(
        "off_topic",
        MeshRouter(["fundamental_researcher", "sentiment_researcher", "macro_researcher", "narrative_researcher", "generic_researcher", "code_generator", "supervisor", "summarizer"])
    )

    workflow.add_edge("summarizer", END)
    
    return workflow.compile(checkpointer=checkpointer)
