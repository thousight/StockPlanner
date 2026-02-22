from src.state import AgentState
from src.database.database import SessionLocal
from src.database.crud import cleanup_expired_cache

def cache_maintenance_agent(state: AgentState):
    """
    Clean up expired news cache entries. This agent is always called as the last agent in the graph before it ends, can be treated as an END agent.
    """
    try:
        db = SessionLocal()
        cleanup_expired_cache(db)
        db.close()
    except Exception as e:
        print(f"Error in cache maintenance: {e}")
        
    return state