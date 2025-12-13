"""Tests for TTS Generator module (Edge-TTS)."""
from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock

import pytest

from core.generators import tts_generator
from core.utils.config_loader import ProjectConfig, ConfigNode

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
                "edge-tts": {
                    "voice": "ru-RU-SvetlanaNeural",
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

# ============ TESTS ============

class TestRateCalculation:
    """Test rate calculation for Edge-TTS."""

    @patch("core.generators.tts_generator.edge_tts.Communicate")
    @pytest.mark.asyncio
    async def test_rate_formatting(self, mock_communicate_cls, tmp_path):
        """Test that rate is formatted correctly (e.g. +0%, +20%, -10%)."""
        # Configure the instance returned by the class mock
        mock_instance = mock_communicate_cls.return_value
        mock_instance.save = AsyncMock()
        
        # Test 1.0 -> +0%
        await tts_generator._synthesize_edge_tts_async("text", "voice", tmp_path / "1.mp3", speed=1.0)
        args, kwargs = mock_communicate_cls.call_args
        assert kwargs["rate"] == "+0%"
        
        # Test 1.2 -> +20%
        await tts_generator._synthesize_edge_tts_async("text", "voice", tmp_path / "2.mp3", speed=1.2)
        args, kwargs = mock_communicate_cls.call_args
        assert kwargs["rate"] == "+20%"
        
        # Test 0.8 -> -20%
        await tts_generator._synthesize_edge_tts_async("text", "voice", tmp_path / "3.mp3", speed=0.8)
        args, kwargs = mock_communicate_cls.call_args
        assert kwargs["rate"] == "-20%"

class TestSynthesizeModes:
    """Test synthesis for different modes with mocks."""
    
    @patch("core.generators.tts_generator._synthesize_edge_tts_async")
    def test_synthesize_shorts(self, mock_synth, mock_config, sample_script_shorts):
        """Test shorts synthesis calls edge_tts."""
        mock_synth.return_value = 10.0  # duration
        
        result = tts_generator.synthesize(
            mock_config,
            sample_script_shorts,
            "shorts",
            api_key="dummy"
        )
        
        assert result["engine_used"] == "edge-tts"
        assert result["total_duration_sec"] == 10.0
        assert "main" in result["blocks"]
        
        # Verify call
        mock_synth.assert_called_once()
        args = mock_synth.call_args[0] # text, voice, output_path, speed
        assert args[1] == "ru-RU-SvetlanaNeural"  # Voice from config
        assert args[3] == 1.0  # Speed from config

    @patch("core.generators.tts_generator._synthesize_edge_tts_async")
    def test_synthesize_long_form(self, mock_synth, mock_config):
        """Test long-form synthesis."""
        mock_synth.return_value = 5.0
        script = {
            "blocks": {
                "love": "Love text",
                "money": "Money text",
                "health": "Health text"
            }
        }
        
        result = tts_generator.synthesize(
            mock_config,
            script,
            "long_form",
            api_key="dummy"
        )
        
        assert result["engine_used"] == "edge-tts"
        assert result["total_duration_sec"] == 15.0  # 3 blocks * 5.0
        assert len(result["blocks"]) == 3
        assert mock_synth.call_count == 3

    def test_synthesize_missing_api_key(self, mock_config, sample_script_shorts):
        """Test that Edge-TTS works WITHOUT API key (it is not required)."""
        # We need to mock the async call to avoid network
        with patch("core.generators.tts_generator._synthesize_edge_tts_async") as mock_synth:
            mock_synth.return_value = 5.0
            
            # Should NOT raise error
            result = tts_generator.synthesize(
                mock_config,
                sample_script_shorts,
                "shorts",
                api_key=None  # Explicitly None
            )
            assert result["engine_used"] == "edge-tts"

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
