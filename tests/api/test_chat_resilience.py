import pytest
import asyncio
import importlib
from unittest.mock import AsyncMock, MagicMock
from main import app
from src.database.session import get_db

@pytest.mark.asyncio
async def test_chat_manual_is_disconnected_mock(client, mocker):
    """
    Verify the logic specifically when request.is_disconnected() returns True.
    """
    # 1. Mock dependencies
    mock_db = AsyncMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    
    # Mock ChatThread check
    mock_result = MagicMock()
    mock_db.execute.return_value = mock_result
    mock_result.scalar_one_or_none.return_value = MagicMock(id="test-id")
    
    mocker.patch("src.controllers.chat.get_user_context_data", return_value={})
    
    mock_checkpointer = AsyncMock()
    mock_checkpointer.__aenter__.return_value = mock_checkpointer
    mocker.patch("src.controllers.chat.get_checkpointer", return_value=mock_checkpointer)
    
    mock_graph = MagicMock()
    mocker.patch("src.controllers.chat.create_graph", return_value=mock_graph)

    state = {"events_yielded": 0}

    async def mock_astream_events(*args, **kwargs):
        for i in range(10):
            state["events_yielded"] += 1
            yield {"event": "on_chat_model_stream", "data": {"chunk": MagicMock(content=f"token {i}")}}
            
    mock_graph.astream_events.side_effect = mock_astream_events
    
    # 2. Mock the request object's is_disconnected to return True immediately
    # We need to patch where it's used. It's passed to event_generator.
    # In controllers/chat.py, it's the 'request' parameter.
    
    # We'll use a wrapper to intercept the call to event_generator
    real_gen = importlib.import_module("src.controllers.chat").event_generator
    
    async def mock_event_generator(*args, **kwargs):
        # The 'request' object is the first positional arg
        req = args[0]
        # Force it to return True after 2 calls
        req.is_disconnected = AsyncMock(side_effect=[False, False, True, True, True])
        async for item in real_gen(*args, **kwargs):
            yield item

    mocker.patch("src.controllers.chat.event_generator", side_effect=mock_event_generator)

    # 3. Execute
    payload = {"message": "test"}
    headers = {"X-User-ID": "user-1"}
    
    response_tokens = []
    async with client.stream("POST", "/chat", json=payload, headers=headers) as response:
        assert response.status_code == 200
        async for line in response.aiter_lines():
            if line.startswith("data: "):
                response_tokens.append(line)

    # 4. Verify
    # It should have stopped after ~3 tokens because we forced is_disconnected=True
    assert len(response_tokens) < 10
    assert state["events_yielded"] < 10

    # Cleanup
    app.dependency_overrides.clear()
