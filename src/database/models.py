from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Stock(Base):
    __tablename__ = "stocks"

    symbol = Column(String, primary_key=True, index=True)
    name = Column(String)
    sector = Column(String)
    industry = Column(String)
    
    transactions = relationship("Transaction", back_populates="stock")
    daily_snapshots = relationship("DailySnapshot", back_populates="stock")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.utcnow)
    symbol = Column(String, ForeignKey("stocks.symbol"))
    action = Column(String)  # BUY, SELL
    quantity = Column(Float)
    price_per_share = Column(Float)
    fees = Column(Float, default=0.0)
    
    stock = relationship("Stock", back_populates="transactions")

class DailySnapshot(Base):
    __tablename__ = "daily_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True)
    symbol = Column(String, ForeignKey("stocks.symbol"))
    quantity_held = Column(Float)
    avg_cost_basis = Column(Float)
    market_price = Column(Float)
    total_value = Column(Float)
    
    stock = relationship("Stock", back_populates="daily_snapshots")
