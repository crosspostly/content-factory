# Architecture & Internals

## Обзор архитектуры

Content Factory — это модульная система генерации видео-контента с четким разделением ответственности между компонентами. Основана на паттерне **pipeline orchestration** с автоматическим fallback и retry механизмами.

### Диаграмма потока данных

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   Script Generation │────│   TTS Synthesis     │────│   Video Rendering   │
│                     │    │                     │    │                     │
│ • Gemini 2.5 Flash  │    │ • Edge-TTS          │    │ • MoviePy           │
│ • ModelRouter       │    │ • Voice selection   │    │ • Pixabay API       │
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

| Компонент | Файл | Ответственность |
|-----------|------|-----------------|
| **Config Loader** | `core/utils/config_loader.py` | Загрузка и валидация YAML конфигов |
| **Script Generator** | `core/generators/script_generator.py` | Генерация текстов сценариев |
| **Model Router** | `core/utils/model_router.py` | LLM балансировка и retry |
| **Pipeline Orchestrator** | `core/orchestrators/pipeline_orchestrator.py` | Главный координатор |
| **TTS Generator** | `core/generators/tts_generator.py`
| **Video Renderer** | `core/generators/video_renderer.py` | Создание видео |
| **Batch Generator** | `core/generators/batch_generator.py` | Массовая генерация |

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

### Валидация (КРИТИЧЕСКИ ВАЖНО!)

**Обязательные поля**:
- `project.name` - название проекта (не может быть пустым)
- Конфиг файл должен быть словарём, не списком

**Проверки пустых файлов**:
```python
# YAML файлы
if raw is None:
    raise ValueError(f"Config file is empty: {path}")

# JSON файлы  
if not raw:
    raise ValueError(f"Config file is empty: {path}")
```

### ConfigNode механика

**Dot-access паттерн**:
```python
config = load("youtube_horoscope")

# Работает:
config.project.name          # → "YouTube Гороскопы"  
config.generation.models.primary  # → "gemini-2.5-flash"

# Автоматический fallback:
config.audio.get("edge-tts", {}).get("voice", "default_voice")
```

**Поддержка hyphen/underscore**:
```python
# Оба варианта работают:
config.audio.engines.get("edge-tts") 
config.audio.engines.get("edge_tts")

# Потому что ConfigNode автоматически нормализует ключи
```

**Глубокая нормализация**:
```python
def _resolve_key(self, key: str) -> str | None:
    # 1. Точное совпадение
    if key in self._data:
        return key
    
    # 2. underscore ↔ hyphen конверсия
    if "_" in key:
        alt = key.replace("_", "-")
        if alt in self._data:
            return alt
    
    # 3. Рекурсивная нормализация
    normalized = self._normalize_key(key)
    for k in self._data.keys():
        if self._normalize_key(k) == normalized:
            return k
    
    return None
```

---

## Script Generator

### ModelRouter интеграция

**Ключевые особенности**:
- Автоматический fallback: `gemini-2.0-flash-exp` → `gemini-1.5-flash`
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
#     "model_usage": {"gemini-2.0-flash-exp": 2}
# }
```

### Length validation логика

**Цель**: Обеспечить качественный контент нужной длины

**Константы**:
```python
MIN_SCRIPT_LENGTH = {
    "shorts": 200,      # ~30 секунд TTS
    "long_form": 800,   # ~10 минут TTS  
    "weekly": 500,      # ~5 минут TTS
    "ad": 100,          # ~15 секунд TTS
}

MAX_SCRIPT_LENGTH = {
    "shorts": 400,
    "long_form": 1500,
    "weekly": 1000,
    "ad": 200,
}

