import pytest
import ast
from src.graph.utils.security import (
    ASTValidator, 
    SecurityError, 
    redact_paths, 
    map_exception_to_error_code, 
    strip_pii
)

# --- ASTValidator Tests ---

def test_ast_validator_safe_math_and_logic():
    validator = ASTValidator()
    code = """
x = 10
y = 20
if x < y:
    z = (x + y) * 2 / 5
    items = [i for i in range(10) if i % 2 == 0]
"""
    assert validator.validate(code) is True

def test_ast_validator_forbidden_import():
    validator = ASTValidator()
    # Direct import
    with pytest.raises(SecurityError) as exc:
        validator.validate("import os")
    assert "Forbidden syntax: Import" in str(exc.value)
    
    # ImportFrom
    with pytest.raises(SecurityError) as exc:
        validator.validate("from subprocess import Popen")
    assert "Forbidden syntax: ImportFrom" in str(exc.value)

def test_ast_validator_private_attribute_access():
    validator = ASTValidator()
    # Attribute access
    with pytest.raises(SecurityError) as exc:
        validator.validate("x.__dict__")
    assert "Private attribute access forbidden: __dict__" in str(exc.value)
    
    # Method call
    with pytest.raises(SecurityError) as exc:
        validator.validate("obj.__init__()")
    assert "Forbidden method call: __init__" in str(exc.value)

def test_ast_validator_forbidden_builtins():
    validator = ASTValidator()
    forbidden = ['eval', 'exec', 'open', 'getattr', 'globals', 'locals']
    for func in forbidden:
        with pytest.raises(SecurityError) as exc:
            validator.validate(f"{func}('something')")
        assert f"Forbidden function" in str(exc.value)

def test_ast_validator_syntax_error():
    validator = ASTValidator()
    with pytest.raises(SecurityError) as exc:
        validator.validate("def invalid_syntax")
    assert exc.value.code == "SYNTAX_ERROR"

def test_ast_validator_private_name():
    validator = ASTValidator()
    with pytest.raises(SecurityError) as exc:
        validator.validate("__secret = 1")
    assert "Private name access forbidden: __secret" in str(exc.value)

# --- Redaction Tests ---

def test_redact_paths_single_and_multiple():
    # Single path
    text = "Error at /usr/local/bin/python3"
    assert redact_paths(text) == "Error at [REDACTED_PATH]"
    
    # Multiple paths
    text = "From /home/user/file.py to /tmp/output.txt"
    assert redact_paths(text) == "From [REDACTED_PATH] to [REDACTED_PATH]"
    
    # No path
    assert redact_paths("No paths here") == "No paths here"

# --- PII Stripping Tests ---

def test_strip_pii_edge_cases():
    # Mixed formats
    text = "Email: user.name+test@provider.co.uk, Phone: (555) 123-4567, Token: 1234567890abcdef1234567890abcdef"
    stripped = strip_pii(text)
    assert "[REDACTED_EMAIL]" in stripped
    assert "[REDACTED_PHONE]" in stripped
    assert "[REDACTED_TOKEN]" in stripped
    assert "user.name" not in stripped
    assert "555" not in stripped
    assert "abcdef" not in stripped

def test_strip_pii_no_pii():
    text = "Standard financial data: {'price': 150.25, 'volume': 1000}"
    assert strip_pii(text) == text

# --- Error Mapping Tests ---

def test_map_exception_to_error_code():
    assert map_exception_to_error_code(TimeoutError()) == "TIMEOUT"
    assert map_exception_to_error_code(ZeroDivisionError()) == "MATH_ERROR"
    assert map_exception_to_error_code(RecursionError()) == "RESOURCE_LIMIT"
    assert map_exception_to_error_code(SyntaxError()) == "SYNTAX_ERROR"
    assert map_exception_to_error_code(SecurityError("Violated", code="TEST_CODE")) == "TEST_CODE"
    assert map_exception_to_error_code(ValueError()) == "RUNTIME_ERROR"
