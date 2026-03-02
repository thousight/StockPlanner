# Plan Summary - Phase 3-01: Refine Financial Schema & Polymorphic Metadata

## Implementation Summary
Successfully established the polymorphic financial schema and migrated existing stock data to the new unified `Asset` model. This wave provides the high-precision foundation required for multi-currency portfolio tracking.

- **Polymorphic Asset Model:** Refactored the `stocks` table into a more flexible `assets` table supporting multiple types (Stock, Real Estate, Fund, Metal, Generic).
- **Data Migration:** Implemented custom Alembic logic to seamlessly move existing stock records into the new `assets` table while maintaining data integrity.
- **High-Precision Financials:** Updated all transaction and snapshot fields to use `Numeric(20, 10)` to prevent floating-point errors in financial calculations.
- **Multi-Tenancy Foundation:** Added `user_id` to all core models to support future user isolation.
- **Polymorphic Schemas:** Created Pydantic v2 schemas using Discriminated Unions to handle specialized metadata for different asset classes.
- **Audit & Safety:** Added `is_deleted` for soft-deletion and granular fee fields (`commission`, `tax`).

## File Changes
- `src/database/models.py`: Refactored to include `Asset`, `Holding`, `FXRate`, and updated `Transaction`, `DailySnapshot`, and `Report` models.
- `src/schemas/transactions.py`: New polymorphic Pydantic schemas for asset metadata and transaction CRUD.
- `migrations/versions/9069782f9828_financial_schema_upgrade.py`: Complex migration handling table refactoring, data migration, and constraint management.

## Technical Decisions
- **Unified Asset Table:** Chose a single table with a type discriminator and a JSONB metadata column for asset-specific details, providing the best balance between query performance and flexibility.
- **Base Currency Normalization:** Added `price_base` and `total_base` to transactions to store the USD-equivalent value at the time of entry, ensuring historical performance accuracy.
- **Row-Level Locking Ready:** The schema and model updates are optimized for the row-level locking patterns identified in research.

## Verification
- `alembic upgrade head` executed successfully with data migration.
- Manual check confirms 9 stock records were migrated to the `assets` table.
- Pydantic schemas verified for correct polymorphic validation.
