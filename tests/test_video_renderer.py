"""Tests for Video Renderer module."""
from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from core.generators import video_renderer, tts_generator
from core.utils.config_loader import load

# Mock google.genai to prevent import errors
import sys
if 'google.genai' not in sys.modules:
    sys.modules['google'] = MagicMock()
    sys.modules['google.genai'] = MagicMock()


class TestBackgroundGeneration:
    """Test background video/image generation."""
    
    def test_create_background_clip(self):
        """Test gradient background creation."""
        width, height = 1080, 1920
        duration = 5.0
        fps = 30
        
        clip = video_renderer._create_background_clip(
            width=width,
            height=height,
            duration=duration,
            fps=fps,
            style="mystical"
        )
        
        assert clip is not None
        assert clip.duration == duration
        assert clip.size == (width, height)
    
    def test_create_background_different_styles(self):
        """Test different background styles."""
        width, height = 1920, 1080
        duration = 3.0
        fps = 30
        
        for style in ["mystical", "intro", "outro", "love", "money", "health", "ad"]:
            clip = video_renderer._create_background_clip(
                width=width,
                height=height,
                duration=duration,
                fps=fps,
                style=style
            )
            assert clip is not None
            assert clip.duration == duration


class TestTextOverlay:
    """Test text overlay generation."""
    
    def test_create_text_frame(self):
        """Test PIL text frame creation."""
        text = "Тестовый текст"
        width, height = 1080, 1920
        
        img = video_renderer._create_text_frame(
            text=text,
            width=width,
            height=height,
            font_size=50,
            color=(255, 255, 255)
        )
        
        assert img is not None
        assert img.size == (width, height)
        assert img.mode == "RGBA"
    
    def test_create_text_frame_long_text(self):
        """Test text wrapping for long text."""
        text = "Это очень длинный текст, который должен автоматически переноситься на несколько строк для корректного отображения."
        width, height = 1080, 1920
        
        img = video_renderer._create_text_frame(
            text=text,
            width=width,
            height=height,
            font_size=40
        )
        
        assert img is not None
        assert img.size == (width, height)


class TestPixabayIntegration:
    """Test Pixabay API integration."""
    
    @patch('requests.get')
    def test_get_pixabay_video_success(self, mock_get):
        """Test successful Pixabay video retrieval."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "hits": [
                {
                    "videos": {
                        "medium": {
                            "url": "https://example.com/video.mp4",
                            "width": 1280,
                            "height": 720
                        }
                    }
                }
            ]
        }
        mock_get.return_value = mock_response
        
        api_key = "test_api_key"
        query = "stars"
        duration = 10.0
        
        url = video_renderer._get_pixabay_video(api_key, query, duration)
        
        assert url is not None
        assert "example.com" in url
    
    @patch('requests.get')
    def test_get_pixabay_video_no_results(self, mock_get):
        """Test Pixabay with no results."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"hits": []}
        mock_get.return_value = mock_response
        
        api_key = "test_api_key"
        query = "nonexistent"
        duration = 10.0
        
        url = video_renderer._get_pixabay_video(api_key, query, duration)
        
        assert url is None
    
    @patch('requests.get')
    def test_get_pixabay_video_api_error(self, mock_get):
        """Test Pixabay API error handling."""
        mock_get.side_effect = Exception("API Error")
        
        api_key = "test_api_key"
        query = "stars"
        duration = 10.0
        
        url = video_renderer._get_pixabay_video(api_key, query, duration)
        
        assert url is None


