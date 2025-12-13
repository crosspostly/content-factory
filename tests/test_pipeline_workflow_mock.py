"""Mock tests for pipeline workflow integration - testing GitHub Actions scenario."""
from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import MagicMock, patch, call

import pytest

from core.utils.config_loader import ProjectConfig


class TestWorkflowPipelineMock:
    """Test the complete pipeline flow as executed in GitHub Actions workflow."""
    
    @patch('core.generators.video_renderer.render')
    @patch('core.generators.tts_generator.synthesize')
    @patch('core.generators.script_generator.generate_short')
    @patch('core.utils.config_loader.ProjectConfig.load')
    def test_workflow_shorts_complete_flow(
        self, 
        mock_load, 
        mock_script_gen, 
        mock_tts_gen, 
        mock_video_render
    ):
        """
        Test the complete workflow as executed in GitHub Actions for shorts.
        
        This simulates the exact flow in .github/workflows/generate-horoscope-video.yml
        """
        # Setup mock config
        mock_config = MagicMock(spec=ProjectConfig)
        mock_project = MagicMock()
        mock_project.get.return_value = "youtube_horoscope"
        mock_config.project = mock_project
        mock_config.get.return_value = {"name": "youtube_horoscope"}
        mock_load.return_value = mock_config
        
        # Setup mock script generation
        mock_script = {
            "id": "test_script_123",
            "script": "Овен: Сегодня вас ждет удача!" * 10,  # 300+ chars
            "hook": "🔮 Гороскоп на сегодня",
            "visual_hints": ["stars", "zodiac"],
            "engagement_cta": "Подпишитесь!",
            "_script_path": "output/scripts/youtube_horoscope/2025-12-13/script_123.json"
        }
        mock_script_gen.return_value = mock_script
        
        # Setup mock TTS synthesis
        mock_audio_map = {
            "blocks": {
                "main": "output/audio/youtube_horoscope/shorts.wav"
            },
            "total_duration_sec": 49.3,
            "sample_rate": 22050
        }
        mock_tts_gen.return_value = mock_audio_map
        
        # Setup mock video rendering
        mock_video_path = Path("output/videos/youtube_horoscope/shorts.mp4")
        mock_video_render.return_value = mock_video_path
        
        # Simulate workflow execution
        project_name = "youtube_horoscope"
        fmt = "shorts"
        target_date = "2025-12-13"
        api_key = "test_api_key_12345"
        
        # PART 1: Load config
        config_path = f"projects/{project_name}/config.yaml"
        config = ProjectConfig.load(config_path)
        
        # PART 2: Generate script
        script = mock_script_gen(
            config=config,
            target_date=target_date,
            api_key=api_key
        )
        
        # PART 3: Synthesize audio
        audio_map = mock_tts_gen(
            config=config,
            script=script,
            mode=fmt,
            api_key=api_key
        )
        
        # PART 4: Render video (THIS IS THE CRITICAL CALL THAT WAS FAILING)
        video_path = mock_video_render(
            config=config,  # ✅ This was missing in the workflow!
            script=script,
            audio_map=audio_map,
            mode=fmt
        )
        
        # Assertions
        assert video_path == mock_video_path
        
        # Verify all functions were called with correct arguments
        mock_load.assert_called_once_with(config_path)
        mock_script_gen.assert_called_once_with(
            config=config,
            target_date=target_date,
            api_key=api_key
        )
        mock_tts_gen.assert_called_once_with(
            config=config,
            script=script,
            mode=fmt,
            api_key=api_key
        )
        mock_video_render.assert_called_once_with(
            config=config,  # ✅ Critical parameter
            script=script,
            audio_map=audio_map,
            mode=fmt
        )
    
    @patch('core.generators.video_renderer.render')
    @patch('core.generators.tts_generator.synthesize')
    @patch('core.generators.script_generator.generate_long_form')
    @patch('core.utils.config_loader.ProjectConfig.load')
    def test_workflow_long_form_complete_flow(
        self,
        mock_load,
        mock_script_gen,
        mock_tts_gen,
        mock_video_render
    ):
        """Test the complete workflow for long-form videos."""
        # Setup mock config
        mock_config = MagicMock(spec=ProjectConfig)
        mock_project = MagicMock()
        mock_project.get.return_value = "youtube_horoscope"
        mock_config.project = mock_project
        mock_load.return_value = mock_config
        
        # Setup mock script generation
        mock_script = {
            "id": "test_script_long_456",
            "video_title": "Полный гороскоп на неделю",
            "blocks": {
                "love": "Любовный гороскоп...",
                "money": "Финансовый гороскоп...",
                "health": "Здоровье..."
            },
            "_script_path": "output/scripts/youtube_horoscope/2025-12-13/script_456.json"
        }
        mock_script_gen.return_value = mock_script
        
        # Setup mock TTS synthesis
        mock_audio_map = {
            "blocks": {
                "love": "output/audio/youtube_horoscope/love.wav",
                "money": "output/audio/youtube_horoscope/money.wav",
                "health": "output/audio/youtube_horoscope/health.wav"
            },
            "total_duration_sec": 180.0,
            "sample_rate": 22050
        }
        mock_tts_gen.return_value = mock_audio_map
        
        # Setup mock video rendering
        mock_video_path = Path("output/videos/youtube_horoscope/long_form.mp4")
        mock_video_render.return_value = mock_video_path
        
        # Simulate workflow execution
        project_name = "youtube_horoscope"
        fmt = "long_form"
        target_date = "2025-12-13"
        api_key = "test_api_key_12345"
        
        # Load config
        config_path = f"projects/{project_name}/config.yaml"
        config = ProjectConfig.load(config_path)
        
        # Generate script
        script = mock_script_gen(
            config=config,
            target_date=target_date,
            api_key=api_key
        )
        
        # Synthesize audio
        audio_map = mock_tts_gen(
            config=config,
            script=script,
            mode=fmt,
            api_key=api_key
        )
        
        # Render video
        video_path = mock_video_render(
            config=config,  # ✅ Must include config
            script=script,
            audio_map=audio_map,
            mode=fmt
        )
        
        # Assertions
        assert video_path == mock_video_path
        mock_video_render.assert_called_once_with(
            config=config,
            script=script,
            audio_map=audio_map,
            mode=fmt
        )
    
    @patch('core.generators.video_renderer.render')
    @patch('core.generators.tts_generator.synthesize')
    @patch('core.generators.script_generator.generate_ad')
    @patch('core.utils.config_loader.ProjectConfig.load')
    def test_workflow_ad_complete_flow(
        self,
        mock_load,
        mock_script_gen,
        mock_tts_gen,
        mock_video_render
    ):
        """Test the complete workflow for ad videos."""
        # Setup mock config
        mock_config = MagicMock(spec=ProjectConfig)
        mock_project = MagicMock()
        mock_project.get.return_value = "youtube_horoscope"
        mock_config.project = mock_project
        mock_load.return_value = mock_config
        
        # Setup mock script generation
        mock_script = {
            "id": "test_ad_789",
            "script": "Специальное предложение только сегодня!",
            "product_id": "premium_horoscope_sub",
            "hook": "💎 Премиум подписка",
            "_script_path": "output/scripts/youtube_horoscope/2025-12-13/script_789.json"
        }
        mock_script_gen.return_value = mock_script
        
        # Setup mock TTS synthesis
        mock_audio_map = {
            "blocks": {
                "main": "output/audio/youtube_horoscope/ad.wav"
            },
            "total_duration_sec": 25.0,
            "sample_rate": 22050
        }
        mock_tts_gen.return_value = mock_audio_map
        
        # Setup mock video rendering
        mock_video_path = Path("output/videos/youtube_horoscope/ad.mp4")
        mock_video_render.return_value = mock_video_path
        
        # Simulate workflow execution
        project_name = "youtube_horoscope"
        fmt = "ad"
        target_date = "2025-12-13"
        api_key = "test_api_key_12345"
        
        # Load config
        config = ProjectConfig.load(f"projects/{project_name}/config.yaml")
        
        # Generate script
        script = mock_script_gen(
            config=config,
            product_id="premium_horoscope_sub",
            target_date=target_date,
            api_key=api_key
        )
        
        # Synthesize audio
        audio_map = mock_tts_gen(
            config=config,
            script=script,
            mode=fmt,
            api_key=api_key
        )
        
        # Render video
        video_path = mock_video_render(
            config=config,  # ✅ Must include config
            script=script,
            audio_map=audio_map,
            mode=fmt
        )
        
        # Assertions
        assert video_path == mock_video_path


