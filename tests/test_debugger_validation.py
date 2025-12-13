"""Test to validate debugger functionality.

This test deliberately fails to verify that the auto-fix-agent
can detect, analyze, and fix the issue.
"""
import pytest


def test_deliberate_assertion_failure():
    """This test will definitely fail with assertion error."""
    # This will ALWAYS fail
    assert False, "Deliberate test failure for debugger validation"


def test_math_error():
    """Simple math assertion that must fail."""
    result = 1 + 1
    assert result == 3, f"Expected 3 but got {result}"


def test_type_error_on_purpose():
    """This test will raise TypeError."""
    data = None
    # This line will raise: TypeError: 'NoneType' object is not subscriptable
    value = data[0]
    assert value is not None
