#!/usr/bin/env python3
"""
Configuration loader for content-factory projects.

Handles loading, validating, and merging project configurations.
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class ProjectConfig:
    """Represents a project configuration."""
    
    name: str
    description: str
    content_type: str
    platforms: list
    enabled: bool = True
    
    generation: Dict[str, Any] = None
    api_keys: list = None
    scheduling: Dict[str, Any] = None
    output: Dict[str, Any] = None
    
    _raw: Dict[str, Any] = None  # Original config dict
    _path: Path = None  # Config file path
    
    def __post_init__(self):
        """Initialize defaults."""
        if self.generation is None:
            self.generation = {
                "primary_model": "gemini-2.5-flash",
                "fallback_models": ["gemini-2.5-pro"],
                "temperature": 0.7,
                "max_retries": 2,
            }
        
        if self.api_keys is None:
            self.api_keys = ["GOOGLE_AI_API_KEY"]
        
        if self.scheduling is None:
            self.scheduling = {
                "enabled": False,
                "cron": None,
                "timezone": "UTC",
            }
        
        if self.output is None:
            self.output = {
                "format": "video",
                "video_quality": "1080p",
                "frame_rate": 30,
            }
    
    @classmethod
    def load(cls, config_path: str) -> "ProjectConfig":
        """Load config from YAML or JSON file.
        
        Args:
            config_path: Path to config file (relative to repo root)
            
        Returns:
            ProjectConfig instance
            
        Raises:
            FileNotFoundError: If config file not found
            ValueError: If config is invalid
        """
        # Resolve path
        if not Path(config_path).is_absolute():
            repo_root = Path(__file__).parent.parent.parent
            config_path = repo_root / config_path
        else:
            config_path = Path(config_path)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Config not found: {config_path}")
        
        # Load config
        with open(config_path, "r") as f:
            if config_path.suffix == ".yaml" or config_path.suffix == ".yml":
                raw_config = yaml.safe_load(f)
            elif config_path.suffix == ".json":
                raw_config = json.load(f)
            else:
                raise ValueError(f"Unsupported config format: {config_path.suffix}")
        
        if not raw_config:
            raise ValueError(f"Empty config: {config_path}")
        
        # Extract project section
        if "project" not in raw_config:
            raise ValueError("Config must have 'project' section")
        
        project_data = raw_config["project"]
        
        # Create instance
        config = cls(
            name=project_data.get("name", ""),
            description=project_data.get("description", ""),
            content_type=project_data.get("content_type", "shorts"),
            platforms=project_data.get("platforms", ["youtube"]),
            enabled=project_data.get("enabled", True),
            generation=raw_config.get("generation", {}),
            api_keys=raw_config.get("api_keys", []),
            scheduling=raw_config.get("scheduling", {}),
            output=raw_config.get("output", {}),
            _raw=raw_config,
            _path=config_path,
        )
        
        config._validate()
        return config
    
    def _validate(self) -> None:
        """Validate config values."""
        if not self.name:
            raise ValueError("Project name is required")
        
        if self.content_type not in ["shorts", "long-form", "ad", "podcast", "custom"]:
            raise ValueError(f"Invalid content_type: {self.content_type}")
        
        if not isinstance(self.platforms, list) or not self.platforms:
            raise ValueError("Platforms must be a non-empty list")
        
        if not isinstance(self.api_keys, list):
            raise ValueError("API keys must be a list")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from raw config.
        
        Args:
            key: Config key (supports dot notation: 'generation.temperature')
            default: Default value if key not found
            
        Returns:
            Config value or default
        """
        if not self._raw:
            return default
        
        parts = key.split(".")
        value = self._raw
        
        try:
            for part in parts:
                value = value[part]
            return value
        except (KeyError, TypeError):
            return default
    
    def has_api_key(self, key: str) -> bool:
        """Check if API key is configured.
        
        Args:
            key: API key name
            
        Returns:
            True if key is in api_keys list
        """
        return key in self.api_keys
    
    def get_env_var(self, key: str) -> Optional[str]:
        """Get environment variable for API key.
        
        Args:
            key: API key name
            
        Returns:
            Environment variable value or None
        """
        return os.getenv(key)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self._raw, indent=2)
    
    def __repr__(self) -> str:
        return f"ProjectConfig(name={self.name}, type={self.content_type}, platforms={self.platforms})"


class ConfigManager:
    """Manage multiple project configurations."""
    
    def __init__(self, repo_root: str = None):
        """Initialize config manager.
        
        Args:
            repo_root: Repository root directory
        """
        self.repo_root = Path(repo_root) if repo_root else Path(__file__).parent.parent.parent
        self.projects_dir = self.repo_root / "projects"
        self._configs: Dict[str, ProjectConfig] = {}
    
    def load_all(self) -> Dict[str, ProjectConfig]:
        """Load all project configs.
        
        Returns:
            Dictionary of {project_name: ProjectConfig}
        """
        if not self.projects_dir.exists():
            return {}
        
        configs = {}
        for project_dir in self.projects_dir.iterdir():
            if not project_dir.is_dir():
                continue
            
            config_file = project_dir / "config.yaml"
            if not config_file.exists():
                config_file = project_dir / "config.json"
            
            if config_file.exists():
                try:
                    config = ProjectConfig.load(str(config_file))
                    configs[project_dir.name] = config
                except Exception as e:
                    print(f"⚠️  Failed to load {project_dir.name}: {e}")
        
        self._configs = configs
        return configs
    
    def get(self, project_name: str) -> Optional[ProjectConfig]:
        """Get config for a project.
        
        Args:
            project_name: Project name
            
        Returns:
            ProjectConfig or None
        """
        if project_name not in self._configs:
            config_path = self.projects_dir / project_name / "config.yaml"
            if not config_path.exists():
                config_path = self.projects_dir / project_name / "config.json"
            
            if config_path.exists():
                try:
                    self._configs[project_name] = ProjectConfig.load(str(config_path))
                except Exception as e:
                    print(f"❌ Failed to load {project_name}: {e}")
                    return None
        
        return self._configs.get(project_name)
    
    def list_projects(self) -> list:
        """List all available projects.
        
        Returns:
            List of project names
        """
        self.load_all()
        return list(self._configs.keys())
    
    def list_enabled(self) -> list:
        """List enabled projects.
        
        Returns:
            List of enabled project names
        """
        self.load_all()
        return [name for name, config in self._configs.items() if config.enabled]


if __name__ == "__main__":
    # Test loading config
    import sys
    
    if len(sys.argv) < 2:
        # List all projects
        manager = ConfigManager()
        projects = manager.list_projects()
        
        print("\n📦 Available projects:")
        for name in projects:
            config = manager.get(name)
            print(f"  - {config.name} ({config.content_type})")
            print(f"    {config.description}")
            if config.scheduling.get("enabled"):
                print(f"    Schedule: {config.scheduling.get('cron')}")
    else:
        # Load specific project
        project_name = sys.argv[1]
        manager = ConfigManager()
        config = manager.get(project_name)
        
        if config:
            print(f"\n✅ Loaded: {config}")
            print(f"\nConfiguration:")
            print(json.dumps(config.to_dict(), indent=2, default=str))
        else:
            print(f"❌ Project not found: {project_name}")
