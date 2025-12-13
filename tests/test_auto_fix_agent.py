"""Tests for Auto-Fix Agent."""
from __future__ import annotations

import json
import os
from unittest.mock import MagicMock, patch

import pytest
from core.auto_fix_agent import (
    analyze_workflow_error,
    create_issue,
    create_pr,
    classify_error_complexity,
    _normalize_analysis
)

class TestAnalyzeWorkflowError:
    """Test analyze_workflow_error function."""

    @patch("core.auto_fix_agent.get_router")
    def test_analyze_workflow_error_success(self, mock_get_router, mock_config):
        """Test successful analysis."""
        mock_router = MagicMock()
        mock_get_router.return_value = mock_router
        
        analysis_response = {
            "problem": "Missing dependency",
            "root_cause": "google-generativeai not installed",
            "severity": "high",
            "solution_steps": ["Add to requirements.txt"],
            "code_fix": "google-generativeai==0.7.2",
            "file_to_modify": "requirements.txt",
            "auto_fix_possible": True
        }
        mock_router.generate.return_value = json.dumps(analysis_response)

        # Mock env var
        with patch.dict(os.environ, {"GOOGLE_AI_API_KEY": "test-key"}):
            result = analyze_workflow_error(
                project_name="test_project",
                workflow_name="test_workflow",
                error_logs="ModuleNotFoundError",
                config=mock_config
            )

        assert result["problem"] == "Missing dependency"
        assert result["severity"] == "high"
        assert result["auto_fix_possible"] is True

    @patch("core.auto_fix_agent.get_router")
    def test_analyze_workflow_error_missing_key(self, mock_get_router, mock_config):
        """Test analysis fails when API key is missing."""
        # Ensure no API key
        with patch.dict(os.environ, {}, clear=True):
            result = analyze_workflow_error(
                project_name="test_project",
                workflow_name="test_workflow",
                error_logs="error",
                config=mock_config
            )
        
        assert "Missing GOOGLE_AI_API_KEY" in result["problem"]

    @patch("core.auto_fix_agent.get_router")
    def test_analyze_workflow_error_invalid_json(self, mock_get_router, mock_config):
        """Test handling of invalid JSON from LLM."""
        mock_router = MagicMock()
        mock_get_router.return_value = mock_router
        mock_router.generate.return_value = "Not JSON"

        with patch.dict(os.environ, {"GOOGLE_AI_API_KEY": "test-key"}):
            result = analyze_workflow_error(
                project_name="test_project",
                workflow_name="test_workflow",
                error_logs="error",
                config=mock_config
            )

        assert "No JSON found" in result["problem"] or "Could not parse" in result["problem"]


class TestIssueCreationData:
    """Test Issue creation data structure."""

    def test_issue_title_format_critical(self):
        """Test Issue title format for critical severity."""
        analysis = {
            "problem": "Database connection failed",
            "severity": "critical",
            "root_cause": "db down",
            "technical_notes": "notes"
        }
        analysis = _normalize_analysis(analysis)
        
        # We need to simulate the create_issue logic since we are testing internal formatting 
        # but create_issue calls subprocess. Let's just test what we can or mock subprocess.
        # But here we want to test the logic inside create_issue roughly.
        
        # Actually, let's just inspect the logic in the code by mocking subprocess
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "http://github.com/issue/1"
            
            create_issue("test_proj", "123", "42", analysis)
            
            args = mock_run.call_args[0][0]
            # args is list: ['gh', 'issue', 'create', '--title', TITLE, '--body', BODY, ...]
            title = args[4]
            assert "🔴" in title
            assert "CRITICAL" in title
            assert "Database connection failed" in title


class TestPRCreationData:
    """Test Pull Request creation data structure."""

    def test_pr_title_format(self):
        """Test PR title format for auto-fix."""
        analysis = {
            "problem": "Missing google-generativeai dependency",
            "root_cause": "missing",
            "severity": "high"
        }
        analysis = _normalize_analysis(analysis)
        
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "http://github.com/pr/1"
            
            create_pr("test_proj", "fix-branch", analysis, "http://issue/1")
            
            args = mock_run.call_args[0][0]
            title = args[8] # check index based on implementation
            
            assert "🔧" in title
            assert "Auto-Fix:" in title
            assert "Missing google-generativeai dependency" in title


class TestErrorComplexity:
    """Test error complexity classification."""
    
    def test_simple_error(self):
        analysis = {
            "auto_fix_possible": True,
            "code_fix": "import foo",
            "file_to_modify": "foo.py"
        }
        assert classify_error_complexity(analysis) == "SIMPLE"
        
    def test_complex_error(self):
        analysis = {
            "auto_fix_possible": False,
            "problem": "Logic error in business rule"
        }
        assert classify_error_complexity(analysis) == "COMPLEX"
        
    def test_simple_pattern_match(self):
        # Even if auto_fix_possible is False initially, if it matches patterns AND has fix... 
        # wait, the logic says "if pattern in problem... But only if we have a fix"
        
        analysis = {
            "problem": "ModuleNotFoundError: foo",
            "code_fix": "pip install foo",
            "file_to_modify": "requirements.txt",
            "auto_fix_possible": False # explicit false
        }
        # The code checks patterns if auto_fix_possible is False/missing
        assert classify_error_complexity(analysis) == "SIMPLE"
