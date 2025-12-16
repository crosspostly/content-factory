# Architecture & Internals

## Обзор архитектуры

Content Factory — это модульная система генерации видео-контента с четким разделением ответственности между компонентами. Основана на паттерне **pipeline orchestration** с автоматическим fallback и retry механизмами.

### Диаграмма потока данных

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   Script Generation │────│   TTS Synthesis     │────│   Video Rendering   │
│                     │    │                     │    │                     │
│ • Gemini 2.5 Flash  │    │ • Gemini 2.5 TTS    │    │ • MoviePy           │
│ • ModelRouter       │    │ • Voice synthesis   │    │ • Pixabay API       │
│ • Length validation │    │ • WAV output        │    │ • H.264 encoding    │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
         │                          │                          │
         ▼                          ▼                          ▼
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   Metadata & Logs   │    │   Batch Processing  │    │   GitHub Actions    │
│                     │    │                     │    │                     │
│ • JSON metadata     │    │ • Multi-day gen     │    │ • CI/CD automation  │
│ • Pipeline stats    │    │ • Error recovery    │    │ • Auto-fix agent    │
│ • Model usage       │    │ • Success metrics   │    │ • Caching layers    │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
```

### Основные компоненты

| Компонент | Файл | Ответственность | Статус |
|-----------|------|---------------|--------|
| **Config Loader** | `core/utils/config_loader.py` | Загрузка и валидация YAML конфигов | ✅ Работает |
| **Script Generator** | `core/generators/script_generator.py` | Генерация текстов сценариев | ✅ Работает |
| **Model Router** | `core/utils/model_router.py` | LLM балансировка и retry (Gemini 2.5 only) | ✅ Работает |
| **Pipeline Orchestrator** | `core/orchestrators/pipeline_orchestrator.py` | Главный координатор | ✅ Работает |
| **TTS Generator** | `core/generators/tts_generator.py` | Синтез речи Gemini 2.5 TTS | ❌ НЕ РАБОТАЕТ |
| **Video Renderer** | `core/generators/video_renderer.py` | Создание видео | ⚠️ НЕЗАВЕРШЕН |
| **Batch Generator** | `core/generators/batch_generator.py` | Массовая генерация | ✅ Работает |
| **YouTube Uploader** | `core/uploaders/youtube_uploader.py` | Загрузка на YouTube | ❌ НЕ РЕАЛИЗОВАНО |

---

## Model Router - Gemini 2.5 ONLY

### ✅ Актуальная конфигурация (December 2025)

**PRIMARY**: `gemini-2.5-flash`
- Последняя версия Gemini (декабрь 2025)
- Оптимизирован для скорости и качества
- Используется для ВСЕХ генеративных задач

**FALLBACK**: `gemini-2.5-flash-lite`
- Облегченная версия для fallback
- Быстрее отвечает при высокой нагрузке

**FALLBACK**: `gemini-2.5-flash-lite`
- Легкая версия Gemini 2.5
- Быстрее, но качество немного ниже
- Автоматический fallback при ошибках primary

**TTS**: `gemini-2.5-flash-tts`
- Специализированный TTS engine
- Высокое качество синтеза русской речи
- ТОЛЬКО для audio synthesis (не для текста!)

### ❌ Deprecated Models (НЕ ИСПОЛЬЗОВАТЬ!)

Следующие модели **НЕ ПОДДЕРЖИВАЮТСЯ** и должны быть удалены:
- `gemini-1.5-flash` ❌ (старое поколение)
- `gemini-1.5-pro` ❌ (старое поколение)
- `gemini-2.0-flash` ❌ (deprecated)
- `gemini-2.0-flash-exp` ❌ (experimental, removed Dec 2025)
- `gemini-exp-1206` ❌ (experimental, removed)

### Конфигурация по задачам

```python
MODELS = {
    "script": {
        "primary": "gemini-2.5-flash",
        "fallback": "gemini-2.5-flash-lite"
    },
    "tts": {
        "primary": "gemini-2.5-flash-tts",
        "fallback": "gemini-2.5-flash-lite"
    },
    "image_gen": {
        "primary": "gemini-2.5-flash",
        "fallback": "gemini-2.5-flash-lite"
    },
    "error_analysis": {
        "primary": "gemini-2.5-flash",
        "fallback": "gemini-2.5-flash-lite"
    }
}
```

### ModelRouter Retry Flow

```
Task: Generate Script
     ↓
