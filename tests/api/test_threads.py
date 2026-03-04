import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
from src.database.models import ChatThread, RecordStatus, User
from main import app
from src.database.session import get_db

@pytest.fixture
def mock_thread(test_user):
    thread = MagicMock(spec=ChatThread)
    thread.id = "thread_123"
    thread.user_id = test_user.id
    thread.title = "Test Thread"
    thread.status = RecordStatus.ACTIVE
    thread.created_at = datetime.now()
    thread.updated_at = datetime.now()
    return thread

@pytest.mark.asyncio
async def test_get_threads(client, mock_session, mock_thread, auth_headers, test_user):
    """
    Test GET /threads.
    Verify retrieval of active conversation threads.
    """
    # Mock user for auth
    mock_user_result = MagicMock()
    mock_user_result.scalar_one_or_none.return_value = test_user
    
    # Mock total count
    mock_count_result = MagicMock()
    mock_count_result.scalar.return_value = 1
    
    # Mock threads result
    mock_threads_result = MagicMock()
    mock_threads_result.scalars.return_value.all.return_value = [mock_thread]
    
    mock_session.execute.side_effect = [mock_user_result, mock_count_result, mock_threads_result]
    
    app.dependency_overrides[get_db] = lambda: mock_session
    
    response = await client.get(
        "/threads",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["threads"]) == 1
    assert data["threads"][0]["id"] == "thread_123"
    
    # User lookup + count + select
    assert mock_session.execute.call_count == 3
    
    del app.dependency_overrides[get_db]

@pytest.mark.asyncio
async def test_delete_thread(client, mock_session, mock_thread, auth_headers, test_user):
    """
    Test DELETE /threads/{id}.
    Verify thread deletion logic (soft delete).
    """
    # Mock user for auth
    mock_user_result = MagicMock()
    mock_user_result.scalar_one_or_none.return_value = test_user
    
    # Mock finding the thread
    mock_thread_result = MagicMock()
    mock_thread_result.scalar_one_or_none.return_value = mock_thread
    
    # Mock the update query for ChatMessages
    mock_update_result = MagicMock()
    
    mock_session.execute.side_effect = [mock_user_result, mock_thread_result, mock_update_result]
    
    app.dependency_overrides[get_db] = lambda: mock_session
    
    response = await client.delete(
        "/threads/thread_123",
        headers=auth_headers
    )
    
    assert response.status_code == 204 # Returns 204 No Content now
    
    # Verify deleted_at was set
    assert mock_thread.deleted_at is not None
    mock_session.commit.assert_called_once()
    
    del app.dependency_overrides[get_db]

@pytest.mark.asyncio
async def test_delete_thread_not_found(client, mock_session, auth_headers, test_user):
    """
    Test DELETE /threads/{id} when thread not found.
    """
    # Mock user for auth
    mock_user_result = MagicMock()
    mock_user_result.scalar_one_or_none.return_value = test_user
    
    # Mock thread not found
    mock_thread_result = MagicMock()
    mock_thread_result.scalar_one_or_none.return_value = None
    
    mock_session.execute.side_effect = [mock_user_result, mock_thread_result]
    
    app.dependency_overrides[get_db] = lambda: mock_session
    
    response = await client.delete(
        "/threads/non_existent",
        headers=auth_headers
    )
    
    assert response.status_code == 404
    
    del app.dependency_overrides[get_db]

@pytest.mark.asyncio
async def test_response_headers(client, mock_session, auth_headers, test_user):
    """
    Verify that correct headers (e.g., X-Request-ID) are present in responses.
    """
    # Mock user for auth
    mock_user_result = MagicMock()
    mock_user_result.scalar_one_or_none.return_value = test_user
    
    mock_count_result = MagicMock()
    mock_count_result.scalar.return_value = 0
    mock_threads_result = MagicMock()
    mock_threads_result.scalars.return_value.all.return_value = []
    
    mock_session.execute.side_effect = [mock_user_result, mock_count_result, mock_threads_result]
    
    app.dependency_overrides[get_db] = lambda: mock_session
    
    response = await client.get(
        "/threads",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    # X-Request-ID is added by CorrelationIdMiddleware
    assert "X-Request-ID" in response.headers
    
    del app.dependency_overrides[get_db]
