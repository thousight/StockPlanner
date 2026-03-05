import pytest
import json
from main import app
from src.database.session import get_db
from src.database.models import ChatThread
from unittest.mock import AsyncMock, MagicMock, patch

@pytest.mark.asyncio
async def test_stream_protocol_subgraph_propagation(client, mock_session, test_user, auth_headers):
    """
    Verify that the stream protocol yields metadata events showing node transitions,
    including potential subgraph activity.
    """
    thread_id = "subgraph-test-thread"
    
    # Mock user and thread
    mock_user_result = MagicMock()
    mock_user_result.scalar_one_or_none.return_value = test_user
    
    mock_thread = ChatThread(id=thread_id, user_id=test_user.id, deleted_at=None, title="Test")
    mock_thread_result = MagicMock()
    mock_thread_result.scalar_one_or_none.return_value = mock_thread
    
    # Mock holdings lookup
    mock_holdings_result = MagicMock()
    mock_holdings_result.scalars.return_value.all.return_value = []

    mock_session.execute.side_effect = [
        mock_user_result,     # get_current_user
        mock_thread_result,   # stream_run ownership check
        mock_holdings_result, # get_portfolio_summary
        mock_user_result,     # get_current_user
    ]
    app.dependency_overrides[get_db] = lambda: mock_session

    payload = {
        "input": {"message": "Analyze AAPL"},
        "stream_mode": ["metadata", "messages"]
    }

    # We mock create_graph to use a simple graph that mimics subgraph behavior
    # or just let it run if we mock the LLM.
    # Let's mock the internal astream to verify our generator's handling of the output.
    
    with patch("src.controllers.threads.get_checkpointer") as mock_cp_ctx:
        mock_cp_ctx.return_value.__aenter__.return_value = AsyncMock()
        with patch("src.controllers.threads.create_graph") as mock_create_graph:
            mock_graph = MagicMock()
            mock_graph.aget_state = AsyncMock(return_value=MagicMock(values={}))
            mock_graph.aupdate_state = AsyncMock()
            
            async def mock_astream(*args, **kwargs):
                # Simulate events from main graph and subgraph
                yield ("metadata", {"langgraph_node": "supervisor"})
                yield ("messages", [{"content": "Working...", "type": "ai"}, {"langgraph_node": "supervisor"}])
                # Simulate subgraph event (LangGraph standard format for subgraphs is usually "node:subnode")
                yield ("metadata", {"langgraph_node": "analyst:bull"})
                yield ("messages", [{"content": "Bullish!", "type": "ai"}, {"langgraph_node": "analyst:bull"}])
                
            mock_graph.astream.side_effect = mock_astream
            mock_create_graph.return_value = mock_graph

            events = []
            async with client.stream("POST", f"/threads/{thread_id}/runs/stream", json=payload, headers=auth_headers) as response:
                assert response.status_code == 200
                async for line in response.aiter_lines():
                    if line.startswith("event: "):
                        events.append({"event": line[len("event: "):]})
                    elif line.startswith("data: "):
                        events[-1]["data"] = json.loads(line[len("data: "):])

            # Verify protocol compliance
            assert any(e["event"] == "metadata" and e["data"][0]["langgraph_node"] == "supervisor" for e in events)
            assert any(e["event"] == "metadata" and e["data"][0]["langgraph_node"] == "analyst:bull" for e in events)
            assert any(e["event"] == "messages" and e["data"][0][0]["content"] == "Bullish!" for e in events)
            assert events[-1]["event"] == "end"

    app.dependency_overrides.clear()