MAX_LENGTH_ATTEMPTS = 3
```

**Логика валидации**:
1. **Первая попытка**: Обычный промпт
2. **Оценка длины**: `len(script_text)`
3. **Retry с усилением**: Если слишком короткий, добавляется строгое требование по длине
4. **Финальный fallback**: Использует последний результат с предупреждением

**Auto-retry промпт**:
```python
enhanced_prompt = prompt + f"""

**КРИТИЧЕСКОЕ ТРЕБОВАНИЕ ПО ДЛИНЕ:**
Текст в поле "script" ОБЯЗАН быть минимум {MIN_SCRIPT_LENGTH['shorts']} символов.
Текущая попытка: {len(script_text)} символов (недостаточно на {deficit}).
Добавь более детальные астрологические прогнозы, чтобы достичь требуемой длины.
"""
```

### Retry и fallback механика

**ModelRouter retry flow**:
```
Primary Model (gemini-2.5-flash)
├── Attempt 1 (2s wait on fail)
├── Attempt 2 (4s wait on fail)  
└── Attempt 3 (8s wait on fail)
    ↓ (all failed)
Fallback Model (gemini-1.5-flash)
    ├── Attempt 1 (2s wait on fail)
    ├── Attempt 2 (4s wait on fail)
    └── Attempt 3 (8s wait on fail)
```

**JSON repair логика**:
1. Попытка прямого парсинга `json.loads()`
2. Извлечение из markdown: ` ```json ... ``` `
3. Запрос на починку malformed JSON
4. Вторая попытка парсинга отремонтированного JSON

### JSON repair логика

**Repair prompt template**:
```
Fix this malformed JSON and return ONLY the corrected JSON object:
{response_text[:500]}

Rules:
- Remove trailing commas
- Fix unclosed brackets  
- Escape unescaped quotes
- Return ONLY valid JSON, no markdown, no explanation
```

---

## Pipeline Orchestrator

### Полный цикл генерации

**Этапы обработки**:

1. **Step 1: Script Generation**
   - Загрузка конфигурации проекта
   - Получение API ключа из окружения
   - Генерация скрипта через `script_generator.generate_*()`
   - Логирование статистики ModelRouter

2. **Step 2: TTS Synthesis**  
   - Синтез речи через `tts_generator.synthesize()`
   - Создание WAV файлов (22050Hz, mono)
   - Сохранение аудио блоков по типам контента

3. **Step 3: Video Rendering**
   - Композиция видео через `video_renderer.render()`
   - Генерация или получение фоновых материалов
   - H.264 кодирование в нужном разрешении

4. **Step 4: Metadata & Logs**
   - Сохранение метаданных генерации
   - Статистика ModelRouter в JSON
   - Финальное логирование результатов

### Dependency между шагами

**Строгие зависимости**:
```
Script → TTS → Video
   ↓        ↓      ↓
Metadata ← Logs ← Results
```

**Error handling стратегия**:
- **Script fails**: Полный pipeline останавливается
- **TTS fails**: Попытка продолжить с default audio  
- **Video fails**: Попытка продолжить с базовым рендерингом
- **Metadata fails**: Не критично, pipeline продолжается

### Error handling

**Telegram notifications** (если настроено):
```python
if config.monitoring.telegram_notifications:
    if stage == "script":
        send_telegram_alert(config, f"❌ Script generation failed: {str(e)}")
    elif stage == "tts":  
        send_telegram_alert(config, f"❌ TTS failed: {str(e)}")
    elif stage == "video":
        send_telegram_alert(config, f"❌ Video rendering failed: {str(e)}")
```

**Graceful degradation**:
- Пропуск неудачных этапов с default значениями
- Сохранение частичных результатов
- Подробное логирование для отладки

---

## TTS & Video Rendering

### Edge-TTS интеграция

**Голоса по умолчанию**:
```python
VOICES = {
    "russian_female_warm": "ru-RU-SvetlanaNeural",   # Female, friendly (default)
    "russian_female_dariya": "ru-RU-DariyaNeural",   # Female, natural  
    "russian_male": "ru-RU-DmitryNeural",            # Male voice
}
```

**Конфигурация через YAML**:
```yaml
audio:
  engines:
    edge-tts:
      voice: "ru-RU-SvetlanaNeural"  # Можно переопределить
      speed: 1.0                     # 0.5-2.0
