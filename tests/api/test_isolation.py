import pytest
from httpx import AsyncClient, ASGITransport
from main import app
from src.database.session import get_db
from src.database.models import User, UserStatus, ChatThread, Transaction, Asset, RecordStatus
from src.services.auth import create_access_token
from unittest.mock import AsyncMock, MagicMock
from decimal import Decimal
from datetime import datetime

@pytest.fixture
def user_a():
    return User(id="user-a", email="a@example.com", status=UserStatus.ACTIVE, first_name="A", last_name="U")

@pytest.fixture
def user_b():
    return User(id="user-b", email="b@example.com", status=UserStatus.ACTIVE, first_name="B", last_name="U")

@pytest.fixture
def auth_a(user_a):
    token = create_access_token(user_a.id)
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def auth_b(user_b):
    token = create_access_token(user_b.id)
    return {"Authorization": f"Bearer {token}"}

@pytest.mark.asyncio
async def test_thread_isolation_stealth_404(client, mock_session, user_a, user_b, auth_a, auth_b):
    """
    Verify that User B cannot access User A's thread.
    Should return 404.
    """
    thread_id = "thread-a"
    mock_thread_a = ChatThread(id=thread_id, user_id=user_a.id, status=RecordStatus.ACTIVE)
    
    # 1. Mock user lookup for User B's request
    mock_user_b_result = MagicMock()
    mock_user_b_result.scalar_one_or_none.return_value = user_b
    
    # 2. Mock thread lookup (simulate DB filtering: if not owned by user, return None)
    mock_empty_result = MagicMock()
    mock_empty_result.scalar_one_or_none.return_value = None
    
    mock_session.execute.side_effect = [mock_user_b_result, mock_empty_result]
    
    app.dependency_overrides[get_db] = lambda: mock_session
    
    # User B tries to DELETE User A's thread
    response = await client.delete(f"/threads/{thread_id}", headers=auth_b)
    assert response.status_code == 404
    
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_transaction_isolation_stealth_404(client, mock_session, user_a, user_b, auth_a, auth_b):
    """
    Verify that User B cannot read or delete User A's transaction.
    """
    tx_id = 100
    mock_tx_a = Transaction(id=tx_id, user_id=user_a.id, asset_id=1)
    
    # Mock user B
    mock_user_b_result = MagicMock()
    mock_user_b_result.scalar_one_or_none.return_value = user_b
    
    # Mock tx lookup (using get_transaction logic which filters by user_id in service)
    # The controller calls get_transaction(db, current_user.id, tx_id)
    with patch("src.controllers.transactions.get_transaction", new_callable=AsyncMock) as mock_get_tx:
        mock_get_tx.return_value = None # Service returns None if ownership mismatch
        
        mock_session.execute.return_value = mock_user_b_result
        app.dependency_overrides[get_db] = lambda: mock_session
        
        response = await client.get(f"/investment/transactions/{tx_id}", headers=auth_b)
        assert response.status_code == 404
        
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_portfolio_zero_state_new_user(client, mock_session, user_b, auth_b):
    """
    Verify that a new user with no data gets a 200 OK with empty metrics.
    """
    from src.schemas.portfolio import PortfolioSummary
    
    mock_user_b_result = MagicMock()
    mock_user_b_result.scalar_one_or_none.return_value = user_b
    mock_session.execute.return_value = mock_user_b_result
    
    app.dependency_overrides[get_db] = lambda: mock_session
    
    empty_summary = PortfolioSummary(
        total_value_usd=Decimal("0"),
        total_cost_basis_usd=Decimal("0"),
        total_gain_loss_usd=Decimal("0"),
        total_gain_loss_pct=Decimal("0"),
        daily_pnl_usd=Decimal("0"),
        daily_pnl_pct=Decimal("0"),
        sector_allocation=[]
    )
    
    with patch("src.controllers.portfolio.get_portfolio_summary", new_callable=AsyncMock) as mock_get_sum:
        mock_get_sum.return_value = empty_summary
        
        response = await client.get("/investment", headers=auth_b)
        assert response.status_code == 200
        assert response.json()["total_value_usd"] == "0"
        
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_history_isolation_stealth_404(client, mock_session, user_a, user_b, auth_a, auth_b):
    """
    Verify that User B cannot access User A's history.
    """
    thread_id = "thread-a"
    
    # Mock user B lookup
    mock_user_b_result = MagicMock()
    mock_user_b_result.scalar_one_or_none.return_value = user_b
    
    # Mock thread lookup fails (ownership check)
    mock_empty_result = MagicMock()
    mock_empty_result.scalar_one_or_none.return_value = None
    
    mock_session.execute.side_effect = [mock_user_b_result, mock_empty_result]
    app.dependency_overrides[get_db] = lambda: mock_session
    
    response = await client.get(f"/threads/{thread_id}/history", headers=auth_b)
    assert response.status_code == 404
    
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_message_deletion_isolation_stealth_404(client, mock_session, user_a, user_b, auth_a, auth_b):
    """
    Verify that User B cannot delete User A's message.
    """
    thread_id = "thread-a"
    msg_id = "msg-a"
    
    # Mock user B lookup
    mock_user_b_result = MagicMock()
    mock_user_b_result.scalar_one_or_none.return_value = user_b
    
    # Mock message lookup fails (ownership check)
    mock_empty_result = MagicMock()
    mock_empty_result.scalar_one_or_none.return_value = None
    
    mock_session.execute.side_effect = [mock_user_b_result, mock_empty_result]
    app.dependency_overrides[get_db] = lambda: mock_session
    
    response = await client.delete(f"/threads/{thread_id}/messages/{msg_id}", headers=auth_b)
    assert response.status_code == 404
    
    app.dependency_overrides.clear()

from unittest.mock import patch
