"""Fixed version of debugger validation tests.

All 6 intentional errors have been corrected to pass.
This validates the auto-fix-agent workflow's ability to:
1. Detect test failures
2. Analyze error types (AssertionError, NameError, TypeError, ImportError, ValueError)
3. Extract error information
4. Create issues with analysis
5. Generate and create fix PRs with corrections
"""

import pytest


def undefined_function():
    """Helper function that was previously undefined.
    
    This function is now defined to fix the NameError.
    """
    return "Function is now defined!"


def test_deliberate_assertion_failure():
    """FIXED: Correct math assertion.
    
    Previously failed with:
    AssertionError: assert 1 + 1 == 3
    
    Now passes with correct math: 1 + 1 == 2
    """
    result = 1 + 1
    assert result == 2, f"Expected 2 but got {result}"


def test_undefined_function_call():
    """FIXED: Function is now defined.
    
    Previously failed with:
    NameError: name 'undefined_function' is not defined
    
    Now the function is defined above and can be called.
    """
    # This function now exists!
    result = undefined_function()
    assert result == "Function is now defined!"


def test_type_error_subscript():
    """FIXED: Using a list instead of None.
    
    Previously failed with:
    TypeError: 'NoneType' object is not subscriptable
    
    Now value is a list that can be subscripted.
    """
    value = ["first", "second", "third"]
    # Now we can subscript value
    assert value[0] == "first"
    return value[0]


class TestDebuggerValidation:
    """Test class for validating debugger error detection - FIXED."""

    def test_class_assertion_error(self):
        """FIXED: Correct math in class assertion.
        
        Previously failed with:
        AssertionError: 5 * 2 should equal 11
        
        Now uses correct math: 5 * 2 == 10
        """
        assert 5 * 2 == 10, "5 * 2 should equal 10"

    def test_class_import_error(self):
        """FIXED: Import from real module instead.
        
        Previously failed with:
        ImportError: No module named 'nonexistent_module'
        
        Now imports from a real module (os is always available).
        """
        from os import path  # Real module that exists
        assert path is not None
        assert callable(path.exists)

    def test_class_value_error(self):
        """FIXED: Convert a valid number string.
        
        Previously failed with:
        ValueError: invalid literal for int() with base 10: 'not a number'
        
        Now converts a valid numeric string.
        """
        result = int("42")
        assert result == 42
        assert isinstance(result, int)