Primary Model (gemini-2.5-flash)
├── Attempt 1 (2s wait on fail)
├── Attempt 2 (4s wait on fail)
└── Attempt 3 (8s wait on fail)
    ↓ (all failed)
Fallback Model (gemini-2.5-flash-lite)
    ├── Attempt 1 (2s wait on fail)
    ├── Attempt 2 (4s wait on fail)
    └── Attempt 3 (8s wait on fail)
    ↓ (success or final failure)
Return Result or Exception
```

---

## 🚨 Критические проблемы архитектуры

### ❌ TTS Generator - Silent WAV Bug
**Файл**: `core/generators/tts_generator.py`
**Проблема**: Строка 149 создает silent WAV файлы вместо синтеза речи
```python
# КРИТИЧЕСКАЯ ОШИБКА в _synthesize_gemini_tts_async():
logger.warning(f"⚠️ Gemini TTS returned no audio, created silent placeholder")
return estimated_duration  # Это создает тишину!
```
**Влияние**: Видео не имеют озвучки, только тишина
**Решение**: Исправить Gemini TTS API integration

### ⚠️ Video Renderer - Incomplete Pixabay Logic
**Файл**: `core/generators/video_renderer.py`
**Проблема**: Строки 88-99 - незавершенная логика обработки Pixabay video formats
```python
# НЕЗАВЕРШЕННЫЙ КОД:
for fmt in ["large", "medium", "small", "tiny"]:
    pass  # НЕ ЗАВЕРШЕНО!
