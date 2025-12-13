"""Test to validate debugger functionality.

This test deliberately fails to verify that the auto-fix-agent
can detect, analyze, and fix the issue.
"""
import pytest


def test_deliberate_failure_for_debugger_validation():
    """This test will fail to validate debugger workflow."""
    # Intentional assertion that will fail
    assert 1 + 1 == 3, "Math check failed: 1 + 1 should equal 3 for testing"


def test_undefined_function_call():
    """This test calls an undefined function to test error handling."""
    result = undefined_helper_function(42)  # noqa: F821
    assert result == 42


def test_type_error():
    """This test will cause a TypeError."""
    value = None
    # This should raise TypeError: 'NoneType' object is not subscriptable
    result = value[0]
    assert result is not None
