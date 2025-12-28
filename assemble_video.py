#!/usr/bin/env python3
"""
Video Assembly Script
Assembles video from generated slides, narration, and background music.
Integrates with GitHub Actions workflow.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any

from PIL import Image
from moviepy.editor import (
    ImageClip,
    AudioFileClip,
    concatenate_videoclips,
    CompositeAudioClip,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VideoAssembler:
    """Assembles video from components."""

    def __init__(self, output_dir: str = ".", fps: int = 30):
        """
        Initialize VideoAssembler.
        
        Args:
            output_dir: Directory for output video
            fps: Frames per second for video
        """
        self.output_dir = Path(output_dir)
        self.fps = fps
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def assemble_from_slides(
        self,
        slides_dir: str,
        audio_file: Optional[str] = None,
        slide_duration: float = 3.0,
        output_file: str = "final_video.mp4",
    ) -> str:
        """
        Assemble video from image slides.
        
        Args:
            slides_dir: Directory containing slide images
            audio_file: Optional audio file to include
            slide_duration: Duration each slide is shown (seconds)
            output_file: Output video filename
            
        Returns:
            Path to assembled video
        """
        slides_path = Path(slides_dir)
        if not slides_path.exists():
            raise FileNotFoundError(f"Slides directory not found: {slides_path}")

        # Collect and sort slides
        slide_files = sorted(
            slides_path.glob("*.png") + slides_path.glob("*.jpg"),
            key=lambda x: x.name
        )

        if not slide_files:
            raise ValueError(f"No slide images found in {slides_path}")

        logger.info(f"Found {len(slide_files)} slides")

        # Create video clips from slides
        clips = []
        for slide_file in slide_files:
            try:
                clip = ImageClip(str(slide_file)).set_duration(slide_duration)
                clips.append(clip)
                logger.info(f"Loaded slide: {slide_file.name}")
            except Exception as e:
                logger.warning(f"Failed to load slide {slide_file}: {e}")
                continue

        if not clips:
            raise ValueError("No valid slides could be loaded")

        # Concatenate clips
        logger.info(f"Concatenating {len(clips)} clips...")
        final_clip = concatenate_videoclips(clips, method="chain")

        # Add audio if provided
        if audio_file and Path(audio_file).exists():
            try:
                audio = AudioFileClip(audio_file)
                # Adjust video duration to match audio
                video_duration = final_clip.duration
                audio_duration = audio.duration
                
                if audio_duration > video_duration:
                    logger.warning(
                        f"Audio ({audio_duration}s) longer than video ({video_duration}s). "
                        "Trimming audio."
                    )
                    audio = audio.subclipped(0, video_duration)
                elif audio_duration < video_duration:
                    logger.warning(
                        f"Audio ({audio_duration}s) shorter than video ({video_duration}s). "
                        "Will loop or pad."
                    )
                
                final_clip = final_clip.set_audio(audio)
                logger.info(f"Added audio: {audio_file}")
            except Exception as e:
                logger.warning(f"Failed to add audio: {e}")

        # Write output
        output_path = self.output_dir / output_file
        logger.info(f"Writing video to {output_path}...")
        
        try:
            final_clip.write_videofile(
                str(output_path),
                fps=self.fps,
                verbose=False,
                logger=None,
            )
            logger.info(f"Video successfully created: {output_path}")
            return str(output_path)
        except Exception as e:
            logger.error(f"Failed to write video: {e}")
            raise
        finally:
            final_clip.close()
            if audio_file and Path(audio_file).exists():
                try:
                    audio.close()
                except:
                    pass

    def assemble_from_config(
        self,
        config_file: str,
        output_file: str = "final_video.mp4",
    ) -> str:
        """
        Assemble video from configuration file.
        
        Config structure:
        {
            "slides_dir": "path/to/slides",
            "audio_file": "path/to/audio.mp3",
            "slide_duration": 3.0,
            "fps": 30
        }
        
        Args:
            config_file: Path to JSON config file
            output_file: Output video filename
            
        Returns:
            Path to assembled video
        """
        config_path = Path(config_file)
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_file}")

        with open(config_path, "r") as f:
            config = json.load(f)

        logger.info(f"Loaded config from {config_file}")

        slides_dir = config.get("slides_dir")
        audio_file = config.get("audio_file")
        slide_duration = config.get("slide_duration", 3.0)
        fps = config.get("fps", 30)

        if not slides_dir:
            raise ValueError("Config missing 'slides_dir'")

        self.fps = fps

        return self.assemble_from_slides(
            slides_dir=slides_dir,
            audio_file=audio_file,
            slide_duration=slide_duration,
            output_file=output_file,
        )


def find_latest_project_data() -> Optional[Dict[str, Any]]:
    """
    Find latest project data from GitHub workflow context.
    
    Returns:
        Project metadata or None
    """
    # Check environment variables from GitHub Actions
    github_ref = os.getenv("GITHUB_REF", "")
    github_sha = os.getenv("GITHUB_SHA", "")
    github_run_id = os.getenv("GITHUB_RUN_ID", "")

    if not github_ref or not github_ref.startswith("refs/heads/project/"):
        logger.warning("Not running in project branch context")
        return None

    # Extract project ID from branch name
    project_branch = github_ref.replace("refs/heads/", "")
    project_id = project_branch.replace("project/", "")

    return {
        "project_id": project_id,
        "branch": project_branch,
        "commit": github_sha,
        "run_id": github_run_id,
    }


def main():
    """
    Main entry point for video assembly.
    """
    logger.info("Starting video assembly process...")

    # Try to load configuration
    config_files = [
        "video_config.json",
        "config/video_config.json",
    ]

    config_file = None
    for cf in config_files:
        if Path(cf).exists():
            config_file = cf
            break

    assembler = VideoAssembler()

    try:
        if config_file:
            logger.info(f"Using config file: {config_file}")
            output = assembler.assemble_from_config(config_file)
        else:
            # Try default directories
            slides_dir = "slides"
            audio_file = None

            # Look for audio file
            for ext in [".mp3", ".wav", ".m4a"]:
                audio_candidates = list(Path(".").glob(f"*{ext}"))
                if audio_candidates:
                    audio_file = str(audio_candidates[0])
                    break

            if not Path(slides_dir).exists():
                logger.error(f"Slides directory not found: {slides_dir}")
                logger.info("Creating sample slides for testing...")
                Path(slides_dir).mkdir(exist_ok=True)
                
                # Create a test slide
                img = Image.new('RGB', (1280, 720), color='blue')
                img.save(f"{slides_dir}/slide_001.png")
                logger.info("Created test slide")

            logger.info(f"Using slides from: {slides_dir}")
            if audio_file:
                logger.info(f"Using audio: {audio_file}")
            else:
                logger.info("No audio file found, creating video with slides only")

            output = assembler.assemble_from_slides(
                slides_dir=slides_dir,
                audio_file=audio_file,
            )

        logger.info(f"✅ Video assembly completed successfully!")
        logger.info(f"Output: {output}")
        
        # Log project metadata if available
        project_data = find_latest_project_data()
        if project_data:
            logger.info(f"Project metadata: {json.dumps(project_data, indent=2)}")

        return 0

    except Exception as e:
        logger.error(f"❌ Video assembly failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
