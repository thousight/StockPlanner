from decimal import Decimal
import pytest
from src.services.portfolio import (
    calculate_new_acb, 
    calculate_gain_loss, 
    calculate_daily_pnl, 
    process_transactions_chronologically
)
from src.schemas.transactions import TransactionAction
from fastapi import HTTPException
from dataclasses import dataclass
from datetime import datetime

@dataclass
class MockTransaction:
    action: TransactionAction
    quantity: Decimal
    total_base: Decimal
    date: datetime

def test_calculate_new_acb_buy():
    # Initial state: 10 shares @ 100 ACB
    old_qty = Decimal("10")
    old_acb = Decimal("100")
    # Buy 5 shares @ 150 (total cost 750)
    tx_qty = Decimal("5")
    tx_total_base = Decimal("750")
    
    new_acb = calculate_new_acb(old_qty, old_acb, tx_qty, tx_total_base)
    # Total cost = 1000 + 750 = 1750
    # New Qty = 15
    # New ACB = 1750 / 15 = 116.666...
    assert new_acb == Decimal("1750") / Decimal("15")

def test_calculate_new_acb_zero_quantity():
    # Test division by zero when qty becomes 0
    old_qty = Decimal("0")
    old_acb = Decimal("0")
    tx_qty = Decimal("10")
    tx_total_base = Decimal("1000")
    new_acb = calculate_new_acb(old_qty, old_acb, tx_qty, tx_total_base)
    assert new_acb == Decimal("100")

def test_calculate_new_acb_division_by_zero_safety():
    # If old_qty + tx_qty == 0, it should return 0 or handle it
    assert calculate_new_acb(Decimal("-10"), Decimal("100"), Decimal("10"), Decimal("1000")) == Decimal("0")

def test_calculate_gain_loss():
    # Gain
    val, pct = calculate_gain_loss(Decimal("1200"), Decimal("1000"))
    assert val == Decimal("200")
    assert pct == Decimal("20")
    
    # Loss
    val, pct = calculate_gain_loss(Decimal("800"), Decimal("1000"))
    assert val == Decimal("-200")
    assert pct == Decimal("-20")
    
    # Zero cost
    val, pct = calculate_gain_loss(Decimal("1000"), Decimal("0"))
    assert val == Decimal("1000")
    assert pct == Decimal("0")

def test_calculate_daily_pnl():
    # Current value: 1000, start of day: 900, net cash flow: 50 (buy)
    # Expected Daily PNL = 1000 - (900 + 50) = 50
    val, pct = calculate_daily_pnl(Decimal("1000"), Decimal("900"), Decimal("50"))
    assert val == Decimal("50")
    assert pct == Decimal("50") / Decimal("900") * 100

def test_calculate_daily_pnl_zero_start_value():
    val, pct = calculate_daily_pnl(Decimal("1000"), Decimal("0"), Decimal("1000"))
    assert val == Decimal("0")
    assert pct == Decimal("0")

def test_process_transactions_consistency():
    # Valid sequence: BUY 10, SELL 5, BUY 10, SELL 10
    txs = [
        MockTransaction(TransactionAction.BUY, Decimal("10"), Decimal("1000"), datetime(2024, 1, 1)),
        MockTransaction(TransactionAction.SELL, Decimal("5"), Decimal("600"), datetime(2024, 1, 2)),
        MockTransaction(TransactionAction.BUY, Decimal("10"), Decimal("1500"), datetime(2024, 1, 3)),
        MockTransaction(TransactionAction.SELL, Decimal("10"), Decimal("1600"), datetime(2024, 1, 4)),
    ]
    
    qty, acb = process_transactions_chronologically(txs)
    assert qty == Decimal("5")
    # Step 1: Qty 10, TotalCost 1000, ACB 100
    # Step 2: Qty 5, TotalCost 500, ACB 100
    # Step 3: Qty 15, TotalCost 500 + 1500 = 2000, ACB 133.333...
    # Step 4: Qty 5, TotalCost 2000 - (10 * 133.333) = 666.666..., ACB 133.333...
    assert acb == Decimal("2000") / Decimal("15")

def test_process_transactions_out_of_order_failure():
    # Invalid sequence: BUY 10, SELL 15 (Results in -5)
    txs = [
        MockTransaction(TransactionAction.BUY, Decimal("10"), Decimal("1000"), datetime(2024, 1, 1)),
        MockTransaction(TransactionAction.SELL, Decimal("15"), Decimal("1500"), datetime(2024, 1, 2)),
    ]
    
    with pytest.raises(HTTPException) as excinfo:
        process_transactions_chronologically(txs)
    assert excinfo.value.status_code == 400
    assert "negative holdings" in excinfo.value.detail

def test_process_transactions_immediate_sell_failure():
    # Invalid sequence: SELL 10 (no prior BUY)
    txs = [
        MockTransaction(TransactionAction.SELL, Decimal("10"), Decimal("1000"), datetime(2024, 1, 1)),
    ]
    
    with pytest.raises(HTTPException) as excinfo:
        process_transactions_chronologically(txs)
    assert excinfo.value.status_code == 400
    assert "negative holdings" in excinfo.value.detail
