import json
import logging
import time
import asyncio
from typing import Any, Dict, Optional
from e2b_code_interpreter import AsyncSandbox
from asgi_correlation_id import correlation_id
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.config import settings
from src.graph.utils.security import (
    ASTValidator, 
    SecurityError, 
    redact_paths, 
    map_exception_to_error_code,
    strip_pii,
    scan_and_redact_pii
)

logger = logging.getLogger(__name__)
# Dedicated audit logger for sandbox execution
audit_logger = logging.getLogger("audit.sandbox")

# Global semaphore to manage E2B concurrency (Limit is 100 for Pro)
E2B_SEMAPHORE = asyncio.Semaphore(90)

class PythonSandbox:
    """
    Wrapper around E2B AsyncSandbox for secure Python execution.
    Handles auditing, concurrency, and error mapping.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.E2B_API_KEY
        self.validator = ASTValidator()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        # In a real scenario, we'd catch E2B's specific rate limit exception
        # For now, we use a generic placeholder or catch Exception for safety
        retry=retry_if_exception_type(Exception),
        reraise=True
    )
    async def _create_sandbox(self):
        """Creates a sandbox with retry logic."""
        return await AsyncSandbox.create(api_key=self.api_key)

    async def execute(self, code: str, data: Optional[Dict[str, Any]] = None, timeout: float = 5.0, thread_id: str = "N/A") -> Dict[str, Any]:
        """
        Validates and executes Python code in an isolated E2B sandbox.
        Injects data as 'input_data' variable.
        """
        start_time = time.perf_counter()
        correlation_id_val = correlation_id.get() or "N/A"
        
        # 1. Static Analysis (AST Validation)
        try:
            self.validator.validate(code)
        except SecurityError as e:
            self._log_audit(code, data, "SECURITY_VIOLATION", 0, thread_id, correlation_id_val, error=str(e))
            return {
                "success": False,
                "error_code": e.code,
                "error_message": str(e)
            }

        # 2. PII Filtering for input data (REQ-520)
        # Optimized: Use recursive scanning on the object directly instead of json roundtrip
        if data:
            data = scan_and_redact_pii(data)

        # 3. Sandbox Execution with Concurrency Control
        sandbox = None
        try:
            async with E2B_SEMAPHORE:
                # Initialize Sandbox
                sandbox = await self._create_sandbox()
                
                # Prepare injection code
                injection = ""
                if data is not None:
                    injection = f"input_data = {json.dumps(data)}\n\n"
                
                full_code = injection + code
                
                # Run code with timeout
                execution = await sandbox.run_code(full_code, timeout=timeout)
                
                duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

                if execution.error:
                    # Execution-level error (e.g. Runtime Error)
                    sanitized_stderr = redact_paths(execution.logs.stderr)
                    sanitized_error = redact_paths(str(execution.error))
                    
                    self._log_audit(code, data, "RUNTIME_ERROR", duration_ms, thread_id, correlation_id_val, error=sanitized_error)
                    
                    return {
                        "success": False,
                        "error_code": "RUNTIME_ERROR",
                        "error_message": sanitized_error,
                        "stderr": sanitized_stderr,
                        "stdout": execution.logs.stdout
                    }

                # Success
                self._log_audit(code, data, "SUCCESS", duration_ms, thread_id, correlation_id_val)
                
                return {
                    "success": True,
                    "stdout": execution.logs.stdout,
                    "results": [res.to_dict() for res in execution.results],
                    "error_code": None
                }

        except Exception as e:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            error_code = map_exception_to_error_code(e)
            sanitized_msg = redact_paths(str(e))
            
            self._log_audit(code, data, error_code, duration_ms, thread_id, correlation_id_val, error=sanitized_msg)
            
            logger.error(f"Sandbox execution failed: {e}")
            return {
                "success": False,
                "error_code": error_code,
                "error_message": sanitized_msg
            }
        finally:
            if sandbox:
                await sandbox.kill()

    def _log_audit(self, code: str, data: Any, status: str, duration_ms: float, thread_id: str, correlation_id: str, error: str = None):
        """Logs execution details in a structured JSON format."""
        audit_entry = {
            "event": "sandbox_execution",
            "thread_id": thread_id,
            "correlation_id": correlation_id,
            "status": status,
            "duration_ms": duration_ms,
            "code": code,
            "input_data": data,
            "error": error
        }
        # Using a simple JSON print/log for the audit trail
        audit_logger.info(json.dumps(audit_entry))

async def execute_python_code(code: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> str:
    """
    Tool for agents to execute Python code safely for financial analysis or complex math.
    'data' should be a dictionary of variables to inject into the script.
    """
    thread_id = kwargs.get("thread_id", "N/A")
    executor = PythonSandbox()
    result = await executor.execute(code, data=data, thread_id=thread_id)
    
    if result["success"]:
        # 4. Output Safeguarding (REQ-520)
        sanitized_stdout = strip_pii(result["stdout"])
        sanitized_results = scan_and_redact_pii(result["results"])

        output = ["Execution Successful:"]
        if sanitized_stdout:
            output.append(f"Output:\n{sanitized_stdout}")
        
        # Add rich results if any (e.g. returned values)
        for res in sanitized_results:
            if "text" in res:
                output.append(f"Result: {res['text']}")
        
        return "\n".join(output)
    else:
        return f"Execution Failed ({result['error_code']}): {result['error_message']}"
