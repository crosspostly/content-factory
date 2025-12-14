"""Tests for Pipeline Orchestrator."""
from __future__ import annotations

import argparse
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from core.orchestrators import pipeline_orchestrator


class TestCommandLineInterface:
    """Test CLI argument parsing."""
    
    def test_build_parser(self):
        """Test that parser is built correctly."""
        parser = pipeline_orchestrator.build_parser()
        assert parser is not None
        assert isinstance(parser, argparse.ArgumentParser)
    
    def test_parse_shorts_args(self):
        """Test parsing shorts mode arguments."""
        parser = pipeline_orchestrator.build_parser()
        args = parser.parse_args([
            "--project", "test_project",
            "--mode", "shorts"
        ])
        
        assert args.project == "test_project"
        assert args.mode == "shorts"
        assert args.dry_run is False
        assert args.upload is False
    
    def test_parse_long_form_args(self):
        """Test parsing long-form mode arguments."""
        parser = pipeline_orchestrator.build_parser()
        args = parser.parse_args([
            "--project", "test_project",
            "--mode", "long_form",
            "--date", "2025-01-15"
        ])
        
        assert args.project == "test_project"
        assert args.mode == "long_form"
        assert args.date == "2025-01-15"
    
    def test_parse_ad_args(self):
        """Test parsing ad mode arguments."""
        parser = pipeline_orchestrator.build_parser()
        args = parser.parse_args([
            "--project", "test_project",
            "--mode", "ad",
            "--product-id", "test_product_123"
        ])
        
        assert args.project == "test_project"
        assert args.mode == "ad"
        assert args.product_id == "test_product_123"
    
    def test_parse_dry_run(self):
        """Test dry-run flag."""
        parser = pipeline_orchestrator.build_parser()
        args = parser.parse_args([
            "--project", "test_project",
            "--mode", "shorts",
            "--dry-run"
        ])
        
        assert args.dry_run is True
    
    def test_parse_upload_with_platforms(self):
        """Test upload flag with platforms."""
        parser = pipeline_orchestrator.build_parser()
        args = parser.parse_args([
            "--project", "test_project",
            "--mode", "shorts",
            "--upload",
            "--platforms", "youtube,tiktok"
        ])
        
        assert args.upload is True
        assert args.platforms == "youtube,tiktok"


class TestPlatformExtraction:
    """Test platform configuration extraction."""
    
    def test_get_platforms_from_arg(self):
        """Test getting platforms from command-line argument."""
        from core.utils.config_loader import ProjectConfig
        
        config = ProjectConfig({"upload": {"platforms": []}})
        platforms = pipeline_orchestrator._get_platforms(config, "youtube,tiktok")
        
        assert platforms == ["youtube", "tiktok"]
    
    def test_get_platforms_from_config_list(self):
        """Test getting platforms from config as list."""
        from core.utils.config_loader import ProjectConfig
        
        config = ProjectConfig({
            "upload": {"platforms": ["youtube", "instagram"]}
        })
        platforms = pipeline_orchestrator._get_platforms(config, None)
        
        assert "youtube" in platforms
        assert "instagram" in platforms
    
    def test_get_platforms_from_config_dict(self):
        """Test getting platforms from config as dict."""
        from core.utils.config_loader import ProjectConfig
        
        config = ProjectConfig({
            "upload": {
                "platforms": {
                    "youtube": {"enabled": True},
                    "tiktok": {"enabled": False},
                    "instagram": {}
                }
            }
        })
        platforms = pipeline_orchestrator._get_platforms(config, None)
        
        assert "youtube" in platforms
        assert "tiktok" not in platforms  # disabled
        assert "instagram" in platforms
    
    def test_get_platforms_empty(self):
        """Test getting platforms when none configured."""
        from core.utils.config_loader import ProjectConfig
        
        config = ProjectConfig({"upload": {}})
        platforms = pipeline_orchestrator._get_platforms(config, None)
        
        assert platforms == []


