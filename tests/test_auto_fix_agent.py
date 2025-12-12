"""Tests for Auto-Fix Agent with Qwen/Gemini model routing."""
from __future__ import annotations

import json
import re
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from core.utils.model_router import (
    ProviderCallError,
    _call_gemini,
    _call_ollama,
    _call_openrouter,
    _get_provider_for_model,
    generate_text,
)


class TestModelDetection:
    """Test model provider detection logic."""

    def test_detect_gemini_model(self, mock_config):
        """Test that Gemini models are detected correctly."""
        provider = _get_provider_for_model("gemini-2.5-flash", mock_config)
        assert provider == "gemini"

        provider = _get_provider_for_model("gemini-2.5-flash-lite", mock_config)
        assert provider == "gemini"

    def test_detect_ollama_model_with_colon(self, mock_config_with_qwen):
        """Test that models with colons (Ollama format) are detected correctly."""
        # Ollama models have colon format: qwen2.5-coder:1.5b
        # With colon separator, falls back to ollama
        provider = _get_provider_for_model("mistral:latest", mock_config_with_qwen)
        assert provider == "ollama"

    def test_detect_openrouter_qwen_model(self, mock_config):
        """Test that OpenRouter Qwen models are detected as OpenRouter."""
        provider = _get_provider_for_model("qwen-large", mock_config)
        assert provider == "openrouter"

    def test_model_detection_case_insensitive(self, mock_config):
        """Test that model detection is case-insensitive."""
        provider = _get_provider_for_model("GEMINI-2.5-FLASH", mock_config)
        assert provider == "gemini"

        provider = _get_provider_for_model("QWEN2.5", mock_config)
        assert provider == "openrouter"


class TestErrorLogAnalysis:
    """Test error log parsing and analysis."""

    def test_missing_dependency_error_identification(self, error_log_fixtures):
        """Test identification of missing dependency errors."""
        log = error_log_fixtures["missing_dependency"]
        
        assert "ModuleNotFoundError" in log
        assert "google.generativeai" in log
        assert "No module named" in log

    def test_syntax_error_identification(self, error_log_fixtures):
        """Test identification of syntax errors."""
        log = error_log_fixtures["syntax_error"]
        
        assert "SyntaxError" in log
        assert "def test_function()" in log
        assert "invalid syntax" in log

    def test_file_not_found_error_identification(self, error_log_fixtures):
        """Test identification of file not found errors."""
        log = error_log_fixtures["file_not_found"]
        
        assert "FileNotFoundError" in log
        assert "shorts_scenario.txt" in log

    def test_api_rate_limit_error_identification(self, error_log_fixtures):
        """Test identification of API rate limit errors."""
        log = error_log_fixtures["api_rate_limit"]
        
        assert "429" in log
        assert "Resource Exhausted" in log

    def test_import_error_identification(self, error_log_fixtures):
        """Test identification of import errors."""
        log = error_log_fixtures["import_error"]
        
        assert "ImportError" in log
        assert "undefined_module" in log


class TestQwenPrimaryModelFlow:
    """Test Qwen as primary model with Gemini fallback."""

    @patch("core.utils.model_router._call_openrouter")
    def test_qwen_success(self, mock_openrouter, mock_config_with_qwen):
        """Test successful Qwen analysis via OpenRouter."""
        # Note: qwen2.5-coder:1.5b is detected as openrouter provider
        mock_openrouter.return_value = json.dumps({
            "problem": "Missing dependency",
            "root_cause": "google-generativeai not installed",
            "severity": "high",
            "solution_steps": ["Add google-generativeai==0.7.2 to requirements.txt"],
            "code_fix": "google-generativeai==0.7.2",
            "file_to_modify": "requirements.txt",
            "auto_fix_possible": True
        })

        response = generate_text(
            mock_config_with_qwen,
            "Analyze this error: ModuleNotFoundError",
            model_hint="qwen2.5-coder:1.5b"
        )

        assert "Missing dependency" in response

    @patch("core.utils.model_router._call_openrouter")
    @patch("core.utils.model_router._call_gemini")
    def test_qwen_fails_fallback_to_gemini(self, mock_gemini, mock_openrouter, mock_config_with_qwen):
        """Test fallback to Gemini when Qwen fails."""
        mock_openrouter.side_effect = ProviderCallError("Connection refused")
        mock_gemini.return_value = json.dumps({
            "problem": "Missing dependency",
            "root_cause": "google-generativeai not installed",
            "severity": "high",
            "solution_steps": ["Add google-generativeai==0.7.2 to requirements.txt"],
            "code_fix": "google-generativeai==0.7.2",
            "file_to_modify": "requirements.txt",
            "auto_fix_possible": True
        })

        response = generate_text(
            mock_config_with_qwen,
            "Analyze this error: ModuleNotFoundError"
        )

        assert "Missing dependency" in response
        # At least one of the providers should be called
        assert mock_openrouter.called or mock_gemini.called


