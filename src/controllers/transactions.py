from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

from src.database.session import get_db
from src.schemas.transactions import TransactionCreate, TransactionRead, TransactionAction
from src.services.portfolio import create_transaction, get_transactions, delete_transaction, get_transaction, recalculate_holding
from src.database.models import Transaction, Asset

router = APIRouter(prefix="/investment/transactions", tags=["transactions"])

@router.post("", response_model=TransactionRead)
def add_transaction_endpoint(t_data: TransactionCreate, db: Session = Depends(get_db)):
    """
    Create a new transaction.
    """
    # For MVP, assume user_id is hardcoded or from a header (future Phase will handle Auth)
    user_id = "default_user" 
    
    # Check if asset exists
    asset = db.get(Asset, t_data.asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset ID {t_data.asset_id} not found")

    try:
        new_tx = create_transaction(db, user_id, t_data)
        db.commit()
        db.refresh(new_tx)
        return new_tx
    except HTTPException as e:
        db.rollback()
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("", response_model=List[TransactionRead])
def list_transactions_endpoint(
    asset_id: Optional[int] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    List transactions with pagination and optional filtering by asset_id.
    """
    user_id = "default_user"
    return get_transactions(db, user_id, asset_id=asset_id, limit=limit, offset=offset)

@router.get("/{transaction_id}", response_model=TransactionRead)
def read_transaction_endpoint(transaction_id: int, db: Session = Depends(get_db)):
    user_id = "default_user"
    tx = get_transaction(db, user_id, transaction_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return tx

@router.delete("/{transaction_id}")
def delete_transaction_endpoint(transaction_id: int, db: Session = Depends(get_db)):
    """
    Soft-delete a transaction and recalculate holding.
    """
    user_id = "default_user"
    try:
        delete_transaction(db, user_id, transaction_id)
        db.commit()
        return {"status": "success", "message": "Transaction deleted and holding recalculated"}
    except HTTPException as e:
        db.rollback()
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{transaction_id}", response_model=TransactionRead)
def update_transaction_endpoint(transaction_id: int, t_data: TransactionCreate, db: Session = Depends(get_db)):
    """
    Update a transaction's details. Requires recalculating Holding/ACB.
    """
    user_id = "default_user"
    tx = get_transaction(db, user_id, transaction_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Re-verify asset_id if changed?
    if tx.asset_id != t_data.asset_id:
        # Complex case: changing the asset. 
        # We'd need to recalculate both old and new asset holdings.
        # For MVP, maybe restrict changing asset_id or handle it.
        old_asset_id = tx.asset_id
        tx.asset_id = t_data.asset_id
    else:
        old_asset_id = None

    # Update fields
    tx.action = t_data.action
    tx.quantity = t_data.quantity
    tx.price_per_share = t_data.price_per_share
    tx.commission = t_data.commission
    tx.tax = t_data.tax
    tx.currency = t_data.currency
    tx.date = t_data.date or tx.date
    
    # Recalculate base values (Task 3: this might need FX rate refresh)
    from src.services.market_data import get_historical_fx_rate
    fx_rate = get_historical_fx_rate(db, t_data.currency, "USD", tx.date.date())
    tx.fx_rate = fx_rate
    tx.price_base = t_data.price_per_share * fx_rate
    
    total_fees_base = (t_data.commission + t_data.tax) * fx_rate
    if t_data.action == TransactionAction.BUY:
        tx.total_base = (t_data.quantity * tx.price_base) + total_fees_base
    else:
        tx.total_base = (t_data.quantity * tx.price_base) - total_fees_base
    
    if t_data.asset_metadata:
        tx.asset_metadata = t_data.asset_metadata.model_dump(mode='json')

    try:
        db.flush()
        # Recalculate holding for the asset(s)
        recalculate_holding(db, user_id, tx.asset_id)
        if old_asset_id:
            recalculate_holding(db, user_id, old_asset_id)
        
        db.commit()
        db.refresh(tx)
        return tx
    except HTTPException as e:
        db.rollback()
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
