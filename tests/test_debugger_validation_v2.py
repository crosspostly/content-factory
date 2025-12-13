"""Deliberate failing tests for auto-fix-agent validation.

These tests are intentionally failing to validate the auto-fix-agent
workflow's ability to:
1. Detect test failures
2. Analyze error types (AssertionError, NameError, TypeError)
3. Extract error information
4. Create issues with analysis
5. Generate and create fix PRs
"""

import pytest


def test_deliberate_assertion_failure():
    """AssertionError: Math assertion that's intentionally wrong.
    
    Expected to fail with:
    AssertionError: assert 1 + 1 == 3
    """
    result = 1 + 1
    assert result == 3, f"Expected 3 but got {result}"


def test_undefined_function_call():
    """NameError: Call to undefined function.
    
    Expected to fail with:
    NameError: name 'undefined_function' is not defined
    """
    # This function doesn't exist
    undefined_function()  # noqa: F821


def test_type_error_subscript():
    """TypeError: Attempt to subscript NoneType.
    
    Expected to fail with:
    TypeError: 'NoneType' object is not subscriptable
    """
    value = None
    # Trying to subscript None
    return value[0]  # Will raise TypeError


class TestDebuggerValidation:
    """Test class for validating debugger error detection."""

    def test_class_assertion_error(self):
        """Class method with AssertionError."""
        assert 5 * 2 == 11, "5 * 2 should equal 11 according to this broken test"

    def test_class_import_error(self):
        """Class method with ImportError."""
        from nonexistent_module import something  # noqa: F401

    def test_class_value_error(self):
        """Class method with ValueError."""
        int("not a number")