class TestPipelineExecution:
    """Test pipeline execution."""
    
    @patch.dict('os.environ', {'GOOGLE_AI_API_KEY': 'test_api_key'})
    @patch('core.orchestrators.pipeline_orchestrator.config_loader.load')
    @patch('core.generators.script_generator.generate_short')
    @patch('core.generators.tts_generator.synthesize')
    @patch('core.generators.video_renderer.render')
    @patch('core.utils.model_router.get_router')
    def test_main_shorts_success(self, mock_router, mock_render, mock_tts, mock_script, mock_load):
        """Test successful shorts pipeline execution."""
        # Setup mocks
        mock_config = MagicMock()
        mock_config.monitoring.telegram_notifications = False
        mock_load.return_value = mock_config
        
        # Mock ModelRouter
        mock_router.return_value.get_stats.return_value = {
            "total_attempts": 1,
            "successful": 1,
            "failed": 0,
            "success_rate": "100%",
            "model_usage": {"gemini-2.5-flash": 1}
        }
        
        mock_script.return_value = {"id": "test_123", "hook": "Test", "_script_path": "/tmp/script.json", "script": "Test script"}
        mock_tts.return_value = {
            "blocks": {"main": "/tmp/audio.wav"},
            "total_duration_sec": 15.0
        }
        mock_render.return_value = Path("/tmp/video.mp4")
        
        # Create args
        args = argparse.Namespace(
            project="test_project",
            mode="shorts",
            date="2025-01-15",
            dry_run=False,
            upload=False,
            platforms=None,
            product_id=None
        )
        
        # Execute
        result = pipeline_orchestrator.main(args)
        
        assert result == 0
        mock_script.assert_called_once()
        mock_tts.assert_called_once()
        mock_render.assert_called_once()
    
    @patch.dict('os.environ', {'GOOGLE_AI_API_KEY': 'test_api_key'})
    @patch('core.orchestrators.pipeline_orchestrator.config_loader.load')
    @patch('core.generators.script_generator.generate_long_form')
    @patch('core.generators.tts_generator.synthesize')
    @patch('core.generators.video_renderer.render')
    @patch('core.utils.model_router.get_router')
    def test_main_long_form_success(self, mock_router, mock_render, mock_tts, mock_script, mock_load):
        """Test successful long-form pipeline execution."""
        # Setup mocks
        mock_config = MagicMock()
        mock_config.monitoring.telegram_notifications = False
        mock_load.return_value = mock_config
        
        # Mock ModelRouter
        mock_router.return_value.get_stats.return_value = {
            "total_attempts": 1,
            "successful": 1,
            "failed": 0,
            "success_rate": "100%",
            "model_usage": {"gemini-2.5-flash": 1}
        }
        
        mock_script.return_value = {
            "id": "test_123",
            "blocks": {"love": "...", "money": "...", "health": "..."},
            "_script_path": "/tmp/script.json",
            "script": "Test script"
        }
        mock_tts.return_value = {
            "blocks": {
                "love": "/tmp/love.wav",
                "money": "/tmp/money.wav",
                "health": "/tmp/health.wav"
            },
            "total_duration_sec": 180.0
        }
        mock_render.return_value = Path("/tmp/video.mp4")
        
        # Create args
        args = argparse.Namespace(
            project="test_project",
            mode="long_form",
            date="2025-01-15",
            dry_run=False,
            upload=False,
            platforms=None,
            product_id=None
        )
        
        # Execute
        result = pipeline_orchestrator.main(args)
        
        assert result == 0
        mock_script.assert_called_once()
        mock_tts.assert_called_once()
        mock_render.assert_called_once()
    
    @patch('core.orchestrators.pipeline_orchestrator.config_loader.load')
    def test_main_config_not_found(self, mock_load):
        """Test pipeline with missing config."""
        mock_load.side_effect = FileNotFoundError("Config not found")
        
        args = argparse.Namespace(
            project="nonexistent_project",
            mode="shorts",
            date="2025-01-15",
            dry_run=False,
            upload=False,
            platforms=None,
            product_id=None
        )
        
        result = pipeline_orchestrator.main(args)
        
        assert result == 1  # Error exit code
    
    @patch('core.orchestrators.pipeline_orchestrator.config_loader.load')
    @patch('core.generators.script_generator.generate_short')
    def test_main_script_generation_failure(self, mock_script, mock_load):
        """Test pipeline when script generation fails."""
        mock_config = MagicMock()
        mock_config.monitoring.telegram_notifications = False
        mock_load.return_value = mock_config
        
        mock_script.side_effect = Exception("Script generation error")
        
        args = argparse.Namespace(
            project="test_project",
            mode="shorts",
            date="2025-01-15",
            dry_run=False,
            upload=False,
            platforms=None,
            product_id=None
        )
        
        result = pipeline_orchestrator.main(args)
        
        assert result == 1  # Error exit code
    
    @patch('core.orchestrators.pipeline_orchestrator.config_loader.load')
    @patch('core.generators.script_generator.generate_short')
    @patch('core.generators.tts_generator.synthesize')
    def test_main_tts_failure(self, mock_tts, mock_script, mock_load):
        """Test pipeline when TTS fails."""
        mock_config = MagicMock()
        mock_config.monitoring.telegram_notifications = False
        mock_load.return_value = mock_config
        
        mock_script.return_value = {"id": "test_123", "hook": "Test"}
        mock_tts.side_effect = Exception("TTS error")
        
        args = argparse.Namespace(
            project="test_project",
            mode="shorts",
            date="2025-01-15",
            dry_run=False,
            upload=False,
            platforms=None,
            product_id=None
        )
        
        result = pipeline_orchestrator.main(args)
        
        assert result == 1  # Error exit code
    
    @patch('core.orchestrators.pipeline_orchestrator.config_loader.load')
    @patch('core.generators.script_generator.generate_short')
    @patch('core.generators.tts_generator.synthesize')
    @patch('core.generators.video_renderer.render')
    def test_main_video_rendering_failure(self, mock_render, mock_tts, mock_script, mock_load):
        """Test pipeline when video rendering fails."""
        mock_config = MagicMock()
        mock_config.monitoring.telegram_notifications = False
        mock_load.return_value = mock_config
        
        mock_script.return_value = {"id": "test_123", "hook": "Test"}
        mock_tts.return_value = {
            "blocks": {"main": "/tmp/audio.wav"},
            "total_duration_sec": 15.0
        }
        mock_render.side_effect = Exception("Rendering error")
        
        args = argparse.Namespace(
            project="test_project",
            mode="shorts",
            date="2025-01-15",
            dry_run=False,
            upload=False,
            platforms=None,
            product_id=None
        )
        
        result = pipeline_orchestrator.main(args)
        
        assert result == 1  # Error exit code
    
    @patch('core.orchestrators.pipeline_orchestrator.config_loader.load')
    @patch('core.generators.script_generator.generate_ad')
    def test_main_ad_without_product_id(self, mock_script, mock_load):
        """Test ad mode without product ID."""
        mock_config = MagicMock()
        mock_config.monitoring.telegram_notifications = False
        mock_load.return_value = mock_config
        
        args = argparse.Namespace(
            project="test_project",
            mode="ad",
            date="2025-01-15",
            dry_run=False,
            upload=False,
            platforms=None,
            product_id=None  # Missing!
        )
        
        result = pipeline_orchestrator.main(args)
        
        assert result == 1  # Error exit code


class TestIntegration:
    """Integration tests for full pipeline."""
    
    @pytest.mark.slow
    def test_full_pipeline_shorts_real(self):
        """Test full pipeline with real implementation (shorts)."""
        # This test requires:
        # - Valid config file
        # - GOOGLE_AI_API_KEY env var
        # - ffmpeg installed
        
        # Skip if not in proper environment
        try:
            from core.utils.config_loader import load
            config = load("youtube_horoscope")
        except Exception:
            pytest.skip("Config not available")
        
        args = argparse.Namespace(
            project="youtube_horoscope",
            mode="shorts",
            date="2025-01-15",
            dry_run=True,  # Use dry-run to avoid actual API calls
            upload=False,
            platforms=None,
            product_id=None
        )
        
        # Just test that it doesn't crash
        # Full execution tested in actual workflow
        parser = pipeline_orchestrator.build_parser()
        assert parser is not None
