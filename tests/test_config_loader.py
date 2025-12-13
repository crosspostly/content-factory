"""Tests for core.utils.config_loader module."""

import json
from pathlib import Path

import pytest

try:
    import yaml
except ModuleNotFoundError:
    yaml = None

from core.utils.config_loader import (
    ConfigNode,
    ProjectConfig,
    _deep_merge,
    load,
)


class TestConfigNode:
    """Tests for ConfigNode class."""

    def test_basic_dict_access(self):
        node = ConfigNode({"key": "value", "nested": {"inner": 42}})
        assert node["key"] == "value"
        assert node["nested"]["inner"] == 42

    def test_dot_access(self):
        node = ConfigNode({"key": "value", "nested": {"inner": 42}})
        assert node.key == "value"
        assert node.nested.inner == 42

    def test_hyphen_underscore_normalization(self):
        node = ConfigNode({"edge-tts": {"voice": "ru-RU"}})
        # Access via underscore
        assert node.edge_tts.voice == "ru-RU"
        assert node.get("edge_tts").voice == "ru-RU"
        # Access via hyphen
        assert node.get("edge-tts").voice == "ru-RU"

    def test_missing_key_returns_empty_node(self):
        node = ConfigNode({"key": "value"})
        missing = node.missing_key
        assert isinstance(missing, ConfigNode)
        assert not missing  # Empty ConfigNode is falsy
        assert len(missing) == 0

    def test_get_with_default(self):
        node = ConfigNode({"key": "value"})
        assert node.get("key") == "value"
        assert node.get("missing", "default") == "default"

    def test_contains(self):
        node = ConfigNode({"key": "value", "edge-tts": {}})
        assert "key" in node
        assert "missing" not in node
        # Hyphen/underscore normalization
        assert "edge_tts" in node
        assert "edge-tts" in node

    def test_list_wrapping(self):
        node = ConfigNode({"items": [{"name": "a"}, {"name": "b"}]})
        items = node["items"]  # Use bracket access to get the actual list
        assert isinstance(items, list)
        assert len(items) == 2
        assert items[0].name == "a"
        assert items[1].name == "b"

    def test_to_dict(self):
        node = ConfigNode({"key": "value", "nested": {"inner": 42}})
        result = node.to_dict()
        assert result == {"key": "value", "nested": {"inner": 42}}

    def test_mapping_interface(self):
        node = ConfigNode({"a": 1, "b": 2, "c": 3})
        assert len(node) == 3
        assert list(node.keys()) == ["a", "b", "c"]
        assert set(node.values()) == {1, 2, 3}
        assert dict(node.items()) == {"a": 1, "b": 2, "c": 3}

    def test_bool(self):
        assert ConfigNode({}) is not None
        assert not ConfigNode({})
        assert ConfigNode({"key": "value"})


class TestDeepMerge:
    """Tests for _deep_merge helper."""

    def test_simple_merge(self):
        base = {"a": 1, "b": 2}
        override = {"b": 3, "c": 4}
        result = _deep_merge(base, override)
        assert result == {"a": 1, "b": 3, "c": 4}

    def test_nested_merge(self):
        base = {"a": {"x": 1, "y": 2}, "b": 3}
        override = {"a": {"y": 20, "z": 30}}
        result = _deep_merge(base, override)
        assert result == {"a": {"x": 1, "y": 20, "z": 30}, "b": 3}

    def test_override_non_dict(self):
        base = {"a": {"x": 1}}
        override = {"a": "string"}
        result = _deep_merge(base, override)
        assert result == {"a": "string"}


