from __future__ import annotations

from pathlib import Path
from typing import Any

from core.utils.config_loader import ProjectConfig


def upload(config: ProjectConfig, video_path: Path, script: Any, mode: str) -> str:
    raise NotImplementedError("YouTube uploader will be implemented in Part 4")
