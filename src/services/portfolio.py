from typing import Optional
from collections import defaultdict
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from src.database.models import Asset, Transaction, Holding, NewsCache, AssetType, RecordStatus
from src.schemas.transactions import TransactionCreate, TransactionAction
from src.schemas.portfolio import PortfolioSummary, SectorAllocation
from src.services.market_data import get_historical_fx_rate, get_current_price
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from fastapi import HTTPException
import yfinance as yf

def calculate_new_acb(old_qty: Decimal, old_acb: Decimal, tx_qty: Decimal, tx_total_base: Decimal) -> Decimal:
    """
    Calculate new Average Cost Basis after a BUY transaction.
    """
    if old_qty + tx_qty == 0:
        return Decimal("0")
    old_total_cost = old_qty * old_acb
    new_total_cost = old_total_cost + tx_total_base
    return new_total_cost / (old_qty + tx_qty)

def calculate_gain_loss(total_value: Decimal, total_cost: Decimal) -> tuple[Decimal, Decimal]:
    """
    Calculate gain/loss in USD and percentage.
    """
    gain_loss_usd = total_value - total_cost
    gain_loss_pct = (gain_loss_usd / total_cost * 100) if total_cost > 0 else Decimal("0")
    return gain_loss_usd, gain_loss_pct

def calculate_daily_pnl(current_value: Decimal, start_of_day_value: Decimal, net_cash_flow: Decimal) -> tuple[Decimal, Decimal]:
    """
    Calculate daily PNL in USD and percentage.
    Daily PNL = Current_Value - (Value_At_Start_Of_Day + Net_Cash_Flow_Today)
    """
    daily_pnl_usd = current_value - (start_of_day_value + net_cash_flow)
    daily_pnl_pct = (daily_pnl_usd / start_of_day_value * 100) if start_of_day_value > 0 else Decimal("0")
    return daily_pnl_usd, daily_pnl_pct

def process_transactions_chronologically(transactions: list[Transaction]) -> tuple[Decimal, Decimal]:
    """
    Process a list of transactions to calculate final quantity and ACB.
    Enforces strict consistency (no negative holdings at any point).
    """
    qty = Decimal("0")
    total_cost_base = Decimal("0")
    
    for t in transactions:
        if t.action == TransactionAction.BUY:
            qty += t.quantity
            total_cost_base += t.total_base
        else:
            # SELL
            if qty < t.quantity:
                raise HTTPException(status_code=400, detail=f"Consistency error: Transaction at {t.date} results in negative holdings (Owned: {qty}, Sell: {t.quantity})")
            
            # ACB doesn't change on sell, but total_cost does (proportionally)
            if qty > 0:
                avg_cost = total_cost_base / qty
                qty -= t.quantity
                total_cost_base = qty * avg_cost
            else:
                qty = Decimal("0")
                total_cost_base = Decimal("0")
    
    final_acb = (total_cost_base / qty) if qty > 0 else Decimal("0")
    return qty, final_acb

async def get_or_create_asset(db: AsyncSession, user_id: str, symbol: str, asset_type: AssetType = AssetType.STOCK, name: str = None) -> Asset:
    stmt = select(Asset).where(Asset.user_id == user_id, Asset.symbol == symbol)
    result = await db.execute(stmt)
    asset = result.scalar_one_or_none()
    if not asset:
        asset = Asset(user_id=user_id, symbol=symbol, type=asset_type, name=name or symbol)
        db.add(asset)
        await db.flush() # Ensure asset has an ID
    return asset

