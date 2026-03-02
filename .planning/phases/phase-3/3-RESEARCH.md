# Phase 3: Financial APIs - Research

**Researched:** 2026-02-28
**Domain:** Financial Data Engineering, Portfolio Analytics, Multi-Currency Accounting
**Confidence:** HIGH

## Summary

Phase 3 transitions the StockPlanner backend into a production-grade financial engine. Research confirms that multi-currency "Average Cost Basis" (ACB) must be tracked in a unified base currency (USD) using historical exchange rates at the time of each transaction to ensure accurate capital gains reporting. For data integrity, "Strict Consistency" (preventing overselling) is best enforced via a dedicated `holdings` table with a Postgres `CHECK (quantity >= 0)` constraint combined with `SELECT ... FOR UPDATE` row-level locking in SQLAlchemy.

Benchmarking against the S&P 500 (SPY) should utilize a "Fetch-if-Missing" pattern with Alpaca Markets as the primary data source and a local Postgres table for caching. Polymorphic asset metadata (Real Estate vs. Stocks) is most effectively handled using Pydantic v2 Discriminated Unions mapped to PostgreSQL `JSONB` columns via custom SQLAlchemy `TypeDecorator` patterns.

**Primary recommendation:** Use a dedicated `holdings` table for real-time validation and a `daily_snapshots` table for historical performance tracking to keep the analytics API (`GET /investment`) high-performing.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **Fractional Support:** Support fractional shares (e.g., 0.0001) for all asset types.
- **Fee Granularity:** Explicit fields for `commission` and `tax`.
- **Multi-Currency:** Base: USD. Fallback: nearest available date's rate. No manual rate overrides.
- **Response Depth:** Return both original currency/value and converted base value.
- **Price Validation:** Active validation against market data (yfinance/alpaca).
- **Cost Basis:** Use **Average Cost** method for all calculations.
- **Benchmarking:** Compare against S&P 500 (SPY).
- **Asset Metadata:** 
  - Real Estate: Type, Address, Purchase Price.
  - Private Equity: Commitment Date, Vintage Year.
  - Metals: Simple Quantity.
- **Data Integrity:** Enforce **Strict Consistency**. Reject SELL if insufficient BUY history.
- **Soft Deletion:** Required for all records.

### Claude's Discretion
- Implementation of the SQL/ORM pattern for Daily Change.
- Specific implementation of the Multi-currency ACB formula.
- Choice of benchmarking data source and caching strategy.
- Selection of locking mechanisms for consistency.

### Deferred Ideas (OUT OF SCOPE)
- Searchable descriptions (descriptions are view-only metadata).
- Non-stock pricing APIs (rely on last transaction price for now).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| REQ-021 | Portfolio Analytics API (`GET /investment`) | SQL Window Functions (`LAG`) over daily snapshots with cash-flow adjustment. |
| REQ-022 | Transaction CRUD (`/investment/transactions`) | SQLAlchemy `with_for_update()` and Pydantic polymorphic JSONB decorators. |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `alpaca-py` | ^0.30.0 | Market Data | Professional API, reliable ETF data, free tier for individuals. |
| `pydantic` | ^2.6.0 | Validation | Discriminated unions for polymorphic asset metadata. |
| `sqlalchemy` | ^2.0.0 | Async ORM | Native JSONB support and `with_for_update()` for consistency. |
| `decimal` | Built-in | Precision | Absolute requirement for fractional shares and currency. |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `py-moneyed` | ^3.0.0 | Currency Logic | Optional but useful for ISO currency handling. |
| `pandas` | ^2.2.0 | Benchmarking | Efficiently calculating % change and normalization for SPY. |

**Installation:**
```bash
pip install alpaca-py pydantic[email] sqlalchemy[asyncio] asyncpg
```

## Architecture Patterns

### Recommended Project Structure
```
src/
├── schemas/
│   ├── transactions/      # Polymorphic Pydantic models (Real Estate, Stocks, etc.)
│   └── analytics/         # Response schemas for portfolio metrics
├── services/
│   ├── portfolio.py       # ACB and Daily Change calculation logic
│   ├── market_data.py     # Alpaca integration and SPY caching
│   └── validation.py      # Price validation against market data
└── database/
    ├── decorators.py      # PydanticType for JSONB mapping
    └── models.py          # Updated models (Asset, Transaction, Holding, Snapshot)
```

### Pattern 1: Multi-Currency Average Cost Basis (ACB)
**Formula:**
- `Transaction_Cost_USD = (Quantity * Price_Foreign + Fees_Foreign) * FX_Rate_Date`
- `New_Avg_Cost_USD = (Total_Cost_USD_Pre + Transaction_Cost_USD) / Total_Shares_Pre + Quantity` (for BUYS)
- `Sale_Proceeds_USD = (Quantity * Price_Foreign - Fees_Foreign) * FX_Rate_Date`
- `Capital_Gain_USD = Sale_Proceeds_USD - (Quantity * Current_Avg_Cost_USD)`

