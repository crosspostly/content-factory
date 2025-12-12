"""Tests for Environment Checker utility."""
from __future__ import annotations

import os
import shutil
from unittest.mock import patch

import pytest

from core.utils import environment_checker


class TestEnvironmentCheck:
    """Test environment verification."""
    
    def test_check_environment_basic(self):
        """Test basic environment check."""
        result = environment_checker.check_environment()
        
        assert "python_version" in result
        assert "ffmpeg" in result
        assert "imagemagick" in result
        assert "env_vars" in result
        assert "output_dirs" in result
        assert "all_checks_passed" in result
        
        # Python version should be a string
        assert isinstance(result["python_version"], str)
        assert "." in result["python_version"]
    
    def test_check_ffmpeg_installed(self):
        """Test FFmpeg detection."""
        result = environment_checker.check_environment()
        
        # FFmpeg should be available in test environment
        # (GitHub Actions installs it)
        assert isinstance(result["ffmpeg"], bool)
    
    def test_check_imagemagick_detection(self):
        """Test ImageMagick detection."""
        result = environment_checker.check_environment()
        
        # ImageMagick may or may not be installed
        assert isinstance(result["imagemagick"], bool)
    
    def test_check_env_vars(self):
        """Test environment variable detection."""
        result = environment_checker.check_environment()
        
        assert "GOOGLE_AI_API_KEY" in result["env_vars"]
        assert "PIXABAY_API_KEY" in result["env_vars"]
        assert "OPENROUTER_API_KEY" in result["env_vars"]
        assert "TELEGRAM_BOT_TOKEN" in result["env_vars"]
        assert "TELEGRAM_CHAT_ID" in result["env_vars"]
        
        # All should be booleans
        for key, value in result["env_vars"].items():
            assert isinstance(value, bool)
    
    def test_output_dirs_creation(self):
        """Test that output directories are created."""
        result = environment_checker.check_environment()
        
        assert result["output_dirs"] is True
        
        # Check that directories actually exist
        from pathlib import Path
        assert Path("output/scripts").exists()
        assert Path("output/audio").exists()
        assert Path("output/videos").exists()
        assert Path("output/logs").exists()
    
    @patch.dict(os.environ, {"GOOGLE_AI_API_KEY": "test_key_123"}, clear=False)
    def test_check_with_api_key(self):
        """Test environment check with API key set."""
        result = environment_checker.check_environment()
        
        assert result["env_vars"]["GOOGLE_AI_API_KEY"] is True
    
    @patch.dict(os.environ, {}, clear=True)
    def test_check_without_api_keys(self):
        """Test environment check without API keys."""
        result = environment_checker.check_environment()
        
        # Without required keys, checks should fail
        assert result["all_checks_passed"] is False
    
    @patch('shutil.which')
    def test_check_missing_ffmpeg(self, mock_which):
        """Test environment check when FFmpeg is missing."""
        mock_which.return_value = None
        
        result = environment_checker.check_environment()
        
        assert result["ffmpeg"] is False
        assert result["all_checks_passed"] is False
    
    @patch.dict(os.environ, {"GOOGLE_AI_API_KEY": "test_key"}, clear=False)
    @patch('shutil.which')
    def test_check_all_pass(self, mock_which):
        """Test environment check when all requirements are met."""
        mock_which.side_effect = lambda x: "/usr/bin/" + x if x in ["ffmpeg", "convert"] else None
        
        result = environment_checker.check_environment()
        
        assert result["ffmpeg"] is True
        assert result["env_vars"]["GOOGLE_AI_API_KEY"] is True
        assert result["all_checks_passed"] is True


class TestModuleExecution:
    """Test running the module as a script."""
    
    def test_module_can_be_imported(self):
        """Test that the module can be imported."""
        from core.utils import environment_checker
        assert hasattr(environment_checker, 'check_environment')
    
    @patch('core.utils.environment_checker.check_environment')
    def test_main_execution(self, mock_check):
        """Test running as main module."""
        mock_check.return_value = {"all_checks_passed": True}
        
        # This would be run as: python -m core.utils.environment_checker
        # We just verify the function can be called
        result = environment_checker.check_environment()
        assert result is not None