```

**Async синтез**:
```python
async def _synthesize_edge_tts_async(
    text: str,
    voice: str, 
    output_path: Path,
    speed: float = 1.0
) -> float:
    # Edge-TTS communication object
    communicate = edge_tts.Communicate(text, voice, rate=f"{int(speed * 100)}%")
    
    # Сохранение в файл
    await communicate.save(str(output_path))
    
    # Оценка длительности (приблизительно)
    duration = max(len(text) / 10.0 * (2.0 - speed), 1.0)
    return duration
```

### MoviePy работа

**Версионность критична**: Используется **moviepy v1.0.3**, НЕ v2!

**Импорты для v1**:
```python
from moviepy.editor import (
    CompositeVideoClip, CompositeAudioClip,
    TextClip, ImageClip, AudioFileClip,  
    VideoFileClip, VideoClip,
    concatenate_videoclips, vfx
)
```

**Импорты для v2 (НЕ ИСПОЛЬЗОВАТЬ!)**:
```python
from moviepy import VideoFileClip, TextClip  # ❌ v2 API
```

### Resolution логика

**Конфигурация по типам**:
```python
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
```

### Fallback механика (ImageMagick → PIL)

**Когда TextClip (ImageMagick) падает**:

1. **Primary**: MoviePy TextClip с ImageMagick
2. **Fallback**: PIL-based text rendering
3. **Final fallback**: Plain colored background

**PIL text rendering**:
```python
def _create_text_frame(text: str, size: tuple) -> Image.Image:
    """Create text frame using PIL when ImageMagick fails."""
    img = Image.new('RGB', size, color=(20, 20, 30))
    draw = ImageDraw.Draw(img)
    
    # Try to load font, fallback to default
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    # Calculate text position (center)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2
    
    # Draw text with shadow
    draw.text((x+2, y+2), text, font=font, fill=(0, 0, 0))  # Shadow
    draw.text((x, y), text, font=font, fill=(255, 255, 255))  # Main text
    
    return img
```

---

## Batch Generator

### Как работает batch processing

**Основной цикл**:
```python
for i in range(num_days):
    date = (start + timedelta(days=i)).strftime("%Y-%m-%d")
    
    try:
        # 1. Script generation
        script = script_generator.generate_short(config, target_date=date, api_key=api_key)
        
        # 2. TTS synthesis  
        audio_map = tts_generator.synthesize(config, script, mode, api_key=api_key)
        
        # 3. Video rendering
        video_path = video_renderer.render(config, script, audio_map, mode)
        
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

### Error recovery

**Continue-on-failure стратегия**:
- Каждый день обрабатывается независимо
- Ошибки одного дня не влияют на другие
- Подробное логирование каждого failure
- Финальная сводка успешности

**Success metrics**:
```python
successful = sum(1 for r in results if r["status"] == "success")
failed = num_days - successful

logger.info(f"Total: {num_days} days")
logger.info(f"Success: {successful} ({successful/num_days*100:.1f}%)")
logger.info(f"Failed: {failed} ({failed/num_days*100:.1f}%)")
```

---

## Audio Optimization (50+ audience)

### Как работает audio mixing

**Edge-TTS voice optimization для старшей аудитории**:

1. **Параметры речи**:
   - Скорость: 0.8-0.9x (медленнее для лучшего понимания)
   - Паузы: автоматические через punctuation
   - Четкость: используются Neural2 voices

2. **Post-processing**:
   - Нормализация громкости
   - Удаление фоновых шумов
   - Увеличение контрастности частот

3. **Output settings**:
   - Sample rate: 22050 Hz (достаточно для речи)
   - Channels: Mono (экономия места)
   - Format: WAV (без компрессии)

### Senior-optimized settings

**Рекомендуемые настройки для 50+**:
```yaml
audio:
  engines:
    edge-tts:
      voice: "ru-RU-SvetlanaNeural"  # Четкий женский голос
      speed: 0.85                    # Медленнее для понимания
      pitch: 0                       # Нормальная высота
      
  post_processing:
    normalize: true                  # Нормализация громкости  
    noise_reduction: true           # Удаление шумов
    enhance_speech: true            # Улучшение речи
```

