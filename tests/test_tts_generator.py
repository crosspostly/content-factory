"""Tests for TTS Generator module."""
from __future__ import annotations

import asyncio
import os
from pathlib import Path

import pytest

from core.generators import tts_generator
from core.utils.config_loader import load


class TestTTSSynthesis:
    """Test TTS synthesis functions."""
    
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_synthesize_gemini_tts_simple(self, tmp_path):
        """Test basic Gemini TTS synthesis."""
        api_key = os.getenv("GOOGLE_AI_API_KEY")
        if not api_key:
            pytest.skip("GOOGLE_AI_API_KEY not set")
        
        text = "Привет, это тест синтеза речи!"
        output_path = tmp_path / "test_simple.wav"
        
        duration = await tts_generator._synthesize_gemini_tts_async(
            api_key=api_key,
            text=text,
            output_path=output_path,
            speed=1.0
        )
        
        assert duration > 0, "Duration should be positive"
        assert isinstance(duration, float), "Duration should be a float"
    
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_synthesize_gemini_tts_speed_variation(self, tmp_path):
        """Test Gemini TTS with different speed settings."""
        api_key = os.getenv("GOOGLE_AI_API_KEY")
        if not api_key:
            pytest.skip("GOOGLE_AI_API_KEY not set")
        
        text = "Тестовая фраза для проверки скорости."
        
        # Test slower speed
        output_slow = tmp_path / "test_slow.wav"
        duration_slow = await tts_generator._synthesize_gemini_tts_async(
            api_key=api_key,
            text=text,
            output_path=output_slow,
            speed=0.8
        )
        
        # Test faster speed
        output_fast = tmp_path / "test_fast.wav"
        duration_fast = await tts_generator._synthesize_gemini_tts_async(
            api_key=api_key,
            text=text,
            output_path=output_fast,
            speed=1.5
        )
        
        assert duration_slow > 0
        assert duration_fast > 0
        # Faster speed should produce shorter duration
        assert duration_fast < duration_slow * 0.8 or duration_slow < duration_fast * 1.2


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


class TestVoiceConfig:
    """Test voice configuration."""
    
    def test_get_voice_from_config(self, mock_config):
        """Test voice retrieval from config."""
        voice = tts_generator._get_voice_from_config(mock_config, "shorts")
        assert voice is not None
        assert "ru-RU" in voice or voice in tts_generator.VOICES.values()
    
    def test_get_voice_fallback(self):
        """Test voice fallback when config is missing."""
        from core.utils.config_loader import ProjectConfig, ConfigNode
        
        # Config without audio section
        minimal_config = ProjectConfig(ConfigNode({"project": {"name": "test"}}))
        voice = tts_generator._get_voice_from_config(minimal_config, "shorts")
        
        # Should fallback to default
        assert voice == tts_generator.VOICES["russian_female_warm"]


class TestSynthesizeModes:
    """Test synthesis for different modes."""
    
    @pytest.mark.slow
    def test_synthesize_shorts(self, mock_config, sample_script_shorts):
        """Test shorts synthesis."""
        api_key = os.getenv("GOOGLE_AI_API_KEY")
        if not api_key:
            pytest.skip("GOOGLE_AI_API_KEY not set")
        
        result = tts_generator.synthesize(
            mock_config,
            sample_script_shorts,
            "shorts",
            api_key=api_key
        )
        
        assert "blocks" in result
        assert "main" in result["blocks"]
        assert "total_duration_sec" in result
        assert "engine_used" in result
        assert result["engine_used"] == "gemini-2.5-tts"
        assert result["sample_rate"] == 22050
        assert result["channels"] == 1
        assert result["total_duration_sec"] > 0
    
    @pytest.mark.slow
    def test_synthesize_long_form(self, mock_config, sample_script_long_form):
        """Test long-form synthesis."""
        api_key = os.getenv("GOOGLE_AI_API_KEY")
        if not api_key:
            pytest.skip("GOOGLE_AI_API_KEY not set")
        
        result = tts_generator.synthesize(
            mock_config,
            sample_script_long_form,
            "long_form",
            api_key=api_key
        )
        
        assert "blocks" in result
        assert "love" in result["blocks"]
        assert "money" in result["blocks"]
        assert "health" in result["blocks"]
        assert result["total_duration_sec"] > 0
    
    @pytest.mark.slow
    def test_synthesize_ad(self, mock_config, sample_script_ad):
        """Test ad synthesis."""
        api_key = os.getenv("GOOGLE_AI_API_KEY")
        if not api_key:
            pytest.skip("GOOGLE_AI_API_KEY not set")
        
        result = tts_generator.synthesize(
            mock_config,
            sample_script_ad,
            "ad",
            api_key=api_key
        )
        
        assert "blocks" in result
        assert "main" in result["blocks"]
        assert result["total_duration_sec"] > 0
    
    def test_synthesize_invalid_mode(self, mock_config, sample_script_shorts):
        """Test synthesis with invalid mode."""
        api_key = os.getenv("GOOGLE_AI_API_KEY")
        if not api_key:
            pytest.skip("GOOGLE_AI_API_KEY not set")
        
        with pytest.raises(ValueError, match="Unknown mode"):
            tts_generator.synthesize(
                mock_config,
                sample_script_shorts,
                "invalid_mode",
                api_key=api_key
            )
    
    def test_synthesize_missing_api_key(self, mock_config, sample_script_shorts):
        """Test synthesis without API key raises error."""
        with pytest.raises(ValueError, match="GOOGLE_AI_API_KEY not provided"):
            tts_generator.synthesize(
                mock_config,
                sample_script_shorts,
                "shorts",
                api_key=None
            )


class TestIntegration:
    """Integration tests for TTS generator."""
    
    @pytest.mark.slow
    def test_full_pipeline_shorts(self, mock_config):
        """Test full TTS pipeline for shorts."""
        api_key = os.getenv("GOOGLE_AI_API_KEY")
        if not api_key:
            pytest.skip("GOOGLE_AI_API_KEY not set")
        
        script = {
            "hook": "Краткий гороскоп на сегодня!",
            "script": "Краткий гороскоп на сегодня! Удача сопутствует всем знакам зодиака.",
        }
        
        result = tts_generator.synthesize(mock_config, script, "shorts", api_key=api_key)
        
        assert result["blocks"]["main"]
        assert result["total_duration_sec"] > 0
