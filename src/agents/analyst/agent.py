from langchain_core.runnables import RunnableConfig
from src.state import AgentState
from src.agents.analyst.subgraph import create_debate_graph

def analyst_agent(state: AgentState, config: RunnableConfig):
    """
    Adversarial Analyst: Orchestrates a 'Bull vs. Bear' debate and synthesizes a final investment report.
    """
    user_question = state.get("user_question", "Analyze the current portfolio and provide recommendations.")
    
    # Analysis is now always computed fresh (analysis cache removed)
    debate_graph = create_debate_graph()
    debate_input = {
        "research_data": state.get("research_data", {}),
        "user_question": user_question
    }
    
    print(f"--- ANALYST: Starting adversarial debate for {user_question} ---")
    debate_results = debate_graph.invoke(debate_input, config=config)
    
    debate_output = {
        "bull_argument": debate_results["bull_argument"],
        "bear_argument": debate_results["bear_argument"],
        "confidence_score": debate_results["confidence_score"]
    }
    
    return {
        "analysis_report": debate_results["final_report"],
        "debate_output": debate_output,
        "next_agent": "cache_maintenance"
    }
