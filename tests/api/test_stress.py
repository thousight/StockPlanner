import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from main import app
from unittest.mock import patch, AsyncMock, MagicMock
from src.database.session import get_db

@pytest.mark.asyncio
async def test_input_stress_long_message(client, mock_session, test_user, auth_headers):
    """
    Test handling of extremely long messages.
    """
    long_msg = "A" * 15000
    
    # Mock user for auth
    mock_user_result = MagicMock()
    mock_user_result.scalar_one_or_none.return_value = test_user
    
    # Mock thread lookup
    mock_thread_result = MagicMock()
    mock_thread_result.scalar_one_or_none.return_value = MagicMock(id="long-msg", user_id=test_user.id)
    
    mock_session.execute.side_effect = [mock_user_result, mock_thread_result]

    with patch("src.controllers.chat.get_checkpointer") as mock_cp_ctx:
        mock_cp_ctx.return_value.__aenter__.return_value = AsyncMock()
        with patch("src.controllers.chat.create_graph") as mock_create:
            mock_graph = MagicMock()
            
            async def fast_stream(*args, **kwargs):
                yield {"event": "on_chain_end", "metadata": {"langgraph_node": "end"}, "data": {"output": {}}}
                
            mock_graph.astream_events.side_effect = fast_stream
            mock_create.return_value = mock_graph
            
            app.dependency_overrides[get_db] = lambda: mock_session

            response = await client.post("/chat", json={"message": long_msg}, headers=auth_headers)
            assert response.status_code == 200
                
            app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_llm_timeout_resilience(client, mock_session, test_user, auth_headers):
    """
    Test that the API handles underlying timeouts without crashing.
    """
    # Mock user for auth
    mock_user_result = MagicMock()
    mock_user_result.scalar_one_or_none.return_value = test_user
    
    # Mock thread lookup
    mock_thread_result = MagicMock()
    mock_thread_result.scalar_one_or_none.return_value = MagicMock(id="timeout", user_id=test_user.id)
    
    mock_session.execute.side_effect = [mock_user_result, mock_thread_result]

    with patch("src.controllers.chat.get_checkpointer") as mock_cp_ctx:
        mock_cp_ctx.return_value.__aenter__.return_value = AsyncMock()
        with patch("src.controllers.chat.create_graph") as mock_create:
            mock_graph = MagicMock()
            
            async def timeout_stream(*args, **kwargs):
                # Simulate timeout during streaming
                raise asyncio.TimeoutError("LLM Timeout")
                yield # Never reached
                
            mock_graph.astream_events.side_effect = timeout_stream
            mock_create.return_value = mock_graph
            
            app.dependency_overrides[get_db] = lambda: mock_session

            response = await client.post("/chat", json={"message": "fail"}, headers=auth_headers)
            
            # It's a StreamingResponse, so status code 200 is sent immediately.
            # The error is yielded as an SSE event.
            assert response.status_code == 200
            
            # Check for error event in stream
            content = ""
            async for line in response.aiter_lines():
                content += line
            
            assert "unexpected error" in content or "error" in content.lower()
                
            app.dependency_overrides.clear()
