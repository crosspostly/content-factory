"""
Tests for script_generator with ModelRouter integration.
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from core.generators import script_generator
from core.utils.config_loader import ProjectConfig


@pytest.fixture
def mock_config():
    """Mock project configuration."""
    return ProjectConfig({
        "project": {
            "name": "test_horoscope",
            "folder": "test_horoscope",
            "niche": "astrology",
            "target_audience": "Women 18-45"
        },
        "generation": {
            "prompt_files": {
                "shorts_script": "prompts/shorts_scenario.txt",
                "long_form_script": "prompts/long_form_scenario.txt",
                "ad_script": "prompts/ad_script.txt"
            }
        }
    })


@pytest.fixture
def mock_api_key():
    """Mock API key."""
    return "test_api_key_12345"


class TestLengthValidation:
    """Test script length validation."""
    
    def test_validate_short_script_valid(self):
        """Valid shorts script should pass."""
        script = "x" * 250  # 250 chars - within range
        is_valid, reason = script_generator._validate_script_length(script, "shorts")
        assert is_valid
        assert "Valid: 250 chars" in reason
    
    def test_validate_short_script_too_short(self):
        """Too short script should fail."""
        script = "x" * 100  # 100 chars - below minimum 200
        is_valid, reason = script_generator._validate_script_length(script, "shorts")
        assert not is_valid
        assert "Too short" in reason
        assert "deficit: 100" in reason
    
    def test_validate_short_script_too_long(self):
        """Too long script should fail."""
        script = "x" * 500  # 500 chars - above maximum 400
        is_valid, reason = script_generator._validate_script_length(script, "shorts")
        assert not is_valid
        assert "Too long" in reason
        assert "excess: 100" in reason
    
    def test_validate_long_form_valid(self):
        """Valid long-form script should pass."""
        script = "x" * 1000
        is_valid, reason = script_generator._validate_script_length(script, "long_form")
        assert is_valid
        assert "Valid: 1000 chars" in reason


class TestPromptBuilding:
    """Test horoscope prompt building."""
    
    def test_build_shorts_prompt(self, mock_config):
        """Test shorts prompt building."""
        prompt = script_generator._build_horoscope_prompt(
            mock_config, "2025-12-13", "shorts"
        )
        
        # Date should be formatted (locale-dependent)
        assert "2025" in prompt and "13" in prompt and ("декабря" in prompt or "December" in prompt)
        assert "shorts" in prompt.lower() or "короткий" in prompt.lower()
        assert "JSON" in prompt
        assert "200" in prompt  # Min length
        assert "400" in prompt  # Max length
    
    def test_build_long_form_prompt(self, mock_config):
        """Test long-form prompt building."""
        prompt = script_generator._build_horoscope_prompt(
            mock_config, "2025-12-13", "long_form"
        )
        
        assert "long_form" in prompt.lower() or "подробный" in prompt.lower()
        assert "800" in prompt  # Min length
        assert "1500" in prompt  # Max length
    
    def test_prompt_includes_audience(self, mock_config):
        """Prompt should include target audience."""
        prompt = script_generator._build_horoscope_prompt(
            mock_config, "2025-12-13", "shorts"
        )
        
        assert "Women 18-45" in prompt or "Женщины" in prompt


@pytest.mark.slow
class TestScriptGenerationWithModelRouter:
    """Integration tests with ModelRouter (requires API key)."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset ModelRouter before each test."""
        from core.utils.model_router import reset_router
        reset_router()
    
    @patch('core.generators.script_generator._read_project_prompt')
    def test_generate_short_with_modelrouter(self, mock_read_prompt, mock_config, mock_api_key):
        """Test shorts generation with ModelRouter."""
        mock_read_prompt.return_value = "Test prompt template"
        
        # Skip if no real API key
        if not os.getenv("GOOGLE_AI_API_KEY"):
            pytest.skip("GOOGLE_AI_API_KEY not set")
        
        result = script_generator.generate_short(
            mock_config,
            target_date="2025-12-13",
            api_key=os.getenv("GOOGLE_AI_API_KEY")
        )
        
        assert "script" in result
        assert "hook" in result
        assert "_script_path" in result
        assert len(result["script"]) >= 200  # Minimum length enforced
    
    @patch('core.generators.script_generator._read_project_prompt')
    def test_length_validation_retries(self, mock_read_prompt, mock_config):
        """Test that length validation triggers retries."""
        mock_read_prompt.return_value = ""
        
        # Mock ModelRouter to return short script first, then valid
        with patch('core.utils.model_router.ModelRouter.generate_json') as mock_gen:
            # First call: too short
            # Second call: valid length
            mock_gen.side_effect = [
                {
                    "script": "Too short",  # < 200 chars
                    "hook": "Test",
                },
                {
                    "script": "x" * 250,  # Valid length
                    "hook": "Test",
                }
            ]
            
            result = script_generator.generate_short(
                mock_config,
                target_date="2025-12-13",
                api_key="test_key"
            )
            
            # Should have called twice (1 initial + 1 retry)
            assert mock_gen.call_count >= 2
            assert len(result["script"]) >= 200


class TestMetadataSaving:
    """Test script metadata saving."""
    
    def test_save_script_creates_file(self, tmp_path, mock_config):
        """Test that script is saved to JSON file."""
        script = {
            "hook": "Test hook",
            "script": "Test script content",
            "content_type": "shorts"
        }
        
        # Temporarily change output dir to tmp
        with patch('core.generators.script_generator.Path') as mock_path:
            mock_output_dir = tmp_path / "output" / "scripts" / "test" / "20251213"
            mock_output_dir.mkdir(parents=True, exist_ok=True)
            
            mock_path.return_value = mock_output_dir
            
            path = script_generator._save_script_to_file(
                script, "test", "2025-12-13", "short"
            )
            
            assert "short_" in path
            assert ".json" in path


class TestBuildPromptWithTemplate:
    """Test prompt building with custom templates."""
    
    def test_custom_template_with_date_replacement(self, mock_config):
        """Custom template should have {date} replaced."""
        template = "Generate horoscope for {date}"
        
        prompt = script_generator._build_horoscope_prompt(
            mock_config, "2025-12-13", "shorts", template
        )
        
        assert "{date}" not in prompt  # Should be replaced
        assert "2025" in prompt and "13" in prompt  # Date formatted (locale-dependent)
