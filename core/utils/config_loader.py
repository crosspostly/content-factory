from __future__ import annotations

import json
from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import Any

from .yaml_loader import safe_load


def _wrap(value: Any) -> Any:
    if isinstance(value, dict):
        return ConfigNode(value)
    if isinstance(value, list):
        return [_wrap(v) for v in value]
    return value


class ConfigNode(Mapping[str, Any]):
    """Dict-like config node with attribute access (stdlib-only)."""

    def __init__(self, data: dict[str, Any] | None = None):
        self._data: dict[str, Any] = {}
        for k, v in (data or {}).items():
            self._data[str(k)] = _wrap(v)

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __getattr__(self, name: str) -> Any:
        try:
            return self._data[name]
        except KeyError as e:
            raise AttributeError(name) from e

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def to_dict(self) -> dict[str, Any]:
        def unwrap(obj: Any) -> Any:
            if isinstance(obj, ConfigNode):
                return {k: unwrap(v) for k, v in obj._data.items()}
            if isinstance(obj, list):
                return [unwrap(v) for v in obj]
            return obj

        return unwrap(self)


class ProjectConfig:
    """Project config loaded from YAML.

    Provides dot-access similar to Pydantic models in the tech spec.
    """

    def __init__(self, data: dict[str, Any]):
        self._raw = data

        self.project = ConfigNode(data.get("project") or {})
        self.content_strategy = ConfigNode(data.get("content_strategy") or {})
        self.generation = ConfigNode(data.get("generation") or {})
        self.audio = ConfigNode(data.get("audio") or {})
        self.video = ConfigNode(data.get("video") or {})
        self.subtitles = ConfigNode(data.get("subtitles") or {})
        self.upload = ConfigNode(data.get("upload") or {})
        self.caching = ConfigNode(data.get("caching") or {})
        self.monitoring = ConfigNode(data.get("monitoring") or {})

        self.content_plan_file = data.get("content_plan_file")

    def to_dict(self) -> dict[str, Any]:
        return {
            **self._raw,
            "project": self.project.to_dict(),
            "content_strategy": self.content_strategy.to_dict(),
            "generation": self.generation.to_dict(),
            "audio": self.audio.to_dict(),
            "video": self.video.to_dict(),
            "subtitles": self.subtitles.to_dict(),
            "upload": self.upload.to_dict(),
            "caching": self.caching.to_dict(),
            "monitoring": self.monitoring.to_dict(),
        }


def _validate_required(data: dict[str, Any]) -> None:
    required = [
        "project",
        "content_strategy",
        "generation",
        "audio",
        "video",
        "subtitles",
        "upload",
        "caching",
        "monitoring",
    ]
    missing = [k for k in required if k not in data]
    if missing:
        raise ValueError(f"Missing required config sections: {', '.join(missing)}")


def load(project_name: str) -> ProjectConfig:
    """Read `projects/<project_name>/config.yaml`.

    Raises:
        FileNotFoundError: if config.yaml is missing
        ValueError: if YAML is invalid or missing required sections
    """

    config_path = Path("projects") / project_name / "config.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as f:
        data = safe_load(f) or {}

    if not isinstance(data, dict):
        raise ValueError("Top-level YAML must be a mapping")

    data.setdefault("project", {})
    if isinstance(data["project"], dict):
        data["project"].setdefault("folder", project_name)

    # Defaults for tech-spec compatibility
    gen = data.setdefault("generation", {})
    if isinstance(gen, dict):
        gen.setdefault("fallback_models", [])
        gen.setdefault("provider_priority", [])
        gen.setdefault("retry_delay_sec", 2)

    _validate_required(data)
    return ProjectConfig(data)


def load_content_plan(project_name: str) -> dict[str, Any]:
    plan_path = Path("projects") / project_name / "content_plan.json"
    if not plan_path.exists():
        return {}

    with plan_path.open("r", encoding="utf-8") as f:
        return json.load(f)
