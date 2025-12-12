# 🎬 TECH_SPEC_PIPELINE.md — Полная Спецификация для ИИ-Агента
## Content Factory: от конфига к готовому видео

> **Цель:** Агент/команда агентов реализует полный пайплайн генерации контента, начиная с конфига и заканчивая готовым видеофайлом на YouTube/TikTok/Instagram/VK.

---

## 📋 Содержание

1. [Общая цель и архитектура](#общая-цель-и-архитектура)
2. [Файловая структура](#файловая-структура)
3. [Главный оркестратор](#главный-оркестратор-pipeline_orchestratorpy)
4. [Загрузка конфига](#загрузка-конфига-config_loaderpy)
5. [LLM маршрутизация](#llm-маршрутизация-model_routerpy)
6. [TTS маршрутизация](#tts-маршрутизация-tts_routerpy--tts_generatorpy)

**Оставшиеся части загружаются отдельно.**

---

## Общая цель и архитектура

### На входе:
- Конфиг проекта: `projects/youtube_horoscope/config.yaml`
- Типы контента: шорты (2x в день), длинные видео (1x в неделю), реклама (по необходимости)
- Платформы: YouTube, TikTok, Instagram, VK (или любые другие в конфиге)

### На выходе:
- Готовый видеофайл в локальной папке `output/videos/`
- (Опционально) загруженный на платформы с чистыми метаданными

### Общий поток:
```
Конфиг → LLM (сценарий) → TTS (озвучка) → Видео (монтаж) → Upload → Done
```

### Ключевая особенность — **универсальность через конфиг**:
- Агент **ничего не хардкодит** под конкретный проект.
- Все настройки читаются из YAML.
- Для нового проекта просто добавляем папку в `projects/` — код не меняется.

---

## Файловая структура

```
core/
├── orchestrators/
│   └── pipeline_orchestrator.py          # Главная точка входа
├── generators/
│   ├── script_generator.py                # Генерация JSON-сценариев (Part 3)
│   ├── tts_generator.py                   # Синтез речи (Part 2)
│   └── video_renderer.py                  # Монтаж видео (Part 3)
├── uploaders/
│   ├── youtube_uploader.py                # (Part 4)
│   ├── tiktok_uploader.py
│   ├── instagram_uploader.py
│   └── vk_uploader.py
└── utils/
    ├── config_loader.py                   # Чтение YAML конфигов (Part 1)
    ├── model_router.py                    # LLM фолбеки (Part 1)
    ├── tts_router.py                      # TTS выбор (Part 2)
    ├── stock_client.py                    # API Pixabay/Pexels/Unsplash (Part 3)
    ├── secrets_manager.py                 # GitHub Secrets / .env (Part 1)
    └── logging_utils.py                   # Логи + Telegram (Part 1)
```

---

## Главный оркестратор: `pipeline_orchestrator.py`

**Роль:** Единая точка входа. Координирует все остальные модули.

### CLI интерфейс

```bash
# Генерация шорта (без загрузки)
python -m core.orchestrators.pipeline_orchestrator \
  --project youtube_horoscope \
  --mode shorts \
  --date 2025-12-12 \
  --dry-run

# Генерация длинного видео с загрузкой
python -m core.orchestrators.pipeline_orchestrator \
  --project youtube_horoscope \
  --mode long_form \
  --platforms youtube,tiktok \
  --upload

# Генерация рекламы для конкретного продукта
python -m core.orchestrators.pipeline_orchestrator \
  --project youtube_horoscope \
  --mode ad \
  --product-id crystal_shop_001 \
  --upload
```

### Параметры

| Параметр | Тип | Обязателен | Пояснение |
|----------|-----|-----------|----------|
| `--project` | str | ✅ | Имя проекта (папка в `projects/`) |
| `--mode` | str | ✅ | `shorts` / `long_form` / `ad` |
| `--date` | str | ❌ | Дата (YYYY-MM-DD), по умолчанию сегодня |
| `--platforms` | str | ❌ | Список платформ через запятую, иначе из конфига |
| `--dry-run` | flag | ❌ | Если указан — только генерация, без upload |
| `--upload` | flag | ❌ | Если указан — загружать на платформы |
| `--product-id` | str | ❌ | Для `mode=ad` — ID продукта из ads/products.yaml |

### Алгоритм работы

```python
import argparse
import datetime
from pathlib import Path
from core.utils import config_loader, secrets_manager, logging_utils
from core.generators import script_generator, tts_generator, video_renderer
from core import uploaders

def main(args):
    # 1. Инициализация логирования
    logging_utils.setup_logging(args.project, args.date)
    
    # 2. Загрузить конфиг проекта
    try:
        config = config_loader.load(args.project)
    except FileNotFoundError as e:
        logging_utils.log_error(f"Config not found: {e}")
        return 1
    
    # 3. Определить тип контента
    try:
        if args.mode == 'shorts':
            script = script_generator.generate_short(config, args.date)
        elif args.mode == 'long_form':
            script = script_generator.generate_long_form(config, args.date)
        elif args.mode == 'ad':
            script = script_generator.generate_ad(config, args.product_id)
        else:
            raise ValueError(f"Unknown mode: {args.mode}")
    except Exception as e:
        logging_utils.log_error(f"Script generation failed: {e}", e)
        if config.monitoring.telegram_notifications:
            logging_utils.send_telegram_alert(config, f"❌ Script generation failed: {str(e)}")
        return 1
    
    # 4. Синтез речи
    try:
        audio_map = tts_generator.synthesize(config, script, args.mode)
    except Exception as e:
        logging_utils.log_error(f"TTS synthesis failed: {e}", e)
        if config.monitoring.telegram_notifications:
            logging_utils.send_telegram_alert(config, f"❌ TTS failed: {str(e)}")
        return 1
    
    # 5. Монтаж видео
    try:
        video_path = video_renderer.render(config, script, audio_map, args.mode)
    except Exception as e:
        logging_utils.log_error(f"Video rendering failed: {e}", e)
        if config.monitoring.telegram_notifications:
            logging_utils.send_telegram_alert(config, f"❌ Video rendering failed: {str(e)}")
        return 1
    
    # 6. Логирование успеха
    logging_utils.log_success(f"Video created: {video_path}")
    
    # 7. Загрузка (если нужно)
    if not args.dry_run and args.upload:
        platforms = args.platforms.split(',') if args.platforms else config.upload.get('platforms', [])
        for platform in platforms:
            try:
                if platform == 'youtube':
                    video_id = uploaders.youtube_uploader.upload(config, video_path, script, args.mode)
                    logging_utils.log_success(f"YouTube upload: {video_id}")
                elif platform == 'tiktok':
                    logging_utils.log_error(f"TikTok uploader not yet implemented")
                elif platform == 'instagram':
                    logging_utils.log_error(f"Instagram uploader not yet implemented")
                elif platform == 'vk':
                    logging_utils.log_error(f"VK uploader not yet implemented")
            except Exception as e:
                logging_utils.log_error(f"{platform} upload failed: {e}", e)
    
    # 8. Финальное уведомление
    if config.monitoring.telegram_notifications:
        if args.dry_run:
            msg = f"✅ {args.mode} script and video generated (dry-run)"
        else:
            msg = f"✅ {args.mode} ready: {video_path}"
        logging_utils.send_telegram_alert(config, msg)
    
    return 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Content Factory Pipeline')
    parser.add_argument('--project', required=True, help='Project name')
    parser.add_argument('--mode', required=True, choices=['shorts', 'long_form', 'ad'])
    parser.add_argument('--date', default=datetime.date.today().isoformat())
    parser.add_argument('--platforms', help='Comma-separated platforms (youtube,tiktok,...)')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--upload', action='store_true')
    parser.add_argument('--product-id', help='For ad mode')
    
    args = parser.parse_args()
    exit(main(args))
```

---

## Загрузка конфига: `config_loader.py`

**Роль:** Безопасно читать YAML-конфиги и валидировать их.

### Интерфейс

```python
from pydantic import BaseModel
from pathlib import Path
import yaml
import json

class ProjectConfig(BaseModel):
    """Pydantic-модель конфига (mirror структуры config.yaml)"""
    project: dict
    content_strategy: dict
    generation: dict
    audio: dict
    video: dict
    subtitles: dict
    upload: dict
    caching: dict
    monitoring: dict

def load(project_name: str) -> ProjectConfig:
    """
    Читает: projects/{project_name}/config.yaml
    Возвращает: ProjectConfig (pydantic model)
    
    Если файл не найден или невалидный → raises FileNotFoundError / ValidationError
    """
    config_path = Path(f"projects/{project_name}/config.yaml")
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")
    
    with open(config_path) as f:
        data = yaml.safe_load(f)
    
    return ProjectConfig(**data)

def load_content_plan(project_name: str) -> dict:
    """
    Читает: projects/{project_name}/content_plan.json
    Нужно для определения плана контента на неделю/месяц
    """
    plan_path = Path(f"projects/{project_name}/content_plan.json")
    if plan_path.exists():
        with open(plan_path) as f:
            return json.load(f)
    return {}
```

---

## LLM маршрутизация: `model_router.py`

**Роль:** Выбирать LLM-модель с фолбеками, если основная недоступна.

### Конфигурация (в config.yaml)

```yaml
generation:
  primary_model: "gemini-2.5-flash"
  fallback_models:
    - "gemma3:4b"
    - "qwen-2.5-72b"
  provider_priority:
    - "gemini"
    - "ollama"
    - "openrouter"
  temperature: 0.8
  max_retries: 3
  retry_delay_sec: 2
```

### Интерфейс

```python
import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def generate_text(
    config,
    prompt: str,
    system_prompt: str = None,
    model_hint: str = None,
    temperature: float = None
) -> str:
    """
    Генерирует текст используя LLM с фолбеками.
    
    Логика:
    1) Выбрать модель: model_hint или primary_model
    2) Определить провайдера (Gemini / Ollama / OpenRouter)
    3) Вызвать с retry-логикой (max_retries из конфига)
    4) При ошибке (401/403/429/timeout) → следующий фолбек
    5) При всех ошибках → raise + логировать
    
    Обработка ошибок:
    - 401/403: невалидный ключ/отсутствует → пропустить провайдера
    - 429: rate limit → retry с delay (retry_delay_sec)
    - Timeout / Connection error → retry с exponential backoff
    - После max_retries попыток → перейти на следующий фолбек
    """
    temp = temperature or config.generation.temperature
    max_retries = config.generation.max_retries
    retry_delay = config.generation.retry_delay_sec
    
    # Выбираем модель
    if model_hint:
        models_to_try = [model_hint] + config.generation.fallback_models
    else:
        models_to_try = [config.generation.primary_model] + config.generation.fallback_models
    
    last_error = None
    for model in models_to_try:
        provider = _get_provider_for_model(model, config)
        
        for attempt in range(max_retries):
            try:
                response = _call_model(provider, model, prompt, system_prompt, temp)
                logger.info(f"LLM response from {provider}/{model}")
                return response
            
            except HTTPError as e:
                if e.status_code in [401, 403]:
                    logger.warning(f"{provider}/{model}: auth error, skipping provider")
                    break  # Переходим к следующей модели
                elif e.status_code == 429:
                    if attempt < max_retries - 1:
                        wait = retry_delay * (2 ** attempt)  # exponential backoff
                        logger.warning(f"{provider}/{model}: rate limit, retrying in {wait}s")
                        time.sleep(wait)
                        continue
                    last_error = e
                else:
                    last_error = e
            
            except (TimeoutError, ConnectionError) as e:
                if attempt < max_retries - 1:
                    wait = retry_delay * (2 ** attempt)
                    logger.warning(f"{provider}/{model}: connection error, retrying in {wait}s")
                    time.sleep(wait)
                    continue
                last_error = e
        
        logger.info(f"Fallback: {provider}/{model} failed, trying next")
    
    # Все модели исчерпаны
    raise RuntimeError(f"All LLM models failed. Last error: {last_error}")

def _get_provider_for_model(model: str, config) -> str:
    """Определяет провайдера по названию модели"""
    if 'gemini' in model.lower():
        return 'gemini'
    elif 'qwen' in model.lower():
        return 'openrouter'
    else:
        return 'ollama'  # Assume local

def _call_model(provider: str, model: str, prompt: str, system: str, temp: float) -> str:
    """
    Вызывает конкретный LLM через провайдера.
    
    Реализация зависит от провайдера.
    """
    if provider == 'gemini':
        return _call_gemini(model, prompt, system, temp)
    elif provider == 'ollama':
        return _call_ollama(model, prompt, system, temp)
    elif provider == 'openrouter':
        return _call_openrouter(model, prompt, system, temp)
    else:
        raise ValueError(f"Unknown provider: {provider}")

def _call_gemini(model: str, prompt: str, system: str, temp: float) -> str:
    """Calls Google Gemini API"""
    import google.generativeai as genai
    from core.utils import secrets_manager
    
    genai.configure(api_key=secrets_manager.get("GOOGLE_AI_API_KEY"))
    client = genai.Client()
    
    response = client.models.generate_content(
        model=f"models/{model}",
        contents=prompt,
        generation_config={
            'temperature': temp,
            'top_p': 0.95,
        },
        system_instruction=system
    )
    return response.text

def _call_ollama(model: str, prompt: str, system: str, temp: float) -> str:
    """Calls local Ollama"""
    import ollama
    
    response = ollama.generate(
        model=model,
        prompt=prompt,
        system=system,
        stream=False,
        options={'temperature': temp}
    )
    return response['response']

def _call_openrouter(model: str, prompt: str, system: str, temp: float) -> str:
    """Calls OpenRouter API"""
    import openai
    from core.utils import secrets_manager
    
    client = openai.OpenAI(
        api_key=secrets_manager.get("OPENROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1"
    )
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {'role': 'system', 'content': system or ''},
            {'role': 'user', 'content': prompt}
        ],
        temperature=temp
    )
    return response.choices[0].message.content
```

---

## TTS маршрутизация: `tts_router.py` + `tts_generator.py` (краткий обзор)

**Роль:** Выбирать TTS-движок и синтезировать речь.

### `tts_router.py` — выбор движка и голоса

```python
def choose_tts_engine(config, video_type: str) -> tuple[str, str]:
    """
    Выбирает (engine_name, voice_name) для конкретного типа видео.
    
    Логика:
    1) Берёт config.audio.voice_selection[video_type]
    2) Проверяет, что engines[engine].enabled == True
    3) Возвращает (engine, voice)
    4) Если движок отключен → fallback_engine
    
    Возвращает: ("edge-tts", "female_neutral") или ("gemini-tts", "Gladia")
    """
    preferred_engine = config.audio.voice_selection.get(video_type, "edge-tts")
    engine_config = config.audio.engines.get(preferred_engine, {})
    
    if engine_config.get("enabled", False):
        return preferred_engine
    
    return config.audio.fallback_engine

def map_content_to_voice(content_type: str) -> str:
    """
    Мэпит контент на конкретный голос для выразительности.
    """
    voice_map = {
        "love": "female_warm",
        "money": "female_neutral",
        "health": "female_neutral",
        "warning": "female_mysterious",
        "lucky": "female_warm",
    }
    return voice_map.get(content_type, "female_neutral")
```

**`tts_generator.py` — детальная реализация в Part 2.**

---

## Secrets Manager: `secrets_manager.py`

```python
import os
from dotenv import load_dotenv

def get(key: str) -> str:
    """
    Берёт secret из GitHub Secrets или .env файла.
    
    Приоритет:
    1) Переменные окружения (GitHub Actions)
    2) .env файл (локально)
    3) Если не найдено → raise KeyError
    """
    # Сначала проверяем env
    value = os.getenv(key)
    if value:
        return value
    
    # Пробуем .env
    load_dotenv()
    value = os.getenv(key)
    if value:
        return value
    
    raise KeyError(f"Secret '{key}' not found in env or .env file")
```

---

## Что дальше

**Part 1 готова к реализации! ✅**

Следующие части:
- **Part 2**: TTS Generator + Stock Client (audio, music, effects)
- **Part 3**: Script Generator + Video Renderer
- **Part 4**: Uploaders + Logging + Tests

Текущая часть содержит **~600 строк готового кода + спека**.

Когда эта часть готова, загружу Part 2.
