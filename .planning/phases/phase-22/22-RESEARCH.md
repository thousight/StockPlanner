# Phase 22 Research: Code Generation & Verification

## 1. Quantitative Developer Persona
The `CodeGeneratorAgent` will be prompted as a **Senior Quant Developer** specializing in financial data analysis using the Python data stack.

### Core Prompting Principles:
- **Vectorization First:** Explicitly forbid `for` loops for data manipulation. Require `pandas` and `numpy` vectorized operations.
- **Data Integrity:** The agent must handle `NaN` values, infinite returns, and division by zero.
- **Strict Structure:** Enforce the `def run(input_data):` pattern for all generated code.
- **Defensive Coding:** Instructions to include type hints and docstrings for better self-explanation.

---

## 2. Hybrid Self-Correction Loop
To satisfy REQ-512 (Feedback Loop), we will implement a hybrid of **Self-Debug** and **Reflexion** patterns.

### The Refinement Process:
1.  **Predict (Attempt 1):** Agent writes the code using Chain of Thought (explaining logic first).
2.  **Verify (Pre-exec):** `ASTValidator` checks for security violations.
3.  **Execute:** `PythonSandbox` runs the code.
4.  **Analyze (If Fail):** 
    - If validation or execution fails, the agent receives the **Full Context** (Previous Code + Sanitized Error).
    - **Self-Debug Step:** The agent is prompted to explain *why* the code failed.
    - **Reflexion Step:** The agent writes a one-sentence "lesson learned" to avoid repeating the mistake.
5.  **Refine:** Agent generates a new attempt incorporating the reflection.
6.  **Limit:** Maximum of **3 retries**.

---

## 3. Library Selection (Whitelist)
The agent will be prompted to use the following libraries, which match our `ASTValidator` whitelist:
- `pandas` (Primary data handling)
- `numpy` (Mathematical operations)
- `math`, `statistics` (Standard libraries)
- `datetime` (Time-series analysis)
- `scipy` (Advanced financial calculations)

---

## 4. Few-Shot Examples for Prompting
The `CODE_GEN_PROMPT` will include 2-3 high-signal examples:
- **Sector Allocation:** Calculating the percentage of a portfolio invested in each GICS sector.
- **CAGR Calculation:** Computing the Compound Annual Growth Rate for a specific ticker over a given timeframe.
- **Currency Translation:** Converting portfolio value into a target currency using provided exchange rates.
