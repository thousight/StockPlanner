import pytest
from unittest.mock import MagicMock, patch, AsyncMock, PropertyMock
from datetime import date
from decimal import Decimal
from src.services.market_data import (
    get_historical_fx_rate,
    get_current_price,
    _parse_yf_news_item,
    fetch_yfinance_news_urls,
    validate_transaction_price
)
from src.database.models import FXRate, Asset, AssetType
import pandas as pd

@pytest.fixture
def mock_db():
    db = AsyncMock()
    # db.add is a synchronous method in AsyncSession
    db.add = MagicMock()
    return db

@pytest.mark.asyncio
async def test_get_historical_fx_rate_same_currency(mock_db):
    rate = await get_historical_fx_rate(mock_db, "USD", "USD")
    assert rate == Decimal("1.0")
    mock_db.execute.assert_not_called()

@pytest.mark.asyncio
async def test_get_historical_fx_rate_cache_hit(mock_db):
    transaction_date = date(2023, 1, 1)
    mock_fx_rate = FXRate(source="EUR", target="USD", rate=Decimal("1.1"), date=transaction_date)
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_fx_rate
    mock_db.execute.return_value = mock_result
    
    rate = await get_historical_fx_rate(mock_db, "EUR", "USD", transaction_date)
    assert rate == Decimal("1.1")

@pytest.mark.asyncio
async def test_get_historical_fx_rate_yfinance_success(mock_db):
    transaction_date = date(2023, 1, 1)
    
    # 1. Cache miss (returns None or different date)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result
    
    # 2. Mock yfinance
    with patch("src.services.market_data.get_ticker") as mock_get_ticker:
        mock_ticker = MagicMock()
        mock_get_ticker.return_value = mock_ticker
        
        # Mock history returns a DataFrame with 'Close'
        df = pd.DataFrame({"Close": [1.05]}, index=[pd.Timestamp(transaction_date)])
        mock_ticker.history.return_value = df
        
        rate = await get_historical_fx_rate(mock_db, "EUR", "USD", transaction_date)
        
        assert rate == Decimal("1.05")
        assert mock_db.add.called
        assert mock_db.commit.called

@pytest.mark.asyncio
async def test_get_historical_fx_rate_fallback_to_cache(mock_db):
    transaction_date = date(2023, 1, 2)
    # Cache has an older rate
    mock_fx_rate = FXRate(source="EUR", target="USD", rate=Decimal("1.1"), date=date(2023, 1, 1))
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_fx_rate
    mock_db.execute.return_value = mock_result
    
    # Mock yfinance failure
    with patch("src.services.market_data.get_ticker") as mock_get_ticker:
        mock_ticker = MagicMock()
        mock_get_ticker.return_value = mock_ticker
        mock_ticker.history.side_effect = Exception("API Down")
        
        rate = await get_historical_fx_rate(mock_db, "EUR", "USD", transaction_date)
        
        assert rate == Decimal("1.1") # Fallback to nearest in cache

@pytest.mark.asyncio
async def test_get_current_price_stock_fast_info(mock_db):
    asset = Asset(symbol="AAPL", type=AssetType.STOCK)
    
    with patch("src.services.market_data.get_ticker") as mock_get_ticker:
        mock_ticker = MagicMock()
        mock_get_ticker.return_value = mock_ticker
        
        # Mock fast_info
        mock_ticker.fast_info = {"last_price": 150.0}
        
        price = await get_current_price(mock_db, asset)
        assert price == Decimal("150.0")

@pytest.mark.asyncio
async def test_get_current_price_stock_history_fallback(mock_db):
    asset = Asset(symbol="AAPL", type=AssetType.STOCK)
    
    with patch("src.services.market_data.get_ticker") as mock_get_ticker:
        mock_ticker = MagicMock()
        mock_get_ticker.return_value = mock_ticker
        
        # fast_info fails
        mock_ticker.fast_info = property(lambda x: Exception("No fast info")) # This doesn't work well with lambda
        # Simpler: just make the access fail
        type(mock_ticker).fast_info = PropertyMock(side_effect=Exception("No fast info"))
        
        # Mock history
        df = pd.DataFrame({"Close": [155.0]}, index=[pd.Timestamp.now()])
        mock_ticker.history.return_value = df
        
        price = await get_current_price(mock_db, asset)
        assert price == Decimal("155.0")

