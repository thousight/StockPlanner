import pytest
from src.graph.persistence import get_checkpointer
from src.config import settings
import redis.asyncio as redis

@pytest.mark.asyncio
async def test_redis_checkpointer_persistence():
    """
    Verify that checkpoints are correctly saved to and retrieved from Redis.
    """
    async with get_checkpointer() as checkpointer:
        # Initialize
        await checkpointer.setup()
        
        thread_id = "test-thread-123"
        checkpoint_id = "cp-1"
        config = {"configurable": {"thread_id": thread_id, "checkpoint_id": checkpoint_id, "checkpoint_ns": ""}}
        
        checkpoint = {
            "v": 1,
            "ts": "2023-01-01T00:00:00Z",
            "id": checkpoint_id,
            "channel_values": {"my_key": "my_value"},
            "channel_versions": {"my_key": 1},
            "versions_seen": {},
            "pending_sends": []
        }
        
        # Save
        await checkpointer.aput(config, checkpoint, {}, {})
        
        # Retrieve
        retrieved = await checkpointer.aget(config)
        
        assert retrieved is not None
        # AsyncRedisSaver returns the checkpoint dict directly in aget()
        assert retrieved["channel_values"]["my_key"] == "my_value"

@pytest.mark.asyncio
async def test_redis_checkpointer_ttl():
    """
    Verify that keys in Redis have a TTL set.
    """
    async with get_checkpointer() as checkpointer:
        await checkpointer.setup()
        
        thread_id = "test-ttl-thread"
        config = {"configurable": {"thread_id": thread_id, "checkpoint_ns": ""}}
        
        checkpoint = {
            "v": 1,
            "ts": "2023-01-01T00:00:00Z",
            "id": "cp-ttl",
            "channel_values": {"foo": "bar"},
            "channel_versions": {"foo": 1},
            "versions_seen": {},
            "pending_sends": []
        }
        
        await checkpointer.aput(config, checkpoint, {}, {})
        
        # Check TTL directly in Redis
        r = redis.from_url(settings.REDIS_URL)
        
        # Let's find the keys
        keys = await r.keys("*test-ttl-thread*")
        assert len(keys) > 0
        
        for key in keys:
            ttl = await r.ttl(key)
            # TTL should be around 1800 seconds (30 mins)
            assert 0 < ttl <= 1800
            
        await r.aclose()
