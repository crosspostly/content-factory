"""Advanced tests for ModelRouter with Auto-Fix Agent scenarios."""
from __future__ import annotations

import json
import pytest
from unittest.mock import MagicMock, patch, call
from core.utils.model_router import ModelRouter, get_router, reset_router

@pytest.fixture
def router():
    reset_router()
    return get_router("test-api-key")

class TestModelRouterFallback:
    """Test ModelRouter fallback and retry logic."""
    
    @patch("core.utils.model_router.ModelRouter._call_ollama_api")
    @patch("core.utils.model_router.ModelRouter._call_gemini_api")
    def test_error_analysis_fallback(self, mock_gemini, mock_ollama, router):
        """Test fallback from Qwen (Ollama) to Gemini for error_analysis."""
        # Qwen fails
        mock_ollama.return_value = None
        # Gemini succeeds
        mock_gemini.return_value = "Gemini Analysis"
        
        response = router.generate("error_analysis", "Analyze error")
        
        assert response == "Gemini Analysis"
        # Verify Qwen was tried (primary for error_analysis)
        assert mock_ollama.called
        # Verify Gemini was tried (fallback)
        assert mock_gemini.called

    @patch("core.utils.model_router.ModelRouter._call_ollama_api")
    @patch("core.utils.model_router.ModelRouter._call_gemini_api")
    def test_error_analysis_primary_success(self, mock_gemini, mock_ollama, router):
        """Test Qwen (Ollama) succeeds, Gemini not called."""
        mock_ollama.return_value = "Qwen Analysis"
        
        response = router.generate("error_analysis", "Analyze error")
        
        assert response == "Qwen Analysis"
        assert mock_ollama.called
        assert not mock_gemini.called

    @patch("core.utils.model_router.ModelRouter._call_gemini_api")
    @patch("time.sleep") # speed up tests
    def test_retry_logic(self, mock_sleep, mock_gemini, router):
        """Test retry logic on failure."""
        # First 2 attempts fail, 3rd succeeds
        mock_gemini.side_effect = [Exception("Fail 1"), Exception("Fail 2"), "Success"]
        
        # task 'script' uses Gemini as primary
        response = router.generate("script", "Write script")
        
        assert response == "Success"
        assert mock_gemini.call_count == 3
        assert mock_sleep.call_count == 2 # 2 retries = 2 sleeps

    @patch("core.utils.model_router.ModelRouter._call_gemini_api")
    def test_exhausted_retries(self, mock_gemini, router):
        """Test exception raised when all retries exhausted."""
        mock_gemini.side_effect = Exception("Permanent Failure")
        
        # 'script' task has primary and fallback, both are Gemini models (different versions)
        # Each model has 3 retries.
        # So we expect 6 calls total (3 for primary, 3 for fallback)
        
        with pytest.raises(RuntimeError) as exc:
            router.generate("script", "Write script")
            
        assert "All models exhausted" in str(exc.value)
        assert mock_gemini.call_count == 6


class TestModelRouterJson:
    """Test JSON generation and repair."""
    
    @patch("core.utils.model_router.ModelRouter.generate")
    def test_generate_json_success(self, mock_generate, router):
        """Test successful JSON generation."""
        mock_generate.return_value = '```json\n{"key": "value"}\n```'
        
        result = router.generate_json("script", "prompt")
        
        assert result == {"key": "value"}
        
    @patch("core.utils.model_router.ModelRouter.generate")
    def test_generate_json_repair(self, mock_generate, router):
        """Test JSON repair logic."""
        # First call returns bad JSON
        # Second call (repair) returns good JSON
        mock_generate.side_effect = [
            '{"key": "value"', # Missing closing brace
            '{"key": "value"}' # Repaired
        ]
        
        result = router.generate_json("script", "prompt")
        
        assert result == {"key": "value"}
        assert mock_generate.call_count == 2
        
