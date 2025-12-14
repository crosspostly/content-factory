#!/usr/bin/env python3
"""
Test script for horoscope_leo project with slides mode.

Runs the complete pipeline:
1. Load config from projects/horoscope_leo/config.yaml
2. Use example content from config
3. Generate video using SlidesMode
4. Verify output

Usage:
    python scripts/test_horoscope_leo.py
"""

import asyncio
import logging
from pathlib import Path
import yaml
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add core to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.content_modes.slides_mode.mode import SlidesMode
from core.content_modes.registry import get_mode


def load_config(config_path: Path) -> dict:
    """""""
    """
    Load YAML config file.
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    logger.info(f"✅ Loaded config from {config_path}")
    return config


def extract_design_config(config: dict) -> dict:
    """"""
    """
    Extract design config for slides mode.
    """
    design = config.get('design', {})
    output = config.get('output', {})
    transitions = config.get('transitions', {})
    audio = config.get('audio', {})
    
    return {
        'width': int(output.get('resolution', '1080x1920').split('x')[0]),
        'height': int(output.get('resolution', '1080x1920').split('x')[1]),
        'background_color': design.get('background_color', '#2B1B3D'),
        'background_secondary': design.get('background_secondary', '#1a0f2e'),
        'text_color': design.get('text_color', 'white'),
        'font_size': design.get('font_size', 70),
        'font_family': design.get('font_family', 'Arial'),
        'fps': output.get('fps', 30),
        'bitrate': output.get('bitrate', '5000k'),
        'transitions': transitions,
    }


async def test_horoscope_leo():
    """"""
    """
    Main test function.
    """
    logger.info("\n" + "="*60)
    logger.info("🦁 TESTING HOROSCOPE LEO PROJECT WITH SLIDES MODE")
    logger.info("="*60 + "\n")
    
    # 1. Load config
    logger.info("📋 Step 1: Loading configuration...")
    config_path = Path('projects/horoscope_leo/config.yaml')
    config = load_config(config_path)
    logger.info(f"   Project: {config['project']['title']}")
    logger.info(f"   Mode: {config['video_mode']} ({config['variant']})\n")
    
    # 2. Prepare content
    logger.info("📝 Step 2: Preparing content...")
    content = config['example_content'].strip()
    logger.info(f"   Content length: {len(content)} chars")
    logger.info(f"   Expected slides: {config['content']['slides_count']}")
    logger.info(f"\n   Preview:\n   {content[:100]}...\n")
    
    # 3. Extract design config
    logger.info("⚙️  Step 3: Extracting design settings...")
    design_config = extract_design_config(config)
    logger.info(f"   Resolution: {design_config['width']}x{design_config['height']}")
    logger.info(f"   Background: {design_config['background_color']}")
    logger.info(f"   Text Color: {design_config['text_color']}")
    logger.info(f"   Font Size: {design_config['font_size']}pt")
    logger.info(f"   FPS: {design_config['fps']}")
    logger.info(f"   Transitions: {design_config['transitions'].get('type', 'fade')}\n")
    
    # 4. Get SlidesMode
    logger.info("🎯 Step 4: Initializing SlidesMode...")
    try:
        mode = SlidesMode(variant='carousel')
        logger.info(f"   ✅ Mode: {mode.name}")
        logger.info(f"   Description: {mode.description}\n")
    except Exception as e:
        logger.error(f"   ❌ Failed to initialize SlidesMode: {e}")
        return False
    
    # 5. Prepare output directory
    logger.info("📁 Step 5: Preparing output directory...")
    output_dir = Path('output/horoscope_leo')
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"   Output dir: {output_dir.absolute()}\n")
    
    # 6. Generate video
    logger.info("🎬 Step 6: Generating video...")
    logger.info("   (This may take 30-60 seconds)\n")
    
    try:
        result = await mode.generate(
            scenario=content,
            audio_map={},  # No audio for now
            config=design_config,
            output_dir=output_dir,
        )
        
        logger.info(f"\n   ✅ VIDEO GENERATION SUCCESSFUL!\n")
        logger.info(f"   📹 Video Path: {result.video_path}")
        logger.info(f"   ⏱️  Duration: {result.duration:.2f} seconds")
        logger.info(f"   📐 Resolution: {result.width}x{result.height}")
        logger.info(f"   📊 Metadata: {result.metadata}\n")
        
        # 7. Verify file exists
        logger.info("🔍 Step 7: Verifying output file...")
        video_path = Path(result.video_path)
        if video_path.exists():
            file_size_mb = video_path.stat().st_size / (1024 * 1024)
            logger.info(f"   ✅ File exists: {video_path}")
            logger.info(f"   📦 File size: {file_size_mb:.2f} MB\n")
        else:
            logger.error(f"   ❌ Video file not found: {video_path}")
            return False
        
        # 8. Summary
        logger.info("="*60)
        logger.info("✅ ALL TESTS PASSED!")
        logger.info("="*60)
        logger.info(f"\n🎉 Video successfully generated!")
        logger.info(f"\n📺 Next steps:")
        logger.info(f"   1. Open video: {result.video_path}")
        logger.info(f"   2. Verify quality on mobile (1080x1920 vertical)")
        logger.info(f"   3. Add TTS audio in next phase")
        logger.info(f"   4. Upload to YouTube Shorts/TikTok\n")
        
        return True
    
    except Exception as e:
        logger.error(f"\n   ❌ ERROR during video generation:")
        logger.error(f"   {type(e).__name__}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


async def main():
    """"""
    """
    Entry point.
    """
    success = await test_horoscope_leo()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    asyncio.run(main())
