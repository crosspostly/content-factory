from __future__ import annotations

from core.utils.config_loader import ProjectConfig


def _normalize_engine_key(engine: str) -> str:
    return engine.lower().replace("-", "_")


def choose_tts_engine(config: ProjectConfig, video_type: str) -> tuple[str, str]:
    """Choose (engine_name, voice_name) for a given video type.

    Engine names in config may be written with hyphens while `audio.engines`
    keys may be snake_case. We support both.
    
    Note: Gemini TTS doesn't use voice selection like Edge-TTS.
    Voice selection happens in API call, not config.
    """

    audio = config.audio
    preferred_engine = audio.primary_engine
    fallback_engine = audio.fallback_engine or audio.primary_engine

    for engine_name in [preferred_engine, fallback_engine]:
        engine_key = _normalize_engine_key(engine_name)
        engine_cfg = audio.engines.get(engine_key)
        if engine_cfg and engine_cfg.enabled:
            # Gemini TTS uses API-level voice selection, not config
            return engine_name, "default"

    return fallback_engine, "default"


def map_content_to_voice(content_type: str) -> str:
    # Note: This mapping is for Edge-TTS compatibility
    # Gemini TTS uses different voice system
    return "default"
