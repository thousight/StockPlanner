---
phase: phase-7
plan: 7-03
type: execute
wave: 2
depends_on: [7-01, 7-02]
files_modified:
  - src/services/portfolio.py
  - src/graph/utils/news.py
autonomous: true
requirements: [Audit]
---

<objective>
Final codebase audit for unused code and logical separation. 

Purpose: Ensure the project remains lean and logically structured.
Output: A cleaner codebase with no unused imports or redundant utils.
</objective>

<execution_context>
@/Users/marwen/.gemini/get-shit-done/workflows/execute-plan.md
@/Users/marwen/.gemini/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/phase-7/7-CONTEXT.md
@.planning/phases/phase-7/7-RESEARCH.md
@src/services/portfolio.py
@src/graph/utils/news.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Code Audit and Dead Code Removal</name>
  <files>src/**/*.py</files>
  <action>
    - Perform a general sweep for unused imports across the `src/` directory.
    - Remove unused functions, variables, or variables that are assigned but never used.
    - Specifically check `src/graph/utils/` for any leftover functions that are no longer used by tools.
  </action>
  <verify>
    Run `flake8` or a similar linter to check for unused imports (F401).
    Verify no `src/graph/utils/news.py` leftovers if fully migrated.
  </verify>
  <done>
    No unused imports or dead code left in the `src/` directory.
  </done>
</task>

<task type="auto">
  <name>Task 2: Audit Portfolio Service for Logical Separation</name>
  <files>src/services/portfolio.py</files>
  <action>
    - Ensure `src/services/portfolio.py` only contains financial math and core domain logic (ACB, PNL, gain/loss).
    - Remove any direct external API calls (yfinance, etc.) that might have been missed.
    - Ensure it uses `src/services/market_data.py` for all external data requirements.
  </action>
  <verify>
    Ensure `src/services/portfolio.py` only imports from `market_data.py` for market data needs.
  </verify>
  <done>
    Logical separation of concerns is maintained.
  </done>
</task>

<task type="auto">
  <name>Task 3: Final Phase Verification</name>
  <files>src/services/market_data.py</files>
  <action>
    - Final check to verify that all yfinance calls in the system are indeed centralized in `market_data.py` and wrapped in `asyncio.to_thread`.
    - Run `grep -r "yfinance" src/` to confirm.
  </action>
  <verify>
    Grep should only return matches within `src/services/market_data.py`.
  </verify>
  <done>
    Simplification goals are fully met.
  </done>
</task>

</tasks>

<verification>
- Grep confirms no external yfinance calls except in market_data.
- Logging meets the standardized format.
- Codebase is free of unused legacy code.
</verification>

<success_criteria>
- No unused imports in any `src/` file.
- `src/services/portfolio.py` only contains business logic.
- All goals in 7-CONTEXT.md are implemented.
</success_criteria>

<output>
After completion, create `.planning/phases/phase-7/phase-7-03-SUMMARY.md`
</output>