### FFmpeg filter specs

**Для улучшения речи 50+ аудитории**:
```bash
# Улучшение четкости речи
ffmpeg -i input.wav -af "highpass=f=80,lowpass=f=8000,compand=attacks=0.1:decays=0.8:points=-80/-80|-45/-15|-27/-9|0/-7,volume=1.2" output_enhanced.wav

# Параметры:
# - highpass=f=80     # Убираем низкочастотный шум
# - lowpass=f=8000    # Убираем высокочастотный шум  
# - compand           # Компрессия динамического диапазона
# - volume=1.2        # Немного громче
```

---

## Data Flow Examples

### Подробные примеры реальных потоков данных

#### Example 1: Shorts Generation Flow

**Input config**:
```yaml
project:
  name: "YouTube Гороскопы"
  folder: "youtube_horoscope"
  language: "russian"

generation:
  models:
    primary: "gemini-2.0-flash-exp"
    fallback: "gemini-1.5-flash"
    
audio:
  engines:
    edge-tts:
      voice: "ru-RU-SvetlanaNeural"
      speed: 1.0
```

**Step 1: Script Generation**
```python
# Prompt construction
prompt = """Создай короткий, захватывающий гороскоп на 13 декабря 2025 (пятница) для YouTube Shorts.
Формат: hook + основной контент + призыв к действию
Длительность: 30-60 секунд чтения

**Формат ответа:**
{
    "hook": "Захватывающий заголовок для первых 3 секунд", 
    "script": "Полный текст гороскопа (200-400 символов)",
    "visual_hints": ["космос", "звезды", "зодиак"],
    "engagement_cta": "Призыв подписаться/лайкнуть"
}
"""

# ModelRouter call
script_dict = router.generate_json(task="script", prompt=prompt)
# Result:
{
    "hook": "♈ Овен! Твоя судьба изменится уже сегодня!",
    "script": "Сегодня Овнам предстоит важное решение, которое определит ваше будущее на ближайшие месяцы. Звезды советуют не торопиться с выводами...",
    "visual_hints": ["космос", "звезды", "зодиак"], 
    "engagement_cta": "Подпишись на канал и ставь лайк!",
    "_script_path": "output/scripts/youtube_horoscope/20251213/short_a1b2c3d4.json"
}
```

**Step 2: TTS Synthesis**
```python
# Text extraction and sanitization
text = "Сегодня Овнам предстоит важное решение, которое определит ваше будущее на ближайшие месяцы. Звезды советуют не торопиться с выводами..."
clean_text = _sanitize_text_for_tts(text)  # Убираем markdown, HTML

# Edge-TTS synthesis  
audio_map = synthesize(config, script_dict, "shorts")
# Result:
{
    "blocks": {"main": "output/audio/youtube_horoscope/shorts_main.wav"},
    "engine_used": "edge-tts", 
    "total_duration_sec": 42.5,
    "sample_rate": 22050,
    "channels": 1
}
```

**Step 3: Video Rendering**
```python
# Video composition
video_path = video_renderer.render(config, script_dict, audio_map, "shorts")
# Result: "output/videos/youtube_horoscope/shorts.mp4"
```

**Step 4: Metadata saving**
```json
{
    "date": "2025-12-13",
    "mode": "shorts", 
    "project": "youtube_horoscope",
    "video_path": "output/videos/youtube_horoscope/shorts.mp4",
    "script_path": "output/scripts/youtube_horoscope/20251213/short_a1b2c3d4.json",
    "script_length": 187,
    "audio_blocks": 1,
    "generation_stats": {
        "total_attempts": 1,
        "successful": 1,
        "failed": 0,
        "success_rate": "100%", 
        "model_usage": {"gemini-2.0-flash-exp": 1}
    },
    "generated_at": "2025-12-13T10:30:15"
}
```

#### Example 2: ModelRouter Fallback Flow

**Сценарий**: Primary model падает, активируется fallback

