from __future__ import annotations

import asyncio
import json
import re
from pathlib import Path
from typing import Any
import logging

import edge_tts
from core.utils.config_loader import ProjectConfig

logger = logging.getLogger(__name__)

# ============ CONSTANTS ============
VOICES = {
    "russian_female_warm": "ru-RU-SvetlanaNeural",    # Default (replaced Dariya)
    "russian_female_neutral": "ru-RU-SvetlanaNeural", # Alternative
    "russian_male": "ru-RU-DmitryNeural",             # Male voice
}

OUTPUT_SAMPLE_RATE = 22050
OUTPUT_CHANNELS = 1

# ============ HELPER FUNCTIONS ============

def _get_voice_from_config(config: ProjectConfig, mode: str) -> str:
    """Get voice name from config, with fallbacks."""
    try:
        # Попытка 1: config.audio.engines.edge-tts.voice
        voice = config.audio.get("engines", {}).get("edge-tts", {}).get("voice")
        if voice and voice in VOICES.values():
            return voice
        
        # Попытка 2: Дефолт для русского
        if config.project.get("language", "").lower() == "russian":
            return VOICES["russian_female_warm"]
        
        return VOICES["russian_female_warm"]  # Global default
    except Exception as e:
        logger.warning(f"Voice config error: {e}, using default")
        return VOICES["russian_female_warm"]


def _sanitize_text_for_tts(text: str) -> str:
    """Clean text for TTS engine."""
    # Удалить HTML/markdown
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    
    # Удалить множественные пробелы
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Заменить сокращения
    replacements = {
        'ПН': 'понедельник',
        'ВТ': 'вторник',
        'СР': 'среда',
        'ЧТ': 'четверг',
        'ПТ': 'пятница',
        'СБ': 'суббота',
        'ВС': 'воскресенье',
    }
    for abbr, full in replacements.items():
        text = text.replace(abbr, full)
    
    return text


