import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.graph.agents.research.code_gen import code_generator_agent

@pytest.fixture
def mock_state():
    return {
        "user_input": "Calculate my sector distribution.",
        "user_context": {"portfolio": [{"symbol": "TSLA", "sector": "Auto", "value": 1000}]},
        "agent_interactions": [],
        "session_context": {"revision_count": 0}
    }

@pytest.mark.asyncio
async def test_code_gen_to_execution_flow(mock_state):
    # This test verifies the integration between the agent and the execution tool
    # without calling the real E2B API.
    
    mock_llm_response = MagicMock()
    mock_llm_response.content = """
**Audit**: Calculating sector distribution.
```python
def run(input_data):
    return {"Auto": 1.0}
print(run(input_data))
```
"""
    
    # We patch get_llm and the AsyncSandbox (called inside execute_python_code -> PythonSandbox)
    with patch("src.graph.agents.research.code_gen.get_llm") as mock_llm_func, \
         patch("src.graph.tools.code_executor.AsyncSandbox", new_callable=AsyncMock) as mock_sandbox_cls:
        
        # Setup LLM Mock
        mock_llm_instance = mock_llm_func.return_value
        mock_llm_instance.ainvoke = AsyncMock(return_value=mock_llm_response)
        
        # Setup E2B Sandbox Mock
        mock_sandbox_instance = AsyncMock()
        mock_sandbox_cls.create.return_value = mock_sandbox_instance
        
        mock_execution = MagicMock()
        mock_execution.error = None
        mock_execution.logs.stdout = "{'Auto': 1.0}"
        mock_execution.results = []
        mock_sandbox_instance.run_code.return_value = mock_execution
        
        # Run Agent
        result = await code_generator_agent(mock_state)
        
        # Verify Flow
        assert len(result["agent_interactions"]) == 1
        interaction = result["agent_interactions"][0]
        assert interaction["agent"] == "code_generator"
        assert "Execution Successful" in interaction["answer"]
        assert "{'Auto': 1.0}" in interaction["answer"]
        
        # Verify tool was called with correct data
        mock_sandbox_instance.run_code.assert_called_once()
        code_sent = mock_sandbox_instance.run_code.call_args[0][0]
        assert "input_data = " in code_sent
        assert "TSLA" in code_sent
