import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from main import app
from src.database.session import get_db
from src.schemas.chat import ChatTokenEvent, ChatStatusEvent

@pytest.mark.asyncio
async def test_chat_streaming_success(client, mocker, test_user, auth_headers):
    """
    Verify that /chat SSE stream yields expected content from mocked graph events.
    """
    # 1. Mock dependencies
    mock_db = AsyncMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    
    # Mock user for auth
    mock_user_result = MagicMock()
    mock_user_result.scalar_one_or_none.return_value = test_user
    
    # Mock thread check in database
    mock_thread_result = MagicMock()
    mock_thread_result.scalar_one_or_none.return_value = MagicMock(id="test-thread-id", user_id=test_user.id)
    
    mock_db.execute.side_effect = [mock_user_result, mock_thread_result]
    
    # Mock context injection
    mocker.patch("src.controllers.chat.get_user_context_data", return_value={"portfolio_summary": "Mocked Summary"})
    
    # Mock checkpointer
    mock_checkpointer = AsyncMock()
    mock_checkpointer.__aenter__.return_value = mock_checkpointer
    mocker.patch("src.controllers.chat.get_checkpointer", return_value=mock_checkpointer)
    
    # Mock graph
    mock_graph = MagicMock()
    mocker.patch("src.controllers.chat.create_graph", return_value=mock_graph)
    
    # Mock astream_events
    async def mock_astream_events(*args, **kwargs):
        events = [
            {
                "event": "on_chain_start", 
                "metadata": {"langgraph_node": "supervisor"}, 
                "data": {}
            },
            {
                "event": "on_chat_model_stream", 
                "data": {"chunk": MagicMock(content="Hello")}
            },
            {
                "event": "on_chat_model_stream", 
                "data": {"chunk": MagicMock(content=" world!")}
            }
        ]
        for event in events:
            yield event
            
    mock_graph.astream_events.side_effect = mock_astream_events

    # 2. Execute request
    payload = {
        "message": "Hi",
        "thread_id": "test-thread-id"
    }
    
    events = []
    async with client.stream("POST", "/chat", json=payload, headers=auth_headers) as response:
        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]
        assert response.headers["X-Thread-ID"] == "test-thread-id"
        
        async for line in response.aiter_lines():
            if line.startswith("data: "):
                event_data = json.loads(line[len("data: "):])
                events.append(event_data)

    # 3. Verify events
    assert len(events) == 3
    assert events[0]["type"] == "status"
    assert "Supervisor" in events[0]["content"]
    assert events[1]["type"] == "token"
    assert events[1]["content"] == "Hello"
    assert events[2]["type"] == "token"
    assert events[2]["content"] == " world!"
    
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_chat_streaming_error(client, mocker, test_user, auth_headers):
    """
    Verify that explicit error events are yielded when the graph fails.
    """
    # 1. Mock dependencies
    mock_db = AsyncMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    
    mock_user_result = MagicMock()
    mock_user_result.scalar_one_or_none.return_value = test_user
    
    mock_thread_result = MagicMock()
    mock_thread_result.scalar_one_or_none.return_value = MagicMock(id="test-thread-id", user_id=test_user.id)
    
    mock_db.execute.side_effect = [mock_user_result, mock_thread_result]
    
    mocker.patch("src.controllers.chat.get_user_context_data", return_value={})
    
    mock_checkpointer = AsyncMock()
    mock_checkpointer.__aenter__.return_value = mock_checkpointer
    mocker.patch("src.controllers.chat.get_checkpointer", return_value=mock_checkpointer)
    
    mock_graph = MagicMock()
    mocker.patch("src.controllers.chat.create_graph", return_value=mock_graph)
    
    async def mock_astream_events_error(*args, **kwargs):
        yield {
            "event": "on_chat_model_stream", 
            "data": {"chunk": MagicMock(content="Wait...")}
        }
        raise ValueError("Graph crashed!")
            
    mock_graph.astream_events.side_effect = mock_astream_events_error

    # 2. Execute request
    payload = {"message": "Crashing test"}
    
    events = []
    async with client.stream("POST", "/chat", json=payload, headers=auth_headers) as response:
        assert response.status_code == 200
        async for line in response.aiter_lines():
            if line.startswith("data: "):
                event_data = json.loads(line[len("data: "):])
                events.append(event_data)

    # 3. Verify events
    assert len(events) == 2
    assert events[0]["type"] == "token"
    assert events[1]["type"] == "error"
    assert "An unexpected error occurred" in events[1]["content"]

    app.dependency_overrides.clear()