class TestProjectConfig:
    """Tests for ProjectConfig class."""

    def test_load_valid_yaml(self, tmp_path):
        if yaml is None:
            pytest.skip("PyYAML not installed")

        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            """
project:
  name: test_project
  id: test_id
generation:
  temperature: 0.7
"""
        )

        config = ProjectConfig.load(str(config_file))
        assert config.project.name == "test_project"
        assert config.generation.temperature == 0.7

    def test_load_valid_json(self, tmp_path):
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps(
                {
                    "project": {"name": "test_project", "id": "test_id"},
                    "generation": {"temperature": 0.7},
                }
            )
        )

        config = ProjectConfig.load(str(config_file))
        assert config.project.name == "test_project"
        assert config.generation.temperature == 0.7

    def test_load_missing_file(self, tmp_path):
        with pytest.raises(FileNotFoundError, match="Config not found"):
            ProjectConfig.load(str(tmp_path / "missing.yaml"))

    def test_load_unsupported_format(self, tmp_path):
        config_file = tmp_path / "config.txt"
        config_file.write_text("invalid")
        with pytest.raises(ValueError, match="Unsupported config format"):
            ProjectConfig.load(str(config_file))

    def test_load_empty_file(self, tmp_path):
        """Test that empty config files raise an error."""
        if yaml is None:
            pytest.skip("PyYAML not installed")

        config_file = tmp_path / "config.yaml"
        config_file.write_text("")

        with pytest.raises(ValueError, match="Config file is empty"):
            ProjectConfig.load(str(config_file))

    def test_load_missing_project_name(self, tmp_path):
        """Test that configs without project.name raise an error."""
        if yaml is None:
            pytest.skip("PyYAML not installed")

        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            """
generation:
  temperature: 0.7
"""
        )

        with pytest.raises(ValueError, match="Project name is required"):
            ProjectConfig.load(str(config_file))

    def test_load_with_project_folder_enrichment(self, tmp_path):
        """Test that project metadata is enriched from folder structure."""
        if yaml is None:
            pytest.skip("PyYAML not installed")

        # Create projects/test_project/config.yaml structure
        projects_dir = tmp_path / "projects" / "test_project"
        projects_dir.mkdir(parents=True)
        config_file = projects_dir / "config.yaml"
        config_file.write_text(
            """
project:
  name: Test Project
"""
        )

        # Note: This will not auto-enrich folder/id because tmp_path is not _repo_root()
        # But it should still load successfully
        config = ProjectConfig.load(str(config_file))
        assert config.project.name == "Test Project"

    def test_load_non_dict_root(self, tmp_path):
        """Test that non-dict root configs raise an error."""
        if yaml is None:
            pytest.skip("PyYAML not installed")

        config_file = tmp_path / "config.yaml"
        config_file.write_text("- item1\n- item2")

        with pytest.raises(ValueError, match="Config root must be a mapping"):
            ProjectConfig.load(str(config_file))


class TestLoadFunction:
    """Tests for module-level load() function."""

    def test_load_existing_project(self, tmp_path, monkeypatch):
        """Test loading a project by name."""
        if yaml is None:
            pytest.skip("PyYAML not installed")

        # Mock _repo_root to return tmp_path
        def mock_repo_root():
            return tmp_path

        import core.utils.config_loader

        monkeypatch.setattr(core.utils.config_loader, "_repo_root", mock_repo_root)

        # Create projects/test_project/config.yaml
        projects_dir = tmp_path / "projects" / "test_project"
        projects_dir.mkdir(parents=True)
        config_file = projects_dir / "config.yaml"
        config_file.write_text(
            """
project:
  name: Test Project
  id: test_project
generation:
  temperature: 0.7
"""
        )

        config = load("test_project")
        assert config.project.name == "Test Project"
        assert config.project.id == "test_project"
        assert config.generation.temperature == 0.7

    def test_load_missing_project(self, tmp_path, monkeypatch):
        """Test loading a non-existent project."""

        def mock_repo_root():
            return tmp_path

        import core.utils.config_loader

        monkeypatch.setattr(core.utils.config_loader, "_repo_root", mock_repo_root)

        with pytest.raises(FileNotFoundError, match="Project config not found"):
            load("nonexistent_project")


class TestBackwardCompatibility:
    """Tests for backward compatibility with old code patterns."""

    def test_dict_like_access(self):
        """Test that ConfigNode works as a dict."""
        node = ConfigNode({"key": "value"})
        assert node["key"] == "value"
        assert node.get("key") == "value"
        assert "key" in node

    def test_empty_node_is_falsy(self):
        """Test that empty ConfigNode is falsy (like empty dict)."""
        node = ConfigNode({})
        assert not node
        if node:
            pytest.fail("Empty ConfigNode should be falsy")

    def test_nested_access_chains(self):
        """Test that missing nested access returns empty node."""
        node = ConfigNode({"a": {"b": {"c": 42}}})
        assert node.a.b.c == 42
        # Missing chain
        missing = node.x.y.z
        assert isinstance(missing, ConfigNode)
        assert not missing
