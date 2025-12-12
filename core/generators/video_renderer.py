"""Video Renderer — монтаж видео из компонентов"""
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from core.utils.config_loader import ProjectConfig
from core.utils.stock_client import StockClient
from core.utils.logging_utils import log_success, log_error


def render(
    config: ProjectConfig,
    script: Dict[str, Any],
    audio_map: Dict[str, Any],
    video_type: str
) -> str:
    """
    Собирает финальный видеофайл.
    
    На входе:
      - config: ProjectConfig
      - script: JSON-сценарий
      - audio_map: пути к озвучке (из tts_generator)
      - video_type: "shorts" | "long_form" | "ad"
    
    На выходе: путь к готовому видеофайлу (MP4)
    
    Процесс:
    1) Получить фоновое видео/картинку
    2) Определить размер (1080x1920 для shorts, 1920x1080 для long-form)
    3) Подготовить текстовые слои (hook, content, CTA)
    4) Сборка в MoviePy:
       - Фон + текст
       - Озвучка + фоновая музыка
       - Звуковые эффекты
       - Переходы
    5) Экспорт в MP4
    6) Сохранение в output/videos/
    """
    log_success(f"Starting video render for {video_type}")
    
    try:
        output_dir = Path(f"output/videos/{config.project['name']}/{datetime.now().date()}")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if video_type == "shorts":
            return _render_short(config, script, audio_map, output_dir)
        elif video_type == "long_form":
            return _render_long_form(config, script, audio_map, output_dir)
        elif video_type == "ad":
            return _render_ad(config, script, audio_map, output_dir)
        else:
            raise ValueError(f"Unknown video_type: {video_type}")
    
    except Exception as e:
        log_error(f"Video render failed", e)
        raise


def _render_short(
    config: ProjectConfig,
    script: Dict[str, Any],
    audio_map: Dict[str, Any],
    output_dir: Path
) -> str:
    """
    Монтирует YouTube Shorts (15-60 сек, 1080x1920 портрет).
    
    Структура:
    1) Фоновое видео или картинка (весь ролик)
    2) Hook текст (первые 2-3 сек, крупный, золотой)
    3) Основной контент (15-30 сек)
    4) CTA текст (последние 3-5 сек)
    5) Озвучка + фоновая музыка
    6) Звуковые эффекты на переходах
    
    Возвращает: путь к готовому MP4
    """
    try:
        from moviepy.editor import (
            VideoFileClip, ImageClip, TextClip, concatenate_videoclips,
            CompositeVideoClip, ColorClip, CompositeAudioFileClip, AudioFileClip
        )
        
        log_success("Starting shorts render")
        
        # Получаем фон
        stock_client = StockClient(config)
        keywords = script.get('visual_hints', 'astrology mystical').split()
        background_videos = stock_client.get_video_background('shorts', keywords, duration_sec=60)
        
        duration_target = script.get('duration_sec_target', 30)
        
        if background_videos:
            try:
                bg = VideoFileClip(background_videos[0])
                bg = bg.resize((1080, 1920))
                bg = bg.speedx(1080 * 1920 / (bg.size[0] * bg.size[1]))  # Fit
                if bg.duration < duration_target:
                    # Повторяем фон
                    bg = concatenate_videoclips([bg] * (int(duration_target / bg.duration) + 1))
                bg = bg.subclipped(0, duration_target)
            except:
                bg = ColorClip(size=(1080, 1920), color=(20, 10, 40))
                bg = bg.set_duration(duration_target)
        else:
            # Fallback: темный фон
            bg = ColorClip(size=(1080, 1920), color=(20, 10, 40))
            bg = bg.set_duration(duration_target)
        
        # Текстовые слои
        hook = script.get('hook', '')
        hook_clip = TextClip(
            hook,
            fontsize=80,
            color='gold',
            font='Georgia',
            size=(1000, 200),
            method='caption'
        ).set_position(('center', 'top')).set_duration(3)
        
        main_text = script.get('script', '')
        main_clip = TextClip(
            main_text,
            fontsize=48,
            color='white',
            font='Georgia',
            size=(1000, 800),
            method='caption'
        ).set_position(('center', 'center')).set_duration(duration_target - 5).set_start(3)
        
        cta = script.get('engagement_cta', '')
        cta_clip = TextClip(
            cta,
            fontsize=40,
            color='gold',
            font='Georgia',
            size=(1000, 200),
            method='caption'
        ).set_position(('center', 'bottom')).set_duration(3).set_start(duration_target - 3)
        
        # Собираем видео
        final = CompositeVideoClip([bg, hook_clip, main_clip, cta_clip])
        
        # Добавляем аудио
        try:
            main_audio = AudioFileClip(audio_map['blocks']['main'])
            bg_music = AudioFileClip(audio_map['background_music_path']).volumex(0.3)
            audio = CompositeAudioFileClip([main_audio, bg_music])
            final = final.set_audio(audio)
        except:
            log_error("Audio composition failed, continuing without audio")
        
        # Экспортируем
        output_path = output_dir / f"short_{uuid.uuid4().hex[:8]}.mp4"
        log_success(f"Exporting to {output_path}")
        final.write_videofile(
            str(output_path),
            fps=30,
            codec='libx264',
            audio_codec='aac',
            verbose=False,
            logger=None
        )
        
        log_success(f"Shorts render complete: {output_path}")
        return str(output_path)
    
    except Exception as e:
        log_error(f"Shorts render failed", e)
        raise


def _render_long_form(
    config: ProjectConfig,
    script: Dict[str, Any],
    audio_map: Dict[str, Any],
    output_dir: Path
) -> str:
    """
    Монтирует длинное видео (20-45 мин, 1920x1080).
    
    TODO: Полная реализация с блоками, переходами и эффектами.
    """
    log_success("Starting long-form render (PLACEHOLDER)")
    
    # TODO: реализовать
    output_path = output_dir / f"long_form_{uuid.uuid4().hex[:8]}.mp4"
    output_path.touch()  # Создаем пустой файл для теста
    
    return str(output_path)


def _render_ad(
    config: ProjectConfig,
    script: Dict[str, Any],
    audio_map: Dict[str, Any],
    output_dir: Path
) -> str:
    """
    Монтирует рекламный ролик.
    
    TODO: Реализация.
    """
    log_success("Starting ad render (PLACEHOLDER)")
    
    # TODO: реализовать
    output_path = output_dir / f"ad_{uuid.uuid4().hex[:8]}.mp4"
    output_path.touch()
    
    return str(output_path)