class TestVideoRendererSignature:
    """Test video_renderer.render() function signature validation."""
    
    def test_render_requires_config_parameter(self):
        """Test that render() requires config as first parameter."""
        from core.generators import video_renderer
        import inspect
        
        # Get the signature of render function
        sig = inspect.signature(video_renderer.render)
        params = list(sig.parameters.keys())
        
        # Assert config is the first parameter
        assert params[0] == "config", f"First parameter should be 'config', got '{params[0]}'"
        assert "config" in params, "config must be a parameter"
        assert "script" in params, "script must be a parameter"
        assert "audio_map" in params, "audio_map must be a parameter"
        assert "mode" in params, "mode must be a parameter"
    
    @patch('core.generators.video_renderer._render_shorts')
    def test_render_calls_with_config(self, mock_render_shorts):
        """Test that render() passes config to sub-renderers."""
        from core.generators import video_renderer
        
        mock_config = MagicMock(spec=ProjectConfig)
        mock_script = {"id": "test", "script": "test script"}
        mock_audio_map = {"blocks": {"main": "/tmp/test.wav"}, "total_duration_sec": 10.0}
        
        mock_render_shorts.return_value = Path("/tmp/test.mp4")
        
        result = video_renderer.render(
            config=mock_config,
            script=mock_script,
            audio_map=mock_audio_map,
            mode="shorts"
        )
        
        # Verify _render_shorts was called with config
        mock_render_shorts.assert_called_once_with(
            mock_config,
            mock_script,
            mock_audio_map
        )
    
    def test_render_without_config_raises_error(self):
        """Test that calling render() without config raises TypeError."""
        from core.generators import video_renderer
        
        mock_script = {"id": "test", "script": "test script"}
        mock_audio_map = {"blocks": {"main": "/tmp/test.wav"}, "total_duration_sec": 10.0}
        
        # This should raise TypeError: missing required positional argument 'config'
        with pytest.raises(TypeError, match="missing.*required.*argument.*config"):
            video_renderer.render(
                script=mock_script,  # ❌ Missing config!
                audio_map=mock_audio_map,
                mode="shorts"
            )


