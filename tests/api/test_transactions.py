import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from decimal import Decimal
from datetime import datetime
from src.database.models import Asset, Transaction, RecordStatus
from src.schemas.transactions import TransactionAction
from main import app
from src.database.session import get_db

@pytest.fixture
def mock_asset():
    asset = MagicMock(spec=Asset)
    asset.id = 1
    asset.user_id = "user123"
    asset.symbol = "AAPL"
    return asset

@pytest.fixture
def mock_transaction():
    tx = MagicMock(spec=Transaction)
    tx.id = 100
    tx.user_id = "user123"
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
async def test_add_transaction(client, mock_session, mock_asset, mock_transaction):
    """
    Test POST /investment/transactions.
    Verify creation of transactions with polymorphic metadata.
    """
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
            headers={"X-User-ID": "user123"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 100
        assert data["user_id"] == "user123"
        assert data["total_base"] == "1505.0"
        
        mock_session.get.assert_called_once()
        mock_create_tx.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(mock_transaction)

    # Clean up
    del app.dependency_overrides[get_db]

@pytest.mark.asyncio
async def test_add_transaction_asset_not_found(client, mock_session):
    """
    Test POST /investment/transactions with non-existent asset.
    Should return 404.
    """
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
        headers={"X-User-ID": "user123"}
    )
    
    assert response.status_code == 404
    assert "Asset ID 999 not found" in response.json()["detail"]

    del app.dependency_overrides[get_db]

@pytest.mark.asyncio
async def test_list_transactions(client, mock_session, mock_transaction):
    """
    Test GET /investment/transactions.
    """
    app.dependency_overrides[get_db] = lambda: mock_session

    with patch("src.controllers.transactions.get_transactions", new_callable=AsyncMock) as mock_get_txs:
        mock_get_txs.return_value = [mock_transaction]
        
        response = await client.get(
            "/investment/transactions",
            headers={"X-User-ID": "user123"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == 100
        
        mock_get_txs.assert_called_once()

    del app.dependency_overrides[get_db]

@pytest.mark.asyncio
async def test_read_transaction(client, mock_session, mock_transaction):
    """
    Test GET /investment/transactions/{id}.
    """
    app.dependency_overrides[get_db] = lambda: mock_session

    with patch("src.controllers.transactions.get_transaction", new_callable=AsyncMock) as mock_get_tx:
        mock_get_tx.return_value = mock_transaction
        
        response = await client.get(
            "/investment/transactions/100",
            headers={"X-User-ID": "user123"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 100
        
        mock_get_tx.assert_called_once_with(mock_session, "user123", 100)

    del app.dependency_overrides[get_db]

@pytest.mark.asyncio
async def test_read_transaction_not_found(client, mock_session):
    """
    Test GET /investment/transactions/{id} not found.
    """
    app.dependency_overrides[get_db] = lambda: mock_session

    with patch("src.controllers.transactions.get_transaction", new_callable=AsyncMock) as mock_get_tx:
        mock_get_tx.return_value = None
        
        response = await client.get(
            "/investment/transactions/999",
            headers={"X-User-ID": "user123"}
        )
        
        assert response.status_code == 404

    del app.dependency_overrides[get_db]

@pytest.mark.asyncio
async def test_delete_transaction(client, mock_session):
    """
    Test DELETE /investment/transactions/{id}.
    """
    app.dependency_overrides[get_db] = lambda: mock_session

    with patch("src.controllers.transactions.delete_transaction", new_callable=AsyncMock) as mock_delete_tx:
        response = await client.delete(
            "/investment/transactions/100",
            headers={"X-User-ID": "user123"}
        )
        
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        
        mock_delete_tx.assert_called_once_with(mock_session, "user123", 100)
        mock_session.commit.assert_called_once()

    del app.dependency_overrides[get_db]
