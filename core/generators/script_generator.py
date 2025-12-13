from __future__ import annotations

import datetime as _dt
import json
import logging
import uuid
from pathlib import Path
from typing import Any

from core.utils.config_loader import ProjectConfig
from core.utils.model_router import get_router

logger = logging.getLogger(__name__)

# ==================== LENGTH VALIDATION CONSTANTS ====================

MIN_SCRIPT_LENGTH = {
    "shorts": 200,      # ~30 seconds TTS
    "long_form": 800,   # ~10 minutes TTS
    "weekly": 500,      # ~5 minutes TTS
    "ad": 100,          # ~15 seconds TTS
}

MAX_SCRIPT_LENGTH = {
    "shorts": 400,
    "long_form": 1500,
    "weekly": 1000,
    "ad": 200,
}

MAX_LENGTH_ATTEMPTS = 3

# ==================== HELPER FUNCTIONS ====================


def _read_project_prompt(project_name: str, relative_path: str) -> str:
    """Read prompt template from project directory."""
    prompt_path = Path("projects") / project_name / relative_path
    return prompt_path.read_text(encoding="utf-8")


def _save_script_to_file(script: dict[str, Any], project_name: str, date: str, script_type: str) -> str:
    """Save script to JSON file and return the path."""
    # Format date as YYYYMMDD for directory structure
    date_obj = _dt.datetime.strptime(date, '%Y-%m-%d').date() if '-' in date else _dt.datetime.strptime(date, '%Y%m%d').date()
    date_dir = date_obj.strftime('%Y%m%d')
    
    output_dir = Path("output") / "scripts" / project_name / date_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    script_id = uuid.uuid4().hex[:8]
    script_path = output_dir / f"{script_type}_{script_id}.json"
    with open(script_path, "w", encoding="utf-8") as f:
        json.dump(script, f, indent=2, ensure_ascii=False)

    return str(script_path)


def _validate_script_length(script_text: str, format_type: str) -> tuple[bool, str]:
    """
    Validate script length.
    
    Args:
        script_text: The script content
        format_type: Type of content (shorts, long_form, ad)
    
    Returns:
        (is_valid, reason)
        
    Example:
        (True, "Valid: 356 chars")
        (False, "Too short: 150 < 200 (deficit: 50)")
    """
    length = len(script_text)
    min_len = MIN_SCRIPT_LENGTH.get(format_type, 100)
    max_len = MAX_SCRIPT_LENGTH.get(format_type, 1000)
    
    if length < min_len:
        deficit = min_len - length
        return False, f"Too short: {length} < {min_len} (deficit: {deficit})"
    
    if length > max_len:
        excess = length - max_len
        return False, f"Too long: {length} > {max_len} (excess: {excess})"
    
    return True, f"Valid: {length} chars"


