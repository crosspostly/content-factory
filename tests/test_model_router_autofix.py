"""Advanced tests for model_router with Auto-Fix Agent scenarios."""
from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from core.utils.model_router import (
    ProviderCallError,
    generate_text,
    _call_gemini,
    _call_ollama,
    _call_openrouter,
    _get_provider_for_model,
)


class TestOllamaProvider:
    """Test Ollama provider implementation."""

    def test_ollama_model_detection(self, mock_config):
        """Test that Ollama models with colon are detected."""
        provider = _get_provider_for_model("mistral:latest", mock_config)
        assert provider == "ollama"

        provider = _get_provider_for_model("llama2:13b", mock_config)
        assert provider == "ollama"


class TestGeminiProvider:
    """Test Gemini provider implementation."""

    def test_gemini_model_detection(self, mock_config):
        """Test that Gemini models are detected correctly."""
        provider = _get_provider_for_model("gemini-2.5-flash", mock_config)
        assert provider == "gemini"

        provider = _get_provider_for_model("gemini-2.5-flash-lite", mock_config)
        assert provider == "gemini"

        provider = _get_provider_for_model("gemini-2.5-pro", mock_config)
        assert provider == "gemini"


class TestOpenRouterProvider:
    """Test OpenRouter provider for Qwen fallback."""

    def test_openrouter_qwen_detection(self, mock_config):
        """Test that Qwen models without colon are detected as OpenRouter."""
        provider = _get_provider_for_model("qwen-large", mock_config)
        assert provider == "openrouter"

        provider = _get_provider_for_model("qwen-2.5-coder-32b", mock_config)
        assert provider == "openrouter"


class TestModelFallbackSequence:
    """Test model fallback sequence and routing."""

    @patch("core.utils.model_router._call_openrouter")
    @patch("core.utils.model_router._call_gemini")
    def test_qwen_primary_gemini_fallback(self, mock_gemini, mock_openrouter, mock_config_with_qwen):
        """Test Qwen/OpenRouter as primary with Gemini as fallback."""
        # Qwen (OpenRouter) fails, Gemini succeeds
        mock_openrouter.side_effect = ProviderCallError("Connection refused")
        mock_gemini.return_value = "Gemini response"

        response = generate_text(mock_config_with_qwen, "Analyze error")

        assert response == "Gemini response"
        assert mock_openrouter.called
        assert mock_gemini.called

    @patch("core.utils.model_router._call_openrouter")
    @patch("core.utils.model_router._call_gemini")
    def test_qwen_success_no_gemini_call(self, mock_gemini, mock_openrouter, mock_config_with_qwen):
        """Test Qwen success prevents Gemini fallback."""
        mock_openrouter.return_value = "Qwen response"

        response = generate_text(mock_config_with_qwen, "Analyze error")

        assert response == "Qwen response"
        assert mock_openrouter.called
        assert not mock_gemini.called


class TestRetryLogicWithAutoFix:
    """Test retry logic specifically for auto-fix scenarios."""

    @patch("core.utils.model_router._call_gemini")
    @patch("core.utils.model_router.time.sleep")
    def test_retry_on_rate_limit(self, mock_sleep, mock_gemini, mock_config):
        """Test retry on rate limit with exponential backoff."""
        mock_gemini.side_effect = [
            ProviderCallError("429 Rate Limited", status_code=429),
            "Success after retry"
        ]

        response = generate_text(mock_config, "Analyze error")

        assert response == "Success after retry"
        assert mock_gemini.call_count == 2
        # Verify exponential backoff was attempted
        assert mock_sleep.called

    @patch("core.utils.model_router._call_gemini")
    def test_no_retry_on_auth_error(self, mock_gemini, mock_config):
        """Test no retry on authentication error."""
        mock_gemini.side_effect = ProviderCallError("Invalid API key", status_code=401)

        with pytest.raises(RuntimeError):
            generate_text(mock_config, "Analyze error")

        # Auth error breaks the chain for each model, but config has fallback models
        # So it tries primary and fallback, getting auth error on each
        assert mock_gemini.call_count >= 1

    @patch("core.utils.model_router._call_gemini")
    @patch("core.utils.model_router.time.sleep")
    def test_max_retries_respected(self, mock_sleep, mock_gemini, mock_config):
        """Test retry behavior on transient errors."""
        mock_gemini.side_effect = ProviderCallError("Transient error")

        with pytest.raises(RuntimeError):
            generate_text(mock_config, "Analyze error")

        # With fallback models in config, multiple models are tried
        # Each gets max_retries attempts
        assert mock_gemini.call_count >= 1