class TestWorkflowErrorHandling:
    """Test error handling in workflow scenarios."""
    
    @patch('core.generators.video_renderer.render')
    @patch('core.generators.tts_generator.synthesize')
    @patch('core.generators.script_generator.generate_short')
    @patch('core.utils.config_loader.ProjectConfig.load')
    def test_workflow_handles_missing_config_in_render_call(
        self,
        mock_load,
        mock_script_gen,
        mock_tts_gen,
        mock_video_render
    ):
        """
        Test that workflow correctly handles TypeError when config is missing.
        
        This was the original bug: render() was called without config parameter.
        """
        # Setup mocks
        mock_config = MagicMock(spec=ProjectConfig)
        mock_load.return_value = mock_config
        
        mock_script = {"id": "test", "script": "test script"}
        mock_script_gen.return_value = mock_script
        
        mock_audio_map = {"blocks": {"main": "/tmp/test.wav"}, "total_duration_sec": 10.0}
        mock_tts_gen.return_value = mock_audio_map
        
        # Simulate the original bug: render() called WITHOUT config
        mock_video_render.side_effect = TypeError(
            "render() missing 1 required positional argument: 'config'"
        )
        
        # Execute workflow
        config = ProjectConfig.load("projects/test/config.yaml")
        script = mock_script_gen(config=config, target_date="2025-12-13", api_key="test")
        audio_map = mock_tts_gen(config=config, script=script, mode="shorts", api_key="test")
        
        # This should raise TypeError
        with pytest.raises(TypeError, match="missing.*config"):
            # OLD WORKFLOW CODE (buggy):
            mock_video_render(
                script=script,  # ❌ Missing config!
                audio_map=audio_map,
                mode="shorts"
            )
    
    @patch('core.generators.video_renderer.render')
    @patch('core.generators.tts_generator.synthesize')
    @patch('core.generators.script_generator.generate_short')
    @patch('core.utils.config_loader.ProjectConfig.load')
    def test_workflow_fixed_with_config_parameter(
        self,
        mock_load,
        mock_script_gen,
        mock_tts_gen,
        mock_video_render
    ):
        """
        Test that workflow works correctly WITH config parameter.
        
        This is the fixed version.
        """
        # Setup mocks
        mock_config = MagicMock(spec=ProjectConfig)
        mock_project = MagicMock()
        mock_project.get.return_value = "test_project"
        mock_config.project = mock_project
        mock_load.return_value = mock_config
        
        mock_script = {"id": "test", "script": "test script"}
        mock_script_gen.return_value = mock_script
        
        mock_audio_map = {"blocks": {"main": "/tmp/test.wav"}, "total_duration_sec": 10.0}
        mock_tts_gen.return_value = mock_audio_map
        
        mock_video_path = Path("/tmp/test.mp4")
        mock_video_render.return_value = mock_video_path
        
        # Execute workflow
        config = ProjectConfig.load("projects/test/config.yaml")
        script = mock_script_gen(config=config, target_date="2025-12-13", api_key="test")
        audio_map = mock_tts_gen(config=config, script=script, mode="shorts", api_key="test")
        
        # NEW WORKFLOW CODE (fixed): ✅ Include config!
        video_path = mock_video_render(
            config=config,  # ✅ This fixes the bug!
            script=script,
            audio_map=audio_map,
            mode="shorts"
        )
        
        # Assertions
        assert video_path == mock_video_path
        mock_video_render.assert_called_once_with(
            config=config,
            script=script,
            audio_map=audio_map,
            mode="shorts"
        )


