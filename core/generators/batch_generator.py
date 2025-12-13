"""
Batch Generator - Generate multiple videos in one run.

Useful for:
- Pre-generating a week/month of content
- Bulk testing quality
- Preparing content before vacation
"""

import logging
import os
from datetime import datetime, timedelta
from typing import Any

from core.utils.config_loader import ProjectConfig, load
from core.utils import logging_utils

logger = logging.getLogger(__name__)


def generate_batch(
    project_name: str,
    start_date: str,
    num_days: int,
    mode: str,
    api_key: str = None,
    pixabay_key: str = None,
) -> list[dict[str, Any]]:
    """
    Generate multiple horoscope videos in batch.
    
    Args:
        project_name: Project name (e.g., "youtube_horoscope")
        start_date: Start date (YYYY-MM-DD)
        num_days: Number of days to generate
        mode: Video mode (shorts, long_form, ad)
        api_key: Google AI API key (or from env)
        pixabay_key: Pixabay API key (or from env)
    
    Returns:
        List of results: [{"date": ..., "status": "success", "video_path": ...}, ...]
    
    Example:
        results = generate_batch("youtube_horoscope", "2025-12-13", 7, "shorts")
        # Generates 7 days of shorts: 2025-12-13 → 2025-12-19
    """
    
    # Get API keys from args or env
    if not api_key:
        api_key = os.getenv("GOOGLE_AI_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_AI_API_KEY not provided and not in environment")
    
    if not pixabay_key:
        pixabay_key = os.getenv("PIXABAY_API_KEY", "")
    
    # Load config
    try:
        config = load(project_name)
    except Exception as e:
        logger.error(f"Failed to load config for project '{project_name}': {e}")
        raise
    
    logger.info("\n" + "="*70)
    logger.info("🚀 BATCH GENERATION START")
    logger.info("="*70)
    logger.info(f"Project: {project_name}")
    logger.info(f"Start date: {start_date}")
    logger.info(f"Number of days: {num_days}")
    logger.info(f"Mode: {mode}")
    logger.info("="*70 + "\n")
    
    start = datetime.strptime(start_date, "%Y-%m-%d")
    results = []
    
    for i in range(num_days):
        date = (start + timedelta(days=i)).strftime("%Y-%m-%d")
        day_num = i + 1
        
        logger.info("\n" + "="*70)
        logger.info(f"📅 [{day_num}/{num_days}] Generating: {date}")
        logger.info("="*70 + "\n")
        
        try:
            # Setup logging for this day
            logging_utils.setup_logging(project_name, date)
            
            # Run full pipeline for this date
            from core.generators import script_generator, tts_generator, video_renderer
            from core.utils.model_router import get_router
            
            # Step 1: Script
            logger.info("📝 Step 1: Generating script...")
            if mode == "shorts":
                script = script_generator.generate_short(config, target_date=date, api_key=api_key)
            elif mode == "long_form":
                script = script_generator.generate_long_form(config, target_date=date, api_key=api_key)
            elif mode == "ad":
                script = script_generator.generate_ad(config, target_date=date, api_key=api_key)
            else:
                raise ValueError(f"Unknown mode: {mode}")
            
            router = get_router(api_key)
            stats = router.get_stats()
            logger.info(f"✅ Script generated. API calls: {stats['total_attempts']}")
            
            # Step 2: TTS
            logger.info("🎤 Step 2: Generating audio...")
            audio_map = tts_generator.synthesize(config, script, mode, api_key=api_key)
            logger.info(f"✅ Audio generated. Blocks: {len(audio_map) if isinstance(audio_map, (list, dict)) else 'N/A'}")
            
            # Step 3: Video
            logger.info("🎬 Step 3: Rendering video...")
            video_path = video_renderer.render(config, script, audio_map, mode)
            logger.info(f"✅ Video rendered: {video_path}")
            
            # Store result
            results.append({
                "date": date,
                "status": "success",
                "video_path": str(video_path),
                "script_path": script.get("_script_path", ""),
                "stats": stats
            })
            
            logger.info(f"\n✅ [{day_num}/{num_days}] COMPLETE: {date}\n")
        
        except Exception as e:
            logger.error(f"\n❌ [{day_num}/{num_days}] FAILED for {date}: {e}\n")
            
            results.append({
                "date": date,
                "status": "failed",
                "error": str(e)
            })
    
    # Summary
    successful = sum(1 for r in results if r["status"] == "success")
    failed = num_days - successful
    
    logger.info("\n" + "="*70)
    logger.info("✅ BATCH GENERATION COMPLETE")
    logger.info("="*70)
    logger.info(f"Total: {num_days} days")
    logger.info(f"Success: {successful} ({successful/num_days*100:.1f}%)")
    logger.info(f"Failed: {failed} ({failed/num_days*100:.1f}%)")
    logger.info("="*70)
    
    # List all successful videos
    if successful > 0:
        logger.info("\n📹 Generated videos:")
        for r in results:
            if r["status"] == "success":
                logger.info(f"  ✅ {r['date']}: {r['video_path']}")
    
    # List all failures
    if failed > 0:
        logger.info("\n❌ Failed generations:")
        for r in results:
            if r["status"] == "failed":
                logger.info(f"  ❌ {r['date']}: {r['error']}")
    
    logger.info("\n")
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Batch generate horoscope videos")
    parser.add_argument("--project", required=True, help="Project name")
    parser.add_argument("--start-date", required=True, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--num-days", type=int, default=7, help="Number of days to generate")
    parser.add_argument("--mode", required=True, choices=["shorts", "long_form", "ad"])
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s"
    )
    
    # Run batch
    results = generate_batch(
        project_name=args.project,
        start_date=args.start_date,
        num_days=args.num_days,
        mode=args.mode
    )
    
    # Exit with error if any failed
    failed = sum(1 for r in results if r["status"] == "failed")
    exit(0 if failed == 0 else 1)