```python
# Primary model attempt (gemini-2.0-flash-exp)
router = get_router(api_key)

try:
    # First attempt with primary
    result1 = router._try_model("gemini-2.0-flash-exp", prompt, "script")
    if result1:
        return result1
except Exception as e:
    logger.warning("Primary model failed: " + str(e))

# Fallback model attempt (gemini-1.5-flash) 
try:
    result2 = router._try_model("gemini-1.5-flash", prompt, "script") 
    if result2:
        return result2
except Exception as e:
    logger.warning("Fallback model failed: " + str(e))

# Final statistics
stats = router.get_stats()
# {
#     "total_attempts": 4,
#     "successful": 2,
#     "failed": 2, 
#     "success_rate": "50%",
#     "model_usage": {
#         "gemini-2.0-flash-exp": 2,
#         "gemini-1.5-flash": 2
#     }
# }
```

---

## Internal Patterns

### Все используемые паттерны

#### 1. **Singleton Pattern (ModelRouter)**
```python
_router_instance: Optional[ModelRouter] = None

def get_router(api_key: str) -> ModelRouter:
    global _router_instance
    if _router_instance is None:
        _router_instance = ModelRouter(api_key)
    return _router_instance
```

#### 2. **Pipeline Pattern**  
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

#### 3. **Config Node Pattern**
```python
class ConfigNode(Mapping[str, Any]):
    def __getitem__(self, key: str) -> Any:
        resolved = self._resolve_key(key)
        if resolved is None:
            raise KeyError(key)
        return self._wrap(self._data[resolved])
    
    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):
            raise AttributeError(name)
        resolved = self._resolve_key(name)
        if resolved is None:
            return ConfigNode({})  # Graceful fallback
        return self._wrap(self._data.get(resolved))
```

#### 4. **Fallback Chain Pattern**
```python
def _get_voice_from_config(config, mode):
    # 1. Try explicit config
    voice = config.audio.get("engines", {}).get("edge-tts", {}).get("voice")
    if voice:
        return voice
    
    # 2. Try language-based default  
    if config.project.get("language", "").lower() == "russian":
        return VOICES["russian_female_warm"]
    
    # 3. Ultimate fallback
    return VOICES["russian_female_warm"]
```

#### 5. **Async/Sync Wrapper Pattern**
```python
async def _synthesize_edge_tts_async(...):
    # Real async work
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(str(output_path))
    return duration

def synthesize(...):
    # Sync wrapper for compatibility
    audio_path, duration = asyncio.run(_synthesize_edge_tts_async(...))
    return {"blocks": {"main": audio_path}, ...}
```

### Антипаттерны (что НЕ надо делать)

#### 1. **Hardcoded API Keys**
```python
# ❌ BAD
API_KEY = "sk-1234567890abcdef"

# ✅ GOOD  
API_KEY = os.getenv("GOOGLE_AI_API_KEY")
if not API_KEY:
    raise ValueError("GOOGLE_AI_API_KEY not provided")
```

#### 2. **Naked Exception Catching**
```python
# ❌ BAD
try:
    result = api_call()
except:  # Too broad!
    return default

# ✅ GOOD
try:
    result = api_call()
except requests.exceptions.Timeout as e:
    logger.warning(f"API timeout: {e}")
    return default
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise
```

#### 3. **Synchronous I/O in Loops**
```python
# ❌ BAD
for i in range(100):
    result = slow_api_call()  # Blocks entire thread

# ✅ GOOD  
for i in range(100):
    result = await slow_api_call()  # Non-blocking
```

#### 4. **Mutation of Input Parameters**
```python
# ❌ BAD
def process_script(script):
    script["modified"] = True  # Changes input!
    return script

# ✅ GOOD
def process_script(script):
    modified = script.copy()
    modified["modified"] = True
    return modified
```

### Места где легче всего ошибиться

#### 1. **MoviePy Version Confusion**
- **Проблема**: Импорт v2 API вместо v1
- **Симптомы**: `AttributeError`, `ModuleNotFoundError`
- **Решение**: Всегда использовать `moviepy.editor` импорты

