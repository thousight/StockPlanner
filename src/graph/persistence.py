from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from src.config import settings

def get_checkpointer_conn_string() -> str:
    """Returns a psycopg-compatible connection string."""
    return settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")

def get_checkpointer() -> AsyncPostgresSaver:
    """
    Creates and returns an AsyncPostgresSaver instance.
    Note: This checkpointer must be used within an 'async with' block to 
    initialize its connection pool.
    """
    conn_string = get_checkpointer_conn_string()
    
    # Configure with JsonPlusSerializer for handling complex nested state
    # pickle_fallback=True ensures we can handle things that are not JSON-serializable
    serializer = JsonPlusSerializer(pickle_fallback=True)
    
    return AsyncPostgresSaver.from_conn_string(
        conn_string,
        serde=serializer
    )
