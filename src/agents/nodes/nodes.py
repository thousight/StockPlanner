from src.agents.state import AgentState
from src.database.database import SessionLocal
from src.database.crud import cleanup_expired_cache

def cache_maintenance_node(state: AgentState):
    """
    Clean up expired news cache entries.
    """
    try:
        db = SessionLocal()
        cleanup_expired_cache(db)
        db.close()
    except Exception as e:
        print(f"Error in cache maintenance: {e}")
        
    return state