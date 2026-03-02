---
phase: 05-agentic-flow-refinement
plan: 5-01
type: execute
wave: 1
depends_on: []
files_modified: [src/database/models.py, migrations/versions/..., src/controllers/reports.py, src/main.py]
autonomous: true
requirements: [REQ-011, REQ-023]
---

<objective>
Evolve the Report data model and implement a searchable API for generalized reports.
Purpose: Support high-level synthesis across multiple categories and enable efficient retrieval.
Output: Updated database schema, FTS indices, and a new /reports search endpoint.
</objective>

<execution_context>
@/Users/marwen/.gemini/get-shit-done/workflows/execute-plan.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/phase-5/5-CONTEXT.md
@src/database/models.py
@src/main.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Update Report Model & Category Enum</name>
  <files>src/database/models.py</files>
  <action>
    - Add `ReportCategory` Enum with values: `STOCK`, `REAL_ESTATE`, `MACRO`, `FUND`, `GENERAL`.
    - Update `Report` model:
      - Add `title` (String).
      - Add `category` (Enum(ReportCategory)).
      - Add `topic` (String, indexed).
      - Add `tags` (JSONB).
      - Add `search_vector` (TSVECTOR) for full-text search.
      - Ensure `thread_id` and `user_id` are preserved and indexed.
      - Augment `symbol` with `topic` (maybe rename symbol to topic or keep it for compatibility if needed, but Context says "replaced or augmented").
  </action>
  <verify>Run a local script to verify model definition can be instantiated.</verify>
  <done>Report model matches the generalized report definition from 5-CONTEXT.md.</done>
</task>

<task type="auto">
  <name>Task 2: Alembic Migration with FTS Index</name>
  <files>migrations/versions/...</files>
  <action>
    - Generate a new async migration for the `Report` table updates.
    - Implement a GIN index on `search_vector` column.
    - Add a trigger or update logic to populate `search_vector` from `title`, `topic`, and `content`.
    - Run `alembic upgrade head`.
  </action>
  <verify>`alembic upgrade head` completes successfully on the database.</verify>
  <done>Database schema is updated with new Report fields and Gin index for FTS.</done>
</task>

<task type="auto">
  <name>Task 3: Implement Report Search & Filter API</name>
  <files>src/controllers/reports.py, src/main.py</files>
  <action>
    - Create `src/controllers/reports.py` with a `GET /reports` endpoint.
    - Support query parameters: `category` (optional, filter), `q` (optional, keyword search using FTS).
    - Implement FTS search query using `to_tsquery` or `websearch_to_tsquery` on the `search_vector` column.
    - Include `X-User-ID` header for user isolation.
    - Register the router in `src/main.py`.
  </action>
  <verify>`curl -H "X-User-ID: test" "/reports?category=STOCK&q=NVDA"` returns 200.</verify>
  <done>Reports can be filtered by category and searched via keywords through the API.</done>
</task>

</tasks>

<verification>
Check if `GET /reports` returns expected results and schema reflects 5-CONTEXT.md decisions.
</verification>

<success_criteria>
- Reports table supports Title, Category, Topic, Tags, and FTS.
- Migration is applied successfully.
- Search API is functional and respects user isolation.
</success_criteria>

<output>
After completion, create `.planning/phases/phase-5/5-01-SUMMARY.md`
</output>