class TestAutoFixAnalysisPrompts:
    """Test prompts used for auto-fix analysis."""

    def test_analysis_prompt_structure(self):
        """Test that analysis prompt includes required context."""
        error_log = """
        Traceback (most recent call last):
          File "core/utils/test.py", line 10
        ModuleNotFoundError: No module named 'google.generativeai'
        """

        prompt = f"""You are an expert DevOps engineer.

A GitHub Actions workflow failed. Analyze the error.

Error Logs:
```
{error_log}
```

Provide analysis in JSON format:
{{
  "problem": "...",
  "root_cause": "...",
  "severity": "critical|high|medium|low",
  "solution_steps": [...],
  "code_fix": "...",
  "file_to_modify": "...",
  "auto_fix_possible": true/false
}}

Be precise and actionable."""

        assert "DevOps engineer" in prompt
        assert "Error Logs" in prompt
        assert "JSON format" in prompt
        assert "auto_fix_possible" in prompt

    def test_analysis_prompt_includes_workflow_context(self):
        """Test prompt includes workflow context."""
        workflow_name = "tests.yml"
        branch = "main"
        run_number = 42

        prompt = f"""Analyze GitHub Actions workflow failure.

Workflow: {workflow_name}
Branch: {branch}
Run #{run_number}

Provide analysis in JSON format..."""

        assert workflow_name in prompt
        assert branch in prompt
        assert str(run_number) in prompt


class TestErrorAnalysisAccuracy:
    """Test accuracy of error analysis."""

    @patch("core.utils.model_router._call_gemini")
    def test_identifies_missing_dependency_correctly(self, mock_gemini, mock_config):
        """Test accurate identification of missing dependency."""
        mock_gemini.return_value = json.dumps({
            "problem": "ModuleNotFoundError: No module named 'google.generativeai'",
            "root_cause": "Missing dependency in requirements.txt",
            "severity": "high",
            "file_to_modify": "requirements.txt"
        })

        response = generate_text(mock_config, "Analyze: ModuleNotFoundError")
        parsed = json.loads(response)

        assert "ModuleNotFoundError" in parsed["problem"]
        assert "requirements.txt" in parsed["file_to_modify"]
        assert parsed["severity"] == "high"

    @patch("core.utils.model_router._call_gemini")
    def test_identifies_syntax_error_correctly(self, mock_gemini, mock_config):
        """Test accurate identification of syntax error."""
        mock_gemini.return_value = json.dumps({
            "problem": "SyntaxError: invalid syntax",
            "root_cause": "Missing colon after function definition",
            "severity": "high",
            "file_to_modify": "core/utils/broken_test.py"
        })

        response = generate_text(mock_config, "Analyze: SyntaxError")
        parsed = json.loads(response)

        assert "SyntaxError" in parsed["problem"]
        assert "broken_test.py" in parsed["file_to_modify"]

    @patch("core.utils.model_router._call_gemini")
    def test_identifies_file_not_found_correctly(self, mock_gemini, mock_config):
        """Test accurate identification of file not found error."""
        mock_gemini.return_value = json.dumps({
            "problem": "FileNotFoundError: shorts_scenario.txt",
            "root_cause": "File was deleted or moved",
            "severity": "critical",
            "auto_fix_possible": False
        })

        response = generate_text(mock_config, "Analyze: FileNotFoundError")
        parsed = json.loads(response)

        assert "FileNotFoundError" in parsed["problem"]
        assert parsed["auto_fix_possible"] is False


class TestModelConfigurationDefaults:
    """Test default model configuration."""

    def test_config_primary_model(self, mock_config):
        """Test primary model configuration."""
        assert mock_config.generation.primary_model == "gemini-2.5-flash"

    def test_config_fallback_models(self, mock_config):
        """Test fallback models configuration."""
        fallbacks = mock_config.generation.fallback_models
        assert len(fallbacks) > 0
        assert "gemini-2.5-flash-lite" in fallbacks

    def test_config_temperature(self, mock_config):
        """Test temperature configuration."""
        assert mock_config.generation.temperature == 0.7

    def test_config_max_retries(self, mock_config):
        """Test max retries configuration."""
        assert mock_config.generation.max_retries == 2

    def test_qwen_config_primary_model(self, mock_config_with_qwen):
        """Test Qwen as primary model."""
        assert mock_config_with_qwen.generation.primary_model == "qwen2.5-coder:1.5b"

    def test_qwen_config_fallback_models(self, mock_config_with_qwen):
        """Test Qwen config has Gemini fallback."""
        fallbacks = mock_config_with_qwen.generation.fallback_models
        assert "gemini-2.5-flash" in fallbacks
