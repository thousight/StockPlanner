# Testing Patterns

**Analysis Date:** 2024-05-22

## Test Framework

**Runner:**
- `pytest` (configured in `pytest.ini`)

**Assertion Library:**
- Standard Python `assert` statements.

**Run Commands:**
```bash
pytest                 # Run all tests
pytest -v              # Run in verbose mode
pytest --tb=short      # Show short traceback
```

## Test File Organization

**Location:**
- Separate `tests/` directory at project root.

**Naming:**
- Files: `test_*.py` (e.g., `tests/test_crud.py`, `tests/test_analyst_agent.py`)
- Functions: `test_snake_case` (e.g., `test_add_buy_transaction`)
- Classes: `TestPascalCase` (e.g., `TestAnalystAgent`)

**Structure:**
```
tests/
├── test_analyst_agent.py
├── test_crud.py
├── test_research_tools.py
└── test_supervisor_agent.py
```

## Test Structure

**Suite Organization:**
```python
class TestFeatureName:
    """Tests for a specific feature."""
    
    def test_scenario_one(self, fixture):
        """Docstring describing the test case."""
        # Arrange
        # Act
        # Assert
        assert something == expected
```

**Patterns:**
- **Fixtures:** `pytest.fixture` used for setup (e.g., `db_session` for in-memory DB).
- **Assertions:** Explicit checks with `assert`.

## Mocking

**Framework:** `unittest.mock` (`patch`, `MagicMock`)

**Patterns:**
```python
@patch('src.agents.analyst.agent.create_debate_graph')
def test_analyst_agent_returns_report(self, mock_create_debate_graph):
    mock_graph = MagicMock()
    mock_graph.invoke.return_value = { ... }
    mock_create_debate_graph.return_value = mock_graph
    
    # Run test and verify
    mock_graph.invoke.assert_called_once_with(...)
```

**What to Mock:**
- External API calls (e.g., `ChatOpenAI`).
- Subgraph creation and invocation (e.g., `create_debate_graph`).
- Environment variables (`patch.dict('os.environ', ...)`).

**What NOT to Mock:**
- Database operations (use in-memory SQLite instead via `db_session` fixture).
- Simple utility functions.

## Fixtures and Factories

**Test Data:**
```python
@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
```

**Location:**
- Defined within individual test files (e.g., `tests/test_crud.py`).

## Coverage

**Requirements:** None explicitly enforced in the codebase configuration.

**View Coverage:**
```bash
# Assuming pytest-cov is installed
pytest --cov=src tests/
```

## Test Types

**Unit Tests:**
- CRUD operations in `tests/test_crud.py`.
- Individual agent logic in `tests/test_analyst_agent.py` and `tests/test_supervisor_agent.py`.

**Integration Tests:**
- Testing agent routing and high-level plan generation (e.g., `test_supervisor_routes_using_llm`).

**E2E Tests:**
- Not explicitly detected in the `tests/` directory (likely manual testing of the Streamlit app).

## Common Patterns

**Async Testing:**
- Not observed (logic appears primarily synchronous).

**Error Testing:**
- Testing exception handling or edge cases (e.g., `test_supervisor_loop_detection`).

---

*Testing analysis: 2024-05-22*
