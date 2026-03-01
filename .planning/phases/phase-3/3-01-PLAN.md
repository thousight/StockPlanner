---
phase: 03-financial-apis
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - src/database/models.py
  - src/schemas/transactions.py
  - migrations/versions/xxxx_financial_schema_upgrade.py
autonomous: true
requirements: [REQ-023]

must_haves:
  truths:
    - "Database supports fractional shares with 0.0001 precision (Numeric)"
    - "Transactions track commission, tax, and original currency separately"
    - "Asset metadata is polymorphic (Stock, Real Estate, Fund, etc.) via JSONB"
    - "Holdings table exists for strict consistency enforcement"
  artifacts:
    - path: "src/database/models.py"
      provides: "Updated Financial Models"
    - path: "src/schemas/transactions.py"
      provides: "Polymorphic Pydantic Schemas"
  key_links:
    - from: "Transaction"
      to: "Holding"
      via: "symbol/user_id"
---

<objective>
Refactor the database schema and Pydantic models to support professional financial operations, including multi-currency, fractional shares, and polymorphic asset metadata.

Purpose: Establish the data foundation for accurate ACB (Average Cost Basis) and strict consistency.
Output: Updated SQLAlchemy models, polymorphic Pydantic schemas, and a database migration.
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
@src/database/models.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Update Financial Models in src/database/models.py</name>
  <files>src/database/models.py</files>
  <action>
    - Refactor `Stock` to a more generic `Asset` model with `type` (Enum: STOCK, REAL_ESTATE, FUND, METAL, GENERIC).
    - Update `Transaction` model:
        - Change `quantity`, `price_per_share` to `Numeric(precision=20, scale=10)` (using `decimal.Decimal` in Python).
        - Replace `fees` with `commission` and `tax` (Numeric).
        - Add `currency` (String, 3 chars ISO) and `fx_rate` (Numeric).
        - Add `price_base` and `total_base` (pre-calculated USD values).
        - Add `metadata` (JSONB) for polymorphic asset data.
        - Add `is_deleted` (Boolean, default=False) for soft deletion.
    - Create `Holding` model to track `quantity_held` and `avg_cost_basis` per asset/user.
    - Create `FXRate` model for historical rate caching (source, target, rate, date).
    - Ensure all models use a consistent `user_id` column (for future multi-user support, even if single user now).
  </action>
  <verify>Check models with `pytest` (model instantiation test) and verify schema via `sqlacodegen` or manual inspection.</verify>
  <done>Models reflect all financial precision and multi-currency requirements from RESEARCH.md.</done>
</task>

<task type="auto">
  <name>Task 2: Implement Polymorphic Pydantic Schemas</name>
  <files>src/schemas/transactions.py</files>
  <action>
    - Define Pydantic v2 Discriminated Unions for Asset Metadata:
        - `StockMetadata`: (Empty for now)
        - `RealEstateMetadata`: type (house/etc), address, purchase_price.
        - `FundMetadata`: commitment_date, vintage_year.
        - `MetalMetadata`: (Empty, quantity is in main field).
    - Create `TransactionCreate` schema that uses these unions for the `metadata` field.
    - Ensure `Decimal` is used for all currency/quantity fields.
  </action>
  <verify>Run a script to validate sample JSON payloads for different asset types against the schemas.</verify>
  <done>Pydantic schemas correctly validate and serialize polymorphic asset data.</done>
</task>

<task type="auto">
  <name>Task 3: Generate and Run Alembic Migration</name>
  <files>migrations/versions/</files>
  <action>
    - Run `alembic revision --autogenerate -m "financial_schema_upgrade"`.
    - Review the generated migration to ensure no data loss (use `batch_alter_table` if necessary for SQLite compatibility, though we are targeting Postgres).
    - Apply the migration: `alembic upgrade head`.
  </action>
  <verify>Check database schema using a SQL client or `inspector.get_columns` to confirm Numeric types and JSONB column existence.</verify>
  <done>Database schema is in sync with the new models.</done>
</task>

</tasks>

<verification>
- Model types use Numeric for precision.
- JSONB column present for metadata.
- soft deletion column exists.
</verification>

<success_criteria>
- Migration applied successfully without errors.
- Pydantic models handle mixed asset types (Stock vs Real Estate) correctly.
- Decimal precision is maintained through the ORM layer.
</success_criteria>

<output>
After completion, create `.planning/phases/phase-3/3-01-SUMMARY.md`
</output>
