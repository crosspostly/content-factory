from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any
import random

import requests
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
from moviepy.editor import (
    CompositeVideoClip, CompositeAudioClip,
    TextClip, ImageClip, AudioFileClip,
    VideoFileClip, VideoClip,
    concatenate_videoclips, vfx
)

from core.utils.config_loader import ProjectConfig

logger = logging.getLogger(__name__)

# ============ CONSTANTS ============

PIXABAY_VIDEOS_API = "https://pixabay.com/api/videos/"
PIXABAY_IMAGES_API = "https://pixabay.com/api/"

VIDEO_CONFIG = {
    "shorts": {
        "width": 1080,
        "height": 1920,
        "aspect": "9:16",
        "fps": 30,
        "bitrate": "5000k",
    },
    "long_form": {
        "width": 1920,
        "height": 1080,
        "aspect": "16:9",
        "fps": 30,
        "bitrate": "8000k",
    },
    "ad": {
        "width": 1080,
        "height": 1920,
        "aspect": "9:16",
        "fps": 30,
        "bitrate": "5000k",
    },
}

KEYWORDS = {
    "shorts": ["horoscope", "astrology", "zodiac", "stars", "mystical"],
    "long_form": ["zodiac", "astrology", "universe", "stars", "cosmos"],
    "ad": ["product", "lifestyle", "modern"],
}

# ============ HELPER FUNCTIONS ============