async def create_transaction(db: AsyncSession, user_id: str, t_data: TransactionCreate) -> Transaction:
    """
    Implement Transaction Creation with Strict Consistency.
    - Fetch historical FX rate.
    - Normalize to USD.
    - Row-level lock on Holding.
    - Update Holding (ACB for BUY, quantity for SELL).
    """
    # 1. Fetch historical FX rate for transaction date
    t_date = t_data.date or datetime.now(timezone.utc).replace(tzinfo=None)
    fx_rate = await get_historical_fx_rate(db, t_data.currency, "USD", t_date.date())
    
    # 2. Normalize price and fees to USD base currency
    price_base = t_data.price_per_share * fx_rate
    # Total cost in base currency (price + fees) for BUY
    # Total proceeds in base currency (price - fees) for SELL
    total_fees_base = (t_data.commission + t_data.tax) * fx_rate
    
    if t_data.action == TransactionAction.BUY:
        total_base = (t_data.quantity * price_base) + total_fees_base
    else:
        total_base = (t_data.quantity * price_base) - total_fees_base

    # 3. Use SELECT FOR UPDATE to lock the user's holding for that asset
    stmt = (
        select(Holding)
        .where(Holding.user_id == user_id, Holding.asset_id == t_data.asset_id)
        .with_for_update()
    )
    result = await db.execute(stmt)
    holding = result.scalar_one_or_none()

    if not holding:
        if t_data.action == TransactionAction.SELL:
            raise HTTPException(status_code=400, detail="Insufficient quantity to sell (no holding found)")
        # Create new holding for BUY
        holding = Holding(user_id=user_id, asset_id=t_data.asset_id, quantity_held=Decimal("0"), avg_cost_basis=Decimal("0"))
        db.add(holding)

    # 4. Strict Consistency check for SELL
    if t_data.action == TransactionAction.SELL:
        if holding.quantity_held < t_data.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient quantity to sell. Owned: {holding.quantity_held}, Requested: {t_data.quantity}")
        
        # Update Holding quantity
        holding.quantity_held -= t_data.quantity
        # ACB does not change on sell
    else:
        # BUY: Update New_Avg_Cost = (Old_Total_Cost + New_Total_Cost_USD) / (Old_Qty + New_Qty)
        holding.avg_cost_basis = calculate_new_acb(holding.quantity_held, holding.avg_cost_basis, t_data.quantity, total_base)
        holding.quantity_held += t_data.quantity

    # 5. Create Transaction record
    transaction = Transaction(
        user_id=user_id,
        asset_id=t_data.asset_id,
        action=t_data.action,
        quantity=t_data.quantity,
        price_per_share=t_data.price_per_share,
        commission=t_data.commission,
        tax=t_data.tax,
        currency=t_data.currency,
        fx_rate=fx_rate,
        price_base=price_base,
        total_base=total_base,
        date=t_date,
        asset_metadata=t_data.asset_metadata.model_dump(mode='json') if t_data.asset_metadata else None
    )
    db.add(transaction)
    
    return transaction

