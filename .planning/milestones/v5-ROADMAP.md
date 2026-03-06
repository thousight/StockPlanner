# Roadmap - Milestone 5: Python Code Execution Agent

This roadmap outlines the phases for implementing a secure Python code execution environment for the agent team.

## Phase 21: Secure Runtime Implementation
**Goal:** Build the isolated execution engine using WebAssembly (Pyodide) or Micro-VM (E2B).
- [ ] Implement `PythonSandbox` wrapper for the chosen runtime (Pyodide for math-only).
- [ ] Integration of Python `ast` module for static analysis (Pre-filter for `os`, `subprocess`).
- [ ] Resource limiting (Memory/Time) and Air-gapping verification.

## Phase 22: Code Generation & Verification
**Goal:** Create a specialized agent for writing and auditing Python scripts.
- [ ] Implementation of `CodeGeneratorAgent` with strict formatting requirements.
- [ ] `CodeAuditor` component to check for PII leakage and malicious logic (Safeguard).
- [ ] Integration with LangGraph as a specialized execution node.

## Phase 23: Execution Tooling & Feedback
**Goal:** Link the generator to the sandbox and handle errors.
- [ ] `CodeExecutorTool` implementation.
- [ ] Self-correction logic in the agent graph (retry on syntax or runtime error).
- [ ] End-to-end integration tests (e.g. "Calculate my portfolio's sector ratios").

## Phase 24: Monitoring & Auditing
**Goal:** Finalize security and observability.
- [ ] Implement audit logging for all generated/executed code.
- [ ] Refine safeguarding rules based on initial testing.
- [ ] Stress testing of the sandbox.