### Pattern 2: Strict Consistency with Row-Level Locking
Use a `holdings` table to track current balances.
```python
# Source: Verified SQLAlchemy 2.0 Pattern
async with session.begin():
    # Lock the holding record for this user and symbol
    stmt = select(Holding).where(Holding.symbol == symbol).with_for_update()
    result = await session.execute(stmt)
    holding = result.scalar_one_or_none()
    
    if action == "SELL" and (not holding or holding.quantity < sell_qty):
        raise InsufficientFundsException()
```

### Anti-Patterns to Avoid
- **Floating Point Math:** Never use `float` for currency or quantities. Use `Decimal` or `NUMERIC`.
- **Global ACB:** Calculating ACB across multiple currencies without normalizing to USD first.
- **Unadjusted Daily Change:** Comparing `Total_Value_Today` vs `Total_Value_Yesterday` without subtracting `Net_Cash_Flow` (leads to fake gains/losses).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Currency Logic | Custom Currency Strings | ISO 4217 Codes | Standards prevent "USD" vs "usd" vs "$" bugs. |
| Fractional Shares | Int-based scaling | Python `Decimal` | Handles arbitrary precision (0.0001) natively. |
| JSON Validation | Manual `dict` checks | Pydantic Discriminated Unions | Type-safe, high-performance, and standard in FastAPI. |
| Date Math | Manual string parsing | `datetime.date` + `relativedatetime` | Handles leap years, timezones, and business days correctly. |

## Common Pitfalls

### Pitfall 1: Cash Flow Distortion
**What goes wrong:** A $5,000 deposit is reported as a 20% "gain" in a $25,000 portfolio.
**How to avoid:** Use the formula: `Market_Move = End_Value - (Begin_Value + Net_Cash_Flow)`.
**Warning signs:** Portfolio charts showing massive vertical spikes that coincide with deposits.

### Pitfall 2: Concurrent Sell Race Conditions
**What goes wrong:** Two simultaneous SELL requests both check the balance, see it as sufficient, and both succeed, leaving the user with a negative balance.
**How to avoid:** Use `SELECT ... FOR UPDATE` in a transaction or a database `CHECK (quantity >= 0)` constraint on a summary table.

### Pitfall 3: Missing Historical FX Rates
**What goes wrong:** API fails if a transaction happened on a holiday when FX markets were closed.
**How to avoid:** Implement "Nearest available date" fallback logic (e.g., `ORDER BY date DESC LIMIT 1`).

## Code Examples

### Pydantic JSONB Type Decorator
```python
# Source: Standard SQLAlchemy 2.0 / Pydantic v2 Integration
class PydanticType(TypeDecorator):
    impl = JSONB
    def __init__(self, pydantic_model):
        super().__init__()
        self.pydantic_model = pydantic_model
    def process_bind_param(self, value, dialect):
        return value.model_dump(mode='json') if value else None
    def process_result_value(self, value, dialect):
        return self.pydantic_model.model_validate(value) if value else None
```

### Daily Change SQL (Window Function)
```sql
-- Source: Performance-optimized PostgreSQL
WITH daily_stats AS (
    SELECT 
        date,
        total_value,
        COALESCE(net_cash_flow, 0) as cash_flow,
        LAG(total_value) OVER (ORDER BY date) as prev_value
    FROM daily_snapshots
)
SELECT 
    date,
    (total_value - (COALESCE(prev_value, total_value) + cash_flow)) as daily_pnl
FROM daily_stats;
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| yfinance | Alpaca Markets / Polygon | 2023 | More reliable API-first data vs fragile scraping. |
| Manual Rate Entry | Automated FX Integration | - | Prevents user error and ensures USD consistency. |
| Local SQL Logic | DB-level Constraints | - | Guaranteed integrity even with multiple API workers. |

## Open Questions

1. **How to handle non-stock prices for real-time analytics?**
   - What we know: We rely on the last transaction price for now.
   - What's unclear: How to provide meaningful "Daily Change" for real estate without daily appraisals.
   - Recommendation: For non-liquid assets, report "Daily Change" as 0 unless a new transaction/appraisal is recorded.

## Sources

### Primary (HIGH confidence)
- [SQLAlchemy 2.0 Docs] - `with_for_update` and `TypeDecorator` patterns.
- [Pydantic v2 Docs] - Discriminated Unions and `model_dump`.
- [Alpaca Markets API] - Market data fetching and rate limits.

### Secondary (MEDIUM confidence)
- [Investopedia / Financial Wisdom] - ACB multi-currency formulas.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Industry standards for FastAPI/SQLAlchemy.
- Architecture: HIGH - Proven financial accounting patterns.
- Pitfalls: HIGH - Common "Money & Code" traps documented.

**Research date:** 2026-02-28
**Valid until:** 2026-05-28
