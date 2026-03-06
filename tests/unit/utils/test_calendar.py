import pytest
from datetime import date
from src.graph.utils.calendar import get_previous_trading_day

def test_get_previous_trading_day_normal():
    # Thursday, March 5, 2026 -> Wednesday, March 4
    target = date(2026, 3, 5)
    prev = get_previous_trading_day(target)
    assert prev == date(2026, 3, 4)

def test_get_previous_trading_day_weekend():
    # Monday, March 2, 2026 -> Friday, Feb 27
    target = date(2026, 3, 2)
    prev = get_previous_trading_day(target)
    assert prev == date(2026, 2, 27)

def test_get_previous_trading_day_holiday():
    # Day after New Year 2026 (Friday, Jan 2) -> Thursday, Dec 31
    # Actually Jan 1 is a holiday. Jan 2 is a Friday.
    target = date(2026, 1, 2)
    prev = get_previous_trading_day(target)
    assert prev == date(2025, 12, 31)

def test_get_previous_trading_day_on_holiday():
    # Jan 1, 2026 itself -> Dec 31, 2025
    target = date(2026, 1, 1)
    prev = get_previous_trading_day(target)
    assert prev == date(2025, 12, 31)