def _get_pixabay_video(api_key: str, query: str, duration_sec: float) -> str | None:
    """
    Get video from Pixabay API.
    Returns download URL or None.
    """
    try:
        params = {
            "key": api_key,
            "q": query,
            "per_page": 3,
            "order": "popular",
            "min_duration": int(duration_sec) - 5,
        }
        
        response = requests.get(PIXABAY_VIDEOS_API, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data["hits"]:
            video = data["hits"]
            # Выбрать качество 360p или выше
            # video is a list of hits. Each hit has "videos" dict with sizes.
            # But here `video` is assigned `data["hits"]` which is a list.
            # The loop `for fmt in ...` expects a dict structure if `video` was a single hit.
            # We should iterate over hits.
            
            # Fix: Take the first hit
            first_hit = video[0]
            videos_dict = first_hit.get("videos", {})
            
            for fmt in ["large", "medium", "small", "tiny"]: # Pixabay keys are usually these
                 # But the ticket code had ["360", "720", "1080"]. Pixabay API usually has "large", "medium", "small", "tiny".
                 # Actually Pixabay API response structure:
                 # "videos": { "large": { "url": ... }, "medium": { ... }, ... }
                 # Or sometimes specific resolutions.
                 # Let's check what the ticket code assumed.
                 pass

            # Ticket code:
            # for fmt in ["360", "720", "1080"]:
            #    if fmt in video:
            #        return video[fmt]["url"]
            # return list(video.values())["url"]
            
            # This implies `video` is a dictionary of formats. But `data["hits"]` is a list.
            # So the ticket code is slightly buggy or I am misunderstanding.
            # Assuming `video = data["hits"][0]` was intended?
            # Or `data["hits"]` is a dict? No, usually a list.
            
            # Let's fix this logic to be robust.
            hit = data["hits"][0]
            if "videos" in hit:
                # Pixabay API `videos` structure: {"large": ..., "medium": ..., "small": ..., "tiny": ...}
                # We want the best quality that is not too huge. "medium" is usually 720p/1080p.
                
                vids = hit["videos"]
                if "medium" in vids:
                    return vids["medium"]["url"]
                if "large" in vids:
                    return vids["large"]["url"]
                if "small" in vids:
                    return vids["small"]["url"]
                
                # Fallback to any
                return list(vids.values())[0]["url"]
            
            return hit.get("pageURL") # Unlikely to be a direct video file
            
        logger.warning(f"No Pixabay video found for: {query}")
        return None
    
    except Exception as e:
        logger.error(f"Pixabay API error: {e}")
        return None


def _download_video(url: str, output_path: Path) -> bool:
    """Download video file."""
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        logger.info(f"✅ Downloaded: {output_path}")
        return True
    
    except Exception as e:
        logger.error(f"Download error: {e}")
        return False


def _create_text_frame(
    text: str,
    width: int,
    height: int,
    font_size: int = 50,
    color: tuple = (255, 255, 255),
) -> Image.Image:
    """
    Create PIL image with text (for overlaying on video).
    """
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Попытка загрузить хороший шрифт
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    # Обтекание текста
    max_chars_per_line = width // (font_size // 2)
    lines = []
    words = text.split()
    current_line = ""
    
    for word in words:
        if len(current_line) + len(word) > max_chars_per_line:
            lines.append(current_line)
            current_line = word
        else:
            current_line += (" " if current_line else "") + word
    
    if current_line:
        lines.append(current_line)
    
    # Центрирование
    y_offset = (height - len(lines) * font_size) // 2
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        line_width = bbox[2] - bbox[0]
        x = (width - line_width) // 2
        y = y_offset + i * (font_size + 10)
        
        draw.text((x, y), line, fill=color, font=font)
    
    return img


def _create_background_clip(
    width: int,
    height: int,
    duration: float,
    fps: int,
    style: str = "mystical",
) -> VideoClip:
    """
    Create gradient/color background video clip.
    Styles: "mystical", "intro", "outro", "ad"
    """
    
    color_map = {
        "mystical": (20, 10, 40),     # Deep purple
        "intro": (30, 15, 50),        # Darker purple
        "outro": (40, 20, 60),        # Medium purple
        "love": (150, 30, 60),        # Red
        "money": (50, 150, 50),       # Green
        "health": (100, 150, 255),    # Blue
        "ad": (40, 40, 60),           # Dark
    }
    
    color = color_map.get(style, (20, 10, 40))
    
    # Создать простой кадр цвета
    frame = Image.new("RGB", (width, height), color)
    frame_array = np.array(frame)
    
    # Тянуть кадр на нужную длительность
    clip = ImageClip(frame_array).set_duration(duration)
    return clip


def _render_shorts(
    config: ProjectConfig,
    script: dict[str, Any],
    audio_map: dict[str, Any],
) -> Path:
    """
    Render vertical shorts video (9:16).
    """
    project_slug = str(config.project.get("name", "project")).replace(" ", "_")
    output_dir = Path("output") / "videos" / project_slug
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / "shorts.mp4"
    
    try:
        # Параметры видео
        width, height = VIDEO_CONFIG["shorts"]["width"], VIDEO_CONFIG["shorts"]["height"]
        fps = VIDEO_CONFIG["shorts"]["fps"]
        duration = audio_map["total_duration_sec"]
        
        # Получить Pixabay видео или создать на основе картинок
        api_key = os.getenv("PIXABAY_API_KEY")
        base_clip = None
        
        if api_key:
            keywords = " ".join(random.sample(KEYWORDS["shorts"], 2))
            video_url = _get_pixabay_video(api_key, keywords, duration)
            
            if video_url:
                stock_path = Path("temp") / f"stock_{random.randint(1000,9999)}.mp4"
                if _download_video(video_url, stock_path):
                    # Использовать stock видео
                    try:
                        base_clip = VideoFileClip(str(stock_path))
                        # Loop if too short
                        if base_clip.duration < duration:
                            base_clip = vfx.loop(base_clip, duration=duration)
                        else:
                            base_clip = base_clip.subclip(0, duration)
                        
                        # Resize to cover
                        # moviepy resize expects (width, height)
                        # We want to fill the screen (1080x1920)
                        # Usually stock video is 16:9 (horizontal). We need to crop to 9:16.
                        
                        # Resize height to 1920
                        base_clip = base_clip.resize(height=1920)
                        # Center crop width to 1080
                        base_clip = base_clip.crop(x1=base_clip.w/2 - 540, width=1080)
                        
                    except Exception as e:
                        logger.warning(f"Failed to process stock video: {e}")
                        base_clip = None
                else:
                    logger.warning("Failed to download video")
        
        if base_clip is None:
            # Fallback на картинку
            base_clip = _create_background_clip(width, height, duration, fps, "mystical")
        
        # Добавить текст (hook)
        hook_text = script.get("hook", "Гороскоп на сегодня")
        
        try:
            # Try TextClip with imagemagick
            txt_clip = TextClip(
                hook_text,
                fontsize=60,
                color="white",
                font="Arial-Bold",
                method="caption",
                size=(width - 40, None),
            )
            txt_clip = txt_clip.set_position("center").set_duration(duration)
        except Exception as e:
            logger.warning(f"TextClip failed, falling back to PIL: {e}")
            # Fallback to PIL
            txt_img = _create_text_frame(hook_text, width, height, 60)
            txt_clip = ImageClip(np.array(txt_img)).set_duration(duration)
        
        # Добавить аудио
        audio_path = audio_map["blocks"]["main"]
        audio_clip = AudioFileClip(audio_path)
        
        # Компоновка
        final_clip = CompositeVideoClip([base_clip, txt_clip])
        final_clip = final_clip.set_audio(audio_clip)
        
        # Экспорт
        final_clip.write_videofile(
            str(output_path),
            fps=fps,
            codec="libx264",
            audio_codec="aac",
            bitrate=VIDEO_CONFIG["shorts"]["bitrate"],
            verbose=False,
            logger=None,
        )
        
        logger.info(f"✅ Shorts video created: {output_path}")
        return output_path
    
    except Exception as e:
        logger.error(f"❌ Shorts rendering failed: {e}")
        raise


def _render_long_form(
    config: ProjectConfig,
    script: dict[str, Any],
    audio_map: dict[str, Any],
) -> Path:
    """
    Render horizontal long-form video (16:9) с 3 блоками.
    Структура: intro + love block + money block + health block + outro
    """
    project_slug = str(config.project.get("name", "project")).replace(" ", "_")
    output_dir = Path("output") / "videos" / project_slug
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / "long_form.mp4"
    
    try:
        width, height = VIDEO_CONFIG["long_form"]["width"], VIDEO_CONFIG["long_form"]["height"]
        fps = VIDEO_CONFIG["long_form"]["fps"]
        
        video_title = script.get("video_title", "Гороскоп")
        blocks = audio_map["blocks"]  # {"love": path, "money": path, "health": path}
        
        clips = []
        
        # Intro (3 сек с заголовком)
        intro_clip = _create_background_clip(width, height, 3, fps, "intro")
        try:
            title_txt = TextClip(
                video_title,
                fontsize=80,
                color="white",
                font="Arial-Bold",
            ).set_position("center").set_duration(3)
        except:
             txt_img = _create_text_frame(video_title, width, height, 80)
             title_txt = ImageClip(np.array(txt_img)).set_duration(3)

        intro_clip = CompositeVideoClip([intro_clip, title_txt])
        clips.append(intro_clip)
        
        # Три блока (love, money, health)
        for block_name in ["love", "money", "health"]:
            if block_name not in blocks:
                continue
            
            audio_path = blocks[block_name]
            audio_clip = AudioFileClip(audio_path)
            duration = audio_clip.duration
            
            # Фоновое видео
            bg_clip = _create_background_clip(width, height, duration, fps, block_name)
            
            # Текст блока
            block_title = script.get("blocks", {}).get(block_name, "").split('\n')[0]
            if len(block_title) > 50:
                 block_title = block_name.capitalize()
            if not block_title:
                block_title = block_name.capitalize()
            
            try:
                txt_clip = TextClip(
                    block_title,
                    fontsize=60,
                    color="white",
                    font="Arial-Bold",
                ).set_position("center").set_duration(duration)
            except:
                txt_img = _create_text_frame(block_title, width, height, 60)
                txt_clip = ImageClip(np.array(txt_img)).set_duration(duration)
            
            # Скомпоновать
            block_clip = CompositeVideoClip([bg_clip, txt_clip])
            block_clip = block_clip.set_audio(audio_clip)
            clips.append(block_clip)
        
        # Outro (2 сек)
        outro_clip = _create_background_clip(width, height, 2, fps, "outro")
        try:
            outro_txt = TextClip(
                "Спасибо за просмотр!",
                fontsize=60,
                color="white",
                font="Arial-Bold",
            ).set_position("center").set_duration(2)
        except:
             txt_img = _create_text_frame("Спасибо за просмотр!", width, height, 60)
             outro_txt = ImageClip(np.array(txt_img)).set_duration(2)
             
        outro_clip = CompositeVideoClip([outro_clip, outro_txt])
        clips.append(outro_clip)
        
        # Объединить все клипы
        final_clip = concatenate_videoclips(clips)
        
        # Экспорт
        final_clip.write_videofile(
            str(output_path),
            fps=fps,
            codec="libx264",
            audio_codec="aac",
            bitrate=VIDEO_CONFIG["long_form"]["bitrate"],
            verbose=False,
            logger=None,
        )
        
        logger.info(f"✅ Long-form video created: {output_path}")
        return output_path
    
    except Exception as e:
        logger.error(f"❌ Long-form rendering failed: {e}")
        raise


def _render_ad(
    config: ProjectConfig,
    script: dict[str, Any],
    audio_map: dict[str, Any],
) -> Path:
    """
    Render ad video (9:16 vertical, 15-30 сек).
    """
    project_slug = str(config.project.get("name", "project")).replace(" ", "_")
    output_dir = Path("output") / "videos" / project_slug
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / "ad.mp4"
    
    try:
        width, height = VIDEO_CONFIG["ad"]["width"], VIDEO_CONFIG["ad"]["height"]
        fps = VIDEO_CONFIG["ad"]["fps"]
        duration = audio_map["total_duration_sec"]
        
        # Фоновое видео
        bg_clip = _create_background_clip(width, height, duration, fps, "ad")
        
        # Текст продукта
        product_id = script.get("product_id", "Специальное предложение")
        
        try:
            txt_clip = TextClip(
                product_id,
                fontsize=70,
                color="yellow",
                font="Arial-Bold",
            ).set_position("center").set_duration(duration)
        except:
            txt_img = _create_text_frame(product_id, width, height, 70, (255, 255, 0))
            txt_clip = ImageClip(np.array(txt_img)).set_duration(duration)
        
        # Аудио
        audio_path = audio_map["blocks"]["main"]
        audio_clip = AudioFileClip(audio_path)
        
        # Компоновка
        final_clip = CompositeVideoClip([bg_clip, txt_clip])
        final_clip = final_clip.set_audio(audio_clip)
        
        # Экспорт
        final_clip.write_videofile(
            str(output_path),
            fps=fps,
            codec="libx264",
            audio_codec="aac",
            bitrate=VIDEO_CONFIG["ad"]["bitrate"],
            verbose=False,
            logger=None,
        )
        
        logger.info(f"✅ Ad video created: {output_path}")
        return output_path
    
    except Exception as e:
        logger.error(f"❌ Ad rendering failed: {e}")
        raise


# ============ MAIN FUNCTION ============

def render(
    config: ProjectConfig,
    script: Any,
    audio_map: Any,
    mode: str,
) -> Path:
    """
    Main entry point for video rendering.
    
    Args:
        config: ProjectConfig with video settings
        script: Generated script dict
        audio_map: Output from tts_generator.synthesize()
        mode: "shorts" | "long_form" | "ad"
    
    Returns:
        Path to generated MP4 file
    """
    
    try:
        if mode == "shorts":
            return _render_shorts(config, script, audio_map)
        
        elif mode == "long_form":
            return _render_long_form(config, script, audio_map)
        
        elif mode == "ad":
            return _render_ad(config, script, audio_map)
        
        else:
            raise ValueError(f"Unknown mode: {mode}")
    
    except Exception as e:
        logger.error(f"❌ Video rendering failed: {e}")
        raise RuntimeError(f"Video rendering error: {e}") from e
