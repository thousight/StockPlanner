---
phase: 03-financial-apis
plan: 02
type: execute
wave: 2
depends_on: ["03-financial-apis-01"]
files_modified:
  - src/services/portfolio.py
  - src/services/market_data.py
  - src/main.py
autonomous: true
requirements: [REQ-022]

must_haves:
  truths:
    - "User cannot sell more shares than they own (strict consistency)"
    - "Transactions are normalized to USD using historical FX rates"
    - "Transaction history is paginated and filterable"
    - "Transactions can be soft-deleted"
  artifacts:
    - path: "src/services/portfolio.py"
      provides: "Transaction and ACB logic"
    - path: "src/services/market_data.py"
      provides: "FX and Market Price validation"
  key_links:
    - from: "POST /transactions"
      to: "Holding table"
      via: "SELECT FOR UPDATE"
---

<objective>
Implement the Transaction CRUD API with strict data integrity, multi-currency normalization, and market price validation.

Purpose: Ensure the portfolio remains consistent even with concurrent requests and reflects real-world market values.
Output: Transaction CRUD endpoints, ACB calculation service, and FX rate integration.
</objective>

<execution_context>
@/Users/marwen/.gemini/get-shit-done/workflows/execute-plan.md
@/Users/marwen/.gemini/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/phase-3/3-CONTEXT.md
@.planning/phases/phase-3/3-RESEARCH.md
@.planning/phases/phase-3/3-01-PLAN.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Implement Transaction Creation with Strict Consistency</name>
  <files>src/services/portfolio.py</files>
  <action>
    - Implement `create_transaction` service:
        - Fetch historical FX rate for transaction date (USD fallback logic: nearest available date).
        - Normalize price and fees to USD base currency.
        - Use `session.execute(select(Holding).where(...).with_for_update())` to lock the user's holding for that asset.
        - If action is SELL: Verify `quantity_held >= sell_quantity`. Raise `HTTPException(400)` if insufficient.
        - Update `Holding`:
            - If BUY: `New_Avg_Cost = (Old_Total_Cost + New_Total_Cost_USD) / (Old_Qty + New_Qty)`.
            - If SELL: `Quantity -= Sell_Qty`. (ACB does not change on sell).
        - Create `Transaction` record with all multi-currency fields.
    - Wrap in a single atomic transaction.
  </action>
  <verify>Write a test case with concurrent SELL requests that would exceed the balance to ensure one fails.</verify>
  <done>Transactions are created with atomic locking and correct USD normalization.</done>
</task>

<task type="auto">
  <name>Task 2: Implement Paginated CRUD Endpoints</name>
  <files>src/main.py</files>
  <action>
    - Add FastAPI routes for `/investment/transactions`:
        - `GET`: Implement pagination (`limit`, `offset`) and filtering (`symbol`, `asset_type`, `date_range`, `action`).
        - `PUT`: Support updating transaction details (requires recalculating Holding/ACB).
        - `DELETE`: Implement soft-deletion (set `is_deleted=True` and revert Holding impact).
    - Ensure all responses return both `original_currency` and `base_currency` values.
  </action>
  <verify>Test `GET` endpoint with `limit=5` and verify the `total` count and results. Test `DELETE` and verify record remains in DB but is hidden from `GET`.</verify>
  <done>Full CRUD lifecycle for transactions is operational with pagination.</done>
</task>

<task type="auto">
  <name>Task 3: Market Data & FX Integration</name>
  <files>src/services/market_data.py</files>
  <action>
    - Implement `validate_transaction_price`: Use `yfinance` or `alpaca-py` to check if the entered price is within a reasonable range (e.g., +/- 10%) of the historical high/low for that day.
    - Implement `get_historical_fx_rate`: Integrate with a free FX API or use `yfinance` (e.g., `EURUSD=X`) to get historical rates.
    - Cache FX rates in the `FXRate` table to minimize API calls.
  </action>
  <verify>Call validation with an unrealistic price (e.g., AAPL at $1.00 in 2024) and ensure it flags/warns/rejects.</verify>
  <done>Transaction entries are validated against market reality.</done>
</task>

</tasks>

<verification>
- Concurrent SELL test passes.
- FX rates are cached and reused.
- Pagination works as expected.
</verification>

<success_criteria>
- A user can add a BUY in EUR and see it reflected as USD in their portfolio.
- Selling more than owned returns a 400 error.
- All transaction history is retrievable via paginated API.
</success_criteria>

<output>
After completion, create `.planning/phases/phase-3/3-02-SUMMARY.md`
</output>
