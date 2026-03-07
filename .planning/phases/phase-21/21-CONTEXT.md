# Phase 21 Context: Secure Runtime Implementation

## Phase Goal
Build the isolated execution engine using WebAssembly (Pyodide) or Micro-VM (E2B) for secure, on-the-fly Python analysis.

## Key Decisions

### 1. Runtime & Isolation
- **Primary Runtime:** **Managed Micro-VM (E2B)**. This provides the highest level of security (hardware-level isolation) and supports the full Python ecosystem if needed in the future.
- **Fallback/Alternative:** **Wasm (Pyodide)** can be used for ultra-low latency, math-only tasks that don't require full VM features.
- **Isolation Level:** Instruction-level (Wasm) or Hardware-level (Micro-VM). No host file system or network access is permitted.

### 2. Data & State Management
- **Data Format:** **Inline JSON**. Data (e.g., portfolio holdings, macro indicators) will be injected directly into the generated Python code as variables.
- **Data Size:** Support for **Medium Datasets (up to 10MB)**.
- **Persistence:** **Stateless (Fresh)**. Every execution call starts with a clean environment; no state is preserved between calls.
- **Pre-execution Security:** **Auto-Strip PII**. Implement a filter to redact personally identifiable information from the input data before it enters the sandbox.

### 3. Error Handling & Feedback
- **Feedback Type:** **Sanitized Tracebacks**. The agent will receive the error message but without internal sandbox paths or environment details.
- **Error Categorization:** **Structured Error Codes**. Use codes like `TIMEOUT`, `MEMORY_LIMIT`, `SYNTAX_ERROR`, or `RUNTIME_ERROR` to help the agent's self-correction loop (REQ-512).
- **Sanitization Level:** **Full Redaction**. Redact all sensitive environment variables and system paths from any returned error output.

### 4. Observability & Logging
- **Logging Policy:** **Selective Logging**. Log code and sanitized tracebacks only for critical failures or suspicious patterns to support auditing (REQ-522).
- **Audit Trail:** Maintain a record of all generated code and the resulting outcome (Success/Fail) for security monitoring.

## Code Context & Integration
- **Integration Point:** `src/graph/tools/code_executor.py` (New tool).
- **Async Support:** The executor must be non-blocking (async/await compatible) to fit into the FastAPI/LangGraph flow.
- **Verification Layer:** Implement the `ast` pre-filter in a reusable utility before calling the sandbox runtime.

## Next Steps
1.  **Phase 21 Research:** Investigate the E2B Python SDK and Pyodide's async integration with Python.
2.  **Phase 21 Plan:** Draft the implementation steps for the `PythonSandbox` wrapper and the `ast` validator.
