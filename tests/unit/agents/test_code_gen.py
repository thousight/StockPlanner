import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.graph.agents.research.code_gen import code_generator_agent

@pytest.fixture
def mock_state():
    return {
        "user_input": "Calculate my portfolio's average sector return.",
        "user_context": {"portfolio": [{"symbol": "AAPL", "sector": "Tech", "value": 100}]},
        "agent_interactions": [],
        "session_context": {"revision_count": 0}
    }

@pytest.mark.asyncio
async def test_code_generator_success(mock_state):
    # Mock LLM response
    mock_llm_response = MagicMock()
    mock_llm_response.content = """
**Audit**: I will calculate the average return.
```python
def run(data):
    return 42
print(run(input_data))
```
"""
    
    with patch("src.graph.agents.research.code_gen.get_llm") as mock_llm_func, \
         patch("src.graph.agents.research.code_gen.execute_python_code") as mock_execute:
        
        mock_instance = mock_llm_func.return_value
        mock_instance.ainvoke = AsyncMock(return_value=mock_llm_response)
        
        mock_execute.return_value = "Execution Successful:\nResult: 42"
        
        result = await code_generator_agent(mock_state)
        
        assert len(result["agent_interactions"]) == 1
        interaction = result["agent_interactions"][0]
        assert interaction["agent"] == "code_generator"
        assert "42" in interaction["answer"]
        assert "**Audit**" in interaction["answer"]
        assert interaction["next_agent"] == "analyst"

@pytest.mark.asyncio
async def test_code_generator_retry_and_success(mock_state):
    # Mock LLM to return failing code first, then successful code
    mock_fail_response = MagicMock()
    mock_fail_response.content = "**Audit**: Fails first.\n```python\n1/0\n```"
    
    mock_success_response = MagicMock()
    mock_success_response.content = "**Audit**: Fixed.\n```python\n42\n```"
    
    with patch("src.graph.agents.research.code_gen.get_llm") as mock_llm_func, \
         patch("src.graph.agents.research.code_gen.execute_python_code") as mock_execute:
        
        mock_instance = mock_llm_func.return_value
        mock_instance.ainvoke = AsyncMock(side_effect=[mock_fail_response, mock_success_response])
        
        # First call fails, second succeeds
        mock_execute.side_effect = ["Execution Failed (MATH_ERROR): division by zero", "Execution Successful:\nResult: 42"]
        
        result = await code_generator_agent(mock_state)
        
        assert mock_instance.ainvoke.call_count == 2
        assert mock_execute.call_count == 2
        assert "Result: 42" in result["agent_interactions"][0]["answer"]

@pytest.mark.asyncio
async def test_code_generator_max_retries_failure(mock_state):
    mock_fail_response = MagicMock()
    mock_fail_response.content = "**Audit**: Always fails.\n```python\n1/0\n```"
    
    with patch("src.graph.agents.research.code_gen.get_llm") as mock_llm_func, \
         patch("src.graph.agents.research.code_gen.execute_python_code") as mock_execute:
        
        mock_instance = mock_llm_func.return_value
        mock_instance.ainvoke = AsyncMock(return_value=mock_fail_response)
        
        mock_execute.return_value = "Execution Failed (MATH_ERROR): division by zero"
        
        result = await code_generator_agent(mock_state)
        
        # Max retries is 3, so total 4 attempts (0, 1, 2, 3)
        assert mock_instance.ainvoke.call_count == 4
        assert "failed after 3 attempts" in result["agent_interactions"][0]["answer"]

@pytest.mark.asyncio
async def test_code_generator_parsing_multiple_blocks(mock_state):
    # Test that it takes the LAST code block
    mock_llm_response = MagicMock()
    mock_llm_response.content = """
Here is an example:
```python
print("bad")
```
But here is the final code:
**Audit**: Correct block.
```python
def run(data):
    return "good"
print(run(input_data))
```
"""
    with patch("src.graph.agents.research.code_gen.get_llm") as mock_llm_func, \
         patch("src.graph.agents.research.code_gen.execute_python_code") as mock_execute:
        
        mock_instance = mock_llm_func.return_value
        mock_instance.ainvoke = AsyncMock(return_value=mock_llm_response)
        mock_execute.return_value = "Execution Successful:\nResult: good"
        
        await code_generator_agent(mock_state)
        
        # Verify execute_python_code was called with the second block
        mock_execute.assert_called_once()
        args, _ = mock_execute.call_args
        assert 'return "good"' in args[0]
        assert 'print("bad")' not in args[0]

@pytest.mark.asyncio
async def test_code_generator_no_code_block_retry(mock_state):
    # First response has no code block, second one is fixed
    mock_no_code = MagicMock()
    mock_no_code.content = "I forgot to write code."
    
    mock_with_code = MagicMock()
    mock_with_code.content = "**Audit**: Fixed.\n```python\nprint('fixed')\n```"
    
    with patch("src.graph.agents.research.code_gen.get_llm") as mock_llm_func, \
         patch("src.graph.agents.research.code_gen.execute_python_code") as mock_execute:
        
        mock_instance = mock_llm_func.return_value
        mock_instance.ainvoke = AsyncMock(side_effect=[mock_no_code, mock_with_code])
        mock_execute.return_value = "Execution Successful"
        
        await code_generator_agent(mock_state)
        
        assert mock_instance.ainvoke.call_count == 2
        # Verify retry prompt included the internal error
        retry_prompt = mock_instance.ainvoke.call_args_list[1][0][0]
        assert "No Python code block found" in retry_prompt

@pytest.mark.asyncio
async def test_code_generator_context_injection(mock_state):
    mock_state["market_context"] = "Bullish trend."
    mock_llm_response = MagicMock()
    mock_llm_response.content = "**Audit**: Logic.\n```python\nprint('ok')\n```"
    
    with patch("src.graph.agents.research.code_gen.get_llm") as mock_llm_func, \
         patch("src.graph.agents.research.code_gen.execute_python_code") as mock_execute:
        
        mock_instance = mock_llm_func.return_value
        mock_instance.ainvoke = AsyncMock(return_value=mock_llm_response)
        mock_execute.return_value = "Execution Successful"
        
        await code_generator_agent(mock_state)
        
        # Verify prompt included market context
        prompt = mock_instance.ainvoke.call_args[0][0]
        assert "Bullish trend." in prompt
        assert "'symbol': 'AAPL'" in prompt