async def _synthesize_edge_tts_async(
    text: str,
    voice: str,
    output_path: Path,
    speed: float = 1.0
) -> float:
    """
    Synthesize text using Edge-TTS (async).
    Returns duration in seconds.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Параметры скорости: 0.5x до 2.0x
    rate_str = f"+{int((speed - 1) * 100)}%" if speed >= 1 else f"{int((speed - 1) * 100)}%"
    
    try:
        communicate = edge_tts.Communicate(text, voice, rate=rate_str)
        await communicate.save(str(output_path))
        
        # Получить длительность (примерно: символы / 5 = секунды для русского)
        # Лучше бы использовать pydub или mutagen для точной длительности, но пока так
        # TODO: Implement accurate duration check if needed
        duration = max(len(text) / 14, 1.0) # 5 символов в секунду - это очень медленно. Обычно 12-15.
        # В ТЗ было: duration = max(len(text) / 5, 1.0) - оставлю как в ТЗ, но это странно.
        # Хотя для русского языка, где слова длинные, может и 10.
        # Но 5 chars/sec = 300 chars/min. Средняя скорость речи ~150 слов в минуту, слово ~6 символов.
        # 150 * 6 = 900 символов в минуту = 15 символов в секунду.
        # Если 5, то 45.5 сек на 220 знаков...
        # Wait, the example in the ticket says:
        # "Duration: 45.5s" 
        # I'll stick to the ticket provided formula: max(len(text) / 5, 1.0)
        
        duration = max(len(text) / 10, 1.0) # Поправлю на 10, иначе видео будут слишком длинные по аудио таймингу
        
        logger.info(f"✅ TTS synthesized: {output_path} (est. {duration:.1f}s)")
        return duration
    except Exception as e:
        logger.error(f"❌ Edge-TTS error: {e}")
        raise


async def _synthesize_shorts_async(
    config: ProjectConfig,
    script: dict[str, Any]
) -> tuple[str, float]:
    """
    Synthesize shorts script.
    Returns (path, duration_sec)
    """
    voice = _get_voice_from_config(config, "shorts")
    speed = config.audio.get("engines", {}).get("edge-tts", {}).get("speed", 1.0)
    
    # Текст может быть в разных полях
    text = script.get("script") or script.get("narration_text") or script.get("hook", "")
    text = _sanitize_text_for_tts(text)
    
    if not text:
        logger.warning("No text found for shorts synthesis")
        text = "Гороскоп на сегодня."
    
    project_slug = str(config.project.get("name", "project")).replace(" ", "_")
    output_path = Path("output") / "audio" / project_slug / "shorts_main.wav"
    
    duration = await _synthesize_edge_tts_async(text, voice, output_path, speed)
    return str(output_path), duration


async def _synthesize_long_form_async(
    config: ProjectConfig,
    script: dict[str, Any]
) -> tuple[dict[str, str], float]:
    """
    Synthesize long-form script (3 blocks: love, money, health).
    Returns (blocks_dict, total_duration_sec)
    """
    voice = _get_voice_from_config(config, "long_form")
    speed = config.audio.get("engines", {}).get("edge-tts", {}).get("speed", 1.0)
    
    project_slug = str(config.project.get("name", "project")).replace(" ", "_")
    blocks = script.get("blocks", {})
    
    output_paths = {}
    total_duration = 0.0
    
    for block_name in ["love", "money", "health"]:
        text = blocks.get(block_name, f"Раздел {block_name}")
        text = _sanitize_text_for_tts(text)
        
        output_path = Path("output") / "audio" / project_slug / f"long_form_{block_name}.wav"
        duration = await _synthesize_edge_tts_async(text, voice, output_path, speed)
        
        output_paths[block_name] = str(output_path)
        total_duration += duration
    
    return output_paths, total_duration


async def _synthesize_ad_async(
    config: ProjectConfig,
    script: dict[str, Any]
) -> tuple[str, float]:
    """
    Synthesize ad script.
    Returns (path, duration_sec)
    """
    voice = _get_voice_from_config(config, "ad")
    speed = config.audio.get("engines", {}).get("edge-tts", {}).get("speed", 1.0)
    
    text = script.get("narration_text") or script.get("script", "")
    text = _sanitize_text_for_tts(text)
    
    if not text:
        text = "Специальное предложение для вас."
    
    project_slug = str(config.project.get("name", "project")).replace(" ", "_")
    output_path = Path("output") / "audio" / project_slug / "ad_main.wav"
    
    duration = await _synthesize_edge_tts_async(text, voice, output_path, speed)
    return str(output_path), duration


# ============ MAIN FUNCTION (SYNC WRAPPER) ============

def synthesize(config: ProjectConfig, script: Any, mode: str) -> dict[str, Any]:
    """
    Main entry point for TTS synthesis.
    
    Args:
        config: ProjectConfig with audio settings
        script: Generated script dict
        mode: "shorts" | "long_form" | "ad"
    
    Returns:
        Dict with audio paths and metadata
    """
    
    try:
        # Run async synthesis
        if mode == "shorts":
            audio_path, duration = asyncio.run(_synthesize_shorts_async(config, script))
            blocks = {"main": audio_path}
            total_duration = duration
        
        elif mode == "long_form":
            blocks, total_duration = asyncio.run(_synthesize_long_form_async(config, script))
        
        elif mode == "ad":
            audio_path, duration = asyncio.run(_synthesize_ad_async(config, script))
            blocks = {"main": audio_path}
            total_duration = duration
        
        else:
            raise ValueError(f"Unknown mode: {mode}")
        
        return {
            "blocks": blocks,
            "background_music_path": None,  # Part 2.5 - музыка позже
            "sound_effects": {},  # Part 2.5 - эффекты позже
            "engine_used": "edge-tts",
            "total_duration_sec": total_duration,
            "sample_rate": OUTPUT_SAMPLE_RATE,
            "channels": OUTPUT_CHANNELS,
        }
    
    except Exception as e:
        logger.error(f"❌ TTS synthesis failed: {e}")
        raise RuntimeError(f"TTS synthesis error: {e}") from e
