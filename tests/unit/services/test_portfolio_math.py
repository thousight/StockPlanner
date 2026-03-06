from decimal import Decimal
from hypothesis import given, strategies as st
from src.services.portfolio import (
    calculate_new_acb,
    calculate_gain_loss,
    calculate_daily_pnl,
    process_transactions_chronologically
)
from src.database.models import Transaction
from src.schemas.transactions import TransactionAction
from fastapi import HTTPException

# Strategies for decimals
# Most financial values in the app use precision=20, scale=10
# We'll use a reasonable range for tests to avoid overflows or astronomical numbers
# while still catching edge cases like zero.
st_decimal = st.decimals(min_value=0, max_value=1_000_000_000, places=10)
st_decimal_signed = st.decimals(min_value=-1_000_000_000, max_value=1_000_000_000, places=10)

@given(
    old_qty=st_decimal,
    old_acb=st_decimal,
    tx_qty=st_decimal,
    tx_total_base=st_decimal
)
def test_calculate_new_acb_hypothesis(old_qty, old_acb, tx_qty, tx_total_base):
    # If total quantity is zero, it should return 0
    if old_qty + tx_qty == 0:
        assert calculate_new_acb(old_qty, old_acb, tx_qty, tx_total_base) == Decimal("0")
    else:
        new_acb = calculate_new_acb(old_qty, old_acb, tx_qty, tx_total_base)
        # new_acb = (old_qty * old_acb + tx_total_base) / (old_qty + tx_qty)
        expected = (old_qty * old_acb + tx_total_base) / (old_qty + tx_qty)
        assert new_acb == expected

@given(
    total_value=st_decimal,
    total_cost=st_decimal
)
def test_calculate_gain_loss_hypothesis(total_value, total_cost):
    gain_loss_usd, gain_loss_pct = calculate_gain_loss(total_value, total_cost)
    
    assert gain_loss_usd == total_value - total_cost
    if total_cost > 0:
        assert gain_loss_pct == (gain_loss_usd / total_cost * 100)
    else:
        assert gain_loss_pct == Decimal("0")

@given(
    current_value=st_decimal,
    start_of_day_value=st_decimal,
    net_cash_flow=st_decimal_signed
)
def test_calculate_daily_pnl_hypothesis(current_value, start_of_day_value, net_cash_flow):
    daily_pnl_usd, daily_pnl_pct = calculate_daily_pnl(current_value, start_of_day_value, net_cash_flow)
    
    assert daily_pnl_usd == current_value - (start_of_day_value + net_cash_flow)
    if start_of_day_value > 0:
        assert daily_pnl_pct == (daily_pnl_usd / start_of_day_value * 100)
    else:
        assert daily_pnl_pct == Decimal("0")

def mock_transaction(action, quantity, total_base):
    return Transaction(
        action=action,
        quantity=quantity,
        total_base=total_base,
        date=None # Not used in math but required by model if we were saving
    )

@given(
    transactions_data=st.lists(
        st.tuples(
            st.sampled_from([TransactionAction.BUY, TransactionAction.SELL]),
            st.decimals(min_value=0, max_value=1_000_000, places=10), # Quantity >= 0
            st.decimals(min_value=0, max_value=1_000_000_000, places=10) # total_base
        ),
        min_size=0,
        max_size=20
    )
)
def test_process_transactions_chronologically_hypothesis(transactions_data):
    transactions = [mock_transaction(action, qty, total) for action, qty, total in transactions_data]
    
    # We expect some sequences to fail with 400 if they result in negative holdings
    try:
        qty, final_acb = process_transactions_chronologically(transactions)
        
        # If it succeeds:
        assert qty >= 0
        if qty == 0:
            assert final_acb == 0
        else:
            assert final_acb >= 0
            
        # Manual verification of final quantity
        expected_qty = Decimal("0")
        for t in transactions:
            if t.action == TransactionAction.BUY:
                expected_qty += t.quantity
            else:
                expected_qty -= t.quantity
        assert qty == expected_qty
        
    except HTTPException as e:
        assert e.status_code == 400
        assert "negative holdings" in e.detail

def test_process_transactions_empty():
    qty, final_acb = process_transactions_chronologically([])
    assert qty == 0
    assert final_acb == 0

def test_process_transactions_sell_to_zero():
    txs = [
        mock_transaction(TransactionAction.BUY, Decimal("10"), Decimal("100")),
        mock_transaction(TransactionAction.SELL, Decimal("10"), Decimal("150"))
    ]
    qty, final_acb = process_transactions_chronologically(txs)
    assert qty == 0
    assert final_acb == 0

def test_process_transactions_multiple_buys():
    txs = [
        mock_transaction(TransactionAction.BUY, Decimal("10"), Decimal("100")), # ACB 10
        mock_transaction(TransactionAction.BUY, Decimal("10"), Decimal("200"))  # (100+200)/20 = 15
    ]
    qty, final_acb = process_transactions_chronologically(txs)
    assert qty == 20
    assert final_acb == 15

def test_process_transactions_sell_partial():
    txs = [
        mock_transaction(TransactionAction.BUY, Decimal("10"), Decimal("100")), # ACB 10
        mock_transaction(TransactionAction.SELL, Decimal("5"), Decimal("75"))   # Qty 5, ACB 10
    ]
    qty, final_acb = process_transactions_chronologically(txs)
    assert qty == 5
    assert final_acb == 10
