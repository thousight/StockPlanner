from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from src.database.session import get_db
from src.schemas.transactions import TransactionCreate, TransactionRead, TransactionAction
from src.services.portfolio import (
    create_transaction, 
    get_transactions, 
    delete_transaction, 
    get_transaction, 
    recalculate_holding
)
from src.database.models import Asset
from src.services.market_data import get_historical_fx_rate

router = APIRouter(prefix="/investment/transactions", tags=["transactions"])

@router.post("", response_model=TransactionRead)
async def add_transaction_endpoint(
    t_data: TransactionCreate, 
    db: AsyncSession = Depends(get_db),
    x_user_id: str = Header(..., alias="X-User-ID")
):
    """
    Create a new transaction.
    """
    # Check if asset exists
    asset = await db.get(Asset, t_data.asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset ID {t_data.asset_id} not found")

    try:
        new_tx = await create_transaction(db, x_user_id, t_data)
        await db.commit()
        await db.refresh(new_tx)
        return new_tx
    except HTTPException as e:
        await db.rollback()
        raise e
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("", response_model=List[TransactionRead])
async def list_transactions_endpoint(
    asset_id: Optional[int] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    x_user_id: str = Header(..., alias="X-User-ID")
):
    """
    List transactions with pagination and optional filtering by asset_id.
    """
    return await get_transactions(db, x_user_id, asset_id=asset_id, limit=limit, offset=offset)

@router.get("/{transaction_id}", response_model=TransactionRead)
async def read_transaction_endpoint(
    transaction_id: int, 
    db: AsyncSession = Depends(get_db),
    x_user_id: str = Header(..., alias="X-User-ID")
):
    tx = await get_transaction(db, x_user_id, transaction_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return tx

@router.delete("/{transaction_id}")
async def delete_transaction_endpoint(
    transaction_id: int, 
    db: AsyncSession = Depends(get_db),
    x_user_id: str = Header(..., alias="X-User-ID")
):
    """
    Soft-delete a transaction and recalculate holding.
    """
    try:
        await delete_transaction(db, x_user_id, transaction_id)
        await db.commit()
        return {"status": "success", "message": "Transaction deleted and holding recalculated"}
    except HTTPException as e:
        await db.rollback()
        raise e
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{transaction_id}", response_model=TransactionRead)
async def update_transaction_endpoint(
    transaction_id: int, 
    t_data: TransactionCreate, 
    db: AsyncSession = Depends(get_db),
    x_user_id: str = Header(..., alias="X-User-ID")
):
    """
    Update a transaction's details. Requires recalculating Holding/ACB.
    """
    tx = await get_transaction(db, x_user_id, transaction_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Re-verify asset_id if changed?
    if tx.asset_id != t_data.asset_id:
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
    
    # Recalculate base values
    fx_rate = await get_historical_fx_rate(db, t_data.currency, "USD", tx.date.date())
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
        await db.flush()
        # Recalculate holding for the asset(s)
        await recalculate_holding(db, x_user_id, tx.asset_id)
        if old_asset_id:
            await recalculate_holding(db, x_user_id, old_asset_id)
        
        await db.commit()
        await db.refresh(tx)
        return tx
    except HTTPException as e:
        await db.rollback()
        raise e
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
