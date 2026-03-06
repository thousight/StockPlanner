---
phase: 15
slug: sec-edgar-agent
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-04
---

# Phase 15 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x |
| **Config file** | pytest.ini |
| **Quick run command** | `pytest tests/unit/agents/test_sec_agent.py` |
| **Full suite command** | `pytest tests/unit/agents/test_sec_agent.py tests/integration/test_sec_tools.py` |
| **Estimated runtime** | ~10 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/unit/agents/test_sec_agent.py`
- **After every plan wave:** Run `pytest tests/unit/agents/test_sec_agent.py tests/integration/test_sec_tools.py`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 15-01-01 | 01 | 0 | SEC-01 | setup | `pytest tests/unit/agents/test_sec_agent.py` | ❌ W0 | ⬜ pending |
| 15-01-02 | 01 | 1 | SEC-02 | unit | `pytest tests/unit/agents/test_sec_agent.py` | ✅ W0 | ⬜ pending |
| 15-01-03 | 01 | 1 | SEC-03 | unit | `pytest tests/unit/agents/test_sec_agent.py` | ✅ W0 | ⬜ pending |
| 15-02-01 | 02 | 2 | SEC-04 | integration | `pytest tests/integration/test_sec_tools.py` | ❌ W2 | ⬜ pending |
| 15-02-02 | 02 | 2 | SEC-05 | integration | `pytest tests/integration/test_sec_tools.py` | ✅ W2 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/fixtures/sec/` — static HTML/iXBRL files for AAPL/MSFT 10-K/Q
- [ ] `tests/unit/agents/test_sec_agent.py` — stubs for parsing and delta logic
- [ ] `tests/integration/test_sec_tools.py` — stubs for SEC-API mocking

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Final report layout | SEC-06 | Visual check of interleaved sections | 1. Run full analysis 2. Inspect generated report for SEC sections |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
