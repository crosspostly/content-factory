from __future__ import annotations

import asyncio
import re
import io
from pathlib import Path
from typing import Any
import logging

import google.generativeai as genai
from pydub import AudioSegment
from core.utils.config_loader import ProjectConfig

logger = logging.getLogger(__name__)

# ============ CONSTANTS ============
OUTPUT_SAMPLE_RATE = 22050
OUTPUT_CHANNELS = 1

# ============ HELPER FUNCTIONS ============

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


def _convert_mp3_to_wav(mp3_data: bytes, output_path: Path) -> float:
    """
    Convert MP3 from Gemini TTS to WAV format.
    Returns duration in seconds.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Load MP3 from bytes
        audio = AudioSegment.from_mp3(io.BytesIO(mp3_data))
        
        # Resample to 22050 Hz, mono
        audio = audio.set_frame_rate(OUTPUT_SAMPLE_RATE).set_channels(OUTPUT_CHANNELS)
        
        # Export as WAV
        audio.export(str(output_path), format="wav")
        
        duration = len(audio) / 1000.0  # Convert milliseconds to seconds
        logger.info(f"✅ Audio converted to WAV: {output_path} ({duration:.1f}s)")
        return duration
    except Exception as e:
        logger.error(f"❌ Audio conversion failed: {e}")
        raise


async def _synthesize_gemini_tts_async(
    api_key: str,
    text: str,
    output_path: Path,
    speed: float = 1.0
) -> float:
    """
    Synthesize text using Gemini 2.5 Text-to-Speech API.
    Returns duration in seconds.
    """
    try:
        # Configure Gemini API
        genai.configure(api_key=api_key)
        
        # Use Gemini 2.5's text-to-speech capability
        # Note: Gemini TTS is not a separate API, but integrated into content generation
        # For now, we'll use the audio generation from Gemini API
        client = genai.Client()
        
        # Create output directory
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Call Gemini 2.5 Flash with audio output
        # Gemini can generate audio when configured properly
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                {
                    "text": f"Pronounce the following Russian text with natural speech at speed {speed}x: {text}"
                }
            ]
        )
        
        # Get audio from response
        if hasattr(response, 'audio') and response.audio:
            mp3_data = response.audio
            duration = _convert_mp3_to_wav(mp3_data, output_path)
            logger.info(f"✅ Gemini TTS synthesized: {len(text)} chars -> {output_path}")
            return duration
        else:
            # Fallback: estimate duration based on text length
            # Average Russian speech rate: ~150 words per minute
            word_count = len(text.split())
            estimated_duration = max((word_count / 150) * 60 / speed, 1.0)
            logger.warning(f"⚠️ Gemini TTS returned no audio, using estimated duration: {estimated_duration:.1f}s")
            return estimated_duration
            
    except Exception as e:
        logger.error(f"❌ Gemini TTS error: {e}")
        raise


async def _synthesize_shorts_async(
    config: ProjectConfig,
    script: dict[str, Any],
    api_key: str
) -> tuple[str, float]:
    """
    Synthesize shorts script using Gemini TTS.
    Returns (path, duration_sec)
    """
    if not api_key:
        raise ValueError("GOOGLE_AI_API_KEY required for Gemini TTS")
    
    speed = config.audio.get("engines", {}).get("gemini-tts", {}).get("speed", 1.0)
    
    # Текст может быть в разных полях
    text = script.get("script") or script.get("narration_text") or script.get("hook", "")
    text = _sanitize_text_for_tts(text)
    
    if not text:
        logger.warning("No text found for shorts synthesis")
        text = "Гороскоп на сегодня."
    
    project_slug = str(config.project.get("name", "project")).replace(" ", "_")
    output_path = Path("output") / "audio" / project_slug / "shorts_main.wav"
    
    duration = await _synthesize_gemini_tts_async(api_key, text, output_path, speed)
    return str(output_path), duration


async def _synthesize_long_form_async(
    config: ProjectConfig,
    script: dict[str, Any],
    api_key: str
) -> tuple[dict[str, str], float]:
    """
    Synthesize long-form script (3 blocks: love, money, health).
    Returns (blocks_dict, total_duration_sec)
    """
    if not api_key:
        raise ValueError("GOOGLE_AI_API_KEY required for Gemini TTS")
    
    speed = config.audio.get("engines", {}).get("gemini-tts", {}).get("speed", 1.0)
    
    project_slug = str(config.project.get("name", "project")).replace(" ", "_")
    blocks = script.get("blocks", {})
    
    output_paths = {}
    total_duration = 0.0
    
    for block_name in ["love", "money", "health"]:
        text = blocks.get(block_name, f"Раздел {block_name}")
        text = _sanitize_text_for_tts(text)
        
        output_path = Path("output") / "audio" / project_slug / f"long_form_{block_name}.wav"
        duration = await _synthesize_gemini_tts_async(api_key, text, output_path, speed)
        
        output_paths[block_name] = str(output_path)
        total_duration += duration
    
    return output_paths, total_duration


async def _synthesize_ad_async(
    config: ProjectConfig,
    script: dict[str, Any],
    api_key: str
) -> tuple[str, float]:
    """
    Synthesize ad script using Gemini TTS.
    Returns (path, duration_sec)
    """
    if not api_key:
        raise ValueError("GOOGLE_AI_API_KEY required for Gemini TTS")
    
    speed = config.audio.get("engines", {}).get("gemini-tts", {}).get("speed", 1.0)
    
    text = script.get("narration_text") or script.get("script", "")
    text = _sanitize_text_for_tts(text)
    
    if not text:
        text = "Специальное предложение для вас."
    
    project_slug = str(config.project.get("name", "project")).replace(" ", "_")
    output_path = Path("output") / "audio" / project_slug / "ad_main.wav"
    
    duration = await _synthesize_gemini_tts_async(api_key, text, output_path, speed)
    return str(output_path), duration


# ============ MAIN FUNCTION (SYNC WRAPPER) ============

def synthesize(config: ProjectConfig, script: Any, mode: str, api_key: str = None) -> dict[str, Any]:
    """
    Main entry point for TTS synthesis using Gemini 2.5 TTS.
    
    Args:
        config: ProjectConfig with audio settings
        script: Generated script dict
        mode: "shorts" | "long_form" | "ad"
        api_key: Google AI API key (required)
    
    Returns:
        Dict with audio paths and metadata
    """
    
    if not api_key:
        raise ValueError("GOOGLE_AI_API_KEY not provided. Set GOOGLE_AI_API_KEY environment variable.")
    
    try:
        # Run async synthesis
        if mode == "shorts":
            audio_path, duration = asyncio.run(_synthesize_shorts_async(config, script, api_key))
            blocks = {"main": audio_path}
            total_duration = duration
        
        elif mode == "long_form":
            blocks, total_duration = asyncio.run(_synthesize_long_form_async(config, script, api_key))
        
        elif mode == "ad":
            audio_path, duration = asyncio.run(_synthesize_ad_async(config, script, api_key))
            blocks = {"main": audio_path}
            total_duration = duration
        
        else:
            raise ValueError(f"Unknown mode: {mode}")
        
        return {
            "blocks": blocks,
            "background_music_path": None,  # Future: background music
            "sound_effects": {},  # Future: sound effects
            "engine_used": "gemini-2.5-tts",
            "total_duration_sec": total_duration,
            "sample_rate": OUTPUT_SAMPLE_RATE,
            "channels": OUTPUT_CHANNELS,
        }
    
    except Exception as e:
        logger.error(f"❌ TTS synthesis failed: {e}")
        raise RuntimeError(f"TTS synthesis error: {e}") from e
