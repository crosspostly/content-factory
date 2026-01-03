#!/usr/bin/env python3
"""
Video Assembly Script - Production Ready
Assembles video from chapter data (images + audio + subtitles).
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Optional, Tuple

from PIL import Image
from moviepy.editor import (
    ImageClip,
    AudioFileClip,
    concatenate_videoclips,
    TextClip,
    CompositeVideoClip,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('video_assembly.log')
    ]
)
logger = logging.getLogger(__name__)


class VideoAssembler:
    """Assembles production video from chapter components."""

    def __init__(self, fps: int = 30, output_dir: str = "."):
        """
        Initialize VideoAssembler.
        
        Args:
            fps: Frames per second
            output_dir: Output directory
        """
        self.fps = fps
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"✅ Initialized VideoAssembler (fps={fps})")

    def load_images_as_clips(
        self,
        images_dir: str,
        duration_per_image: float = 3.0
    ) -> list:
        """
        Load images from directory and convert to video clips.
        
        Args:
            images_dir: Directory with images
            duration_per_image: How long each image displays
            
        Returns:
            List of ImageClip objects
        """
        images_path = Path(images_dir)
        
        if not images_path.exists():
            raise FileNotFoundError(f"❌ Images directory not found: {images_path}")
        
        # Find all images (sorted by name)
        image_files = sorted(
            list(images_path.glob("*.png")) +
            list(images_path.glob("*.jpg")) +
            list(images_path.glob("*.jpeg"))
        )
        
        if not image_files:
            raise ValueError(f"❌ No images found in {images_path}")
        
        logger.info(f"📸 Found {len(image_files)} images")
        
        clips = []
        for img_file in image_files:
            try:
                # Load image and create clip
                img = Image.open(img_file)
                logger.info(f"   Loading: {img_file.name} ({img.size[0]}x{img.size[1]})")
                
                clip = ImageClip(str(img_file)).set_duration(duration_per_image)
                clips.append(clip)
            except Exception as e:
                logger.warning(f"   ⚠️  Failed to load {img_file.name}: {e}")
                continue
        
        if not clips:
            raise ValueError("❌ No valid images could be loaded")
        
        logger.info(f"✅ Loaded {len(clips)} video clips from images")
        return clips

    def load_audio(
        self,
        audio_file: str,
        target_duration: Optional[float] = None
    ) -> Optional[AudioFileClip]:
        """
        Load audio file and optionally trim to duration.
        
        Args:
            audio_file: Path to audio file
            target_duration: If set, trim audio to this duration
            
        Returns:
            AudioFileClip or None
        """
        audio_path = Path(audio_file)
        
        if not audio_path.exists():
            logger.warning(f"⚠️  Audio file not found: {audio_file}")
            return None
        
        try:
            audio = AudioFileClip(str(audio_path))
            logger.info(f"🔊 Loaded audio: {audio_path.name} ({audio.duration:.1f}s)")
            
            # Trim if needed
            if target_duration and audio.duration > target_duration:
                logger.info(f"   Trimming audio from {audio.duration:.1f}s to {target_duration:.1f}s")
                audio = audio.subclipped(0, target_duration)
            
            return audio
        except Exception as e:
            logger.error(f"❌ Failed to load audio: {e}")
            return None

    def load_subtitles(
        self,
        subtitles_file: str
    ) -> Optional[dict]:
        """
        Load subtitles from SRT file.
        
        Args:
            subtitles_file: Path to .srt file
            
        Returns:
            Subtitles dict or None
        """
        subtitles_path = Path(subtitles_file)
        
        if not subtitles_path.exists():
            logger.warning(f"⚠️  Subtitles file not found: {subtitles_file}")
            return None
        
        try:
            # Simple SRT parser
            subtitles = {}
            with open(subtitles_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # For now, just validate it's readable
            if len(content) > 0:
                logger.info(f"📝 Loaded subtitles: {subtitles_path.name}")
                return {"path": str(subtitles_path), "data": content}
            
            return None
        except Exception as e:
            logger.error(f"❌ Failed to load subtitles: {e}")
            return None

    def assemble_from_chapter(
        self,
        chapter_dir: str,
        output_file: str = "final_video.mp4",
        image_duration: float = 3.0
    ) -> str:
        """
        Assemble video from chapter directory.
        
        Expected structure:
        chapter_dir/
        ├── images/
        │   ├── 001.png
        │   ├── 002.png
        │   └── ...
        ├── audio.wav (or .mp3)
        ├── subtitles.srt
        └── metadata.json (optional)
        
        Args:
            chapter_dir: Path to chapter directory
            output_file: Output MP4 filename
            image_duration: Duration per image in seconds
            
        Returns:
            Path to output video
        """
        chapter_path = Path(chapter_dir)
        
        if not chapter_path.exists():
            raise FileNotFoundError(f"❌ Chapter directory not found: {chapter_path}")
        
        logger.info(f"\n🎬 ===== ASSEMBLING VIDEO FROM CHAPTER =====")
        logger.info(f"   Chapter: {chapter_path.absolute()}")
        logger.info(f"")
        
        # Load images
        images_dir = chapter_path / "images"
        clips = self.load_images_as_clips(str(images_dir), image_duration)
        
        # Concatenate clips
        logger.info(f"\n⛓️  Concatenating {len(clips)} clips...")
        video = concatenate_videoclips(clips, method="chain")
        video_duration = video.duration
        logger.info(f"✅ Video duration: {video_duration:.1f}s")
        
        # Load audio
        logger.info(f"")
        audio_candidates = [
            chapter_path / "audio.wav",
            chapter_path / "audio.mp3",
            chapter_path / "audio.m4a",
        ]
        audio = None
        for audio_file in audio_candidates:
            if audio_file.exists():
                audio = self.load_audio(str(audio_file), target_duration=video_duration)
                break
        
        if audio:
            video = video.set_audio(audio)
        
        # Load subtitles (optional - just log)
        logger.info(f"")
        subtitles_file = chapter_path / "subtitles.srt"
        subtitles = self.load_subtitles(str(subtitles_file))
        
        # Load metadata (optional)
        logger.info(f"")
        metadata_file = chapter_path / "metadata.json"
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                logger.info(f"📋 Metadata: {json.dumps(metadata, indent=2)}")
            except Exception as e:
                logger.warning(f"⚠️  Failed to load metadata: {e}")
        
        # Write video
        logger.info(f"\n💾 Writing video file...")
        output_path = self.output_dir / output_file
        
        try:
            video.write_videofile(
                str(output_path),
                fps=self.fps,
                codec='libx264',
                audio_codec='aac',
                preset='ultrafast',
                threads=4,
                verbose=False,
                logger=None,
            )
            logger.info(f"✅ Video created: {output_path}")
            logger.info(f"   Size: {output_path.stat().st_size / (1024*1024):.1f} MB")
            return str(output_path)
        except Exception as e:
            logger.error(f"❌ Failed to write video: {e}", exc_info=True)
            raise
        finally:
            video.close()
            if audio:
                try:
                    audio.close()
                except:
                    pass


def find_chapter_directories() -> list:
    """
    Find all chapter directories in standard location.
    
    Returns:
        List of chapter directories
    """
    chapters_root = Path("chapters")
    if not chapters_root.exists():
        return []
    
    chapters = sorted([
        d for d in chapters_root.iterdir()
        if d.is_dir() and (d / "images").exists()
    ])
    
    return chapters


def main():
    """
    Main entry point.
    """
    logger.info("\n" + "="*60)
    logger.info("🎥 VIDEO ASSEMBLY PIPELINE - PRODUCTION")
    logger.info("="*60)
    
    try:
        # Find chapters
        chapters = find_chapter_directories()
        
        if not chapters:
            logger.error("❌ No chapter directories found in ./chapters/")
            logger.info("\nExpected structure:")
            logger.info("  chapters/chapter_01/images/")
            logger.info("  chapters/chapter_01/audio.wav")
            logger.info("  chapters/chapter_01/subtitles.srt")
            return 1
        
        logger.info(f"\n📂 Found {len(chapters)} chapter(s)")
        
        # Assemble each chapter
        assembler = VideoAssembler(fps=30)
        output_files = []
        
        for chapter_dir in chapters:
            chapter_name = chapter_dir.name
            output_file = f"{chapter_name}_final.mp4"
            
            logger.info(f"\n" + "="*60)
            logger.info(f"Processing: {chapter_name}")
            logger.info("="*60)
            
            try:
                output = assembler.assemble_from_chapter(
                    chapter_dir=str(chapter_dir),
                    output_file=output_file,
                    image_duration=3.0
                )
                output_files.append(output)
                logger.info(f"✅ SUCCESS: {output}")
            except Exception as e:
                logger.error(f"❌ FAILED: {e}", exc_info=True)
                return 1
        
        # Summary
        logger.info(f"\n" + "="*60)
        logger.info(f"🎉 ASSEMBLY COMPLETE!")
        logger.info("="*60)
        logger.info(f"\nCreated {len(output_files)} video(s):")
        for output_file in output_files:
            size_mb = Path(output_file).stat().st_size / (1024*1024)
            logger.info(f"  ✅ {output_file} ({size_mb:.1f} MB)")
        
        return 0
    
    except Exception as e:
        logger.error(f"\n❌ FATAL ERROR: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