```
**Влияние**: Fallback на gradient backgrounds вместо стокового видео
**Решение**: Завершить или удалить неиспользуемый код

### ❌ Uploaders - NotImplementedError
**Файлы**: `core/uploaders/*.py`
**Проблема**: Все uploader'ы содержат только `raise NotImplementedError`
**Влияние**: Невозможна автоматическая публикация
**Решение**: Реализовать в Part 4

### ❌ Services Layer - Non-existent
**Ожидаемое**: `services/` directory с интеграциями
**Реальность**: НЕТ services/ directory в проекте
**Влияние**: Нет внешних сервисов (Telegram bot, external APIs)
**Решение**: Создать в будущих частях

---

## Video Modes - THREE VERTICAL FORMATS

### Три вертикальных режима видео

| Режим | Разрешение | Длительность | Назначение |
|-------|-----------|-----------|----------|
| **shorts** | 1080×1920 (9:16) | 5-60 сек | TikTok/Instagram Reels/YT Shorts |
| **weekly** | 1080×1920 (9:16) | ~5 минут | Еженедельный обзор/overview |
| **ad** | 1080×1920 (9:16) | 15-30 сек | Реклама/спонсорский контент |

### Length Validation Constants

```python
MIN_SCRIPT_LENGTH = {
    "shorts": 200,      # ~30 секунд TTS
    "weekly": 500,      # ~5 минут TTS
    "ad": 100,          # ~15 секунд TTS
}

MAX_SCRIPT_LENGTH = {
    "shorts": 400,
    "weekly": 1000,
    "ad": 200,
}
```

### Validation Logic

1. **Первая попытка**: Обычный промпт через `gemini-2.5-flash`
2. **Проверка длины**: Валидация `len(script_text)` против MIN/MAX
3. **Retry с усилением**: Если нужна большая длина, добавляется constraint
4. **Fallback**: Использует `gemini-2.5-flash-lite` если primary падает
5. **Final fallback**: Использует последний результат с предупреждением

---

## Config Loader

### Как работает загрузка

**Основные этапы**:
1. Поиск конфиг файла (`config.yaml` → `config.yml` → `config.json`)
2. Загрузка через `yaml.safe_load()` или `json.loads()`
3. Валидация на пустоту и структуру
4. Merge с `config/shared.yaml` (если существует)
5. Обогащение метаданными проекта
6. Валидация обязательных полей

### ConfigNode механика

**Dot-access паттерн**:
```python
config = load("youtube_horoscope")

# Работает:
config.project.name          # → "YouTube Гороскопы"
config.generation.models.primary  # → "gemini-2.5-flash"
```

---

## Script Generator

### Generation Functions

**Три основные функции для трех режимов**:

```python
# SHORTS mode (5-60 sec)
script = generate_short(config, target_date="2025-12-14", api_key=api_key)

# WEEKLY mode (~5 min)
script = generate_weekly(config, target_date="2025-12-14", api_key=api_key)

# AD mode (15-30 sec)
script = generate_ad(config, target_date="2025-12-14", api_key=api_key)
```

### ModelRouter Integration

**Ключевые особенности**:
- Автоматический fallback: `gemini-2.5-flash` → `gemini-2.5-flash-lite`
- 3 retry попытки на модель с exponential backoff (2s, 4s, 8s)
- Автоматический JSON repair при ошибках парсинга
- Детальная статистика использования

**Usage pattern**:
```python
from core.utils.model_router import get_router

router = get_router(api_key)

# Автоматический fallback + retry + JSON repair
script_dict = router.generate_json(
    task="script",
    prompt=prompt
)

# Получение статистики
stats = router.get_stats()
# {
#     "total_attempts": 2,
#     "successful": 2,
#     "failed": 0,
#     "success_rate": "100%",
#     "model_usage": {"gemini-2.5-flash": 2}
# }
```

---

## TTS Generator - Gemini 2.5 Flash TTS

### TTS Configuration

**Model**: `gemini-2.5-flash-tts` (ONLY)
- Specialized for high-quality Russian speech synthesis
- NOT for text generation (use gemini-2.5-flash instead)
- Optimized for audio generation task

**Voices Available**:
```python
VOICES = {
    "russian_female_warm": "ru-RU-SvetlanaNeural",   # Default
    "russian_female_dariya": "ru-RU-DariyaNeural",   # Natural
    "russian_male": "ru-RU-DmitryNeural",            # Male voice
}
```

**Output Settings**:
- Sample rate: 22050 Hz
- Channels: Mono
- Format: WAV (no compression)
- Speed: 0.5-2.0x configurable

### TTS Synthesis Flow

```python
async def _synthesize_tts_async(
    text: str,
    voice: str,
    output_path: Path,
    speed: float = 1.0
) -> float:
    """
    Synthesize speech using Gemini 2.5 Flash TTS.
    
    CRITICAL: This ONLY uses gemini-2.5-flash-tts
    """
    # Initialize TTS engine
    tts = GeminiTTS(
        model="gemini-2.5-flash-tts",
        api_key=api_key
    )
    
    # Generate audio
    audio_data = await tts.synthesize(
        text=text,
        voice=voice,
        speed=speed
    )
    
    # Save to WAV
    with open(output_path, "wb") as f:
        f.write(audio_data)
    
    # Estimate duration
    duration = max(len(text) / 10.0 * (2.0 - speed), 1.0)
    return duration
```

---

## Pipeline Orchestrator

### Полный цикл генерации

**Этапы обработки**:

1. **Step 1: Script Generation (Gemini 2.5 Flash)**
   - Загрузка конфигурации проекта
   - Получение API ключа из окружения
   - Генерация скрипта через `script_generator.generate_*()`
   - Model: `gemini-2.5-flash` → `gemini-2.5-flash-lite`

2. **Step 2: TTS Synthesis (Gemini 2.5 Flash TTS)**
   - Синтез речи через `tts_generator.synthesize()`
   - Создание WAV файлов (22050Hz, mono)
   - Model: `gemini-2.5-flash-tts` → `gemini-2.5-flash-lite`
   - Сохранение аудио блоков по типам контента

3. **Step 3: Video Rendering**
   - Композиция видео через `video_renderer.render()`
   - Генерация или получение фоновых материалов
   - H.264 кодирование в нужном разрешении

4. **Step 4: Metadata & Logs**
   - Сохранение метаданных генерации
   - Статистика ModelRouter в JSON
   - Финальное логирование результатов

### Error handling

**Strategy**:
- **Script fails**: Полный pipeline останавливается
- **TTS fails**: Попытка продолжить с default audio
- **Video fails**: Попытка продолжить с базовым рендерингом
- **Metadata fails**: Не критично, pipeline продолжается

---

## MoviePy Video Rendering

### Resolution Configuration

**Все три режима используют вертикальное видео (9:16)**:

```python
VIDEO_CONFIG = {
    "shorts": {
        "width": 1080,
        "height": 1920,
        "aspect": "9:16",
        "fps": 30,
        "bitrate": "5000k",
    },
    "weekly": {
        "width": 1080,
        "height": 1920,
        "aspect": "9:16",
        "fps": 30,
        "bitrate": "5000k",
    },
    "ad": {
        "width": 1080,
        "height": 1920,
        "aspect": "9:16",
        "fps": 30,
        "bitrate": "5000k",
    },
}
```

### MoviePy Version Requirements

**CRITICAL**: Используется **moviepy v1.0.3**, НЕ v2!

```python
from moviepy.editor import (
    CompositeVideoClip, CompositeAudioClip,
    TextClip, ImageClip, AudioFileClip,
    VideoFileClip, VideoClip,
    concatenate_videoclips, vfx
)
```

---

## Batch Generator

### Как работает batch processing

**Основной цикл**:
```python
for i in range(num_days):
    date = (start + timedelta(days=i)).strftime("%Y-%m-%d")
    
    try:
        # 1. Script generation (gemini-2.5-flash)
        script = script_generator.generate_short(
            config, target_date=date, api_key=api_key
        )
        
        # 2. TTS synthesis (gemini-2.5-flash-tts)
        audio_map = tts_generator.synthesize(
            config, script, mode, api_key=api_key
        )
        
        # 3. Video rendering
        video_path = video_renderer.render(
            config, script, audio_map, mode
        )
        
        results.append({
            "date": date,
            "status": "success",
            "video_path": str(video_path)
        })
        
    except Exception as e:
        results.append({
            "date": date,
            "status": "failed",
            "error": str(e)
        })
```

### Success Metrics

```python
successful = sum(1 for r in results if r["status"] == "success")
failed = num_days - successful

logger.info(f"Total: {num_days} days")
logger.info(f"Success: {successful} ({successful/num_days*100:.1f}%)")
logger.info(f"Failed: {failed} ({failed/num_days*100:.1f}%)")
```

---

## Internal Patterns

### Singleton Pattern (ModelRouter)
```python
_router_instance: Optional[ModelRouter] = None

def get_router(api_key: str) -> ModelRouter:
    global _router_instance
    if _router_instance is None:
        _router_instance = ModelRouter(api_key)
    return _router_instance
```

### Pipeline Pattern
```python
def main(args) -> int:
    try:
        script = generate_script(config, date, api_key)
        audio = synthesize_audio(config, script, mode)
        video = render_video(config, script, audio, mode)
        metadata = save_metadata(script, audio, video)
        return 0
    except Exception as e:
        logging_utils.log_error(f"Pipeline failed: {e}", e)
        return 1
```

---

## Known Limitations

### Что не работает идеально

#### 1. **Gemini 2.5 API Rate Limiting**
- **Проблема**: Google может ограничивать запросы
- **Обход**: Retry с exponential backoff, fallback на flash-lite
- **Решение**: Использовать кэширование результатов

#### 2. **MoviePy Memory Usage**
- **Проблема**: Высокое потребление RAM при обработке больших видео
- **Обход**: Обработка по частям, очистка ресурсов
- **Решение**: Оптимизировать размер входных материалов

#### 3. **TTS Quality Variance**
- **Проблема**: Quality может отличаться между запусками
- **Обход**: Кэширование синтезированного аудио
- **Решение**: Использовать consistent voice settings

---

## References

**Gemini 2.5 Series (Current - December 2025)**:
- **gemini-2.5-flash**: Latest production model for all generation tasks
- **gemini-2.5-flash-lite**: Lighter variant for fallback
- **gemini-2.5-flash-tts**: Specialized TTS engine for audio synthesis

**DO NOT USE** ❌:
- Gemini 1.5 series (old generation)
- Gemini 2.0 experimental (removed Dec 2025)
- Any other model variants

---

Этот документ содержит ТОЛЬКО Gemini 2.5 серию. Все ссылки на другие модели удалены.