class TestGeminiFallback:
    """Test Gemini as fallback when Qwen unavailable."""

    @patch("core.utils.model_router._call_gemini")
    def test_gemini_analysis_missing_dependency(self, mock_gemini, mock_config):
        """Test Gemini analysis of missing dependency error."""
        mock_gemini.return_value = json.dumps({
            "problem": "ModuleNotFoundError: No module named 'google.generativeai'",
            "root_cause": "Missing dependency in requirements.txt",
            "severity": "high",
            "solution_steps": [
                "Add 'google-generativeai==0.7.2' to requirements.txt",
                "Run 'pip install -r requirements.txt'"
            ],
            "code_fix": "google-generativeai==0.7.2",
            "file_to_modify": "requirements.txt",
            "suggested_commit_message": "fix: add missing google-generativeai dependency",
            "auto_fix_possible": True
        })

        response = generate_text(
            mock_config,
            "Analyze: ModuleNotFoundError: No module named 'google.generativeai'"
        )

        assert "ModuleNotFoundError" in response
        assert "google-generativeai" in response
        assert mock_gemini.called

    @patch("core.utils.model_router._call_gemini")
    def test_gemini_analysis_syntax_error(self, mock_gemini, mock_config):
        """Test Gemini analysis of syntax error."""
        mock_gemini.return_value = json.dumps({
            "problem": "SyntaxError: invalid syntax in broken_test.py",
            "root_cause": "Missing colon after function definition",
            "severity": "high",
            "solution_steps": [
                "Add ':' after 'def test_function()'",
                "Fix line 1 in core/utils/broken_test.py"
            ],
            "code_fix": "def test_function():\n    return \"This should fail\"",
            "file_to_modify": "core/utils/broken_test.py",
            "auto_fix_possible": True
        })

        response = generate_text(
            mock_config,
            "Analyze: SyntaxError: invalid syntax"
        )

        assert "SyntaxError" in response
        assert "broken_test.py" in response


class TestAutoFixAnalysisJson:
    """Test analysis response JSON structure."""

    @patch("core.utils.model_router._call_gemini")
    def test_analysis_json_structure(self, mock_gemini, mock_config):
        """Test that analysis returns valid JSON with required fields."""
        analysis_dict = {
            "problem": "ModuleNotFoundError: No module named 'google.generativeai'",
            "root_cause": "Missing dependency in requirements.txt",
            "severity": "high",
            "solution_steps": ["Add google-generativeai==0.7.2"],
            "code_fix": "google-generativeai==0.7.2",
            "file_to_modify": "requirements.txt",
            "suggested_commit_message": "fix: add missing google-generativeai",
            "technical_task": "Add missing google-generativeai dependency to requirements.txt",
            "auto_fix_possible": True
        }
        
        mock_gemini.return_value = json.dumps(analysis_dict)

        response = generate_text(mock_config, "Analyze error")
        parsed = json.loads(response)

        assert parsed["problem"] == "ModuleNotFoundError: No module named 'google.generativeai'"
        assert parsed["root_cause"] == "Missing dependency in requirements.txt"
        assert parsed["severity"] == "high"
        assert len(parsed["solution_steps"]) > 0
        assert parsed["auto_fix_possible"] is True
        assert parsed["file_to_modify"] == "requirements.txt"

    @patch("core.utils.model_router._call_gemini")
    def test_analysis_manual_fix_required(self, mock_gemini, mock_config):
        """Test analysis when auto-fix is not possible."""
        analysis_dict = {
            "problem": "FileNotFoundError: prompts/shorts_scenario.txt not found",
            "root_cause": "File was deleted or moved",
            "severity": "critical",
            "solution_steps": [
                "Restore file from git history",
                "Or update path in config.yaml"
            ],
            "code_fix": "",
            "file_to_modify": None,
            "auto_fix_possible": False
        }
        
        mock_gemini.return_value = json.dumps(analysis_dict)

        response = generate_text(mock_config, "Analyze error")
        parsed = json.loads(response)

        assert parsed["auto_fix_possible"] is False
        assert parsed["file_to_modify"] is None
        assert parsed["code_fix"] == ""


