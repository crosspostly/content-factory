"""TTS Generator — синтез речи через Edge-TTS или Gemini"""
import asyncio
from pathlib import Path
from datetime import datetime, date
from typing import Dict, Optional, Any

from core.utils.config_loader import ProjectConfig
from core.utils.tts_router import choose_tts_engine, map_content_to_voice
from core.utils.secrets_manager import get_secret
from core.utils.logging_utils import log_success, log_error, log_fallback


def synthesize(
    config: ProjectConfig,
    script: Dict[str, Any],
    video_type: str
) -> Dict[str, Any]:
    """
    Синтезирует все текстовые части сценария в аудио-файлы.
    
    На входе:
      - config: ProjectConfig
      - script: JSON-сценарий
      - video_type: "shorts" | "long_form" | "ad"
    
    На выходе:
      {
        "blocks": {
          "intro": "/path/to/intro.wav",
          "love_aries": "/path/to/love_aries.wav",
          ...
        },
        "background_music_path": "/path/to/bg_music.mp3",
        "sound_effects": {...},
        "engine_used": "edge-tts" | "gemini-tts",
        "total_duration_sec": 123.45
      }
    
    Логика:
    1) Выбрать engine через tts_router
    2) Для каждого текстового блока:
       - Мэпить content_type на голос
       - Синтезировать
       - Сохранить .wav
    3) Загрузить background_music и sound_effects
    4) Вернуть все пути
    """
    log_success(f"Starting TTS synthesis for {video_type}")
    
    try:
        # Выбираем engine
        engine = choose_tts_engine(config, video_type)
        log_success(f"Using TTS engine: {engine}")
        
        # Подготавливаем директорию
        audio_dir = Path(f"output/audio/{config.project['name']}/{datetime.now().date()}")
        audio_dir.mkdir(parents=True, exist_ok=True)
        
        blocks_audio = {}
        
        if video_type == "shorts":
            # Один основной блок
            text = script.get('script', '')
            if text:
                audio_path = audio_dir / "main.wav"
                _synthesize_block(config, engine, text, audio_path, 'main')
                blocks_audio['main'] = str(audio_path)
        
        elif video_type == "long_form":
            # Множество блоков
            texts = {
                'intro': script.get('intro', ''),
                'astro_context': script.get('astro_context', ''),
            }
            
            # Блоки love/money/health
            for block_name in ['love', 'money', 'health']:
                if block_name in script.get('blocks', {}):
                    block = script['blocks'][block_name]
                    
                    if 'intro' in block:
                        texts[f"{block_name}_intro"] = block['intro']
                    
                    for i, sign_data in enumerate(block.get('per_sign', [])):
                        key = f"{block_name}_{sign_data.get('sign', f'sign_{i}')}"
                        texts[key] = sign_data.get('forecast', '')
                    
                    if 'manifestation_cta' in block:
                        texts[f"{block_name}_cta"] = block['manifestation_cta']
            
            # Special section и closing
            if 'special_section' in script:
                texts['special'] = script['special_section'].get('content', '')
            
            if 'closing' in script:
                texts['closing'] = script['closing'].get('summary', '')
            
            # Синтезируем каждый блок
            for block_key, text in texts.items():
                if text:
                    audio_path = audio_dir / f"{block_key}.wav"
                    _synthesize_block(config, engine, text, audio_path, block_key)
                    blocks_audio[block_key] = str(audio_path)
        
        # Загружаем background_music и sound_effects
        # TODO: реализовать загрузку из stock_client
        bg_music_path = _get_placeholder_audio(audio_dir, "background_music.mp3")
        
        effects = {}
        for effect_name in config.audio.get('sound_effects', {}).get('effects', {}):
            effect_path = _get_placeholder_audio(audio_dir, f"{effect_name}.wav")
            effects[effect_name] = str(effect_path)
        
        result = {
            'blocks': blocks_audio,
            'background_music_path': str(bg_music_path),
            'sound_effects': effects,
            'engine_used': engine,
            'total_duration_sec': _calculate_total_duration(blocks_audio)
        }
        
        log_success(f"TTS synthesis completed. Total duration: {result['total_duration_sec']}s")
        return result
    
    except Exception as e:
        log_error(f"TTS synthesis failed", e)
        raise