class TestVideoRendering:
    """Test video rendering for different modes."""
    
    @pytest.mark.slow
    def test_render_shorts_no_pixabay(self, mock_config, sample_script_shorts, tmp_path):
        """Test shorts rendering without Pixabay (gradient background)."""
        # First generate audio
        audio_result = tts_generator.synthesize(mock_config, sample_script_shorts, "shorts", api_key="test-key")
        
        # Remove PIXABAY_API_KEY to force gradient background
        original_key = os.environ.get("PIXABAY_API_KEY")
        if original_key:
            del os.environ["PIXABAY_API_KEY"]
        
        try:
            video_path = video_renderer.render(
                config=mock_config,
                script=sample_script_shorts,
                audio_map=audio_result,
                mode="shorts"
            )
            
            assert video_path.exists(), "Video file should be created"
            assert video_path.suffix == ".mp4", "Video should be MP4"
            assert video_path.stat().st_size > 10000, "Video should not be tiny"
        
        finally:
            # Restore original key
            if original_key:
                os.environ["PIXABAY_API_KEY"] = original_key
    
    @pytest.mark.slow
    def test_render_long_form(self, mock_config, sample_script_long_form):
        """Test long-form video rendering."""
        # First generate audio
        audio_result = tts_generator.synthesize(mock_config, sample_script_long_form, "long_form", api_key="test-key")
        
        video_path = video_renderer.render(
            config=mock_config,
            script=sample_script_long_form,
            audio_map=audio_result,
            mode="long_form"
        )
        
        assert video_path.exists(), "Video file should be created"
        assert video_path.suffix == ".mp4", "Video should be MP4"
        assert video_path.stat().st_size > 10000, "Video should not be tiny"
    
    @pytest.mark.slow
    def test_render_ad(self, mock_config, sample_script_ad):
        """Test ad video rendering."""
        # First generate audio
        audio_result = tts_generator.synthesize(mock_config, sample_script_ad, "ad", api_key="test-key")
        
        video_path = video_renderer.render(
            config=mock_config,
            script=sample_script_ad,
            audio_map=audio_result,
            mode="ad"
        )
        
        assert video_path.exists(), "Video file should be created"
        assert video_path.suffix == ".mp4", "Video should be MP4"
        assert video_path.stat().st_size > 10000, "Video should not be tiny"
    
    @pytest.mark.slow
    def test_render_invalid_mode(self, mock_config, sample_script_shorts):
        """Test rendering with invalid mode."""
        audio_result = tts_generator.synthesize(mock_config, sample_script_shorts, "shorts", api_key="test-key")
        
        with pytest.raises(RuntimeError, match="Unknown mode"):
            video_renderer.render(
                config=mock_config,
                script=sample_script_shorts,
                audio_map=audio_result,
                mode="invalid_mode"
            )


class TestVideoConfig:
    """Test video configuration constants."""
    
    def test_video_config_structure(self):
        """Test that video config has all required modes."""
        assert "shorts" in video_renderer.VIDEO_CONFIG
        assert "long_form" in video_renderer.VIDEO_CONFIG
        assert "ad" in video_renderer.VIDEO_CONFIG
        
        for mode, config in video_renderer.VIDEO_CONFIG.items():
            assert "width" in config
            assert "height" in config
            assert "aspect" in config
            assert "fps" in config
            assert "bitrate" in config
    
    def test_shorts_resolution(self):
        """Test shorts has correct vertical resolution."""
        config = video_renderer.VIDEO_CONFIG["shorts"]
        assert config["width"] == 1080
        assert config["height"] == 1920
        assert config["aspect"] == "9:16"
    
    def test_long_form_resolution(self):
        """Test long-form has correct horizontal resolution."""
        config = video_renderer.VIDEO_CONFIG["long_form"]
        assert config["width"] == 1920
        assert config["height"] == 1080
        assert config["aspect"] == "16:9"


class TestIntegration:
    """Integration tests for video renderer."""
    
    @pytest.mark.slow
    def test_full_pipeline_shorts(self, mock_config):
        """Test full TTS + Video pipeline for shorts."""
        script = {
            "hook": "Гороскоп дня!",
            "script": "Гороскоп дня! Успех ждет всех знаков зодиака.",
        }
        
        # Generate audio
        audio_result = tts_generator.synthesize(mock_config, script, "shorts", api_key="test-key")
        
        # Generate video
        video_path = video_renderer.render(
            config=mock_config,
            script=script,
            audio_map=audio_result,
            mode="shorts"
        )
        
        assert video_path.exists()
        assert video_path.stat().st_size > 20000  # At least 20KB (lowered due to silent audio)
    
    @pytest.mark.slow
    def test_output_directory_structure(self, mock_config, sample_script_shorts):
        """Test that output directories are created with correct structure."""
        audio_result = tts_generator.synthesize(mock_config, sample_script_shorts, "shorts", api_key="test-key")
        video_path = video_renderer.render(
            config=mock_config,
            script=sample_script_shorts,
            audio_map=audio_result,
            mode="shorts"
        )
        
        # Check directory structure
        assert video_path.parent.exists()
        assert video_path.parent.name == "test_horoscope"
        assert video_path.parent.parent.name == "videos"