async def get_holdings(db: AsyncSession, user_id: str):
    """
    Retrieve holdings for a user.
    """
    stmt = select(Holding).where(Holding.user_id == user_id, Holding.quantity_held > 0)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_transactions(db: AsyncSession, user_id: str, asset_id: Optional[int] = None, limit: int = 20, offset: int = 0):
    stmt = select(Transaction).where(Transaction.user_id == user_id, Transaction.status == RecordStatus.ACTIVE)
    if asset_id:
        stmt = stmt.where(Transaction.asset_id == asset_id)
    stmt = stmt.order_by(Transaction.date.desc()).limit(limit).offset(offset)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_transaction(db: AsyncSession, user_id: str, transaction_id: int) -> Optional[Transaction]:
    stmt = select(Transaction).where(Transaction.user_id == user_id, Transaction.id == transaction_id, Transaction.status == RecordStatus.ACTIVE)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def delete_transaction(db: AsyncSession, user_id: str, transaction_id: int):
    """
    Soft-delete transaction and revert impact on Holding.
    For simplicity, we'll recalculate the whole holding from scratch after deletion.
    """
    transaction = await get_transaction(db, user_id, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    transaction.status = RecordStatus.INACTIVE
    await db.flush()
    
    # Recalculate holding for this asset
    await recalculate_holding(db, user_id, transaction.asset_id)
    return transaction

async def recalculate_holding(db: AsyncSession, user_id: str, asset_id: int):
    """
    Recalculates Holding (quantity and ACB) for a specific asset by re-processing
    all non-deleted transactions in chronological order.
    """
    # Lock the holding
    stmt_lock = select(Holding).where(Holding.user_id == user_id, Holding.asset_id == asset_id).with_for_update()
    result_lock = await db.execute(stmt_lock)
    holding = result_lock.scalar_one_or_none()
    
    if not holding:
        holding = Holding(user_id=user_id, asset_id=asset_id, quantity_held=Decimal("0"), avg_cost_basis=Decimal("0"))
        db.add(holding)

    # Get all active transactions for this asset ordered by date
    stmt_tx = (
        select(Transaction)
        .where(Transaction.user_id == user_id, Transaction.asset_id == asset_id, Transaction.status == RecordStatus.ACTIVE)
        .order_by(Transaction.date.asc())
    )
    result_tx = await db.execute(stmt_tx)
    transactions = result_tx.scalars().all()
    
    qty, final_acb = process_transactions_chronologically(transactions)
    
    holding.quantity_held = qty
    holding.avg_cost_basis = final_acb
    await db.flush()

async def get_portfolio_summary(db: AsyncSession, user_id: str) -> PortfolioSummary:
    """
    Calculate the overall portfolio summary for a user.
    """
    # 1. Get all holdings for the user
    stmt = (
        select(Holding)
        .options(selectinload(Holding.asset))
        .where(Holding.user_id == user_id, Holding.quantity_held > 0)
    )
    result_holdings = await db.execute(stmt)
    holdings = result_holdings.scalars().all()
    
    total_value_usd = Decimal("0")
    total_cost_basis_usd = Decimal("0")
    sector_values = defaultdict(Decimal)
    
    # For Daily PNL
    net_cash_flow_today = Decimal("0")
    # Fetch today's transactions
    today = datetime.now(timezone.utc).replace(tzinfo=None).date()
    stmt_tx_today = (
        select(Transaction)
        .where(
            Transaction.user_id == user_id, 
            Transaction.status == RecordStatus.ACTIVE,
            func.date(Transaction.date) == today
        )
    )
    result_tx_today = await db.execute(stmt_tx_today)
    tx_today = result_tx_today.scalars().all()
    for tx in tx_today:
        # For cash flow, we want the net amount of money put in/taken out
        if tx.action == TransactionAction.BUY:
            net_cash_flow_today += tx.total_base
        else:
            net_cash_flow_today -= tx.total_base

    value_at_start_of_day = Decimal("0")

    for h in holdings:
        asset = h.asset
        current_price = await get_current_price(db, asset)
        
        current_val = h.quantity_held * current_price
        total_value_usd += current_val
        total_cost_basis_usd += h.quantity_held * h.avg_cost_basis
        
        # Sector allocation
        sector = asset.sector or "Unknown"
        sector_values[sector] += current_val
        
        # Calculate Value_At_Start_Of_Day for this asset
        # Net Qty today for this asset
        asset_net_qty_today = Decimal("0")
        for tx in tx_today:
            if tx.asset_id == asset.id:
                if tx.action == TransactionAction.BUY:
                    asset_net_qty_today += tx.quantity
                else:
                    asset_net_qty_today -= tx.quantity
        
        qty_at_start = h.quantity_held - asset_net_qty_today
        
        # Try to get yesterday's price
        yesterday_price = current_price # Default
        if asset.type == AssetType.STOCK:
            try:
                ticker = yf.Ticker(asset.symbol)
                # Get last 2 days to be sure to have yesterday's close
                hist = ticker.history(period="2d")
                if len(hist) >= 2:
                    yesterday_price = Decimal(str(hist['Close'].iloc[-2]))
                elif not hist.empty:
                    yesterday_price = Decimal(str(hist['Close'].iloc[0]))
            except Exception:
                pass
        
        value_at_start_of_day += qty_at_start * yesterday_price

    total_gain_loss_usd, total_gain_loss_pct = calculate_gain_loss(total_value_usd, total_cost_basis_usd)
    daily_pnl_usd, daily_pnl_pct = calculate_daily_pnl(total_value_usd, value_at_start_of_day, net_cash_flow_today)
    
    # Sector allocation formatting
    sector_allocation = []
    if total_value_usd > 0:
        for sector, val in sector_values.items():
            sector_allocation.append(SectorAllocation(
                sector=sector,
                value_usd=val,
                percentage=(val / total_value_usd * 100)
            ))
    
    return PortfolioSummary(
        total_value_usd=total_value_usd,
        total_cost_basis_usd=total_cost_basis_usd,
        total_gain_loss_usd=total_gain_loss_usd,
        total_gain_loss_pct=total_gain_loss_pct,
        daily_pnl_usd=daily_pnl_usd,
        daily_pnl_pct=daily_pnl_pct,
        sector_allocation=sector_allocation
    )

async def get_valid_cache(db: AsyncSession, url: str) -> Optional[str]:
    stmt = select(NewsCache).where(NewsCache.url == url)
    result = await db.execute(stmt)
    entry = result.scalar_one_or_none()
    if entry and entry.expire_at > datetime.now(timezone.utc).replace(tzinfo=None):
        return entry.summary
    return None

async def save_cache(db: AsyncSession, url: str, summary: str, expire_at: Optional[datetime] = None, ttl_hours: int = 168):
    if expire_at is None:
        expire_at = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=ttl_hours)

    stmt = select(NewsCache).where(NewsCache.url == url)
    result = await db.execute(stmt)
    entry = result.scalar_one_or_none()
    if entry:
        entry.summary = summary
        entry.expire_at = expire_at
    else:
        entry = NewsCache(url=url, summary=summary, expire_at=expire_at)
        db.add(entry)
    await db.commit()