def _build_horoscope_prompt(config: ProjectConfig, target_date: str, format_type: str, prompt_template: str = "") -> str:
    """
    Build horoscope generation prompt.
    
    Args:
        config: Project configuration
        target_date: Target date (YYYY-MM-DD)
        format_type: shorts, long_form, or ad
        prompt_template: Optional custom prompt template
    
    Returns:
        Complete prompt for LLM
    """
    
    # Parse date
    date_obj = _dt.datetime.strptime(target_date, '%Y-%m-%d')
    date_formatted = date_obj.strftime('%d %B %Y')  # "13 декабря 2025"
    day_of_week = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"][date_obj.weekday()]
    
    # Base prompt template
    if prompt_template:
        base_prompt = prompt_template.replace("{date}", date_formatted)
    elif format_type == "shorts":
        base_prompt = f"""Создай короткий, захватывающий гороскоп на {date_formatted} ({day_of_week}) для YouTube Shorts.
Формат: hook + основной контент + призыв к действию
Длительность: 30-60 секунд чтения
Стиль: таинственный, но понятный"""
    elif format_type == "long_form":
        base_prompt = f"""Создай подробный гороскоп на {date_formatted} ({day_of_week}) для YouTube длинного видео.
Структура: введение + 3 блока (любовь/деньги/здоровье) + заключение
Длительность: 8-12 минут чтения
Стиль: профессиональный астролог, глубокий анализ"""
    else:
        base_prompt = f"""Создай рекламный сценарий для видео на тему астрологии на {date_formatted}."""
    
    # JSON structure requirements
    if format_type == "shorts":
        json_structure = """{
    "hook": "Захватывающий заголовок для первых 3 секунд",
    "content_type": "shorts",
    "script": "Полный текст гороскопа (200-400 символов)",
    "visual_hints": ["космос", "звезды", "зодиак"],
    "engagement_cta": "Призыв подписаться/лайкнуть",
    "duration_sec_target": 45
}"""
    elif format_type == "long_form":
        json_structure = """{
    "video_title": "Заголовок видео",
    "intro": "Вступление (2-3 минуты)",
    "blocks": {
        "love": "Любовные перспективы (3-4 минуты)",
        "money": "Финансовые прогнозы (3-4 минуты)",
        "health": "Здоровье и благополучие (2-3 минуты)"
    },
    "outro": "Заключение и CTA",
    "chapters": [
        {"title": "Любовь", "timestamp": "0:00"},
        {"title": "Деньги", "timestamp": "4:00"},
        {"title": "Здоровье", "timestamp": "8:00"}
    ],
    "duration_target_min": 12
}"""
    else:
        json_structure = """{
    "product_id": "horoscope_premium",
    "hook": "Захватывающее начало",
    "narration_text": "Текст рекламы (100-200 символов)",
    "cta": "Призыв к действию",
    "duration_sec_target": 20
}"""
    
    # Complete prompt
    full_prompt = f"""{base_prompt}

**ВАЖНО: Длина текста**
- Минимальная длина: {MIN_SCRIPT_LENGTH.get(format_type, 100)} символов
- Максимальная длина: {MAX_SCRIPT_LENGTH.get(format_type, 1000)} символов
- Текст должен быть содержательным и насыщенным

**Формат ответа:**
Верни ТОЛЬКО валидный JSON в следующем формате (без markdown, без комментариев):

{json_structure}

**Требования к контенту:**
- Язык: Русский
- Тон: {config.project.get('niche', 'астрология')} стиль
- Целевая аудитория: {config.project.get('target_audience', 'Женщины 18-45')}
- Дата: {date_formatted} ({day_of_week})
"""
    
    return full_prompt


# ==================== GENERATION FUNCTIONS ====================


