import ast
import re
import logging
from typing import Any

logger = logging.getLogger(__name__)

class SecurityError(Exception):
    """Raised when a security violation is detected in code or data."""
    def __init__(self, message: str, code: str = "SECURITY_VIOLATION"):
        super().__init__(message)
        self.code = code

class ASTValidator(ast.NodeVisitor):
    """
    Statically analyzes Python code to prevent malicious executions.
    Follows a whitelisting approach for nodes and a strict blacklist for modules/functions.
    """
    
    # Allowed AST nodes for safe math and data manipulation
    ALLOWED_NODES = {
        ast.Module, ast.Expr, ast.BinOp, ast.UnaryOp, 
        ast.Constant, ast.Load, ast.Add, ast.Sub, ast.Mult, ast.Div, 
        ast.FloorDiv, ast.Mod, ast.Pow, ast.List, ast.Dict, ast.Name,
        ast.Call, ast.Attribute, ast.Subscript, ast.Assign, ast.Store,
        ast.Compare, ast.Lt, ast.Gt, ast.LtE, ast.GtE, ast.Eq, ast.NotEq,
        ast.Is, ast.IsNot, ast.In, ast.NotIn,
        ast.BoolOp, ast.And, ast.Or, ast.Not, ast.IfExp,

        ast.ListComp, ast.DictComp, ast.comprehension, ast.keyword,
        ast.Tuple, ast.Set, ast.Slice,
        ast.FunctionDef, ast.Return, ast.arguments, ast.arg,
        ast.If, ast.For, ast.While, ast.Break, ast.Continue, ast.Pass,
        ast.AugAssign, ast.Starred
    }

    # Specifically forbidden modules
    FORBIDDEN_MODULES = {
        'os', 'subprocess', 'sys', 'shutil', 'platform', 'inspect',
        'importlib', 'pickle', 'marshal', 'shelve', 'socket',
        'requests', 'urllib', 'http', 'gc', 'builtins'
    }

    # Specifically forbidden built-in functions
    FORBIDDEN_FUNCTIONS = {
        'eval', 'exec', 'compile', 'open', '__import__', 'getattr',
        'setattr', 'delattr', 'hasattr', 'globals', 'locals', 'vars', 'dir'
    }

    def __init__(self):
        self.errors = []

    def validate(self, code: str) -> bool:
        """
        Parses and validates the given Python code.
        Raises SecurityError if violations are found.
        """
        try:
            tree = ast.parse(code)
            self.visit(tree)
            if self.errors:
                raise SecurityError("; ".join(self.errors))
            return True
        except SyntaxError as e:
            raise SecurityError(f"Syntax Error: {e}", code="SYNTAX_ERROR")
        except SecurityError:
            raise
        except Exception as e:
            raise SecurityError(f"Validation Error: {e}")

    def visit(self, node):
        # 1. Check if node type is allowed
        if type(node) not in self.ALLOWED_NODES:
            self.errors.append(f"Forbidden syntax: {type(node).__name__}")
            return # Don't recurse into forbidden nodes

        # 2. Check for double underscore (private) access
        if isinstance(node, ast.Attribute):
            if node.attr.startswith('__'):
                self.errors.append(f"Private attribute access forbidden: {node.attr}")
        
        if isinstance(node, ast.Name):
            if node.id.startswith('__'):
                 self.errors.append(f"Private name access forbidden: {node.id}")
            if node.id in self.FORBIDDEN_FUNCTIONS:
                 self.errors.append(f"Forbidden function usage: {node.id}")

        # 3. Check for forbidden imports
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            # While Import nodes aren't in ALLOWED_NODES by default, 
            # we explicitly handle them if someone tries to add them
            self.errors.append("Direct imports are forbidden. Use pre-installed libraries only.")

        # 4. Check for forbidden calls
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id in self.FORBIDDEN_FUNCTIONS:
                    self.errors.append(f"Forbidden function call: {node.func.id}")
            elif isinstance(node.func, ast.Attribute):
                if node.func.attr.startswith('__'):
                    self.errors.append(f"Forbidden method call: {node.func.attr}")

        super().visit(node)

def redact_paths(text: str) -> str:
    """
    Redacts internal system paths from a string (e.g., tracebacks).
    Replaces paths like /Users/marwen/... with [REDACTED_PATH].
    """
    if not text:
        return text
    # Matches common Unix-style paths
    path_pattern = r'/(?:[\w\.-]+/)+[\w\.-]+'
    return re.sub(path_pattern, '[REDACTED_PATH]', text)

def map_exception_to_error_code(exc: Exception) -> str:
    """
    Maps common Python exceptions to structured error codes.
    """
    if isinstance(exc, SecurityError):
        return exc.code
    
    exc_name = type(exc).__name__
    mapping = {
        "TimeoutError": "TIMEOUT",
        "SyntaxError": "SYNTAX_ERROR",
        "MemoryError": "MEMORY_LIMIT",
        "RecursionError": "RESOURCE_LIMIT",
        "ZeroDivisionError": "MATH_ERROR",
        "NameError": "NAME_ERROR",
        "TypeError": "TYPE_ERROR",
        "AttributeError": "ATTRIBUTE_ERROR"
    }
    return mapping.get(exc_name, "RUNTIME_ERROR")

def strip_pii(text: str) -> str:
    """
    Basic PII filtering utility (REQ-520).
    Redacts emails, phone numbers, and common token patterns.
    Optimized for performance on large strings.
    """
    if not text or len(text) < 5:
        return text
    
    # Global safety: If a string is massive (>100KB), skip PII scanning to avoid hangs.
    if len(text) > 100000:
        return text

    # 1. Email pattern
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    text = re.sub(email_pattern, '[REDACTED_EMAIL]', text)
    
    # 2. Phone numbers (Basic)
    phone_pattern = r'\b(?:\+?1[-. ]?)?\(?[0-9]{3}\)?[-. ]?[0-9]{3}[-. ]?[0-9]{4}\b'
    text = re.sub(phone_pattern, '[REDACTED_PHONE]', text)

    # 3. API Keys / Tokens (Generic 32+ char hex/base64-like)
    token_pattern = r'\b[a-zA-Z0-9]{32,}\b'
    text = re.sub(token_pattern, '[REDACTED_TOKEN]', text)
    
    return text

def scan_and_redact_pii(data: Any) -> Any:
    """
    Recursively scans and redacts PII from structured data (dict, list, string).
    """
    if isinstance(data, str):
        return strip_pii(data)
    elif isinstance(data, dict):
        return {k: scan_and_redact_pii(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [scan_and_redact_pii(v) for v in data]
    else:
        return data
