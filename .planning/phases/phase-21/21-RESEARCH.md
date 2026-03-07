# Phase 21 Research: Secure Runtime Implementation

## 1. Runtime Platform: E2B (Micro-VM)
E2B provides a secure, sandboxed environment using Firecracker VMs. It is the chosen primary runtime for this phase.

### Key Async SDK Features:
- **Initialization:** `sandbox = await AsyncSandbox.create()`
- **Execution:** `execution = await sandbox.run_code(code, timeout=10.0)`
- **Termination:** `await sandbox.kill()` (Mandatory to avoid resource leakage).
- **Rich Output:** Handles `stdout`, `stderr`, and structured results (e.g., charts, JSON).

### Stateless Strategy:
To maintain the "Stateless (Fresh)" requirement from `21-CONTEXT.md`, every tool call will:
1. Initialize a new sandbox.
2. Inject input data as inline JSON.
3. Execute the code.
4. Kill the sandbox immediately.

---

## 2. AST Pre-filtering (Defense in Depth)
The Python `ast` module will be used to statically analyze generated code before it is sent to E2B.

### Security Rules:
- **Forbidden Patterns:**
  - Double underscore access (e.g., `__class__`, `__init__`, `__subclasses__`).
  - Access to `__builtins__`.
- **Forbidden Modules (Blacklist/Pre-filter):**
  - `os`, `subprocess`, `sys`, `shutil`, `importlib`.
  - `pickle`, `marshal`, `shelve`.
  - `socket`, `requests`, `urllib`, `http`.
- **Forbidden Functions:**
  - `eval()`, `exec()`, `compile()`, `open()`, `__import__()`.
  - `getattr()`, `setattr()`, `delattr()`.

### Implementation Approach:
- Use a `NodeVisitor` to traverse the AST.
- Raise a `SecurityError` if any forbidden node or attribute access is detected.
- **Reference Library:** `evalidate` or `RestrictedPython` for inspiration, but a custom visitor for high-transparency is preferred for REQ-502.

---

## 3. Data Infiltration (Inline JSON)
Input data will be serialized to JSON and injected as a variable definition at the top of the generated code.

### Example Template:
```python
# Injected Data
input_data = { ... } # Serialized JSON

# User Code
def main(data):
    # Agent logic here
    pass

print(main(input_data))
```

---

## 4. Error Sanitization
To prevent information leakage from the sandbox:
- Redact system paths (e.g., `/home/user/...`).
- Redact environment variable values if they appear in tracebacks.
- Map failures to structured error codes: `TIMEOUT`, `MEMORY_LIMIT`, `SECURITY_VIOLATION`, `SYNTAX_ERROR`.
