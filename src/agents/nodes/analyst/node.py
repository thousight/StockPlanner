from src.agents.state import AgentState
from .subgraph import create_debate_graph
from src.database.database import SessionLocal
from src.database.crud import get_analysis_cache, save_analysis_cache

def analyst_node(state: AgentState):
    """
    Adversarial Analyst: Orchestrates a 'Bull vs. Bear' debate and synthesizes a final investment report.
    """
    db = SessionLocal()
    user_question = state.get("user_question", "Analyze the current portfolio and provide recommendations.")
    
    try:
        # Check cache
        cached = get_analysis_cache(db, user_question)
        if cached:
            print(f"--- ANALYST: Cache hit for {user_question} ---")
            return {
                    "analysis_report": cached.report,
                    "debate_output": cached.debate_output
                }
        
        # Cache miss
        debate_graph = create_debate_graph()
        debate_input = {
            "research_data": state.get("research_data", {}),
            "user_question": user_question
        }
        
        print(f"--- ANALYST: Cache miss. Starting debate for {user_question} ---")
        debate_results = debate_graph.invoke(debate_input)
        
        debate_output = {
            "bull_argument": debate_results["bull_argument"],
            "bear_argument": debate_results["bear_argument"],
            "confidence_score": debate_results["confidence_score"]
        }
        
        # Save to cache
        save_analysis_cache(
                db, 
                user_question, 
                debate_results["final_report"], 
                debate_output
            )
            
        return {
            "analysis_report": debate_results["final_report"],
            "debate_output": debate_output,
            "next_node": "cache_maintenance"
        }
    finally:
        db.close()
