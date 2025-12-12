from __future__ import annotations

from pathlib import Path
from typing import Any

from core.utils.config_loader import ProjectConfig


def render(config: ProjectConfig, script: Any, audio_map: Any, mode: str) -> Path:
    """Render video.

    Part 3 will implement real rendering. For Part 1 we create a placeholder file
    under output/videos/ so the pipeline produces an artifact.
    """

    project_slug = str(config.project.get("name") or "project").replace(" ", "_")
    out_dir = Path("output") / "videos" / project_slug
    out_dir.mkdir(parents=True, exist_ok=True)

    video_path = out_dir / f"{mode}.mp4"
    content = (
        f"PLACEHOLDER VIDEO FILE\n"
        f"project={config.project.get('name')}\n"
        f"mode={mode}\n"
        f"audio={audio_map}\n"
        f"script_keys={list(script.keys()) if isinstance(script, dict) else type(script)}\n"
    )
    video_path.write_text(content, encoding="utf-8")
    return video_path
