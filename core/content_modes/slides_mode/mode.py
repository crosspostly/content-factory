"""Slides mode implementation for carousel-style videos."""

import logging
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
import tempfile
import os

from moviepy.editor import (
    ImageClip, AudioFileClip, CompositeVideoClip,
    concatenate_videoclips, vfx, ColorClip
)

from core.content_modes.base import BaseContentMode, GenerationResult
from core.content_modes.registry import register_mode
from .slide_builder import SlideBuilder
from .slide_renderer import SlideRenderer

logger = logging.getLogger(__name__)


@register_mode("slides")
class SlidesMode(BaseContentMode):
    """
    Generate videos from text by rendering slides and combining with audio.
    
    Pipeline:
    1. Split text into slides
    2. Render each slide as an image
    3. Combine slides with audio and transitions
    4. Export final video
    """
    
    def __init__(self, variant: str = "carousel"):
        """
        Initialize SlidesMode.
        
        Args:
            variant: Variant type ('carousel' is default)
        """
        super().__init__(variant=variant)
        self.temp_dir = Path(tempfile.gettempdir()) / "content-factory"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    @property
    def name(self) -> str:
        """Get mode name."""
        return "slides"
    
    @property
    def description(self) -> str:
        """Get mode description."""
        return "Generate carousel-style videos from text slides"
    
    async def generate(
        self,
        scenario: str,
        audio_map: Dict[str, str],
        config: Dict[str, Any],
        output_dir: Optional[Path] = None,
    ) -> GenerationResult:
        """
        Generate video from text scenario.
        
        Args:
            scenario: Text content (full scenario or joined slides)
            audio_map: Mapping of slide text to audio file paths
            config: Design configuration (colors, font, dimensions)
            output_dir: Output directory for generated files
            
        Returns:
            GenerationResult with video path and metadata
        """
        if output_dir is None:
            output_dir = Path(tempfile.gettempdir()) / "content-factory"
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # 1. Build slides from text
            logger.info("📝 Building slides from text...")
            slide_builder = SlideBuilder()
            slides = slide_builder.build_slides(scenario)
            logger.info(f"✅ Created {len(slides)} slides")
            
            # 2. Render slides to images
            logger.info("🎨 Rendering slide images...")
            renderer = self._create_renderer(config)
            slide_images = await self._render_slides(renderer, slides, output_dir)
            logger.info(f"✅ Rendered {len(slide_images)} slide images")
            
            # 3. Assign audio to slides
            logger.info("🔊 Processing audio...")
            self._assign_audio_to_slides(slides, audio_map)
            
            # 4. Create video clips for each slide
            logger.info("🎬 Creating video clips...")
            video_clips = self._create_video_clips(
                slides,
                slide_images,
                renderer.width,
                renderer.height,
            )
            
            # 5. Combine clips with transitions
            logger.info("🔀 Combining clips with transitions...")
            final_video = self._combine_clips(
                video_clips,
                config.get("transitions", {}),
            )
            
            # 6. Export video
            logger.info("💾 Exporting video...")
            output_path = output_dir / "output.mp4"
            fps = config.get("fps", 30)
            bitrate = config.get("bitrate", "5000k")
            
            final_video.write_videofile(
                str(output_path),
                fps=fps,
                codec="libx264",
                audio_codec="aac",
                bitrate=bitrate,
                verbose=False,
                logger=None,
            )
            
            duration = final_video.duration
            
            logger.info(f"✅ Video generated: {output_path}")
            logger.info(f"   Duration: {duration:.2f}s")
            logger.info(f"   Resolution: {renderer.width}x{renderer.height}")
            
            # Cleanup
            final_video.close()
            
            return GenerationResult(
                video_path=str(output_path),
                duration=duration,
                width=renderer.width,
                height=renderer.height,
                metadata={
                    "slides_count": len(slides),
                    "variant": self.variant,
                    "fps": fps,
                },
            )
        
        except Exception as e:
            logger.error(f"❌ Error generating video: {e}", exc_info=True)
            raise
    
    def _create_renderer(self, config: Dict[str, Any]) -> SlideRenderer:
        """Create a slide renderer from config."""
        return SlideRenderer(
            width=config.get("width", 1080),
            height=config.get("height", 1920),
            background_color=config.get("background_color", "#2B1B3D"),
            text_color=config.get("text_color", "white"),
            font_size=config.get("font_size", 70),
            font_family=config.get("font_family", "Arial"),
        )
    
    async def _render_slides(
        self,
        renderer: SlideRenderer,
        slides,
        output_dir: Path,
    ) -> Dict[int, Path]:
        """Render all slides to image files."""
        slide_images = {}
        slides_dir = output_dir / "slides"
        slides_dir.mkdir(parents=True, exist_ok=True)
        
        for slide in slides:
            image_path = slides_dir / f"slide_{slide.index:03d}.png"
            renderer.render_slide(slide.text, image_path)
            slide_images[slide.index] = image_path
        
        return slide_images
    
    def _assign_audio_to_slides(
        self,
        slides,
        audio_map: Dict[str, str],
    ) -> None:
        """Assign audio files to slides based on text matching."""
        for slide in slides:
            # Try exact match first
            if slide.text in audio_map:
                slide.audio_path = audio_map[slide.text]
            else:
                # Try partial match (first 50 chars)
                text_key = slide.text[:50]
                for key, path in audio_map.items():
                    if key.startswith(text_key) or slide.text.startswith(key):
                        slide.audio_path = path
                        break
    
    def _create_video_clips(
        self,
        slides,
        slide_images: Dict[int, Path],
        width: int,
        height: int,
    ):
        """Create video clips for each slide with audio."""
        clips = []
        
        for slide in slides:
            # Create image clip
            image_path = slide_images.get(slide.index)
            if not image_path:
                logger.warning(f"No image for slide {slide.index}")
                continue
            
            img_clip = ImageClip(str(image_path))
            
            # Add audio if available
            duration = slide.duration
            if slide.audio_path and Path(slide.audio_path).exists():
                try:
                    audio_clip = AudioFileClip(slide.audio_path)
                    duration = max(duration, audio_clip.duration)
                    img_clip = img_clip.set_audio(audio_clip)
                except Exception as e:
                    logger.warning(f"Could not load audio for slide {slide.index}: {e}")
            
            # Set duration
            img_clip = img_clip.set_duration(duration)
            clips.append(img_clip)
        
        return clips
    
    def _combine_clips(
        self,
        clips,
        transitions_config: Dict[str, Any],
    ):
        """Combine video clips with transitions."""
        if not clips:
            raise ValueError("No video clips to combine")
        
        transition_type = transitions_config.get("type", "fade")
        transition_duration = transitions_config.get("duration", 0.5)
        
        # Apply transition effects
        if transition_type == "fade":
            # Apply fade effect to each clip except the first
            for i in range(1, len(clips)):
                clips[i] = clips[i].fadein(transition_duration)
                # Also fade out the previous clip slightly
                # clips[i-1] = clips[i-1].fadeout(transition_duration)
        
        # Concatenate clips
        final_video = concatenate_videoclips(clips, method="chain")
        
        return final_video
