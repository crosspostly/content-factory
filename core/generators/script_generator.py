"""Script Generator — генерация JSON-сценариев через LLM"""
import json
import uuid
from datetime import datetime, date
from pathlib import Path
from typing import Optional, Dict, Any

from core.utils.config_loader import ProjectConfig
from core.utils.model_router import generate_text
from core.utils.logging_utils import log_success, log_error


def generate_short(
    config: ProjectConfig,
    target_date: Optional[date] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Генерирует сценарий для YouTube Shorts (15-60 сек).
    
    Процесс:
    1) Читает prompt из config.generation.prompt_files.shorts_script
    2) Подготавливает system_prompt с инструкциями
    3) Подготавливает user_prompt с датой, нишей, целевой аудиторией
    4) Вызывает LLM с фолбеками
    5) Парсит JSON-ответ
    6) Валидирует структуру
    7) Сохраняет в output/scripts/{project}/{date}/
    
    Returns:
        dict: JSON-сценарий с полями hook, content_type, script, visual_hints и т.д.
    """
    if target_date is None:
        target_date = datetime.now().date()
    
    log_success(f"Generating shorts script for {target_date}")
    
    try:
        # Читаем prompt-файл
        prompt_path = Path(config.generation.prompt_files.get('shorts_script', 'prompts/shorts_scenario.txt'))
        if not prompt_path.exists():
            raise FileNotFoundError(f"Shorts prompt not found: {prompt_path}")
        
        with open(prompt_path) as f:
            system_prompt = f.read()
        
        # Подготавливаем user_prompt
        user_prompt = f"""
Date: {target_date.isoformat()}
Language: {config.project.get('language', 'Russian')}
Niche: {config.project.get('niche', 'astrology')}
Target audience: {config.project.get('target_audience', 'Women 18-45')}

Generate a viral YouTube Shorts scenario in JSON format.
Output MUST be valid JSON matching the schema.
        """
        
        # Генерируем через LLM
        response = generate_text(
            config,
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=config.generation.get('temperature', 0.8)
        )
        
        # Парсим JSON
        script = json.loads(response)
        
        # Валидируем
        required_fields = ['hook', 'content_type', 'script']
        for field in required_fields:
            if field not in script:
                raise ValueError(f"Missing required field in script: {field}")
        
        # Сохраняем
        output_dir = Path(f"output/scripts/{config.project['name']}/{target_date}")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        script_path = output_dir / f"short_{uuid.uuid4().hex[:8]}.json"
        with open(script_path, 'w', encoding='utf-8') as f:
            json.dump(script, f, indent=2, ensure_ascii=False)
        
        script['_script_path'] = str(script_path)
        log_success(f"Shorts script saved: {script_path}")
        
        return script
    
    except Exception as e:
        log_error(f"Failed to generate shorts script", e)
        raise


def generate_long_form(
    config: ProjectConfig,
    target_date: Optional[date] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Генерирует сценарий для длинного видео (20-45 мин).
    
    Структура:
    - intro (2 мин)
    - astro_context (2 мин)
    - blocks: love, money, health (каждый ~10-15 мин)
    - special_section (5-6 мин)
    - closing (1.5 мин)
    
    Гарантирует:
    - Блочную структуру
    - Манифестационные фразы в каждом блоке
    - YouTube chapters
    - Общую длительность 20-45 мин
    
    Returns:
        dict: JSON-сценарий с полной структурой
    """
    if target_date is None:
        target_date = datetime.now().date()
    
    log_success(f"Generating long-form script for {target_date}")
    
    try:
        # Читаем prompt
        prompt_path = Path(config.generation.prompt_files.get('long_form_script', 'prompts/long_form_scenario.txt'))
        if not prompt_path.exists():
            raise FileNotFoundError(f"Long-form prompt not found: {prompt_path}")
        
        with open(prompt_path) as f:
            system_prompt = f.read()
        
        # Подготавливаем user_prompt
        duration_target = config.content_strategy.get('long_form', {}).get('duration', {}).get('target', 30)
        
        user_prompt = f"""
Date: {target_date.isoformat()}
Language: {config.project.get('language', 'Russian')}
Niche: {config.project.get('niche', 'astrology')}
Target duration (minutes): {duration_target}

Generate a long-form horoscope video scenario in JSON.
Must include blocks for love, money, health with manifestation CTAs.
Each sign must have a forecast.
Include chapters for YouTube.
        """
        
        # Генерируем
        response = generate_text(
            config,
            prompt=user_prompt,
            system_prompt=system_prompt
        )
        
        script = json.loads(response)
        
        # Валидируем структуру
        assert 'blocks' in script
        assert all(k in script['blocks'] for k in ['love', 'money', 'health'])
        assert 'chapters' in script
        
        # Сохраняем
        output_dir = Path(f"output/scripts/{config.project['name']}/{target_date}")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        script_path = output_dir / f"long_form_{uuid.uuid4().hex[:8]}.json"
        with open(script_path, 'w', encoding='utf-8') as f:
            json.dump(script, f, indent=2, ensure_ascii=False)
        
        script['_script_path'] = str(script_path)
        log_success(f"Long-form script saved: {script_path}")
        
        return script
    
    except Exception as e:
        log_error(f"Failed to generate long-form script", e)
        raise


def generate_ad(
    config: ProjectConfig,
    product_id: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Генерирует рекламный сценарий для конкретного продукта.
    
    Process:
    1) Читает ads/products.yaml
    2) Находит продукт по product_id
    3) Подготавливает user_prompt с инфо о продукте
    4) Генерирует сценарий
    5) Сохраняет
    
    Args:
        config: ProjectConfig
        product_id: ID продукта из ads/products.yaml
    
    Returns:
        dict: Рекламный сценарий
    """
    log_success(f"Generating ad script for product: {product_id}")
    
    try:
        import yaml
        
        # Читаем продукты
        products_path = Path(f"projects/{config.project['name']}/ads/products.yaml")
        with open(products_path) as f:
            products = yaml.safe_load(f)
        
        product = products.get(product_id)
        if not product:
            raise ValueError(f"Product not found: {product_id}")
        
        # Подготавливаем prompt
        prompt_path = Path(config.generation.prompt_files.get('ad_script', 'prompts/ad_scenario.txt'))
        with open(prompt_path) as f:
            system_prompt = f.read()
        
        user_prompt = f"""
Product: {product.get('name')}
Description: {product.get('description')}
Price: {product.get('price')}
Promo link: {product.get('link')}

Generate a viral ad script in JSON format.
        """
        
        # Генерируем
        response = generate_text(config, user_prompt, system_prompt)
        script = json.loads(response)
        
        # Сохраняем
        output_dir = Path(f"output/scripts/{config.project['name']}/{datetime.now().date()}")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        script_path = output_dir / f"ad_{product_id}.json"
        with open(script_path, 'w', encoding='utf-8') as f:
            json.dump(script, f, indent=2, ensure_ascii=False)
        
        script['_script_path'] = str(script_path)
        log_success(f"Ad script saved: {script_path}")
        
        return script
    
    except Exception as e:
        log_error(f"Failed to generate ad script", e)
        raise