#### 2. **Gemini Model Names**
- **Проблема**: Использование несуществующих моделей
- **Симптомы**: `404 Model not found`
- **Актуальные модели**: `gemini-2.0-flash-exp`, `gemini-1.5-flash`

#### 3. **Config Validation**
- **Проблема**: Пустые или невалидные YAML файлы
- **Симптомы**: `Config file is empty`, `Project name is required`
- **Решение**: Всегда валидировать через `config_loader.py`

#### 4. **Edge-TTS Voice Names**
- **Проблема**: Неправильные имена голосов
- **Симптомы**: `Voice not found` ошибки
- **Правильные**: `ru-RU-SvetlanaNeural`, `ru-RU-DariyaNeural`, `ru-RU-DmitryNeural`

#### 5. **Async/Await Mismatches**
- **Проблема**: Вызов async функций без await
- **Symptons**: `coroutine object` в результатах
- **Решение**: Использовать `asyncio.run()` для sync wrapper

---

## Known Limitations

### Что не работает идеально

#### 1. **Edge-TTS Rate Limiting**
- **Проблема**: Microsoft может ограничивать запросы (403 errors)
- **Обход**: Retry с exponential backoff, fallback на другой голос
- **Решение**: Использовать локальный cache аудио

#### 2. **MoviePy Memory Usage**  
- **Проблема**: Высокое потребление RAM при обработке больших видео
- **Обход**: Обработка по частям, очистка ресурсов
- **Решение**: Оптимизировать размер входных материалов

#### 3. **Pixabay API Limits**
- **Проблема**: Лимиты на количество запросов в час
- **Обход**: Кэширование найденных материалов
- **Решение**: Fallback на сгенерированные фоны

#### 4. **Gemini API Cost**
- **Проблема**: Растущая стоимость при массовой генерации
- **Обход**: ModelRouter с дешевыми fallback моделями
- **Решение**: Batch processing с кэшированием результатов

### Почему не исправлено

#### 1. **Edge-TTS Dependency**
- **Причина**: Бесплатные качественные русские голоса
- **Альтернатива**: Google Cloud TTS (платно), локальные модели (сложно)
- **Планы**: Перейти на более стабильный сервис когда появится

#### 2. **MoviePy v1 Compatibility**
- **Причина**: Большое количество legacy кода зависит от v1 API
- **Альтернатива**: Полный рефакторинг на v2 (рискованно)
- **Планы**: Постепенная миграция в будущих версиях

#### 3. **Single ModelRouter Instance**
- **Причина**: Простота и предотвращение конфликтов
- **Альтернатива**: Factory с multiple instances
- **Планы**: Оставить как есть, работает стабильно

---

## Testing Strategy

### Critical Test Patterns

#### 1. **Config Fixtures**
```python
# ✅ Правильно
@pytest.fixture
def sample_config():
    return ProjectConfig({
        "project": {"name": "test", "folder": "test"},
        "generation": {"models": {"primary": "test"}}
    })

# ❌ Неправильно  
@pytest.fixture
def sample_config():
    return ProjectConfig(ConfigNode({"project": {"name": "test"}}))  # Double wrapping
```

#### 2. **Mock External APIs**
```python
@patch('core.generators.script_generator.router.generate_json')
def test_script_generation(mock_generate):
    mock_generate.return_value = {"script": "test", "hook": "test"}
    result = generate_short(config, "2025-12-13", api_key="test")
    assert result["script"] == "test"
```

#### 3. **Slow Test Marking**
```python
@pytest.mark.slow
def test_real_tts_synthesis():
    """Test requiring actual API calls."""
    pass  # Won't run in default pytest

# Run with: pytest tests/ -v -m "not slow"  (default)
# Run all: pytest tests/ -v
```

#### 4. **Async Test Patterns**
```python
@pytest.mark.asyncio
async def test_async_tts():
    result = await _synthesize_edge_tts_async("test", "voice", Path("test.wav"))
    assert result > 0
```

---

Этот документ должен помочь любому разработчику или AI агенту разобраться в архитектуре Content Factory за 30 минут изучения.
