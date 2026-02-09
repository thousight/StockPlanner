"""
Unit tests for database CRUD operations.
"""
import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database.models import Base, Transaction, Stock, NewsCache
from src.database.crud import (
    add_stock,
    add_transaction,
    get_holdings,
    get_transactions,
    get_valid_cache,
    save_cache,
    cleanup_expired_cache
)


@pytest.fixture
def db_session():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


class TestStockOperations:
    """Tests for stock-related CRUD operations."""
    
    def test_add_stock_creates_new_stock(self, db_session):
        """Test adding a new stock."""
        stock = add_stock(db_session, "AAPL", name="Apple Inc", sector="Technology")
        
        assert stock is not None
        assert stock.symbol == "AAPL"
        assert stock.name == "Apple Inc"
        assert stock.sector == "Technology"
    
    def test_add_stock_returns_existing_stock(self, db_session):
        """Test that adding an existing stock returns the same record."""
        stock1 = add_stock(db_session, "AAPL", name="Apple Inc")
        stock2 = add_stock(db_session, "AAPL", name="Different Name")
        
        assert stock1.symbol == stock2.symbol
        # Original name should be preserved
        assert stock2.name == "Apple Inc"
    
    def test_add_stock_minimal_params(self, db_session):
        """Test adding a stock with only symbol."""
        stock = add_stock(db_session, "MSFT")
        
        assert stock.symbol == "MSFT"
        assert stock.name is None


class TestTransactionOperations:
    """Tests for transaction-related CRUD operations."""
    
    def test_add_buy_transaction(self, db_session):
        """Test adding a buy transaction."""
        transaction = add_transaction(
            db_session,
            symbol="AAPL",
            action="BUY",
            quantity=10.0,
            price=150.0,
            fees=1.0
        )
        
        assert transaction is not None
        assert transaction.symbol == "AAPL"
        assert transaction.action == "BUY"
        assert transaction.quantity == 10.0
        assert transaction.price_per_share == 150.0
        assert transaction.fees == 1.0
    
    def test_add_transaction_creates_stock(self, db_session):
        """Test that adding a transaction auto-creates the stock."""
        add_transaction(db_session, "NVDA", "BUY", 5.0, 200.0)
        
        stock = db_session.query(Stock).filter(Stock.symbol == "NVDA").first()
        assert stock is not None
    
    def test_add_transaction_with_custom_date(self, db_session):
        """Test adding a transaction with a specific date."""
        custom_date = datetime(2024, 1, 15, 10, 30)
        transaction = add_transaction(
            db_session, "AAPL", "BUY", 10.0, 150.0, date=custom_date
        )
        
        assert transaction.date == custom_date
    
    def test_get_transactions_all(self, db_session):
        """Test getting all transactions."""
        add_transaction(db_session, "AAPL", "BUY", 10.0, 150.0)
        add_transaction(db_session, "MSFT", "BUY", 5.0, 300.0)
        
        transactions = get_transactions(db_session)
        
        assert len(transactions) == 2
    
    def test_get_transactions_by_symbol(self, db_session):
        """Test filtering transactions by symbol."""
        add_transaction(db_session, "AAPL", "BUY", 10.0, 150.0)
        add_transaction(db_session, "MSFT", "BUY", 5.0, 300.0)
        add_transaction(db_session, "AAPL", "SELL", 5.0, 160.0)
        
        aapl_transactions = get_transactions(db_session, symbol="AAPL")
        
        assert len(aapl_transactions) == 2
        for t in aapl_transactions:
            assert t.symbol == "AAPL"