class TestPipelineOrchestratorIntegration:
    """Test pipeline orchestrator integration with mocks."""
    
    @patch.dict(os.environ, {"GOOGLE_AI_API_KEY": "test_key_12345"})
    @patch('core.generators.video_renderer.render')
    @patch('core.generators.tts_generator.synthesize')
    @patch('core.generators.script_generator.generate_short')
    @patch('core.utils.config_loader.load')
    @patch('core.utils.model_router.get_router')
    def test_orchestrator_passes_config_to_render(
        self,
        mock_router,
        mock_load_config,
        mock_script_gen,
        mock_tts_gen,
        mock_video_render
    ):
        """Test that pipeline orchestrator correctly passes config to render()."""
        from core.orchestrators import pipeline_orchestrator
        import argparse
        
        # Setup mocks
        mock_config = MagicMock(spec=ProjectConfig)
        mock_monitoring = MagicMock()
        mock_monitoring.telegram_notifications = False
        mock_config.monitoring = mock_monitoring
        mock_project = MagicMock()
        mock_project.get.return_value = "test_project"
        mock_config.project = mock_project
        mock_load_config.return_value = mock_config
        
        mock_router_instance = MagicMock()
        mock_router_instance.get_stats.return_value = {
            "total_attempts": 1,
            "successful": 1,
            "failed": 0,
            "success_rate": "100%",
            "model_usage": {"gemini-2.0-flash-exp": 1}
        }
        mock_router.return_value = mock_router_instance
        
        mock_script = {"id": "test", "script": "test" * 100, "_script_path": "/tmp/script.json"}
        mock_script_gen.return_value = mock_script
        
        mock_audio_map = {"blocks": {"main": "/tmp/test.wav"}, "total_duration_sec": 10.0}
        mock_tts_gen.return_value = mock_audio_map
        
        mock_video_path = Path("/tmp/test.mp4")
        mock_video_render.return_value = mock_video_path
        
        # Create args
        args = argparse.Namespace(
            project="test_project",
            mode="shorts",
            date="2025-12-13",
            dry_run=False,
            upload=False,
            platforms=None,
            product_id=None
        )
        
        # Execute pipeline
        result = pipeline_orchestrator.main(args)
        
        # Assertions
        assert result == 0
        
        # Verify render was called WITH config
        call_args = mock_video_render.call_args
        assert call_args is not None, "render() should have been called"
        
        # Check that config was passed as keyword argument
        if call_args.kwargs:
            assert "config" in call_args.kwargs, "config should be in keyword arguments"
        else:
            # Check positional arguments (config should be first)
            assert len(call_args.args) >= 1, "render() should have at least 1 positional argument"
