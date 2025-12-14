"""Tests for slides mode implementation."""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile

from core.content_modes.registry import ContentModeRegistry
from core.content_modes.base import GenerationResult
from core.content_modes.slides_mode.slide_builder import SlideBuilder, Slide
from core.content_modes.slides_mode.slide_renderer import SlideRenderer
from core.content_modes.slides_mode.mode import SlidesMode


class TestSlideBuilder:
    """Test slide builder."""
    
    def test_build_slides_from_simple_text(self):
        """Test building slides from simple text."""
        builder = SlideBuilder(max_chars_per_slide=25)
        text = "Hello world. This is a test. Another slide here."
        
        slides = builder.build_slides(text)
        
        assert len(slides) >= 2
        assert all(isinstance(s, Slide) for s in slides)
        assert all(s.duration > 0 for s in slides)
    
    def test_build_slides_single_sentence(self):
        """Test building slides from single sentence."""
        builder = SlideBuilder()
        text = "This is a single sentence."
        
        slides = builder.build_slides(text)
        
        assert len(slides) == 1
        assert slides[0].text == "This is a single sentence"
    
    def test_build_slides_with_newlines(self):
        """Test building slides from text with newlines."""
        builder = SlideBuilder(max_chars_per_slide=15)
        text = "First line\nSecond line\nThird line"
        
        slides = builder.build_slides(text)
        
        assert len(slides) >= 2
    
    def test_build_slides_empty_text_raises_error(self):
        """Test that empty text raises error."""
        builder = SlideBuilder()
        
        with pytest.raises(ValueError):
            builder.build_slides("")
    
    def test_duration_calculation(self):
        """Test slide duration calculation."""
        builder = SlideBuilder(min_duration=1.0, max_duration=5.0)
        
        # Short text should get minimum duration
        short_slides = builder.build_slides("Hi.")
        assert short_slides[0].duration >= 1.0
        
        # Longer text should get longer duration
        long_text = "This is a longer text that contains more characters and should get a longer duration."
        long_slides = builder.build_slides(long_text)
        assert long_slides[0].duration > 1.0


class TestSlideRenderer:
    """Test slide renderer."""
    
    def test_renderer_initialization(self):
        """Test renderer initialization."""
        renderer = SlideRenderer(
            width=1080,
            height=1920,
            background_color="#2B1B3D",
            text_color="white",
        )
        
        assert renderer.width == 1080
        assert renderer.height == 1920
    
    def test_render_slide(self):
        """Test rendering a slide to image."""
        renderer = SlideRenderer(width=512, height=512)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_slide.png"
            
            result = renderer.render_slide("Test slide", output_path)
            
            assert result.exists()
            assert result.suffix == ".png"
    
    def test_color_parsing_hex(self):
        """Test hex color parsing."""
        renderer = SlideRenderer()
        
        color = renderer._parse_color("#FF0000")
        assert color == (255, 0, 0)
        
        color = renderer._parse_color("#00FF00")
        assert color == (0, 255, 0)
    
    def test_color_parsing_named(self):
        """Test named color parsing."""
        renderer = SlideRenderer()
        
        color = renderer._parse_color("white")
        assert color == (255, 255, 255)
        
        color = renderer._parse_color("black")
        assert color == (0, 0, 0)
    
    def test_text_wrapping(self):
        """Test text wrapping."""
        renderer = SlideRenderer(width=400, height=400)
        
        from PIL import Image, ImageDraw
        img = Image.new("RGB", (400, 400))
        draw = ImageDraw.Draw(img)
        font = renderer._load_font()
        
        long_text = "This is a very long text that should be wrapped into multiple lines"
        lines = renderer._wrap_text(long_text, draw, font)
        
        assert len(lines) > 1


class TestSlidesMode:
    """Test SlidesMode implementation."""
    
    def test_slides_mode_registration(self):
        """Test that SlidesMode is registered."""
        mode = ContentModeRegistry.get("slides")
        assert isinstance(mode, SlidesMode)
    
    def test_slides_mode_properties(self):
        """Test mode properties."""
        mode = SlidesMode()
        
        assert mode.name == "slides"
        assert mode.description
        assert mode.variant == "carousel"
    
    @pytest.mark.asyncio
    async def test_slides_mode_generate_basic(self):
        """Test basic video generation (mocked)."""
        mode = SlidesMode()
        
        scenario = "Slide one. Slide two. Slide three."
        audio_map = {}
        config = {
            "width": 512,
            "height": 512,
            "background_color": "#2B1B3D",
            "text_color": "white",
            "font_size": 32,
            "fps": 30,
            "bitrate": "1000k",
            "transitions": {"type": "fade", "duration": 0.5},
        }
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            
            # Mock moviepy write_videofile to avoid actual encoding
            with patch('core.content_modes.slides_mode.mode.concatenate_videoclips') as mock_concat:
                mock_video = MagicMock()
                mock_video.duration = 6.0
                mock_video.close = MagicMock()
                mock_concat.return_value = mock_video
                
                # Also mock the write_videofile method
                mock_video.write_videofile = MagicMock()
                
                with patch('moviepy.editor.ImageClip') as mock_img_clip:
                    mock_clip = MagicMock()
                    mock_clip.set_duration = MagicMock(return_value=mock_clip)
                    mock_clip.set_audio = MagicMock(return_value=mock_clip)
                    mock_img_clip.return_value = mock_clip
                    
                    result = await mode.generate(
                        scenario=scenario,
                        audio_map=audio_map,
                        config=config,
                        output_dir=output_dir,
                    )
        
        assert isinstance(result, GenerationResult)
        assert result.video_path
        assert result.duration > 0
        assert result.width == 512
        assert result.height == 512
    
    def test_create_renderer_from_config(self):
        """Test creating renderer from config."""
        mode = SlidesMode()
        config = {
            "width": 1920,
            "height": 1080,
            "background_color": "#000000",
            "text_color": "yellow",
            "font_size": 60,
            "font_family": "Arial",
        }
        
        renderer = mode._create_renderer(config)
        
        assert renderer.width == 1920
        assert renderer.height == 1080
        assert renderer.font_size == 60


class TestContentModeRegistry:
    """Test content mode registry."""
    
    def test_registry_get_slides_mode(self):
        """Test getting slides mode from registry."""
        mode = ContentModeRegistry.get("slides")
        assert mode.name == "slides"
    
    def test_registry_get_with_variant(self):
        """Test getting mode with variant."""
        mode = ContentModeRegistry.get("slides", variant="carousel")
        assert mode.variant == "carousel"
    
    def test_registry_invalid_mode_raises_error(self):
        """Test that invalid mode raises error."""
        with pytest.raises(ValueError):
            ContentModeRegistry.get("nonexistent_mode")
    
    def test_registry_list_modes(self):
        """Test listing available modes."""
        modes = ContentModeRegistry.list_modes()
        
        assert "slides" in modes
        assert isinstance(modes["slides"], str)
