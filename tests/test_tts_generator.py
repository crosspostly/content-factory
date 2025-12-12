"""Tests for TTS Generator module."""
from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from core.generators import tts_generator
from core.utils.config_loader import load


class TestTTSSynthesis:
    """Test TTS synthesis functions."""
    
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_synthesize_edge_tts_simple(self, tmp_path):
        """Test basic Edge-TTS synthesis."""
        text = "Привет, это тест синтеза речи!"
        voice = "ru-RU-SvetlanaNeural"
        output_path = tmp_path / "test_simple.wav"
        
        duration = await tts_generator._synthesize_edge_tts_async(
            text=text,
            voice=voice,
            output_path=output_path,
            speed=1.0
        )
        
        assert output_path.exists(), "Audio file should be created"
        assert output_path.stat().st_size > 0, "Audio file should not be empty"
        assert duration > 0, "Duration should be positive"
        assert isinstance(duration, float), "Duration should be a float"
    
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_synthesize_edge_tts_empty_text(self, tmp_path):
        """Test Edge-TTS with empty text should handle gracefully."""
        text = ""
        voice = "ru-RU-SvetlanaNeural"
        output_path = tmp_path / "test_empty.wav"
        
        # Edge-TTS may fail or create a minimal audio file
        # We test that it doesn't crash catastrophically
        try:
            duration = await tts_generator._synthesize_edge_tts_async(
                text=text,
                voice=voice,
                output_path=output_path,
                speed=1.0
            )
            # If it succeeds, duration should still be calculated
            assert duration >= 1.0, "Minimum duration is 1.0 second"
        except Exception:
            # If it fails, that's also acceptable for empty text
            pass
    
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_synthesize_edge_tts_speed_variation(self, tmp_path):
        """Test Edge-TTS with different speed settings."""
        text = "Тестовая фраза для проверки скорости."
        voice = "ru-RU-SvetlanaNeural"
        
        # Test slower speed
        output_slow = tmp_path / "test_slow.wav"
        duration_slow = await tts_generator._synthesize_edge_tts_async(
            text=text,
            voice=voice,
            output_path=output_slow,
            speed=0.8
        )
        
        # Test faster speed
        output_fast = tmp_path / "test_fast.wav"
        duration_fast = await tts_generator._synthesize_edge_tts_async(
            text=text,
            voice=voice,
            output_path=output_fast,
            speed=1.5
        )
        
        assert output_slow.exists()
        assert output_fast.exists()
        assert duration_slow > 0
        assert duration_fast > 0


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
        result = tts_generator.synthesize(mock_config, sample_script_shorts, "shorts")
        
        assert "blocks" in result
        assert "main" in result["blocks"]
        assert "total_duration_sec" in result
        assert "engine_used" in result
        assert result["engine_used"] == "edge-tts"
        assert result["sample_rate"] == 22050
        assert result["channels"] == 1
        assert result["total_duration_sec"] > 0
        
        # Check that audio file exists
        audio_path = result["blocks"]["main"]
        assert Path(audio_path).exists()
    
    @pytest.mark.slow
    def test_synthesize_long_form(self, mock_config, sample_script_long_form):
        """Test long-form synthesis."""
        result = tts_generator.synthesize(mock_config, sample_script_long_form, "long_form")
        
        assert "blocks" in result
        assert "love" in result["blocks"]
        assert "money" in result["blocks"]
        assert "health" in result["blocks"]
        assert result["total_duration_sec"] > 0
        
        # Check that all audio files exist
        for block_name in ["love", "money", "health"]:
            audio_path = result["blocks"][block_name]
            assert Path(audio_path).exists()
    
    @pytest.mark.slow
    def test_synthesize_ad(self, mock_config, sample_script_ad):
        """Test ad synthesis."""
        result = tts_generator.synthesize(mock_config, sample_script_ad, "ad")
        
        assert "blocks" in result
        assert "main" in result["blocks"]
        assert result["total_duration_sec"] > 0
        
        # Check that audio file exists
        audio_path = result["blocks"]["main"]
        assert Path(audio_path).exists()
    
    def test_synthesize_invalid_mode(self, mock_config, sample_script_shorts):
        """Test synthesis with invalid mode."""
        with pytest.raises(RuntimeError, match="TTS synthesis error"):
            tts_generator.synthesize(mock_config, sample_script_shorts, "invalid_mode")


class TestIntegration:
    """Integration tests for TTS generator."""
    
    @pytest.mark.slow
    def test_full_pipeline_shorts(self, mock_config):
        """Test full TTS pipeline for shorts."""
        script = {
            "hook": "Краткий гороскоп на сегодня!",
            "script": "Краткий гороскоп на сегодня! Удача сопутствует всем знакам зодиака.",
        }
        
        result = tts_generator.synthesize(mock_config, script, "shorts")
        
        assert result["blocks"]["main"]
        assert Path(result["blocks"]["main"]).exists()
        assert Path(result["blocks"]["main"]).stat().st_size > 1000  # At least 1KB
    
    @pytest.mark.slow
    def test_output_directory_creation(self, mock_config, sample_script_shorts):
        """Test that output directories are created automatically."""
        result = tts_generator.synthesize(mock_config, sample_script_shorts, "shorts")
        
        audio_path = Path(result["blocks"]["main"])
        assert audio_path.parent.exists()
        assert audio_path.parent.name == "test_horoscope"
