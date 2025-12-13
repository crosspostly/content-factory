"""Tests for TTS Generator module (Gemini TTS)."""
from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock
import asyncio

import pytest

from core.generators import tts_generator
from core.utils.config_loader import ProjectConfig, ConfigNode

# Mock google.genai to prevent import errors
import sys
if 'google.genai' not in sys.modules:
    sys.modules['google'] = MagicMock()
    sys.modules['google.genai'] = MagicMock()

# ============ FIXTURES ============

@pytest.fixture
def mock_config():
    """Create a mock project config."""
    config_data = {
        "project": {
            "name": "test_project",
            "language": "russian"
        },
        "audio": {
            "engines": {
                "gemini-tts": {
                    "speed": 1.0
                }
            }
        }
    }
    return ProjectConfig(ConfigNode(config_data))

@pytest.fixture
def sample_script_shorts():
    return {
        "hook": "Test hook",
        "script": "Test script content for shorts."
    }

@pytest.fixture
def sample_script_long_form():
    return {
        "blocks": {
            "love": "Love text",
            "money": "Money text",
            "health": "Health text"
        }
    }

# ============ TESTS ============

class TestGeminiTTSSynthesis:
    """Test Gemini TTS synthesis."""

    @patch("core.generators.tts_generator._convert_mp3_to_wav")
    @patch("core.generators.tts_generator.genai.Client")
    def test_synthesize_gemini_tts_basic(self, mock_client_class, mock_convert, tmp_path):
        """Test basic Gemini TTS synthesis."""
        # Setup mocks
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.audio = b"mock_mp3_data"
        mock_client.models.generate_content.return_value = mock_response
        
        # Mock audio conversion
        mock_convert.return_value = 5.0
        
        # Test synthesis (run async function)
        duration = asyncio.run(tts_generator._synthesize_gemini_tts_async(
            api_key="test-key",
            text="Test text",
            output_path=tmp_path / "test.wav",
            speed=1.0
        ))
        
        assert duration == 5.0
        mock_convert.assert_called_once()
    
    def test_synthesize_missing_api_key(self, mock_config, sample_script_shorts):
        """Test that synthesis without API key raises error."""
        with pytest.raises(ValueError, match="GOOGLE_AI_API_KEY"):
            tts_generator.synthesize(
                mock_config,
                sample_script_shorts,
                "shorts",
                api_key=None
            )

class TestSynthesizeModes:
    """Test synthesis for different modes with mocks."""
    
    @patch("core.generators.tts_generator._synthesize_gemini_tts_async")
    def test_synthesize_shorts(self, mock_synth, mock_config, sample_script_shorts):
        """Test shorts synthesis uses Gemini TTS."""
        async def mock_return(*args, **kwargs):
            return 10.0
        mock_synth.side_effect = mock_return        
        result = tts_generator.synthesize(
            mock_config,
            sample_script_shorts,
            "shorts",
            api_key="test-key"
        )
        
        assert result["engine_used"] == "gemini-2.5-tts"
        assert result["total_duration_sec"] == 10.0
        assert "main" in result["blocks"]

    @patch("core.generators.tts_generator._synthesize_gemini_tts_async")
    def test_synthesize_long_form(self, mock_synth, mock_config, sample_script_long_form):
        """Test long-form synthesis with Gemini TTS."""
        # Mock the async function
        async def async_return_dict(val):
            return {
                "love": f"path_love_{val}",
                "money": f"path_money_{val}",
                "health": f"path_health_{val}"
            }, val * 3
        
        # For long_form, we call it 3 times and need to mock differently
        call_count = [0]
        
        async def mock_async_func(*args, **kwargs):
            call_count[0] += 1
            return 5.0
        
        mock_synth.side_effect = mock_async_func
        
        result = tts_generator.synthesize(
            mock_config,
            sample_script_long_form,
            "long_form",
            api_key="test-key"
        )
        
        assert result["engine_used"] == "gemini-2.5-tts"
        assert result["total_duration_sec"] == 15.0  # 3 blocks * 5.0
        assert len(result["blocks"]) == 3
        assert "love" in result["blocks"]
        assert "money" in result["blocks"]
        assert "health" in result["blocks"]
    
    @patch("core.generators.tts_generator._synthesize_gemini_tts_async")
    def test_synthesize_ad(self, mock_synth, mock_config):
        """Test ad synthesis with Gemini TTS."""
                async def mock_return(*args, **kwargs):
            return 3.0
        mock_synth.side_effect = mock_return

        
        script = {
            "narration_text": "Ad text here"
        }
        
        result = tts_generator.synthesize(
            mock_config,
            script,
            "ad",
            api_key="test-key"
        )
        
        assert result["engine_used"] == "gemini-2.5-tts"
        assert result["total_duration_sec"] == 3.0
        assert "main" in result["blocks"]
    
    def test_synthesize_invalid_mode(self, mock_config, sample_script_shorts):
        """Test synthesis with invalid mode."""
        with pytest.raises(RuntimeError, match="Unknown mode"):
            tts_generator.synthesize(
                mock_config,
                sample_script_shorts,
                "invalid_mode",
                api_key="test-key"
            )

class TestTextSanitization:
    """Test text sanitization for TTS."""
    
    def test_sanitize_html_tags(self):
        """Test removal of HTML tags."""
        text = "<p>Привет <b>мир</b></p>"
        result = tts_generator._sanitize_text_for_tts(text)
        assert "<" not in result
        assert ">" not in result
        assert "Привет мир" in result
    
    def test_sanitize_markdown(self):
        """Test removal of markdown formatting."""
        text = "**Жирный** и *курсив* текст"
        result = tts_generator._sanitize_text_for_tts(text)
        assert "**" not in result
        assert "*" not in result
        assert "Жирный" in result
        assert "курсив" in result
    
    def test_sanitize_abbreviations(self):
        """Test replacement of common abbreviations."""
        text = "ПН, ВТ, СР"
        result = tts_generator._sanitize_text_for_tts(text)
        assert "понедельник" in result
        assert "вторник" in result
        assert "среда" in result
    
    def test_sanitize_whitespace(self):
        """Test removal of excessive whitespace."""
        text = "Много    пробелов   здесь"
        result = tts_generator._sanitize_text_for_tts(text)
        assert "  " not in result
        assert result == "Много пробелов здесь"
