from langgraph.checkpoint.redis.aio import AsyncRedisSaver
from src.config import settings

def get_checkpointer() -> AsyncRedisSaver:
    """
    Creates and returns an AsyncRedisSaver instance connected to Redis.
    Configures a 30-minute sliding TTL for checkpoints.
    
    Note: This checkpointer must be used within an 'async with' block to 
    initialize its connection pool.
    """
    # 30-minute sliding window (Note: AsyncRedisSaver uses minutes for default_ttl)
    # refresh_on_read=True ensures TTL is reset every time the state is accessed
    ttl_config = {
        "default_ttl": settings.REDIS_CHECKPOINT_TTL_MIN,
        "refresh_on_read": True
    }
    
    return AsyncRedisSaver.from_conn_string(
        settings.REDIS_URL,
        ttl=ttl_config
    )
