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

    Merges shared config (config/shared.yaml) with project-specific config
    (projects/<project_name>/config.yaml). Project-specific overrides shared.

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
        self.debugger = ConfigNode(data.get("debugger") or {})
        self.ci_cd = ConfigNode(data.get("ci_cd") or {})
        self.workflows = ConfigNode(data.get("workflows") or {})

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
            "debugger": self.debugger.to_dict(),
            "ci_cd": self.ci_cd.to_dict(),
            "workflows": self.workflows.to_dict(),
        }


def _merge_dicts(shared: dict[str, Any], project: dict[str, Any]) -> dict[str, Any]:
    """Deep merge: project values override shared values."""
    result = shared.copy()
    for key, value in project.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _merge_dicts(result[key], value)
        else:
            result[key] = value
    return result


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
    """Load project config by merging shared config with project-specific config.

    1. Load shared config from config/shared.yaml
    2. Load project config from projects/<project_name>/config.yaml
    3. Merge: project values override shared
    4. Validate required sections

    Raises:
        FileNotFoundError: if config files are missing
        ValueError: if YAML is invalid or missing required sections
    """

    # Load shared config
    shared_path = Path("config") / "shared.yaml"
    if not shared_path.exists():
        raise FileNotFoundError(f"Shared config not found: {shared_path}")

    with shared_path.open("r", encoding="utf-8") as f:
        shared_data = safe_load(f) or {}

    if not isinstance(shared_data, dict):
        raise ValueError("Shared config YAML must be a mapping")

    # Load project config
    project_path = Path("projects") / project_name / "config.yaml"
    if not project_path.exists():
        raise FileNotFoundError(f"Project config not found: {project_path}")

    with project_path.open("r", encoding="utf-8") as f:
        project_data = safe_load(f) or {}

    if not isinstance(project_data, dict):
        raise ValueError(f"Project config ({project_name}) YAML must be a mapping")

    # Merge: project overrides shared
    data = _merge_dicts(shared_data, project_data)

    # Ensure project.folder is set
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


def load_all_projects() -> dict[str, ProjectConfig]:
    """Load all project configs from projects/ directory.

    Returns:
        Dict mapping project_name -> ProjectConfig
    """
    projects_dir = Path("projects")
    result = {}

    for project_dir in projects_dir.iterdir():
        if not project_dir.is_dir():
            continue
        config_file = project_dir / "config.yaml"
        if not config_file.exists():
            continue
        try:
            result[project_dir.name] = load(project_dir.name)
        except Exception as e:
            # Log error but continue loading other projects
            print(f"Warning: Failed to load project {project_dir.name}: {e}")

    return result


def load_content_plan(project_name: str) -> dict[str, Any]:
    plan_path = Path("projects") / project_name / "content_plan.json"
    if not plan_path.exists():
        return {}

    with plan_path.open("r", encoding="utf-8") as f:
        return json.load(f)