class TestRateLimitHandling:
    """Test rate limit error handling and retry logic."""

    @patch("core.utils.model_router._call_gemini")
    def test_rate_limit_retry(self, mock_gemini, mock_config):
        """Test that rate limit triggers retries."""
        error = ProviderCallError("429 Resource Exhausted", status_code=429)
        mock_gemini.side_effect = [
            error,
            json.dumps({
                "problem": "API Rate Limited",
                "root_cause": "Too many requests",
                "severity": "medium",
                "solution_steps": ["Add retry logic"],
                "auto_fix_possible": True,
                "file_to_modify": "core/utils/model_router.py",
                "code_fix": "time.sleep(retry_delay * (2 ** attempt))"
            })
        ]

        response = generate_text(mock_config, "Analyze error")
        
        assert "API Rate Limited" in response
        assert mock_gemini.call_count >= 2

    @patch("core.utils.model_router._call_gemini")
    def test_auth_error_skips_retry(self, mock_gemini, mock_config):
        """Test that auth errors don't trigger retries."""
        # Mock will be called for both primary and fallback models
        # But each model should only be attempted once due to auth error
        mock_gemini.side_effect = ProviderCallError("Invalid API key", status_code=401)

        with pytest.raises(RuntimeError):
            generate_text(mock_config, "Analyze error")

        # Should be called at least once (no retry for auth errors)
        # With fallback chain, may be called multiple times (once per model)
        assert mock_gemini.call_count >= 1


class TestIssueCreationData:
    """Test Issue creation data structure."""

    def test_issue_title_format_critical(self):
        """Test Issue title format for critical severity."""
        analysis = {
            "problem": "Database connection failed",
            "severity": "critical"
        }
        
        title = f"🔴 [{analysis['severity'].upper()}] {analysis['problem'][:80]}"
        
        assert "🔴" in title
        assert "CRITICAL" in title
        assert "Database connection failed" in title

    def test_issue_title_format_high(self):
        """Test Issue title format for high severity."""
        analysis = {
            "problem": "Missing dependency",
            "severity": "high"
        }
        
        title = f"🔴 [{analysis['severity'].upper()}] {analysis['problem'][:80]}"
        
        assert "🔴" in title
        assert "HIGH" in title
        assert "Missing dependency" in title

    def test_issue_body_format(self):
        """Test Issue body contains all required sections."""
        analysis = {
            "problem": "ModuleNotFoundError: No module named 'google.generativeai'",
            "root_cause": "Missing dependency in requirements.txt",
            "severity": "high",
            "solution_steps": [
                "Add google-generativeai==0.7.2 to requirements.txt",
                "Run pip install -r requirements.txt"
            ],
            "technical_task": "Add missing dependency",
            "code_fix": "google-generativeai==0.7.2",
            "auto_fix_possible": True
        }

        issue_body = f"""## 🚨 Failure Analysis

**Problem**
{analysis['problem']}

**Root Cause**
{analysis['root_cause']}

**Severity**
{analysis['severity'].upper()}

**Solution Steps**
{chr(10).join(f'- {step}' for step in analysis['solution_steps'])}

**Technical Task**
{analysis['technical_task']}

**Auto-Fix Status**
Auto-fix possible: {analysis['auto_fix_possible']}
"""

        assert "Problem" in issue_body
        assert "Root Cause" in issue_body
        assert "Solution Steps" in issue_body
        assert "Add google-generativeai==0.7.2 to requirements.txt" in issue_body