def generate_short(config: ProjectConfig, target_date: str = None, **kwargs) -> dict[str, Any]:
    """
    Generate shorts script with ModelRouter, fallback, retry, and length validation.
    
    Args:
        config: Project configuration
        target_date: Target date (YYYY-MM-DD)
        **kwargs: Should contain 'api_key' for ModelRouter
    
    Returns:
        Script dict with all required fields
    """
    
    if target_date is None:
        target_date = _dt.date.today().isoformat()
    
    api_key = kwargs.get("api_key")
    if not api_key:
        raise ValueError("api_key is required in kwargs for script generation")
    
    project_name = config.project.get("folder") or config.project.get("id") or config.project.get("name") or "youtube_horoscope"
    
    # Try to read custom prompt template
    prompt_rel = config.generation.prompt_files.get("shorts_script")
    prompt_template = _read_project_prompt(project_name, prompt_rel) if prompt_rel else ""
    
    logger.info("\n" + "="*70)
    logger.info("📝 SHORTS SCRIPT GENERATION START")
    logger.info("="*70)
    logger.info(f"Date: {target_date}")
    logger.info(f"Project: {project_name}")
    
    router = get_router(api_key)
    
    for attempt in range(1, MAX_LENGTH_ATTEMPTS + 1):
        logger.info(f"\n🔄 Attempt {attempt}/{MAX_LENGTH_ATTEMPTS} to generate shorts script")
        
        # Build prompt
        prompt = _build_horoscope_prompt(config, target_date, "shorts", prompt_template)
        
        try:
            # Generate with ModelRouter (automatic fallback + retry)
            script_dict = router.generate_json(task="script", prompt=prompt)
            
            # Validate structure
            if "script" not in script_dict:
                logger.warning(f"⚠️ Missing 'script' field in response, trying to extract...")
                # Try to find text content
                script_text = script_dict.get("narration_text", "") or script_dict.get("content", "") or str(script_dict)
                script_dict["script"] = script_text
            
            # Validate length
            script_text = script_dict.get("script", "")
            is_valid, reason = _validate_script_length(script_text, "shorts")
            
            logger.info(f"📏 Length check: {reason}")
            
            if is_valid:
                logger.info(f"✅ Script valid after attempt {attempt}")
                
                # Ensure all required fields exist
                script_dict.setdefault("hook", f"Гороскоп на {target_date}")
                script_dict.setdefault("content_type", "shorts")
                script_dict.setdefault("visual_hints", ["stars", "zodiac", "cosmos"])
                script_dict.setdefault("engagement_cta", "Подпишись на канал!")
                script_dict.setdefault("duration_sec_target", 45)
                
                # Save to file
                script_path = _save_script_to_file(script_dict, project_name, target_date, "short")
                script_dict["_script_path"] = script_path
                
                logger.info(f"💾 Script saved: {script_path}")
                logger.info("="*70 + "\n")
                
                return script_dict
            
            # Not valid - retry with enhanced prompt
            if attempt < MAX_LENGTH_ATTEMPTS:
                logger.warning(f"🔄 Retrying with length enforcement...")
                
                deficit = MIN_SCRIPT_LENGTH["shorts"] - len(script_text)
                enhanced_prompt = prompt + f"""

**КРИТИЧЕСКОЕ ТРЕБОВАНИЕ ПО ДЛИНЕ:**
Текст в поле "script" ОБЯЗАН быть минимум {MIN_SCRIPT_LENGTH["shorts"]} символов.
Текущая попытка: {len(script_text)} символов (недостаточно на {deficit}).
Добавь более детальные астрологические прогнозы, чтобы достичь требуемой длины.
"""
                
                script_dict = router.generate_json(task="script", prompt=enhanced_prompt)
                script_text = script_dict.get("script", "")
                is_valid, reason = _validate_script_length(script_text, "shorts")
                
                logger.info(f"📏 Enhanced length check: {reason}")
                
                if is_valid:
                    logger.info(f"✅ Script valid after length-enforced retry")
                    
                    # Ensure fields
                    script_dict.setdefault("hook", f"Гороскоп на {target_date}")
                    script_dict.setdefault("content_type", "shorts")
                    script_dict.setdefault("visual_hints", ["stars", "zodiac"])
                    script_dict.setdefault("engagement_cta", "Подпишись!")
                    script_dict.setdefault("duration_sec_target", 45)
                    
                    script_path = _save_script_to_file(script_dict, project_name, target_date, "short")
                    script_dict["_script_path"] = script_path
                    
                    logger.info(f"💾 Script saved: {script_path}")
                    logger.info("="*70 + "\n")
                    
                    return script_dict
        
        except Exception as e:
            logger.error(f"❌ Attempt {attempt} failed: {e}")
            if attempt == MAX_LENGTH_ATTEMPTS:
                raise
    
    # All attempts exhausted - use last result with warning
    logger.warning(f"⚠️ Max attempts reached. Using last result (may not meet length requirements).")
    
    script_dict.setdefault("hook", f"Гороскоп на {target_date}")
    script_dict.setdefault("content_type", "shorts")
    script_dict.setdefault("visual_hints", ["stars"])
    script_dict.setdefault("engagement_cta", "Подпишись!")
    script_dict.setdefault("duration_sec_target", 45)
    
    script_path = _save_script_to_file(script_dict, project_name, target_date, "short")
    script_dict["_script_path"] = script_path
    
    logger.info("="*70 + "\n")
    
    return script_dict


