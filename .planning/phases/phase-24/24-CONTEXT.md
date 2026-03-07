# Phase 24 Context: Monitoring & Auditing

## Phase Goal
Finalize the security and observability of the Python Code Execution environment through structured auditing, output safeguarding, and rigorous stress testing.

## Key Decisions

### 1. Structured Audit Trail
- **Mechanism:** **Structured JSON Logging**. Create a dedicated logger `audit.sandbox` to capture execution events.
- **Scope:** Log every execution attempt, including the **Full Payload** (generated code, input JSON) and the final outcome (stdout, results, errors).
- **Traceability:** Include the **Thread ID** in every log entry. User IDs are excluded to maintain a layer of anonymity in logs.
- **Goal:** Enable post-hoc analysis of agent-generated code and forensic investigation of security events.

### 2. Output Safeguarding (Deep Scan)
- **Scanning:** Implement a **Deep Scan** of the sandbox response. This includes:
  - Raw `stdout` string.
  - The structured `results` list (values returned by the `run()` function).
- **Action:** If PII (Email, Phone, Tokens) is detected in the output, it must be **Redacted** immediately using the `strip_pii` utility.
- **Sync:** Rules for input and output redaction will remain synchronized to ensure consistent data protection.

### 3. Resource Enforcement
- **Time:** Strictly enforce the **5s Timeout** at the E2B level.
- **Memory:** Rely on **E2B Defaults** for this phase. Explicit 50MB enforcement is deferred unless stress tests identify it as a recurring bottleneck.

### 4. Stress Testing & Validation
- **Resource Exhaustion:** Simulate infinite loops and high-recursion depth to verify that sandboxes are reliably killed.
- **Data Volume:** Test with 10MB+ JSON payloads and large Pandas dataframes to verify serialization and memory stability.
- **Concurrency:** Verify system behavior under high load (simultaneous execution requests across different threads).

## Code Context & Integration
- **Logging Integration:** Update `PythonSandbox` in `src/graph/tools/code_executor.py` to use the new audit logger.
- **Output Filter:** Add an output processing step in `execute_python_code` to apply `strip_pii` before returning results to the agent.
- **Stress Suite:** New test file `tests/stress/test_sandbox_stress.py`.

## Next Steps
1.  **Phase 24 Research:** Investigate Python's `logging` configuration for structured JSON output and E2B's concurrency limits.
2.  **Phase 24 Plan:** Define the stress test scenarios and auditing implementation steps.
