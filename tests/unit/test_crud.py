import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from decimal import Decimal
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException

from src.services.portfolio import (
    get_or_create_asset,
    create_transaction,
    get_holdings,
    get_transactions,
    delete_transaction
)
from src.services.market_data import (
    get_valid_cache,
    save_cache
)
from src.database.models import Asset, Transaction, Holding, RecordStatus, NewsCache
from src.schemas.transactions import TransactionCreate, TransactionAction
@pytest.mark.asyncio
async def test_get_or_create_asset_existing(mock_session):
    # Setup
    symbol = "AAPL"
    mock_asset = Asset(id=1, symbol=symbol)

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_asset
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Execute
    asset = await get_or_create_asset(mock_session, symbol)

    # Verify
    assert asset.id == 1
    assert asset.symbol == symbol
    mock_session.add.assert_not_called()

@pytest.mark.asyncio
async def test_get_or_create_asset_new(mock_session):
    # Setup
    symbol = "TSLA"
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.flush = AsyncMock()
    
    # Execute
    asset = await get_or_create_asset(mock_session, symbol)

    # Verify
    assert asset.symbol == symbol
    mock_session.add.assert_called_once()
    mock_session.flush.assert_called_once()

@pytest.mark.asyncio
async def test_create_transaction_buy_new_holding(mock_session):
    # Setup
    user_id = "user1"
    asset_id = 1
    t_data = TransactionCreate(
        asset_id=asset_id,
        action=TransactionAction.BUY,
        quantity=Decimal("10"),
        price_per_share=Decimal("150"),
        commission=Decimal("5"),
        tax=Decimal("2"),
        currency="USD",
        date=datetime(2024, 1, 1, tzinfo=timezone.utc).replace(tzinfo=None)
    )

    # Mock historical FX rate
    with patch("src.services.portfolio.get_historical_fx_rate", new_callable=AsyncMock) as mock_fx:
        mock_fx.return_value = Decimal("1.0")
        
        # Mock session.execute for Holding lock
        mock_result_holding = MagicMock()
        mock_result_holding.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result_holding)
        
        # Execute
        tx = await create_transaction(mock_session, user_id, t_data)
        
        # Verify
        assert tx.user_id == user_id
        assert tx.asset_id == asset_id
        assert tx.action == TransactionAction.BUY
        assert tx.quantity == Decimal("10")
        assert tx.total_base == Decimal("1507") # (10*150) + 5 + 2
        
        mock_session.add.assert_any_call(tx)
        # Verify holding was created
        holding_added = False
        for call in mock_session.add.call_args_list:
            if isinstance(call[0][0], Holding):
                holding_added = True
                assert call[0][0].quantity_held == Decimal("10")
                assert call[0][0].avg_cost_basis == Decimal("150.7")
        assert holding_added

@pytest.mark.asyncio
async def test_create_transaction_sell_insufficient(mock_session):
    # Setup
    user_id = "user1"
    asset_id = 1
    t_data = TransactionCreate(
        asset_id=asset_id,
        action=TransactionAction.SELL,
        quantity=Decimal("10"),
        price_per_share=Decimal("160"),
        commission=Decimal("5"),
        tax=Decimal("2"),
        currency="USD"
    )

    with patch("src.services.portfolio.get_historical_fx_rate", new_callable=AsyncMock) as mock_fx:
        mock_fx.return_value = Decimal("1.0")
        
        # Mock session.execute for Holding lock - return existing holding with less quantity
        mock_holding = Holding(user_id=user_id, asset_id=asset_id, quantity_held=Decimal("5"))
        mock_result_holding = MagicMock()
        mock_result_holding.scalar_one_or_none.return_value = mock_holding
        mock_session.execute = AsyncMock(return_value=mock_result_holding)
        
        # Execute and Verify
        with pytest.raises(HTTPException) as excinfo:
            await create_transaction(mock_session, user_id, t_data)
        assert excinfo.value.status_code == 400
        assert "Insufficient quantity" in excinfo.value.detail

@pytest.mark.asyncio
async def test_get_holdings(mock_session):
    # Setup
    user_id = "user1"
    mock_holdings = [Holding(id=1, user_id=user_id), Holding(id=2, user_id=user_id)]
    
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = mock_holdings
    mock_session.execute = AsyncMock(return_value=mock_result)
    
    # Execute
    holdings = await get_holdings(mock_session, user_id)
    
    # Verify
    assert holdings == mock_holdings
    mock_session.execute.assert_called_once()

@pytest.mark.asyncio
async def test_get_transactions(mock_session):
    # Setup
    user_id = "user1"
    mock_txs = [Transaction(id=1), Transaction(id=2)]
    
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = mock_txs
    mock_session.execute = AsyncMock(return_value=mock_result)
    
    # Execute
    txs = await get_transactions(mock_session, user_id)
    
    # Verify
    assert txs == mock_txs
    mock_session.execute.assert_called_once()

@pytest.mark.asyncio
async def test_delete_transaction(mock_session):
    # Setup
    user_id = "user1"
    tx_id = 101
    mock_tx = Transaction(id=tx_id, user_id=user_id, asset_id=1, status=RecordStatus.ACTIVE)
    
    # Mock get_transaction (which calls session.execute)
    mock_result_tx = MagicMock()
    mock_result_tx.scalar_one_or_none.return_value = mock_tx
    
    # delete_transaction calls recalculate_holding which also calls session.execute twice
    # 1. for Holding lock
    # 2. for Transactions list
    mock_result_holding = MagicMock()
    mock_result_holding.scalar_one_or_none.return_value = Holding(quantity_held=Decimal("10"))
    
    mock_result_tx_list = MagicMock()
    mock_result_tx_list.scalars.return_value.all.return_value = [] # simplified
    
    mock_session.execute = AsyncMock(side_effect=[mock_result_tx, mock_result_holding, mock_result_tx_list])
    mock_session.flush = AsyncMock()
    
    # Execute
    await delete_transaction(mock_session, user_id, tx_id)
    
    # Verify
    assert mock_tx.status == RecordStatus.INACTIVE
    assert mock_session.execute.call_count == 3
    mock_session.flush.assert_called()

@pytest.mark.asyncio
async def test_get_valid_cache_found(mock_session):
    # Setup
    url = "https://example.com"
    future_date = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=1)
    mock_entry = NewsCache(url=url, summary="Test summary", expire_at=future_date)
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_entry
    mock_session.execute = AsyncMock(return_value=mock_result)
    
    # Execute
    summary = await get_valid_cache(mock_session, url)
    
    # Verify
    assert summary == "Test summary"

@pytest.mark.asyncio
async def test_save_cache_update(mock_session):
    # Setup
    url = "https://example.com"
    mock_entry = NewsCache(url=url, summary="Old summary")
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_entry
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.commit = AsyncMock()
    
    # Execute
    await save_cache(mock_session, url, "New summary")
    
    # Verify
    assert mock_entry.summary == "New summary"
    mock_session.commit.assert_called_once()
