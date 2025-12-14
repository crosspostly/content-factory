"""core.utils.config_loader

Configuration loader for Content Factory projects.

This module is intentionally lightweight and dependency-stable because it is
imported very early (often indirectly via `core.utils`).

Key goals:
- Provide a `ProjectConfig` object with convenient dot-access (ConfigNode).
- Provide a module-level `load(project_name)` function used across the codebase.
- Keep backward compatibility for older imports: `load`, `load_content_plan`.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    yaml = None


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Deep-merge two dicts (override wins)."""

    result: dict[str, Any] = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)  # type: ignore[arg-type]
        else:
            result[key] = value
    return result


class ConfigNode(Mapping[str, Any]):
    """Dict wrapper providing dot-access and tolerant lookups.

    - Nested dicts are returned as ConfigNode.
    - Missing attributes return an empty ConfigNode (falsy).
    - `.get()` supports both hyphenated and underscored keys.
    """

    __slots__ = ("_data",)

    def __init__(self, data: Any | None = None):
        if isinstance(data, ConfigNode):
            self._data = data.to_dict()
        elif isinstance(data, dict):
            self._data = data
        else:
            self._data = {}

    @staticmethod
    def _normalize_key(key: str) -> str:
        return key.replace("-", "_")

    def _resolve_key(self, key: str) -> str | None:
        if key in self._data:
            return key

        # Support attr access for hyphenated keys
        if "_" in key:
            alt = key.replace("_", "-")
            if alt in self._data:
                return alt

        # Also allow the reverse: hyphenated keys queried via get("hyphenated-key")
        if "-" in key:
            alt = key.replace("-", "_")
            if alt in self._data:
                return alt

        # Last resort: try normalized match
        normalized = self._normalize_key(key)
        for k in self._data.keys():
            if self._normalize_key(k) == normalized:
                return k

        return None

    def _wrap(self, value: Any) -> Any:
        if isinstance(value, dict):
            return ConfigNode(value)
        if isinstance(value, list):
            return [ConfigNode(v) if isinstance(v, dict) else v for v in value]
        return value

    def to_dict(self) -> dict[str, Any]:
        def unwrap(v: Any) -> Any:
            if isinstance(v, ConfigNode):
                return v.to_dict()
            if isinstance(v, dict):
                return {kk: unwrap(vv) for kk, vv in v.items()}
            if isinstance(v, list):
                return [unwrap(i) for i in v]
            return v

        return {k: unwrap(v) for k, v in self._data.items()}

    def get(self, key: str, default: Any = None) -> Any:
        resolved = self._resolve_key(key)
        if resolved is None:
            return default
        return self._wrap(self._data.get(resolved, default))

    def __getitem__(self, key: str) -> Any:
        resolved = self._resolve_key(key)
        if resolved is None:
            raise KeyError(key)
        return self._wrap(self._data[resolved])

    def __contains__(self, key: object) -> bool:
        if not isinstance(key, str):
            return False
        return self._resolve_key(key) is not None

    def keys(self):
        return self._data.keys()

    def items(self):
        return ((k, self._wrap(v)) for k, v in self._data.items())

    def values(self):
        return (self._wrap(v) for v in self._data.values())

    def __iter__(self):
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __bool__(self) -> bool:
        return bool(self._data)

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):
            raise AttributeError(name)

        resolved = self._resolve_key(name)
        if resolved is None:
            return ConfigNode({})
        return self._wrap(self._data.get(resolved))

    def __repr__(self) -> str:  # pragma: no cover
        return f"ConfigNode({self._data!r})"


class ProjectConfig(ConfigNode):
    """Project configuration with helpers for loading and normalization."""

    @classmethod
    def load(cls, config_path: str) -> "ProjectConfig":
        path = Path(config_path)
        if not path.is_absolute():
            path = _repo_root() / path

        if not path.exists():
            raise FileNotFoundError(f"Config not found: {path}")

        if path.suffix.lower() in {".yml", ".yaml"}:
            if yaml is None:
                raise ModuleNotFoundError(
                    "PyYAML is required to load .yaml configs. Install with: pip install pyyaml"
                )
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
            if raw is None:
                raise ValueError(f"Config file is empty: {path}")
            if not isinstance(raw, dict):
                raise ValueError("Config root must be a mapping")
        elif path.suffix.lower() == ".json":
            raw = json.loads(path.read_text(encoding="utf-8"))
            if not raw:
                raise ValueError(f"Config file is empty: {path}")
            if not isinstance(raw, dict):
                raise ValueError("Config root must be a mapping")
        else:
            raise ValueError(f"Unsupported config format: {path.suffix}")

        # Merge shared config if present
        shared_path = _repo_root() / "config" / "shared.yaml"
        if shared_path.exists() and shared_path != path:
            if yaml is None:
                raise ModuleNotFoundError(
                    "PyYAML is required to load shared.yaml. Install with: pip install pyyaml"
                )
            shared_raw = yaml.safe_load(shared_path.read_text(encoding="utf-8")) or {}
            if isinstance(shared_raw, dict):
                raw = _deep_merge(shared_raw, raw)

        # If this is a project config, enrich project metadata
        projects_dir = _repo_root() / "projects"
        try:
            rel = path.resolve().relative_to(projects_dir.resolve())
            project_folder = rel.parts[0] if rel.parts else None
        except Exception:
            project_folder = None

        if "project" not in raw or not isinstance(raw.get("project"), dict):
            raw["project"] = {}

        if project_folder:
            raw["project"].setdefault("folder", project_folder)
            raw["project"].setdefault("id", project_folder)
            raw["project"].setdefault("name", project_folder)

        config = cls(raw)

        # Validate required fields
        project_section = config.get("project", {})
        if not project_section or not project_section.get("name"):
            raise ValueError(f"Project name is required in {path}")

        return config


def load(project_name: str) -> ProjectConfig:
    """Load project config from `projects/<project_name>/config.yaml`."""

    projects_dir = _repo_root() / "projects" / project_name
    candidates = [
        projects_dir / "config.yaml",
        projects_dir / "config.yml",
        projects_dir / "config.json",
    ]

    for path in candidates:
        if path.exists():
            return ProjectConfig.load(str(path))

    raise FileNotFoundError(
        f"Project config not found for '{project_name}'. Expected one of: "
        + ", ".join(str(p) for p in candidates)
    )


def load_content_plan(project_name: str) -> dict[str, Any]:
    """Load `projects/<project_name>/content_plan.json` if present."""

    plan_path = _repo_root() / "projects" / project_name / "content_plan.json"
    if not plan_path.exists():
        raise FileNotFoundError(f"Content plan not found: {plan_path}")

    raw = json.loads(plan_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("content_plan.json root must be an object")
    return raw