class TestHoldingsCalculation:
    """Tests for portfolio holdings calculation."""
    
    def test_get_holdings_single_buy(self, db_session):
        """Test holdings with a single buy transaction."""
        add_transaction(db_session, "AAPL", "BUY", 10.0, 150.0)
        
        holdings = get_holdings(db_session)
        
        assert len(holdings) == 1
        assert holdings[0]["symbol"] == "AAPL"
        assert holdings[0]["quantity"] == 10.0
        assert holdings[0]["avg_cost"] == 150.0
    
    def test_get_holdings_multiple_buys_avg_cost(self, db_session):
        """Test average cost calculation with multiple buys."""
        add_transaction(db_session, "AAPL", "BUY", 10.0, 100.0)  # $1000
        add_transaction(db_session, "AAPL", "BUY", 10.0, 200.0)  # $2000
        
        holdings = get_holdings(db_session)
        
        assert len(holdings) == 1
        assert holdings[0]["quantity"] == 20.0
        assert holdings[0]["avg_cost"] == 150.0  # $3000 / 20 shares
    
    def test_get_holdings_buy_and_sell(self, db_session):
        """Test holdings after partial sell."""
        add_transaction(db_session, "AAPL", "BUY", 10.0, 100.0)
        add_transaction(db_session, "AAPL", "SELL", 5.0, 120.0)
        
        holdings = get_holdings(db_session)
        
        assert len(holdings) == 1
        assert holdings[0]["quantity"] == 5.0
    
    def test_get_holdings_excludes_sold_positions(self, db_session):
        """Test that fully sold positions are excluded."""
        add_transaction(db_session, "AAPL", "BUY", 10.0, 100.0)
        add_transaction(db_session, "AAPL", "SELL", 10.0, 120.0)
        
        holdings = get_holdings(db_session)
        
        assert len(holdings) == 0
    
    def test_get_holdings_with_fees(self, db_session):
        """Test that fees are included in cost basis."""
        add_transaction(db_session, "AAPL", "BUY", 10.0, 100.0, fees=10.0)
        
        holdings = get_holdings(db_session)
        
        # Total cost = (10 * 100) + 10 = 1010
        # Avg cost = 1010 / 10 = 101
        assert holdings[0]["avg_cost"] == 101.0


class TestNewsCacheOperations:
    """Tests for news cache CRUD operations."""
    
    def test_save_cache_new_entry(self, db_session):
        """Test saving a new cache entry."""
        save_cache(db_session, "https://example.com/article", "Test summary")
        
        entry = db_session.query(NewsCache).filter(NewsCache.url == "https://example.com/article").first()
        assert entry is not None
        assert entry.summary == "Test summary"
        assert entry.expire_at > datetime.now(timezone.utc).replace(tzinfo=None)
    
    def test_save_cache_updates_existing(self, db_session):
        """Test that saving to existing URL updates the entry."""
        save_cache(db_session, "https://example.com/article", "Original summary")
        save_cache(db_session, "https://example.com/article", "Updated summary")
        
        entries = db_session.query(NewsCache).filter(NewsCache.url == "https://example.com/article").all()
        assert len(entries) == 1
        assert entries[0].summary == "Updated summary"
    
    def test_get_valid_cache_returns_summary(self, db_session):
        """Test getting a valid cached summary."""
        save_cache(db_session, "https://example.com/article", "Cached summary")
        
        result = get_valid_cache(db_session, "https://example.com/article")
        
        assert result == "Cached summary"
    
    def test_get_valid_cache_returns_none_for_expired(self, db_session):
        """Test that expired cache returns None."""
        # Save with negative TTL to make it expired
        entry = NewsCache(
            url="https://example.com/expired",
            summary="Expired summary",
            expire_at=datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=1)
        )
        db_session.add(entry)
        db_session.commit()
        
        result = get_valid_cache(db_session, "https://example.com/expired")
        
        assert result is None
    
    def test_get_valid_cache_returns_none_for_missing(self, db_session):
        """Test that missing URL returns None."""
        result = get_valid_cache(db_session, "https://nonexistent.com/article")
        
        assert result is None
    
    def test_cleanup_expired_cache(self, db_session):
        """Test cleanup removes only expired entries."""
        # Add valid entry
        save_cache(db_session, "https://example.com/valid", "Valid summary")
        
        # Add expired entry
        expired_entry = NewsCache(
            url="https://example.com/expired",
            summary="Expired",
            expire_at=datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=1)
        )
        db_session.add(expired_entry)
        db_session.commit()
        
        cleanup_expired_cache(db_session)
        
        # Valid entry should remain
        valid = db_session.query(NewsCache).filter(NewsCache.url == "https://example.com/valid").first()
        assert valid is not None
        
        # Expired entry should be removed
        expired = db_session.query(NewsCache).filter(NewsCache.url == "https://example.com/expired").first()
        assert expired is None
