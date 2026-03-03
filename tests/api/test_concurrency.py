import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from main import app
from unittest.mock import patch, AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_thread_concurrency_409():
    """
    Verify that concurrent requests for the same thread_id return 409 Conflict.
    """
    thread_id = "stress-test-thread"
    user_id = "test-user"
    
    # Mock database session to avoid real DB calls
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = MagicMock() # Thread exists
    mock_db.execute.return_value = mock_result

    # Mock the underlying event generator's graph call to add delay
    with patch("src.controllers.chat.get_checkpointer") as mock_cp_ctx:
        # get_checkpointer is an async context manager
        mock_cp = AsyncMock()
        mock_cp_ctx.return_value.__aenter__.return_value = mock_cp
        
        with patch("src.controllers.chat.create_graph") as mock_create:
            mock_graph = MagicMock()
            
            async def slow_stream(*args, **kwargs):
                await asyncio.sleep(0.5)
                yield {"event": "on_chain_end", "metadata": {"langgraph_node": "end"}, "data": {"output": {}}}
                
            mock_graph.astream_events.side_effect = slow_stream
            mock_create.return_value = mock_graph
            
            # Override get_db dependency
            app.dependency_overrides[app.dependency_overrides.get("get_db", None)] = lambda: mock_db
            # Actually, the standard way:
            from src.database.session import get_db
            app.dependency_overrides[get_db] = lambda: mock_db

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                headers = {
                    "X-Thread-ID": thread_id,
                    "X-User-ID": user_id
                }
                # Send two requests concurrently
                tasks = [
                    ac.post("/chat", json={"message": "hello"}, headers=headers),
                    ac.post("/chat", json={"message": "hello"}, headers=headers)
                ]
                
                responses = await asyncio.gather(*tasks)
                
                status_codes = [r.status_code for r in responses]
                assert 409 in status_codes
                # One should be 200 (StreamingResponse)
                assert 200 in status_codes
                
            app.dependency_overrides.clear()
