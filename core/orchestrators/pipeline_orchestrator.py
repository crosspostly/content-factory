from __future__ import annotations

import argparse
import datetime
import json
import os
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from core.utils import config_loader, logging_utils


def _get_platforms(config: config_loader.ProjectConfig, platforms_arg: str | None) -> list[str]:
    if platforms_arg:
        return [p.strip() for p in platforms_arg.split(",") if p.strip()]

    upload_cfg = config.upload
    platforms = upload_cfg.get("platforms") if hasattr(upload_cfg, "get") else None

    if isinstance(platforms, list):
        return [str(p) for p in platforms]

    if isinstance(platforms, (dict, Mapping)):
        enabled: list[str] = []
        for name, cfg in platforms.items():
            # Check if cfg has get method (dict-like) and enabled is False
            if hasattr(cfg, "get") and cfg.get("enabled") is False:
                continue
            enabled.append(str(name))
        return enabled

    platform = upload_cfg.get("platform") if hasattr(upload_cfg, "get") else None
    if isinstance(platform, str):
        return [platform]

    return []


def main(args: argparse.Namespace) -> int:
    logging_utils.setup_logging(args.project, args.date)

    try:
        config = config_loader.load(args.project)
    except FileNotFoundError as e:
        logging_utils.log_error(f"Config not found: {e}")
        return 1
    except Exception as e:
        logging_utils.log_error(f"Config validation failed: {e}", e)
        return 1

    # Get API key for script generation
    api_key = os.getenv("GOOGLE_AI_API_KEY")
    if not api_key:
        logging_utils.log_error("GOOGLE_AI_API_KEY environment variable not set")
        return 1

    try:
        from core.generators import script_generator
        from core.utils.model_router import get_router

        logging_utils.log_info("\n" + "="*70)
        logging_utils.log_info("🚀 CONTENT FACTORY PIPELINE START")
        logging_utils.log_info("="*70)
        logging_utils.log_info(f"Date: {args.date}")
        logging_utils.log_info(f"Mode: {args.mode}")
        logging_utils.log_info(f"Project: {args.project}")
        logging_utils.log_info("="*70 + "\n")

        logging_utils.log_info("📝 Step 1: Generating script...")
        if args.mode == "shorts":
            script: Any = script_generator.generate_short(config, target_date=args.date, api_key=api_key)
        elif args.mode == "long_form":
            script = script_generator.generate_long_form(config, target_date=args.date, api_key=api_key)
        elif args.mode == "ad":
            if not args.product_id:
                raise ValueError("--product-id is required for mode=ad")
            script = script_generator.generate_ad(config, product_id=args.product_id, target_date=args.date, api_key=api_key)
        else:
            raise ValueError(f"Unknown mode: {args.mode}")

        # Log ModelRouter statistics
        router = get_router(api_key)
        stats = router.get_stats()
        logging_utils.log_info("📊 Script generation statistics:")
        logging_utils.log_info(f"   Total attempts: {stats['total_attempts']}")
        logging_utils.log_info(f"   Successful: {stats['successful']}")
        logging_utils.log_info(f"   Success rate: {stats['success_rate']}")
        logging_utils.log_info(f"   Models used: {stats['model_usage']}")
        logging_utils.log_info("")

    except Exception as e:
        logging_utils.log_error(f"Script generation failed: {e}", e)
        if config.monitoring.telegram_notifications:
            logging_utils.send_telegram_alert(config, f"❌ Script generation failed: {str(e)}")
        return 1

    try:
        from core.generators import tts_generator

        logging_utils.log_info("🎤 Step 2: Generating audio...")
        audio_map = tts_generator.synthesize(config, script, args.mode, api_key=api_key)
        logging_utils.log_info(f"✅ Generated {len(audio_map) if isinstance(audio_map, (list, dict)) else 'N/A'} audio blocks\n")
    except Exception as e:
        logging_utils.log_error(f"TTS synthesis failed: {e}", e)
        if config.monitoring.telegram_notifications:
            logging_utils.send_telegram_alert(config, f"❌ TTS failed: {str(e)}")
        return 1

    try:
        from core.generators import video_renderer
        from core.utils.model_router import get_router

        logging_utils.log_info("🎬 Step 3: Rendering video...")
        video_path = video_renderer.render(config, script, audio_map, args.mode)
        logging_utils.log_info(f"✅ Video created: {video_path}\n")
    except Exception as e:
        logging_utils.log_error(f"Video rendering failed: {e}", e)
        if config.monitoring.telegram_notifications:
            logging_utils.send_telegram_alert(config, f"❌ Video rendering failed: {str(e)}")
        return 1

    # Save metadata
    try:
        logging_utils.log_info("📋 Step 4: Saving metadata...")
        
        router = get_router(api_key)
        stats = router.get_stats()
        
        metadata = {
            "date": args.date,
            "mode": args.mode,
            "project": args.project,
            "video_path": str(video_path),
            "script_path": script.get("_script_path", ""),
            "script_length": len(script.get("script", "")),
            "audio_blocks": len(audio_map) if isinstance(audio_map, (list, dict)) else 0,
            "generation_stats": stats,
            "generated_at": datetime.datetime.now().isoformat(),
        }
        
        metadata_dir = Path("output") / "metadata"
        metadata_dir.mkdir(parents=True, exist_ok=True)
        metadata_path = metadata_dir / f"{args.date}_{args.mode}.json"
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        logging_utils.log_info(f"✅ Metadata saved: {metadata_path}\n")
    except Exception as e:
        logging_utils.log_error(f"Failed to save metadata: {e}", e)
        # Don't fail the pipeline for metadata errors

    # Final summary
    logging_utils.log_info("="*70)
    logging_utils.log_info("✅ PIPELINE COMPLETE")
    logging_utils.log_info("="*70)
    logging_utils.log_info(f"Video: {video_path}")
    logging_utils.log_info(f"Metadata: {metadata_path if 'metadata_path' in locals() else 'N/A'}")
    logging_utils.log_info(f"Script length: {len(script.get('script', ''))} chars")
    logging_utils.log_info(f"API calls: {stats['total_attempts']}")
    logging_utils.log_info(f"Success rate: {stats['success_rate']}")
    logging_utils.log_info("="*70 + "\n")

    logging_utils.log_success(f"Video created: {video_path}")

    if not args.dry_run and args.upload:
        platforms = _get_platforms(config, args.platforms)
        for platform in platforms:
            try:
                if platform == "youtube":
                    from core.uploaders import youtube_uploader

                    video_id = youtube_uploader.upload(config, video_path, script, args.mode)
                    logging_utils.log_success(f"YouTube upload: {video_id}")
                elif platform == "tiktok":
                    logging_utils.log_error("TikTok uploader not yet implemented")
                elif platform == "instagram":
                    logging_utils.log_error("Instagram uploader not yet implemented")
                elif platform == "vk":
                    logging_utils.log_error("VK uploader not yet implemented")
                else:
                    logging_utils.log_error(f"Unknown platform '{platform}', skipping")
            except Exception as e:
                logging_utils.log_error(f"{platform} upload failed: {e}", e)

    if config.monitoring.telegram_notifications:
        if args.dry_run:
            msg = f"✅ {args.mode} script and video generated (dry-run)"
        else:
            msg = f"✅ {args.mode} ready: {video_path}"
        logging_utils.send_telegram_alert(config, msg)

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Content Factory Pipeline")
    parser.add_argument("--project", required=True, help="Project name (folder in projects/)")
    parser.add_argument("--mode", required=True, choices=["shorts", "long_form", "ad"])
    parser.add_argument("--date", default=datetime.date.today().isoformat())
    parser.add_argument("--platforms", help="Comma-separated platforms (youtube,tiktok,...)")
    parser.add_argument("--dry-run", action="store_true", dest="dry_run")
    parser.add_argument("--upload", action="store_true")
    parser.add_argument("--product-id", dest="product_id", help="For ad mode")
    return parser


if __name__ == "__main__":
    parsed = build_parser().parse_args()
    raise SystemExit(main(parsed))
