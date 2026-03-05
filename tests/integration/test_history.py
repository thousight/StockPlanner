import pytest
from main import app
from src.database.session import get_db
from src.database.models import User, UserStatus, ChatThread, ChatMessage
from src.services.auth import create_access_token
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

@pytest.fixture
def test_user_history():
    return User(
        id="user-history-123", 
        email="history@example.com", 
        status=UserStatus.ACTIVE,
        first_name="History",
        last_name="User"
    )

@pytest.fixture
def auth_headers_history(test_user_history):
    token = create_access_token(test_user_history.id)
    return {"Authorization": f"Bearer {token}"}

@pytest.mark.asyncio
async def test_get_history_triggers_backfill(client, mock_session, test_user_history, auth_headers_history):
    """
    Verify that GET /history triggers backfill when relational history is empty.
    """
    thread_id = "thread-backfill-test"
    
    # 1. Mock user lookup for auth
    mock_user_result = MagicMock()
    mock_user_result.scalar_one_or_none.return_value = test_user_history
    
    # 2. Mock thread existence
    mock_thread = ChatThread(id=thread_id, user_id=test_user_history.id, deleted_at=None)
    mock_thread_result = MagicMock()
    mock_thread_result.scalar_one_or_none.return_value = mock_thread
    
    # 3. Mock backfill check (count = 0)
    mock_count_result = MagicMock()
    mock_count_result.scalar.return_value = 0
    
    # 4. Mock message existence checks in sync (2 messages)
    mock_empty_msg_result = MagicMock()
    mock_empty_msg_result.scalar_one_or_none.return_value = None
    
    # 5. Mock message query result (after backfill)
    mock_msg = ChatMessage(id="msg-1", thread_id=thread_id, user_id=test_user_history.id, role="AI", content="Hello", created_at=datetime.now())
    mock_messages_result = MagicMock()
    mock_messages_result.scalars.return_value.all.return_value = [mock_msg]
    
    mock_session.execute.side_effect = [
        mock_user_result,     # get_current_user
        mock_thread_result,   # get_history ownership check
        mock_count_result,    # backfill_history_if_needed count check
        mock_thread_result,   # sync_conversation_to_postgres thread existence check
        mock_empty_msg_result, # sync_conversation_to_postgres msg 1
        mock_empty_msg_result, # sync_conversation_to_postgres msg 2
        mock_messages_result  # get_history final query
    ]
    
    app.dependency_overrides[get_db] = lambda: mock_session
    
    with patch("src.services.history.get_checkpointer") as mock_cp_ctx:
        mock_checkpointer = AsyncMock()
        mock_cp_ctx.return_value.__aenter__.return_value = mock_checkpointer
        
        with patch("src.services.history.create_graph") as mock_create_graph:
            mock_graph = MagicMock()
            mock_graph.aget_state = AsyncMock() # Ensure it is awaitable
            from langchain_core.messages import HumanMessage, AIMessage
            
            # Mock graph state messages
            mock_state = MagicMock()
            mock_state.values = {
                "session_context": {
                    "messages": [
                        HumanMessage(content="Hi", id="lc-1"),
                        AIMessage(content="Hello", id="lc-2")
                    ]
                }
            }
            mock_graph.aget_state.return_value = mock_state
            mock_create_graph.return_value = mock_graph
            
            # Execute
            response = await client.get(f"/threads/{thread_id}/history", headers=auth_headers_history)
            
            assert response.status_code == 200
            # Verify backfill was attempted
            mock_graph.aget_state.assert_called_once()
            # Verify database additions (sync_conversation_to_postgres)
            # 2 messages synced
            assert mock_session.add.call_count >= 2
            
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_get_history_pagination(client, mock_session, test_user_history, auth_headers_history):
    """
    Verify cursor-based pagination returns correct subset.
    """
    thread_id = "thread-pagination"
    
    mock_user_result = MagicMock()
    mock_user_result.scalar_one_or_none.return_value = test_user_history
    
    mock_thread = ChatThread(id=thread_id, user_id=test_user_history.id, deleted_at=None)
    mock_thread_result = MagicMock()
    mock_thread_result.scalar_one_or_none.return_value = mock_thread
    
    # Mock backfill (count > 0 so no backfill)
    mock_count_result = MagicMock()
    mock_count_result.scalar.return_value = 10
    
    # Mock messages (limit + 1)
    msg_ids = [f"uuid-{i}" for i in range(21)] # DESC order
    mock_msgs = [
        ChatMessage(id=mid, thread_id=thread_id, user_id=test_user_history.id, role="AI", content="...", created_at=datetime.now())
        for mid in msg_ids
    ]
    mock_messages_result = MagicMock()
    mock_messages_result.scalars.return_value.all.return_value = mock_msgs
    
    mock_session.execute.side_effect = [
        mock_user_result, 
        mock_thread_result, 
        mock_count_result, 
        mock_messages_result
    ]
    
    app.dependency_overrides[get_db] = lambda: mock_session
    
    response = await client.get(f"/threads/{thread_id}/history?limit=20", headers=auth_headers_history)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["messages"]) == 20
    assert data["cursor"]["has_more"] is True
    assert data["cursor"]["next_cursor"] == msg_ids[19]
    
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_delete_message_stealth_404(client, mock_session, test_user_history, auth_headers_history):
    """
    Verify that deleting a message belonging to another user returns 404.
    """
    thread_id = "thread-1"
    msg_id = "msg-other"
    
    mock_user_result = MagicMock()
    mock_user_result.scalar_one_or_none.return_value = test_user_history
    
    # Mock message lookup returns None (simulating user_id filter mismatch)
    mock_msg_result = MagicMock()
    mock_msg_result.scalar_one_or_none.return_value = None
    
    mock_session.execute.side_effect = [mock_user_result, mock_msg_result]
    
    app.dependency_overrides[get_db] = lambda: mock_session
    
    response = await client.delete(f"/threads/{thread_id}/messages/{msg_id}", headers=auth_headers_history)
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Not Found"
    
    app.dependency_overrides.clear()