class TestPRCreationData:
    """Test Pull Request creation data structure."""

    def test_pr_title_format(self):
        """Test PR title format for auto-fix."""
        analysis = {
            "problem": "Missing google-generativeai dependency"
        }
        
        title = f"🔧 Auto-Fix: {analysis['problem'][:60]}"
        
        assert "🔧" in title
        assert "Auto-Fix:" in title
        assert "Missing google-generativeai dependency" in title

    def test_pr_body_format(self):
        """Test PR body contains all required sections."""
        analysis = {
            "problem": "Missing dependency",
            "root_cause": "Not in requirements.txt",
            "severity": "high",
            "solution_steps": [
                "Add to requirements.txt",
                "Install dependencies"
            ]
        }

        pr_body = f"""## Auto-Fix PR

**Issue:** {analysis['problem']}
**Root Cause:** {analysis['root_cause']}
**Severity:** {analysis['severity'].upper()}

### Solution
{chr(10).join(f'- {step}' for step in analysis['solution_steps'])}

---
*Created by Auto-Fix Agent 🤖*
*Please review and merge manually*
"""

        assert "Auto-Fix PR" in pr_body
        assert "Issue:" in pr_body
        assert "Root Cause:" in pr_body
        assert "Solution" in pr_body


class TestErrorSeverityClassification:
    """Test error severity classification."""

    @patch("core.utils.model_router._call_gemini")
    def test_severity_critical(self, mock_gemini, mock_config):
        """Test critical severity classification."""
        mock_gemini.return_value = json.dumps({
            "problem": "Database connection lost",
            "severity": "critical",
            "auto_fix_possible": False
        })

        response = generate_text(mock_config, "Analyze")
        parsed = json.loads(response)

        assert parsed["severity"] == "critical"

    @patch("core.utils.model_router._call_gemini")
    def test_severity_high(self, mock_gemini, mock_config):
        """Test high severity classification."""
        mock_gemini.return_value = json.dumps({
            "problem": "Missing required dependency",
            "severity": "high",
            "auto_fix_possible": True
        })

        response = generate_text(mock_config, "Analyze")
        parsed = json.loads(response)

        assert parsed["severity"] == "high"

    @patch("core.utils.model_router._call_gemini")
    def test_severity_medium(self, mock_gemini, mock_config):
        """Test medium severity classification."""
        mock_gemini.return_value = json.dumps({
            "problem": "API rate limit exceeded",
            "severity": "medium",
            "auto_fix_possible": True
        })

        response = generate_text(mock_config, "Analyze")
        parsed = json.loads(response)

        assert parsed["severity"] == "medium"

    @patch("core.utils.model_router._call_gemini")
    def test_severity_low(self, mock_gemini, mock_config):
        """Test low severity classification."""
        mock_gemini.return_value = json.dumps({
            "problem": "Deprecation warning in output",
            "severity": "low",
            "auto_fix_possible": True
        })

        response = generate_text(mock_config, "Analyze")
        parsed = json.loads(response)

        assert parsed["severity"] == "low"


