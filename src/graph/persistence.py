from langgraph.checkpoint.redis.aio import AsyncRedisSaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from src.config import settings

def get_checkpointer() -> AsyncRedisSaver:
    """
    Creates and returns an AsyncRedisSaver instance connected to Redis.
    Configures a 30-minute sliding TTL for checkpoints.
    
    Note: This checkpointer must be used within an 'async with' block to 
    initialize its connection pool.
    """
    # Configure with JsonPlusSerializer for handling complex nested state
    # pickle_fallback=True ensures we can handle things that are not JSON-serializable
    serializer = JsonPlusSerializer(pickle_fallback=True)
    
    # 30-minute sliding window (1800 seconds)
    # refresh_on_read=True ensures TTL is reset every time the state is accessed
    ttl_config = {
        "default_ttl": settings.REDIS_CHECKPOINT_TTL_MIN * 60,
        "refresh_on_read": True
    }
    
    return AsyncRedisSaver.from_conn_string(
        settings.REDIS_URL,
        serde=serializer,
        ttl=ttl_config
    )
