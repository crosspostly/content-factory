"""Environment verification utility for Content Factory."""
from __future__ import annotations

import logging
import os
import shutil
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


def check_environment() -> dict[str, any]:
    """
    Check that all dependencies are installed and configured.
    
    Returns:
        dict: {
            "python_version": str,
            "ffmpeg": bool,
            "imagemagick": bool,
            "env_vars": {
                "GOOGLE_AI_API_KEY": bool,
                "PIXABAY_API_KEY": bool,
                ...
            },
            "output_dirs": bool,
            "all_checks_passed": bool
        }
    """
    results = {}
    
    # 1. Python version
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    results["python_version"] = python_version
    logger.info(f"✅ Python version: {python_version}")
    
    if sys.version_info < (3, 11):
        logger.warning(f"⚠️  Python 3.11+ recommended, you have {python_version}")
    
    # 2. FFmpeg
    ffmpeg_path = shutil.which("ffmpeg")
    results["ffmpeg"] = ffmpeg_path is not None
    if ffmpeg_path:
        logger.info(f"✅ ffmpeg found: {ffmpeg_path}")
    else:
        logger.error("❌ ffmpeg NOT FOUND (install: sudo apt-get install ffmpeg)")
    
    # 3. ImageMagick
    imagemagick_path = shutil.which("convert") or shutil.which("magick")
    results["imagemagick"] = imagemagick_path is not None
    if imagemagick_path:
        logger.info(f"✅ ImageMagick found: {imagemagick_path}")
    else:
        logger.warning("⚠️  ImageMagick NOT FOUND (install: sudo apt-get install imagemagick)")
        logger.warning("    Note: Video rendering will work with PIL fallback")
    
    # 4. Environment variables
    env_vars = {
        "GOOGLE_AI_API_KEY": os.getenv("GOOGLE_AI_API_KEY"),
        "PIXABAY_API_KEY": os.getenv("PIXABAY_API_KEY"),
        "OPENROUTER_API_KEY": os.getenv("OPENROUTER_API_KEY"),
        "TELEGRAM_BOT_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN"),
        "TELEGRAM_CHAT_ID": os.getenv("TELEGRAM_CHAT_ID"),
    }
    
    results["env_vars"] = {}
    for key, value in env_vars.items():
        is_set = value is not None and value != ""
        results["env_vars"][key] = is_set
        
        if is_set:
            logger.info(f"✅ {key}: set ({value[:10]}...)")
        else:
            if key in ["GOOGLE_AI_API_KEY"]:
                logger.error(f"❌ {key}: NOT SET (required!)")
            elif key == "PIXABAY_API_KEY":
                logger.warning(f"⚠️  {key}: not set (video will use gradient backgrounds)")
            else:
                logger.info(f"ℹ️  {key}: not set (optional)")
    
    # 5. Output directories
    output_dirs = ["output/scripts", "output/audio", "output/videos", "output/logs"]
    for dir_path in output_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    results["output_dirs"] = True
    logger.info(f"✅ Output directories created: {', '.join(output_dirs)}")
    
    # 6. Summary
    required_checks = [
        results["ffmpeg"],
        results["env_vars"]["GOOGLE_AI_API_KEY"],
    ]
    results["all_checks_passed"] = all(required_checks)
    
    if results["all_checks_passed"]:
        logger.info("\n✅ ALL CRITICAL CHECKS PASSED")
        logger.info("   Ready to run pipeline!")
    else:
        logger.error("\n❌ SOME CRITICAL CHECKS FAILED")
        logger.error("   Fix the issues above before running the pipeline")
    
    return results


if __name__ == "__main__":
    from . import logging_utils
    logging_utils.setup_logging("environment_check")
    check_environment()
