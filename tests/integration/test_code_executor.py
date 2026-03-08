import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.graph.tools.code_executor import PythonSandbox, execute_python_code

@pytest.mark.asyncio
async def test_python_sandbox_validation_failure():
    executor = PythonSandbox(api_key="test_key")
    # Malicious code
    code = "import os; os.system('ls')"
    result = await executor.execute(code)
    
    assert result["success"] is False
    assert result["error_code"] == "SECURITY_VIOLATION"
    assert "Import of library 'os' is forbidden" in result["error_message"]

@pytest.mark.asyncio
async def test_python_sandbox_pii_redaction():
    # Mocking E2B to avoid network calls
    with patch("src.graph.tools.code_executor.AsyncSandbox", new_callable=AsyncMock) as mock_sandbox_cls:
        mock_instance = AsyncMock()
        mock_sandbox_cls.create.return_value = mock_instance
        
        # Mock execution result
        mock_execution = MagicMock()
        mock_execution.error = None
        mock_execution.logs.stdout = "Redacted"
        mock_execution.results = []
        mock_instance.run_code.return_value = mock_execution
        
        executor = PythonSandbox(api_key="test_key")
        code = "print(input_data['email'])"
        data = {"email": "secret@example.com"}
        
        result = await executor.execute(code, data=data)
        
        assert result["success"] is True
        # Verify run_code was called with redacted data
        mock_instance.run_code.assert_called_once()
        args, kwargs = mock_instance.run_code.call_args
        full_code = args[0]
        assert "secret@example.com" not in full_code
        assert "[REDACTED_EMAIL]" in full_code

@pytest.mark.asyncio
async def test_python_sandbox_runtime_error_sanitization():
    with patch("src.graph.tools.code_executor.AsyncSandbox", new_callable=AsyncMock) as mock_sandbox_cls:
        mock_instance = AsyncMock()
        mock_sandbox_cls.create.return_value = mock_instance
        
        # Mock execution failure
        mock_execution = MagicMock()
        mock_execution.error = "Error in /home/user/sandbox/main.py: division by zero"
        mock_execution.logs.stderr = "Traceback ... /home/user/sandbox/main.py ..."
        mock_execution.logs.stdout = ""
        mock_instance.run_code.return_value = mock_execution
        
        executor = PythonSandbox(api_key="test_key")
        code = "1 / 0"
        
        result = await executor.execute(code)
        
        assert result["success"] is False
        assert result["error_code"] == "RUNTIME_ERROR"
        assert "/home/user" not in result["error_message"]
        assert "[REDACTED_PATH]" in result["error_message"]
        assert "[REDACTED_PATH]" in result["stderr"]

@pytest.mark.asyncio
async def test_python_sandbox_timeout_mapping():
    with patch("src.graph.tools.code_executor.AsyncSandbox", new_callable=AsyncMock) as mock_sandbox_cls:
        mock_sandbox_cls.create.side_effect = TimeoutError("Sandbox startup timed out")
        
        executor = PythonSandbox(api_key="test_key")
        result = await executor.execute("print('hi')")
        
        assert result["success"] is False
        assert result["error_code"] == "TIMEOUT"

@pytest.mark.asyncio
async def test_execute_python_code_tool_success():
    with patch("src.graph.tools.code_executor.PythonSandbox.execute") as mock_execute:
        mock_execute.return_value = {
            "success": True,
            "stdout": "Hello World",
            "results": [{"text": "42"}]
        }
        
        result = await execute_python_code("print('hi')", data={"a": 1})
        assert "Execution Successful" in result
        assert "Hello World" in result
        assert "Result: 42" in result

@pytest.mark.asyncio
async def test_execute_python_code_tool_failure():
    with patch("src.graph.tools.code_executor.PythonSandbox.execute") as mock_execute:
        mock_execute.return_value = {
            "success": False,
            "error_code": "MATH_ERROR",
            "error_message": "division by zero"
        }
        
        result = await execute_python_code("1/0")
        assert "Execution Failed (MATH_ERROR)" in result
        assert "division by zero" in result
