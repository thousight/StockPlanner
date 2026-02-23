from langchain_core.runnables import RunnableConfig
from src.state import AgentState
from src.agents.analyst.subgraph import create_debate_graph
from src.agents.utils import get_next_interaction_id, get_current_question

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
        "user_input": user_input
    }
    
    print(f"--- ANALYST: Starting adversarial debate for {user_input} ---")
    debate_results = debate_graph.invoke(debate_input, config=config)
    
    debate_output = {
        "bull_argument": debate_results["bull_argument"],
        "bear_argument": debate_results["bear_argument"],
        "confidence_score": debate_results["confidence_score"]
    }
    
    # Infer step_id from the supervisor's instruction if possible
    interactions = state.get("agent_interactions", [])
    step_id = interactions[-1].get("step_id", 0) if interactions else 0

    return {
        "agent_interactions": [{
            "id": get_next_interaction_id(state),
            "step_id": step_id,
            "agent": "analyst",
            "question": get_current_question(state, f"Analyze and debate: {user_input}"),
            "answer": debate_results["final_report"],
            "next_agent": "summarizer",
            "next_question": "Summarize the final debate results into a comprehensive investment report.",
            "debate_output": debate_output # Store the structured debate results here
        }]
    }
