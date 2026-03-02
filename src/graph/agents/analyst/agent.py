from langchain_core.runnables import RunnableConfig
from langgraph.types import interrupt
from src.graph.state import AgentState
from src.graph.agents.analyst.subgraph import create_debate_graph
from src.graph.utils.agents import with_logging

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
    report = debate_results.get("final_report", "")
    
    # Safety Check: Detect high-risk recommendations
    risk_keywords = ["BUY", "SELL", "RECOMENDATION", "TRADE", "PORTFOLIO CHANGE"]
    is_high_risk = any(kw in report.upper() for kw in risk_keywords)
    
    initial_interactions_count = len(state.get("agent_interactions", []))

    if is_high_risk:
        # Surface interrupt to the user
        interrupt_msg = f"SAFETY CHECK: The analyst has proposed specific trade recommendations. Please review and type 'approve' to continue, or provide feedback/cancellation."
        
        # LangGraph 0.2 interrupt: pauses here and returns the user input upon resumption
        # If the node is re-run, this will return the previously provided response instead of pausing again.
        user_response = interrupt({
            "type": "safety_check",
            "message": interrupt_msg,
            "report_preview": report[:300] + "..."
        })
        
        # Handle rejection or correction upon resumption
        if isinstance(user_response, str) and any(kw in user_response.lower() for kw in ["cancel", "reject", "no", "stop"]):
            return {
                "agent_interactions": [{
                    "id": initial_interactions_count + 1,
                    "agent": "analyst",
                    "answer": f"The analyst's recommendations were cancelled by the user: {user_response}",
                    "next_agent": "summarizer"
                }]
            }
        
        # If corrected, we might want to add that to the state or just proceed
        if isinstance(user_response, str) and user_response.lower() != "approve":
            report = f"{report}\n\n[USER CORRECTION]: {user_response}"

    # Get the newly generated interactions from subgraph
    new_interactions = debate_results.get("agent_interactions", [])[initial_interactions_count:]
    
    # Add the Analyst's own final output interaction
    analyst_interaction = {
        "id": initial_interactions_count + len(new_interactions) + 1,
        "agent": "analyst",
        "answer": report,
        "next_agent": "summarizer",
        "debate_output": {
            "bull_argument": debate_results.get("bull_argument", ""),
            "bear_argument": debate_results.get("bear_argument", ""),
            "confidence_score": debate_results.get("confidence_score", 0)
        }
    }
    new_interactions.append(analyst_interaction)
    
    return {
        "agent_interactions": new_interactions
    }