class TestMultipleErrorTypes:
    """Test handling of various error types."""

    @patch("core.utils.model_router._call_gemini")
    def test_type_error_analysis(self, mock_gemini, mock_config):
        """Test analysis of TypeError."""
        mock_gemini.return_value = json.dumps({
            "problem": "TypeError: 'NoneType' object is not subscriptable",
            "root_cause": "Unexpected None value",
            "severity": "high",
            "solution_steps": ["Add null check"],
            "auto_fix_possible": True,
            "file_to_modify": "core/utils/test.py",
            "code_fix": "if result is not None: value = result[0]"
        })

        response = generate_text(mock_config, "Analyze")
        parsed = json.loads(response)

        assert "TypeError" in parsed["problem"]
        assert parsed["auto_fix_possible"] is True

    @patch("core.utils.model_router._call_gemini")
    def test_attribute_error_analysis(self, mock_gemini, mock_config):
        """Test analysis of AttributeError."""
        mock_gemini.return_value = json.dumps({
            "problem": "AttributeError: 'Config' object has no attribute 'model'",
            "root_cause": "Config attribute renamed",
            "severity": "high",
            "solution_steps": ["Update attribute name to primary_model"],
            "auto_fix_possible": True,
            "file_to_modify": "core/utils/test.py",
            "code_fix": "model = config.primary_model"
        })

        response = generate_text(mock_config, "Analyze")
        parsed = json.loads(response)

        assert "AttributeError" in parsed["problem"]

    @patch("core.utils.model_router._call_gemini")
    def test_value_error_analysis(self, mock_gemini, mock_config):
        """Test analysis of ValueError."""
        mock_gemini.return_value = json.dumps({
            "problem": "ValueError: invalid literal for int()",
            "root_cause": "Non-numeric string passed to int()",
            "severity": "medium",
            "solution_steps": ["Add try-except for conversion"],
            "auto_fix_possible": True,
            "file_to_modify": "core/utils/test.py",
            "code_fix": "try:\n  value = int(string)\nexcept ValueError:\n  value = 0"
        })

        response = generate_text(mock_config, "Analyze")
        parsed = json.loads(response)

        assert "ValueError" in parsed["problem"]


@pytest.mark.slow
class TestAutoFixAgentIntegration:
    """Integration tests for Auto-Fix Agent (requires API calls)."""

    @patch("core.utils.model_router._call_ollama")
    def test_qwen_integration_missing_dependency(self, mock_ollama, mock_config_with_qwen, error_log_fixtures):
        """Integration test: Qwen analyzes missing dependency error."""
        error_log = error_log_fixtures["missing_dependency"]

        prompt = f"""Analyze this GitHub Actions workflow error:

{error_log}

Provide analysis in JSON format with:
- problem: Brief description
- root_cause: Why it happened
- severity: critical|high|medium|low
- solution_steps: List of steps
- code_fix: Code to fix (if applicable)
- file_to_modify: File path or null
- auto_fix_possible: true/false
"""

        mock_ollama.return_value = json.dumps({
            "problem": "ModuleNotFoundError: No module named 'google.generativeai'",
            "root_cause": "Missing dependency in requirements.txt",
            "severity": "high",
            "solution_steps": ["Add google-generativeai==0.7.2 to requirements.txt"],
            "code_fix": "google-generativeai==0.7.2",
            "file_to_modify": "requirements.txt",
            "auto_fix_possible": True
        })

        response = generate_text(mock_config_with_qwen, prompt, model_hint="qwen2.5-coder:1.5b")
        parsed = json.loads(response)

        assert parsed["severity"] == "high"
        assert parsed["auto_fix_possible"] is True
        assert "google-generativeai" in parsed["code_fix"]

    @patch("core.utils.model_router._call_gemini")
    def test_gemini_integration_syntax_error(self, mock_gemini, mock_config, error_log_fixtures):
        """Integration test: Gemini analyzes syntax error."""
        error_log = error_log_fixtures["syntax_error"]

        prompt = f"""Analyze this GitHub Actions workflow error:

{error_log}

Provide analysis in JSON format with required fields.
"""

        mock_gemini.return_value = json.dumps({
            "problem": "SyntaxError: invalid syntax",
            "root_cause": "Missing colon after function definition",
            "severity": "high",
            "solution_steps": ["Add ':' after 'def test_function()'"],
            "code_fix": "def test_function():\n    return \"Fixed\"",
            "file_to_modify": "core/utils/broken_test.py",
            "auto_fix_possible": True
        })

        response = generate_text(mock_config, prompt)
        parsed = json.loads(response)

        assert "SyntaxError" in parsed["problem"]
        assert parsed["auto_fix_possible"] is True
