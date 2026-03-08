import pytest
import asyncio
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
    
    # Mock holdings lookup (two queries now: summary count and raw holdings)
    mock_holdings_result = MagicMock()
    mock_holdings_result.scalars.return_value.all.return_value = []
    
    mock_session.execute.side_effect = [
        mock_user_result,     # get_current_user (Request 1)
        mock_thread_result,   # stream_run ownership check (Request 1)
        mock_holdings_result, # get_portfolio_summary (Request 1)
        mock_holdings_result, # get_user_context_data raw holdings (Request 1)
        mock_user_result,     # get_current_user (Request 2)
        mock_thread_result,   # stream_run ownership check (Request 2)
        mock_holdings_result, # get_portfolio_summary (Request 2)
        mock_holdings_result, # get_user_context_data raw holdings (Request 2)
    ]

    # Mock the underlying event generator's graph call to add delay
    with patch("src.controllers.threads.get_checkpointer") as mock_cp_ctx:
        # get_checkpointer is an async context manager
        mock_cp = AsyncMock()
        mock_cp_ctx.return_value.__aenter__.return_value = mock_cp
        
        with patch("src.controllers.threads.create_graph") as mock_create:
            mock_graph = MagicMock()
            
            async def slow_stream(*args, **kwargs):
                await asyncio.sleep(0.5)
                yield ("metadata", {"langgraph_node": "end"})
                
            mock_graph.astream.side_effect = slow_stream
            mock_create.return_value = mock_graph
            
            app.dependency_overrides[get_db] = lambda: mock_session

            # Send two requests concurrently
            tasks = [
                client.post(f"/threads/{thread_id}/runs/stream", json={"input": {"message": "hello"}}, headers={**auth_headers, "X-Thread-ID": thread_id}),
                client.post(f"/threads/{thread_id}/runs/stream", json={"input": {"message": "hello"}}, headers={**auth_headers, "X-Thread-ID": thread_id})
            ]
            
            responses = await asyncio.gather(*tasks)
            
            status_codes = [r.status_code for r in responses]
            assert 409 in status_codes
            # One should be 200 (StreamingResponse)
            assert 200 in status_codes
                
            app.dependency_overrides.clear()
