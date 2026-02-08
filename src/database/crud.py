from sqlalchemy.orm import Session
from sqlalchemy import func
from .models import Transaction, Stock, DailySnapshot
from datetime import datetime

def add_stock(db: Session, symbol: str, name: str = None, sector: str = None):
    stock = db.query(Stock).filter(Stock.symbol == symbol).first()
    if not stock:
        stock = Stock(symbol=symbol, name=name, sector=sector)
        db.add(stock)
        db.commit()
    return stock

def add_transaction(db: Session, symbol: str, action: str, quantity: float, price: float, date: datetime = None, fees: float = 0.0):
    # Ensure stock exists
    add_stock(db, symbol)
    
    if date is None:
        date = datetime.utcnow()
        
    transaction = Transaction(
        symbol=symbol,
        action=action,
        quantity=quantity,
        price_per_share=price,
        date=date,
        fees=fees
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction

def get_holdings(db: Session):
    """
    Calculate current holdings based on all transactions.
    Returns a dict {symbol: {'quantity': float, 'avg_cost': float}}
    Note: This is a simplified FIFO/Average Cost calculation.
    """
    transactions = db.query(Transaction).order_by(Transaction.date).all()
    portfolio = {}

    for t in transactions:
        if t.symbol not in portfolio:
            portfolio[t.symbol] = {'quantity': 0.0, 'total_cost': 0.0}
        
        pos = portfolio[t.symbol]
        
        if t.action == "BUY":
            pos['quantity'] += t.quantity
            pos['total_cost'] += (t.quantity * t.price_per_share) + t.fees
        elif t.action == "SELL":
            # For selling, we reduce quantity. 
            # Cost basis reduction depends on accounting method. 
            # Using average cost:
            if pos['quantity'] > 0:
                avg_cost = pos['total_cost'] / pos['quantity']
                pos['quantity'] -= t.quantity
                pos['total_cost'] -= (t.quantity * avg_cost) # Reduce cost proportionally
            else:
                # Short selling logic or error? Assuming long only for MVP
                pos['quantity'] -= t.quantity
    
    # Clean up zero holdings
    results = []
    for symbol, data in portfolio.items():
        if data['quantity'] > 0.0001:
            avg_cost = data['total_cost'] / data['quantity']
            results.append({
                "symbol": symbol,
                "quantity": data['quantity'],
                "avg_cost": avg_cost,
                "total_cost": data['total_cost']
            })
            
    return results

def get_transactions(db: Session, symbol: str = None):
    query = db.query(Transaction)
    if symbol:
        query = query.filter(Transaction.symbol == symbol)
    return query.order_by(Transaction.date.desc()).all()
