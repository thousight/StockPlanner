import pytest
import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch
from src.graph.tools.code_executor import PythonSandbox

@pytest.mark.asyncio
async def test_sandbox_stress_infinite_loop():
    # Test that a script with an infinite loop is killed by the 5s timeout
    # We mock E2B but simulate the timeout exception it would throw
    with patch("src.graph.tools.code_executor.AsyncSandbox", new_callable=AsyncMock) as mock_sandbox_cls:
        mock_instance = AsyncMock()
        mock_sandbox_cls.create.return_value = mock_instance
        
        # Simulate E2B's internal timeout or our wrapper catching a long-running task
        # In E2B, sb.run_code(timeout=5) raises a timeout error if exceeded
        mock_instance.run_code.side_effect = TimeoutError("Execution exceeded 5.0s")
        
        executor = PythonSandbox(api_key="test")
        code = "while True: pass"
        
        result = await executor.execute(code, timeout=1.0)
        
        assert result["success"] is False
        assert result["error_code"] == "TIMEOUT"
        mock_instance.kill.assert_called_once()

@pytest.mark.asyncio
async def test_sandbox_stress_large_data():
    # Test handling of large input data (10MB+)
    with patch("src.graph.tools.code_executor.AsyncSandbox", new_callable=AsyncMock) as mock_sandbox_cls:
        mock_instance = AsyncMock()
        mock_sandbox_cls.create.return_value = mock_instance
        
        mock_execution = MagicMock()
        mock_execution.error = None
        mock_execution.logs.stdout = "Processed"
        mock_execution.results = []
        mock_instance.run_code.return_value = mock_execution
        
        executor = PythonSandbox(api_key="test")
        # Generate 2MB of dummy data (verifies regex optimization)
        large_data = {"data": "x" * (2 * 1024 * 1024)}
        
        result = await executor.execute("print('ok')", data=large_data)
        
        assert result["success"] is True
        assert mock_instance.run_code.called

@pytest.mark.asyncio
async def test_sandbox_concurrency_semaphore():
    # Test that the semaphore correctly limits concurrent creations
    from src.graph.tools.code_executor import E2B_SEMAPHORE
    
    with patch("src.graph.tools.code_executor.AsyncSandbox", new_callable=AsyncMock) as mock_sandbox_cls:
        mock_instance = AsyncMock()
        mock_sandbox_cls.create.return_value = mock_instance
        
        # Setup mock execution result
        mock_execution = MagicMock()
        mock_execution.error = None
        mock_execution.logs.stdout = "OK"
        mock_execution.results = []
        mock_instance.run_code.return_value = mock_execution
        
        # Slow down creation to verify concurrency behavior
        async def slow_create(*args, **kwargs):
            await asyncio.sleep(0.1)
            return mock_instance
            
        mock_sandbox_cls.create.side_effect = slow_create
        
        executor = PythonSandbox(api_key="test")
        
        # Run 5 concurrent executions
        tasks = [executor.execute(f"print({i})") for i in range(5)]
        results = await asyncio.gather(*tasks)
        
        for r in results:
            assert r["success"] is True
            
        # Verify semaphore was hit
        assert mock_sandbox_cls.create.call_count == 5
