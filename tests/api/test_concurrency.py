import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from main import app
from src.database.session import get_db
from unittest.mock import patch, AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_thread_concurrency_409(client, mock_session, test_user, auth_headers):
    """
    Verify that concurrent requests for the same thread_id return 409 Conflict.
    """
    thread_id = "stress-test-thread"
    
    # Mock user for auth
    mock_user_result = MagicMock()
    mock_user_result.scalar_one_or_none.return_value = test_user
    
    # Mock database session to avoid real DB calls
    mock_thread_result = MagicMock()
    mock_thread_result.scalar_one_or_none.return_value = MagicMock(id=thread_id, user_id=test_user.id)
    
    mock_session.execute.side_effect = [mock_user_result, mock_thread_result, mock_user_result, mock_thread_result]

    # Mock the underlying event generator's graph call to add delay
    with patch("src.controllers.chat.get_checkpointer") as mock_cp_ctx:
        mock_cp = AsyncMock()
        mock_cp_ctx.return_value.__aenter__.return_value = mock_cp
        
        with patch("src.controllers.chat.create_graph") as mock_create:
            mock_graph = MagicMock()
            
            async def slow_stream(*args, **kwargs):
                await asyncio.sleep(0.5)
                yield {"event": "on_chain_end", "metadata": {"langgraph_node": "end"}, "data": {"output": {}}}
                
            mock_graph.astream_events.side_effect = slow_stream
            mock_create.return_value = mock_graph
            
            app.dependency_overrides[get_db] = lambda: mock_session

            # Send two requests concurrently
            tasks = [
                client.post("/chat", json={"message": "hello"}, headers={**auth_headers, "X-Thread-ID": thread_id}),
                client.post("/chat", json={"message": "hello"}, headers={**auth_headers, "X-Thread-ID": thread_id})
            ]
            
            responses = await asyncio.gather(*tasks)
            
            status_codes = [r.status_code for r in responses]
            assert 409 in status_codes
            # One should be 200 (StreamingResponse)
            assert 200 in status_codes
                
            app.dependency_overrides.clear()
