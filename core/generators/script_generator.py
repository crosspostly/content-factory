from __future__ import annotations

import datetime as _dt
import json
import uuid
from pathlib import Path
from typing import Any

from core.utils.config_loader import ProjectConfig


def _read_project_prompt(project_name: str, relative_path: str) -> str:
    prompt_path = Path("projects") / project_name / relative_path
    return prompt_path.read_text(encoding="utf-8")


def _save_script_to_file(script: dict[str, Any], project_name: str, date: str) -> str:
    """Save script to JSON file and return the path."""
    output_dir = Path("output") / "scripts" / project_name / date
    output_dir.mkdir(parents=True, exist_ok=True)

    script_path = output_dir / f"script_{uuid.uuid4()}.json"
    with open(script_path, "w", encoding="utf-8") as f:
        json.dump(script, f, indent=2, ensure_ascii=False)

    return str(script_path)


def generate_short(config: ProjectConfig, date: str) -> dict[str, Any]:
    """Generate a minimal script structure for shorts.

    Part 3 will replace this with proper LLM-based generation.
    """

    project_name = config.project.get("folder") or config.project.get("id") or "youtube_horoscope"
    prompt_rel = config.generation.prompt_files.get("shorts_script")
    prompt = _read_project_prompt(project_name, prompt_rel) if prompt_rel else ""

    script = {
        "hook": f"Гороскоп на {date}",
        "content_type": "shorts",
        "script": f"Гороскоп на {date}. (placeholder script)",
        "visual_hints": ["stars", "zodiac"],
        "engagement_cta": "Подпишись на новые гороскопы!",
        "duration_sec_target": 30,
    }

    script_path = _save_script_to_file(script, project_name, date)
    script["_script_path"] = script_path

    return script


def generate_long_form(config: ProjectConfig, date: str) -> dict[str, Any]:
    project_name = config.project.get("folder") or config.project.get("id") or "youtube_horoscope"
    prompt_rel = config.generation.prompt_files.get("long_form_script")
    prompt = _read_project_prompt(project_name, prompt_rel) if prompt_rel else ""

    script = {
        "video_title": f"Полный гороскоп на {date}",
        "blocks": {
            "love": "Любовные перспективы на день...",
            "money": "Финансовые прогнозы на день...",
            "health": "Здоровье и благополучие на день...",
        },
        "chapters": [
            {"title": "Любовь", "timestamp": "0:00"},
            {"title": "Деньги", "timestamp": "4:00"},
            {"title": "Здоровье", "timestamp": "8:00"},
        ],
        "duration_target_min": 12,
    }

    script_path = _save_script_to_file(script, project_name, date)
    script["_script_path"] = script_path

    return script


def generate_ad(config: ProjectConfig, product_id: str) -> dict[str, Any]:
    today = _dt.date.today().isoformat()
    project_name = config.project.get("folder") or config.project.get("id") or "youtube_horoscope"
    prompt_rel = config.generation.prompt_files.get("ad_script")
    prompt = _read_project_prompt(project_name, prompt_rel) if prompt_rel else ""

    script = {
        "product_id": product_id,
        "narration_text": f"Реклама продукта {product_id}. (placeholder script)",
        "duration_sec_target": 15,
    }

    script_path = _save_script_to_file(script, project_name, today)
    script["_script_path"] = script_path

    return script
