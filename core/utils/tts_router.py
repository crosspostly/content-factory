from __future__ import annotations

from core.utils.config_loader import ProjectConfig


def _normalize_engine_key(engine: str) -> str:
    return engine.lower().replace("-", "_")


def choose_tts_engine(config: ProjectConfig, video_type: str) -> tuple[str, str]:
    """Choose (engine_name, voice_name) for a given video type.

    Engine names in config may be written with hyphens (edge-tts) while `audio.engines`
    keys may be snake_case (edge_tts). We support both.
    """

    audio = config.audio
    preferred_engine = audio.voice_selection.get(video_type) or audio.primary_engine
    fallback_engine = audio.fallback_engine or audio.primary_engine

    for engine_name in [preferred_engine, fallback_engine]:
        engine_key = _normalize_engine_key(engine_name)
        engine_cfg = audio.engines.get(engine_key)
        if engine_cfg and engine_cfg.enabled:
            # voice selection is handled separately; default is female_neutral
            return engine_name, "female_neutral"

    return fallback_engine, "female_neutral"


def map_content_to_voice(content_type: str) -> str:
    voice_map = {
        "love": "female_warm",
        "money": "female_neutral",
        "health": "female_neutral",
        "warning": "female_mysterious",
        "lucky": "female_warm",
    }
    return voice_map.get(content_type, "female_neutral")
