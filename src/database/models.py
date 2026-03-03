import enum
import uuid_utils as uuid7
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date, Text, Numeric, Enum, Computed, Index
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from src.database.session import Base

class RecordStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"

class UserStatus(enum.Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    DEACTIVATED = "DEACTIVATED"

class RiskTolerance(enum.Enum):
    CONSERVATIVE = "CONSERVATIVE"
    MODERATE = "MODERATE"
    AGGRESSIVE = "AGGRESSIVE"

class AssetType(enum.Enum):
    STOCK = "STOCK"
    REAL_ESTATE = "REAL_ESTATE"
    FUND = "FUND"
    METAL = "METAL"
    GENERIC = "GENERIC"

class ReportCategory(enum.Enum):
    STOCK = "STOCK"
    REAL_ESTATE = "REAL_ESTATE"
    MACRO = "MACRO"
    FUND = "FUND"
    GENERAL = "GENERAL"

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
    date = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
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
    status = Column(Enum(RecordStatus), default=RecordStatus.ACTIVE, nullable=False)
    
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

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid7.uuid7()))
    email = Column(String, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    status = Column(Enum(UserStatus), default=UserStatus.PENDING, nullable=False)
    risk_tolerance = Column(Enum(RiskTolerance), default=RiskTolerance.MODERATE, nullable=False)
    
    # Profile fields
    preferred_currency = Column(String(3), default="USD")
    timezone = Column(String, default="UTC")
    
    # Audit fields
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    last_login_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index(
            "ix_user_email_unique", 
            "email", 
            unique=True, 
            postgresql_where=(deleted_at == None)
        ),
    )

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
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    status = Column(Enum(RecordStatus), default=RecordStatus.ACTIVE, nullable=False)

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    thread_id = Column(String, index=True)
    title = Column(String, nullable=False)
    topic = Column(String, index=True, nullable=False)
    symbol = Column(String, index=True, nullable=True)
    category = Column(Enum(ReportCategory), default=ReportCategory.GENERAL, nullable=False)
    tags = Column(JSONB, nullable=True)
    content = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    search_vector = Column(
        TSVECTOR,
        Computed(
            "to_tsvector('english', coalesce(title, '') || ' ' || coalesce(topic, '') || ' ' || coalesce(content, ''))",
            persisted=True
        )
    )

    __table_args__ = (
        Index("ix_report_search_vector", "search_vector", postgresql_using="gin"),
    )
