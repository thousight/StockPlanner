import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from decimal import Decimal
from datetime import datetime
from src.database.models import Asset, Transaction, RecordStatus, User
from src.schemas.transactions import TransactionAction
from main import app
from src.database.session import get_db

@pytest.fixture
def mock_asset(test_user):
    asset = MagicMock(spec=Asset)
    asset.id = 1
    asset.symbol = "AAPL"
    return asset

@pytest.fixture
def mock_transaction(test_user):
    tx = MagicMock(spec=Transaction)
    tx.id = 100
    tx.user_id = test_user.id
    tx.asset_id = 1
    tx.action = "BUY"
    tx.quantity = Decimal("10.0")
    tx.price_per_share = Decimal("150.0")
    tx.commission = Decimal("5.0")
    tx.tax = Decimal("0.0")
    tx.currency = "USD"
    tx.fx_rate = Decimal("1.0")
    tx.price_base = Decimal("150.0")
    tx.total_base = Decimal("1505.0")
    tx.status = RecordStatus.ACTIVE
    tx.date = datetime.now()
    tx.asset_metadata = {"type": "STOCK"}
    return tx

@pytest.mark.asyncio
async def test_add_transaction(client, mock_session, mock_asset, mock_transaction, auth_headers, test_user):
    """
    Test POST /investment/transactions.
    Verify creation of transactions with polymorphic metadata.
    """
    # Mock user lookup for auth
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = test_user
    mock_session.execute = AsyncMock(return_value=mock_result)
    
    # Setup mock asset check
    mock_session.get.return_value = mock_asset

    # Dependency override
    app.dependency_overrides[get_db] = lambda: mock_session

    with patch("src.controllers.transactions.create_transaction", new_callable=AsyncMock) as mock_create_tx:
        mock_create_tx.return_value = mock_transaction
        
        payload = {
            "asset_id": 1,
            "action": "BUY",
            "quantity": "10.0",
            "price_per_share": "150.0",
            "commission": "5.0",
            "tax": "0.0",
            "currency": "USD",
            "asset_metadata": {"type": "STOCK"}
        }
        
        response = await client.post(
            "/investment/transactions",
            json=payload,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 100
        assert data["user_id"] == test_user.id
        
        mock_create_tx.assert_called_once()
        mock_session.commit.assert_called_once()

    del app.dependency_overrides[get_db]

@pytest.mark.asyncio
async def test_add_transaction_asset_not_found(client, mock_session, auth_headers, test_user):
    """
    Test POST /investment/transactions with non-existent asset.
    Should return 404.
    """
    # Mock user lookup
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = test_user
    mock_session.execute = AsyncMock(return_value=mock_result)
    
    mock_session.get.return_value = None
    app.dependency_overrides[get_db] = lambda: mock_session

    payload = {
        "asset_id": 999,
        "action": "BUY",
        "quantity": "10.0",
        "price_per_share": "150.0"
    }
    
    response = await client.post(
        "/investment/transactions",
        json=payload,
        headers=auth_headers
    )
    
    assert response.status_code == 404
    # Note: Refactored controller message differs slightly
    assert "Asset not found" in response.json()["detail"]

    del app.dependency_overrides[get_db]

@pytest.mark.asyncio
async def test_list_transactions(client, mock_session, mock_transaction, auth_headers, test_user):
    """
    Test GET /investment/transactions.
    """
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = test_user
    mock_session.execute = AsyncMock(return_value=mock_result)
    
    app.dependency_overrides[get_db] = lambda: mock_session

    with patch("src.controllers.transactions.get_transactions", new_callable=AsyncMock) as mock_get_txs:
        mock_get_txs.return_value = [mock_transaction]
        
        response = await client.get(
            "/investment/transactions",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == 100
        
        mock_get_txs.assert_called_once()

    del app.dependency_overrides[get_db]

@pytest.mark.asyncio
async def test_read_transaction(client, mock_session, mock_transaction, auth_headers, test_user):
    """
    Test GET /investment/transactions/{id}.
    """
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = test_user
    mock_session.execute = AsyncMock(return_value=mock_result)
    
    app.dependency_overrides[get_db] = lambda: mock_session

    with patch("src.controllers.transactions.get_transaction", new_callable=AsyncMock) as mock_get_tx:
        mock_get_tx.return_value = mock_transaction
        
        response = await client.get(
            "/investment/transactions/100",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 100
        
        mock_get_tx.assert_called_once_with(mock_session, test_user.id, 100)

    del app.dependency_overrides[get_db]

@pytest.mark.asyncio
async def test_delete_transaction(client, mock_session, auth_headers, test_user):
    """
    Test DELETE /investment/transactions/{id}.
    """
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = test_user
    mock_session.execute = AsyncMock(return_value=mock_result)
    
    app.dependency_overrides[get_db] = lambda: mock_session

    with patch("src.controllers.transactions.delete_transaction", new_callable=AsyncMock) as mock_delete_tx:
        response = await client.delete(
            "/investment/transactions/100",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        
        mock_delete_tx.assert_called_once_with(mock_session, test_user.id, 100)
        mock_session.commit.assert_called_once()

    del app.dependency_overrides[get_db]