@pytest.mark.asyncio
async def test_get_current_price_fallback_to_db(mock_db):
    asset = Asset(id=1, symbol="AAPL", type=AssetType.STOCK)
    
    with patch("src.services.market_data.get_ticker") as mock_get_ticker:
        mock_ticker = MagicMock()
        mock_get_ticker.return_value = mock_ticker
        type(mock_ticker).fast_info = PropertyMock(side_effect=Exception("No fast info"))
        mock_ticker.history.side_effect = Exception("No history")
        
        # Mock DB response for last transaction
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = 145.0
        mock_db.execute.return_value = mock_result
        
        price = await get_current_price(mock_db, asset)
        assert price == Decimal("145.0")


def test_parse_yf_news_item_new_structure():
    item = {
        "content": {
            "title": "Stock Up",
            "clickThroughUrl": {"url": "https://example.com/news1"}
        }
    }
    parsed = _parse_yf_news_item(item)
    assert parsed == {"title": "Stock Up", "link": "https://example.com/news1"}

def test_parse_yf_news_item_legacy_structure():
    item = {
        "title": "Old News",
        "link": "https://example.com/old"
    }
    parsed = _parse_yf_news_item(item)
    assert parsed == {"title": "Old News", "link": "https://example.com/old"}

def test_parse_yf_news_item_malformed():
    assert _parse_yf_news_item({}) is None
    assert _parse_yf_news_item({"content": {}}) is None

@pytest.mark.asyncio
async def test_fetch_yfinance_news_urls_success():
    with patch("src.services.market_data.get_stock_news_data") as mock_news:
        mock_news.return_value = [
            {"content": {"title": "T1", "clickThroughUrl": {"url": "L1"}}},
            {"title": "T2", "link": "L2"},
            {"invalid": "item"}
        ]
        
        results = await fetch_yfinance_news_urls("AAPL")
        assert len(results) == 2
        assert results[0] == {"title": "T1", "link": "L1"}
        assert results[1] == {"title": "T2", "link": "L2"}

@pytest.mark.asyncio
async def test_validate_transaction_price_success():
    transaction_date = date(2023, 1, 1)
    with patch("src.services.market_data.get_ticker") as mock_get_ticker:
        mock_ticker = MagicMock()
        mock_get_ticker.return_value = mock_ticker
        
        # Mock history with Low/High
        df = pd.DataFrame({"Low": [100.0], "High": [110.0]}, index=[pd.Timestamp(transaction_date)])
        mock_ticker.history.return_value = df
        
        # Within range
        assert await validate_transaction_price("AAPL", transaction_date, Decimal("105.0")) is True
        # Within buffer (90-121)
        assert await validate_transaction_price("AAPL", transaction_date, Decimal("95.0")) is True
        assert await validate_transaction_price("AAPL", transaction_date, Decimal("120.0")) is True
        # Outside buffer
        assert await validate_transaction_price("AAPL", transaction_date, Decimal("80.0")) is False
        assert await validate_transaction_price("AAPL", transaction_date, Decimal("130.0")) is False

@pytest.mark.asyncio
async def test_validate_transaction_price_empty_history():
    transaction_date = date(2023, 1, 1)
    with patch("src.services.market_data.get_ticker") as mock_get_ticker:
        mock_ticker = MagicMock()
        mock_get_ticker.return_value = mock_ticker
        mock_ticker.history.return_value = pd.DataFrame()
        
        assert await validate_transaction_price("AAPL", transaction_date, Decimal("100.0")) is True
