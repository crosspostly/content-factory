from __future__ import annotations

import datetime as _dt
from pathlib import Path
from typing import Any

from core.utils.config_loader import ProjectConfig


def _read_project_prompt(project_name: str, relative_path: str) -> str:
    prompt_path = Path("projects") / project_name / relative_path
    return prompt_path.read_text(encoding="utf-8")


def generate_short(config: ProjectConfig, date: str) -> dict[str, Any]:
    """Generate a minimal script structure for shorts.

    Part 3 will replace this with proper LLM-based generation.
    """

    project_name = config.project.get("folder") or config.project.get("id") or "youtube_horoscope"
    prompt_rel = config.generation.prompt_files.get("shorts_script")
    prompt = _read_project_prompt(project_name, prompt_rel) if prompt_rel else ""

    return {
        "mode": "shorts",
        "date": date,
        "prompt": prompt,
        "narration_text": f"Гороскоп на {date}. (placeholder script)",
    }


def generate_long_form(config: ProjectConfig, date: str) -> dict[str, Any]:
    project_name = config.project.get("folder") or config.project.get("id") or "youtube_horoscope"
    prompt_rel = config.generation.prompt_files.get("long_form_script")
    prompt = _read_project_prompt(project_name, prompt_rel) if prompt_rel else ""

    return {
        "mode": "long_form",
        "date": date,
        "prompt": prompt,
        "narration_text": f"Длинный гороскоп на {date}. (placeholder script)",
        "sections": ["love", "money", "health"],
    }


def generate_ad(config: ProjectConfig, product_id: str) -> dict[str, Any]:
    today = _dt.date.today().isoformat()
    project_name = config.project.get("folder") or config.project.get("id") or "youtube_horoscope"
    prompt_rel = config.generation.prompt_files.get("ad_script")
    prompt = _read_project_prompt(project_name, prompt_rel) if prompt_rel else ""

    return {
        "mode": "ad",
        "date": today,
        "product_id": product_id,
        "prompt": prompt,
        "narration_text": f"Реклама продукта {product_id}. (placeholder script)",
    }
