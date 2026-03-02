import enum
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Date, Text, Numeric, Enum, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from src.database.session import Base

class AssetType(enum.Enum):
    STOCK = "STOCK"
    REAL_ESTATE = "REAL_ESTATE"
    FUND = "FUND"
    METAL = "METAL"
    GENERIC = "GENERIC"

class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    symbol = Column(String, index=True, nullable=True)
    name = Column(String)
    type = Column(Enum(AssetType), default=AssetType.STOCK)
    sector = Column(String, nullable=True)
    industry = Column(String, nullable=True)
    
    transactions = relationship("Transaction", back_populates="asset")
    daily_snapshots = relationship("DailySnapshot", back_populates="asset")
    holdings = relationship("Holding", back_populates="asset")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    asset_id = Column(Integer, ForeignKey("assets.id"))
    action = Column(String)  # BUY, SELL
    quantity = Column(Numeric(precision=20, scale=10))
    price_per_share = Column(Numeric(precision=20, scale=10))
    commission = Column(Numeric(precision=20, scale=10), default=0.0)
    tax = Column(Numeric(precision=20, scale=10), default=0.0)
    currency = Column(String(3), default="USD")
    fx_rate = Column(Numeric(precision=20, scale=10), default=1.0)
    price_base = Column(Numeric(precision=20, scale=10))
    total_base = Column(Numeric(precision=20, scale=10))
    asset_metadata = Column(JSONB, nullable=True)
    is_deleted = Column(Boolean, default=False)
    
    asset = relationship("Asset", back_populates="transactions")

class Holding(Base):
    __tablename__ = "holdings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"))
    quantity_held = Column(Numeric(precision=20, scale=10), default=0.0)
    avg_cost_basis = Column(Numeric(precision=20, scale=10), default=0.0)
    
    asset = relationship("Asset", back_populates="holdings")

class DailySnapshot(Base):
    __tablename__ = "daily_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    date = Column(Date, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"))
    quantity_held = Column(Numeric(precision=20, scale=10))
    avg_cost_basis = Column(Numeric(precision=20, scale=10))
    market_price = Column(Numeric(precision=20, scale=10))
    total_value = Column(Numeric(precision=20, scale=10))
    
    asset = relationship("Asset", back_populates="daily_snapshots")

class FXRate(Base):
    __tablename__ = "fx_rates"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(3))
    target = Column(String(3))
    rate = Column(Numeric(precision=20, scale=10))
    date = Column(Date, index=True)

class NewsCache(Base):
    __tablename__ = "news_cache"

    url = Column(String, primary_key=True, index=True)
    summary = Column(Text)
    expire_at = Column(DateTime)

class ChatThread(Base):
    __tablename__ = "chat_threads"

    id = Column(String, primary_key=True, index=True) # UUID as string
    user_id = Column(String, index=True)
    title = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    is_deleted = Column(Boolean, default=False)

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    thread_id = Column(String, index=True)
    symbol = Column(String, index=True)
    content = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
