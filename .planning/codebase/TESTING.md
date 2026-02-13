# Testing Patterns

**Analysis Date:** 2025-02-14

## Test Framework

**Runner:**
- `pytest`
- Config: `pytest.ini`

**Assertion Library:**
- Native Python `assert` statements.

**Run Commands:**
```bash
pytest                 # Run all tests
pytest -v              # Run tests with verbose output
pytest tests/test_crud.py  # Run specific test file
```

## Test File Organization

**Location:**
- Separate `tests/` directory at the project root.

**Naming:**
- Files: `test_*.py`. Example: `tests/test_research_node.py`
- Classes: `Test*`. Example: `class TestStockOperations`
- Functions: `test_*`. Example: `def test_add_stock_creates_new_stock`

**Structure:**
```
tests/
├── test_analyst_node.py
├── test_crud.py
├── test_research_node.py
└── test_research_utils.py
```

## Test Structure

**Suite Organization:**
```python
class TestResearchNode:
    """Tests for the research_node function."""
    
    @patch('src.agents.nodes.research.node.get_macro_economic_news')
    @patch('src.agents.nodes.research.node.resolve_symbol')
    def test_research_node_returns_research_data(self, mock_resolve, mock_macro):
        # Arrange
        mock_macro.return_value = [...]
        state = {"portfolio": [...]}
        
        # Act
        result = research_node(state)
        
        # Assert
        assert "research_data" in result
```

**Patterns:**
- **Setup pattern:** Using `pytest.fixture` for shared resources like database sessions.
- **Teardown pattern:** `yield` in fixtures handles cleanup (e.g., closing the session).
- **Assertion pattern:** Direct equality or containment assertions.

## Mocking

**Framework:** `unittest.mock`

**Patterns:**
```python
@patch('path.to.function')
def test_something(self, mock_func):
    mock_func.return_value = "mocked value"
    # test logic
```

**What to Mock:**
- External API calls (yfinance, DuckDuckGo, LLM calls).
- Database sessions (though often tested with in-memory SQLite).
- Environment-dependent utilities.

**What NOT to Mock:**
- Pure logic functions that don't have side effects.
- Data models and simple CRUD operations (tested with in-memory DB).

## Fixtures and Factories

**Test Data:**
```python
@pytest.fixture
def db_session():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
```

**Location:**
- Fixtures are defined within the test files where they are used. No global `conftest.py` found yet.

## Coverage

**Requirements:** None enforced in config.

**View Coverage:**
```bash
# (Assuming pytest-cov is installed)
pytest --cov=src
```

## Test Types

**Unit Tests:**
- Focus on individual functions in `crud.py` and `utils.py`.
- Mock external dependencies rigorously.

**Integration Tests:**
- Tests for nodes (`analyst_node`, `research_node`) that involve multiple components, though still heavily mocked.

**E2E Tests:**
- Not explicitly detected as part of the automated suite. Manual verification via `test_market_manual.py`.

## Common Patterns

**Async Testing:**
- No explicit `pytest-asyncio` patterns detected. Threading is handled implicitly in the code being tested.

**Error Testing:**
```python
def test_handles_exception(self, mock_ticker):
    mock_ticker.side_effect = Exception("API Error")
    result = resolve_symbol("INVALID")
    assert result["current_price"] == 0
```

---

*Testing analysis: 2025-02-14*