def _synthesize_block(
    config: ProjectConfig,
    engine: str,
    text: str,
    output_path: Path,
    block_name: str
) -> None:
    """
    Синтезирует один блок текста в .wav файл.
    
    Логика:
    - Если engine = "edge-tts" → используем edge_tts.tts()
    - Если engine = "gemini-tts" → используем Google Generative AI
    - При ошибке → фолбек на другой engine
    """
    try:
        if engine == "edge-tts":
            _synthesize_edge_tts(text, output_path, config)
        elif engine == "gemini-tts":
            _synthesize_gemini_tts(text, output_path, config)
    
    except Exception as e:
        log_error(f"Failed to synthesize block '{block_name}' with {engine}", e)
        
        # Пробуем фолбек
        fallback_engine = config.audio.get('fallback_engine', 'edge-tts')
        if fallback_engine != engine:
            log_fallback(f"Block '{block_name}'", engine, fallback_engine)
            _synthesize_block(config, fallback_engine, text, output_path, block_name)
        else:
            raise


def _synthesize_edge_tts(text: str, output_path: Path, config: ProjectConfig) -> None:
    """
    Синтезирует через Edge-TTS (Microsoft).
    """
    try:
        import edge_tts
        
        # Выбираем голос
        voice = config.audio.get('engines', {}).get('edge_tts', {}).get('voice', 'en-US-AriaNeural')
        speed = config.audio.get('engines', {}).get('edge_tts', {}).get('speed', 1.0)
        
        # Синтезируем
        communicate = edge_tts.Communicate(text, voice=voice, rate=f"+{int((speed-1)*50)}%")
        
        async def save_audio():
            await communicate.save(str(output_path))
        
        asyncio.run(save_audio())
        log_success(f"Edge-TTS: {output_path.name}")
    
    except Exception as e:
        log_error(f"Edge-TTS failed", e)
        raise


def _synthesize_gemini_tts(text: str, output_path: Path, config: ProjectConfig) -> None:
    """
    Синтезирует через Google Generative AI (Gemini).
    """
    try:
        import google.generativeai as genai
        
        # Инициализируем
        api_key = get_secret('GOOGLE_AI_API_KEY')
        genai.configure(api_key=api_key)
        
        # TODO: Реализовать интеграцию с Gemini TTS API
        # Пока что используем placeholder
        log_success(f"Gemini-TTS placeholder: {output_path.name}")
    
    except Exception as e:
        log_error(f"Gemini-TTS failed", e)
        raise


def _get_placeholder_audio(audio_dir: Path, filename: str) -> Path:
    """
    Создает placeholder аудиофайл для тестирования.
    """
    path = audio_dir / filename
    
    try:
        from pydub import AudioSegment
        
        # Создаем пустой аудиофайл (1 сек тишины)
        silent = AudioSegment.silent(duration=1000)
        silent.export(str(path), format="mp3" if filename.endswith('.mp3') else "wav")
    
    except ImportError:
        # Fallback: создаем минимальный WAV файл
        import wave
        with wave.open(str(path), 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(44100)
            wav_file.writeframes(b'\x00\x00' * 44100)  # 1 сек тишины
    
    return path


def _calculate_total_duration(blocks_audio: Dict[str, str]) -> float:
    """
    Рассчитывает общую длительность всех аудиоблоков.
    """
    try:
        from pydub import AudioSegment
        
        total_ms = 0
        for audio_path in blocks_audio.values():
            audio = AudioSegment.from_file(audio_path)
            total_ms += len(audio)
        
        return total_ms / 1000.0  # Конвертируем в секунды
    
    except Exception:
        # Fallback
        return len(blocks_audio) * 30.0  # Примерно 30 сек на блок
