import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from main import app
from src.database.session import get_db
from src.schemas.chat import ChatTokenEvent, ChatStatusEvent, ChatUpdateEvent

@pytest.mark.asyncio
async def test_chat_streaming_success(client, mocker):
    """
    Verify that /chat SSE stream yields expected content from mocked graph events.
    """
    # 1. Mock dependencies
    mock_db = AsyncMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    
    # Mock thread check in database
    mock_result = MagicMock()
    mock_db.execute.return_value = mock_result
    # thread = result.scalar_one_or_none()
    mock_result.scalar_one_or_none.return_value = MagicMock(id="test-thread-id")
    
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
        # We need events that match what event_generator expects
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
            },
            {
                "event": "on_chain_end", 
                "metadata": {"langgraph_node": "commit"}, 
                "data": {"output": {"last_report_id": 123}}
            }
        ]
        for event in events:
            yield event
            
    mock_graph.astream_events.side_effect = mock_astream_events
    
    # Mock aget_state for handle_interrupts (called after astream_events)
    mock_state = MagicMock()
    mock_state.next = [] # No interrupts
    mock_graph.aget_state = AsyncMock(return_value=mock_state)

    # 2. Execute request
    payload = {
        "message": "Hi",
        "thread_id": "test-thread-id"
    }
    headers = {"X-User-ID": "user-1"}
    
    events = []
    async with client.stream("POST", "/chat", json=payload, headers=headers) as response:
        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]
        
        async for line in response.aiter_lines():
            if line.startswith("data: "):
                event_data = json.loads(line[len("data: "):])
                events.append(event_data)

    # 3. Verify events
    # Expected: 1 status, 2 tokens, 1 update
    assert len(events) == 4
    
    # Check types and content
    assert events[0]["type"] == "status"
    assert "Supervisor" in events[0]["content"]
    
    assert events[1]["type"] == "token"
    assert events[1]["content"] == "Hello"
    
    assert events[2]["type"] == "token"
    assert events[2]["content"] == " world!"
    
    assert events[3]["type"] == "update"
    assert events[3]["update_type"] == "REPORT_COMMITTED"
    assert events[3]["report_id"] == 123

    # Cleanup
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_chat_streaming_error(client, mocker):
    """
    Verify that explicit error events are yielded when the graph fails.
    """
    # 1. Mock dependencies
    mock_db = AsyncMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    
    mock_result = MagicMock()
    mock_db.execute.return_value = mock_result
    mock_result.scalar_one_or_none.return_value = MagicMock(id="test-thread-id")
    
    mocker.patch("src.controllers.chat.get_user_context_data", return_value={})
    
    mock_checkpointer = AsyncMock()
    mock_checkpointer.__aenter__.return_value = mock_checkpointer
    mocker.patch("src.controllers.chat.get_checkpointer", return_value=mock_checkpointer)
    
    mock_graph = MagicMock()
    mocker.patch("src.controllers.chat.create_graph", return_value=mock_graph)
    
    # Mock astream_events to raise an exception
    async def mock_astream_events_error(*args, **kwargs):
        # Yield one token then crash
        yield {
            "event": "on_chat_model_stream", 
            "data": {"chunk": MagicMock(content="Wait...")}
        }
        raise ValueError("Graph crashed!")
            
    mock_graph.astream_events.side_effect = mock_astream_events_error

    # 2. Execute request
    payload = {"message": "Crashing test"}
    headers = {"X-User-ID": "user-1"}
    
    events = []
    async with client.stream("POST", "/chat", json=payload, headers=headers) as response:
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

    # Cleanup
    app.dependency_overrides.clear()