def generate_long_form(config: ProjectConfig, target_date: str = None, **kwargs) -> dict[str, Any]:
    """
    Generate long-form script with ModelRouter.
    """
    
    if target_date is None:
        target_date = _dt.date.today().isoformat()
    
    api_key = kwargs.get("api_key")
    if not api_key:
        raise ValueError("api_key is required in kwargs for script generation")
    
    project_name = config.project.get("folder") or config.project.get("id") or config.project.get("name") or "youtube_horoscope"
    
    prompt_rel = config.generation.prompt_files.get("long_form_script")
    prompt_template = _read_project_prompt(project_name, prompt_rel) if prompt_rel else ""
    
    logger.info("\n" + "="*70)
    logger.info("📝 LONG-FORM SCRIPT GENERATION START")
    logger.info("="*70)
    logger.info(f"Date: {target_date}")
    logger.info(f"Project: {project_name}")
    
    router = get_router(api_key)
    
    # Build prompt
    prompt = _build_horoscope_prompt(config, target_date, "long_form", prompt_template)
    
    # Generate
    script_dict = router.generate_json(task="script", prompt=prompt)
    
    # Ensure required fields
    script_dict.setdefault("video_title", f"Полный гороскоп на {target_date}")
    script_dict.setdefault("blocks", {
        "love": "Любовные перспективы...",
        "money": "Финансовые прогнозы...",
        "health": "Здоровье и благополучие..."
    })
    script_dict.setdefault("chapters", [
        {"title": "Любовь", "timestamp": "0:00"},
        {"title": "Деньги", "timestamp": "4:00"},
        {"title": "Здоровье", "timestamp": "8:00"}
    ])
    script_dict.setdefault("duration_target_min", 12)
    
    # Save
    script_path = _save_script_to_file(script_dict, project_name, target_date, "long_form")
    script_dict["_script_path"] = script_path
    
    logger.info(f"💾 Script saved: {script_path}")
    logger.info("="*70 + "\n")
    
    return script_dict


def generate_ad(config: ProjectConfig, product_id: str = None, target_date: str = None, **kwargs) -> dict[str, Any]:
    """
    Generate ad script with ModelRouter.
    """
    
    # Compatibility: product_id may come as first positional arg
    if isinstance(product_id, str) and not target_date:
        target_date = _dt.date.today().isoformat()
    
    if target_date is None:
        target_date = _dt.date.today().isoformat()
    
    api_key = kwargs.get("api_key")
    if not api_key:
        raise ValueError("api_key is required in kwargs for script generation")
    
    project_name = config.project.get("folder") or config.project.get("id") or config.project.get("name") or "youtube_horoscope"
    
    prompt_rel = config.generation.prompt_files.get("ad_script")
    prompt_template = _read_project_prompt(project_name, prompt_rel) if prompt_rel else ""
    
    logger.info("\n" + "="*70)
    logger.info("📝 AD SCRIPT GENERATION START")
    logger.info("="*70)
    logger.info(f"Date: {target_date}")
    logger.info(f"Product: {product_id}")
    logger.info(f"Project: {project_name}")
    
    router = get_router(api_key)
    
    # Build prompt
    prompt = _build_horoscope_prompt(config, target_date, "ad", prompt_template)
    if product_id:
        prompt += f"\n\n**Product ID:** {product_id}"
    
    # Generate
    script_dict = router.generate_json(task="script", prompt=prompt)
    
    # Ensure required fields
    script_dict.setdefault("product_id", product_id or "horoscope_premium")
    script_dict.setdefault("narration_text", f"Реклама продукта {product_id}")
    script_dict.setdefault("duration_sec_target", 20)
    
    # Save
    script_path = _save_script_to_file(script_dict, project_name, target_date, "ad")
    script_dict["_script_path"] = script_path
    
    logger.info(f"💾 Script saved: {script_path}")
    logger.info("="*70 + "\n")
    
    return script_dict
