# 🎥 Настройка автогенерации видео гороскопов

## ✅ Что готово

### Workflow: `.github/workflows/generate-horoscope-video.yml`

**Функционал:**
- ✅ **Shorts** (1080×1920 vertical, YouTube Shorts/TikTok/Instagram Reels)
- ✅ **Long-form** (1920×1080 horizontal, YouTube)
- ✅ **Ad** (1080×1920 vertical, 15-30с)

**Как запускать:**
- ✅ Вручно: GitHub → Actions → Generate Horoscope Video → Run workflow
- ✅ По расписанию: Каждые 06:00 UTC (09:00 MSK)

**Параметры:**
```yaml
format:      # shorts | long-form | ad
date:        # YYYY-MM-DD (опционально, по умолчанию сегодня)
project:     # youtube_horoscope (по умолчанию)
```

---

## 🏃 Как работает pipeline

### Part 1: Script Generation (текст сценария)

**Файл:** `core/generators/script_generator.py`

```
Выход:
  - для shorts: {"hook", "script", "engagement_cta", "duration_sec_target"}
  - для long-form: {"video_title", "blocks": {"love", "money", "health"}}
  - для ad: {"narration_text", "product_id"}

Сохраняется в:
  output/scripts/youtube_horoscope/YYYYMMDD/short_*.json
```

### Part 2: TTS Synthesis (озвучка текста)

**Файл:** `core/generators/tts_generator.py`

**Ключевые вызовы:**

```python
audio_result = tts_generator.synthesize(
    config=config,
    script=script,
    mode="shorts",  # | "long_form" | "ad"
    api_key=os.getenv('GOOGLE_AI_API_KEY')
)

# Выдает:
# {
#     "blocks": {"main": "path/to/wav"},  # или {"love", "money", "health"}
#     "engine_used": "gemini-2.5-tts",
#     "total_duration_sec": 23.5,
#     "sample_rate": 22050,
#     "channels": 1
# }
```

**Как работает TTS:**

| Format | Вход | Выход |
|--------|--------|--------|
| **Shorts** | Один блок: hook + script + CTA | `shorts_main.wav` |
| **Long-form** | 3 блока: love, money, health | `long_form_love.wav`, `long_form_money.wav`, `long_form_health.wav` |
| **Ad** | Один блок: narration_text | `ad_main.wav` |

**Голоса (из config.yaml):**
```yaml
audio:
  engines:
    gemini-tts:
      voice: "ru-RU-Neural2-C"  # Женский (тёплый)
      speed: 1.0                 # 0.5-2.0
      sample_rate: 22050         # Hz
      channels: 1                # Mono
```

**Доступные голоса:**
- `ru-RU-Neural2-C` — Женский (тёплый, дружелюбный) 👩
- `ru-RU-Neural2-A` — Женский (нейтральный) 👩
- `ru-RU-Neural2-B` — Мужской 👨

### Part 3: Video Rendering (монтаж видео)

**Файл:** `core/generators/video_renderer.py`

**Ключевые вызовы:**

```python
video_path = video_renderer.render(
    config=config,
    script=script,
    audio_map=audio_result,  # из Part 2
    mode="shorts"  # | "long_form" | "ad"
)

# Выдает: Path к output/videos/youtube_horoscope/shorts.mp4
```

**Мозаика видео (Shorts):**

```
Layer 1: Background Clip (1080×1920, 30 fps)
  ├─ Pixabay видео (кейворды: horoscope, stars)
  └─ Fallback: цветной фон (фиолетовый, RGB 20, 10, 40)

Layer 2: Text Overlay
  └─ Hook: "Гороскоп на сегодня" (60pt, white, bold, centered)

Layer 3: Audio Track
  └─ shorts_main.wav (22050 Hz, Mono, WAV)

OUTPUT: shorts.mp4
  ├─ Codec: libx264 (H.264)
  ├─ FPS: 30
  ├─ Bitrate: 5000k
  ├─ Audio Codec: AAC
  └─ Size: ~45 MB
```

**Параметры видео:**

```python
VIDEO_CONFIG = {
    "shorts": {"width": 1080, "height": 1920, "fps": 30, "bitrate": "5000k"},
    "long_form": {"width": 1920, "height": 1080, "fps": 30, "bitrate": "8000k"},
    "ad": {"width": 1080, "height": 1920, "fps": 30, "bitrate": "5000k"},
}

color_map = {
    "mystical": (20, 10, 40),     # Глубокий фиолетовый
    "love": (150, 30, 60),        # Красный
    "money": (50, 150, 50),       # Зелёный
    "health": (100, 150, 255),    # Синий
}
```

---

## 📥 Необходимые подготовки

### 1. ГитХаб Secrets

**Settings → Secrets and variables → Actions:**

```bash
GOOGLE_AI_API_KEY=AIzaSy...          # Обязательно

PIXABAY_API_KEY=1234567...           # Опционально (если нет → фон вместо видео)

TELEGRAM_BOT_TOKEN=123456...         # Опционально (для уведомлений)

TELEGRAM_CHAT_ID=987654...           # Опционально
```

**Как получить ключи:**
- `GOOGLE_AI_API_KEY`: [ai.google.dev](https://ai.google.dev) → API Key
- `PIXABAY_API_KEY`: [pixabay.com/api](https://pixabay.com/api) → Register → API Key

### 2. Конфиг проекта

**Файл:** `projects/youtube_horoscope/config.yaml`

По умолчанию уже настроен для гороскопов ✅

---

## 🗣️ Пример вывода workflow

```
======================================================================
🎬 HOROSCOPE VIDEO GENERATION PIPELINE
======================================================================
Project: youtube_horoscope
Format: shorts
Date: 2025-12-13

📝 PART 1: Script Generation
----------------------------------------------------------------------
✅ Script generated: output/scripts/youtube_horoscope/20251213/short_a1b2c3d4.json
   Format: shorts
   Date: 2025-12-13

🎙️ PART 2: TTS Synthesis (Gemini)
----------------------------------------------------------------------
✅ Audio synthesized
   Engine: gemini-2.5-tts
   Duration: 23.5s
   Sample rate: 22050 Hz
   Blocks:
     - main: output/audio/youtube_horoscope/shorts_main.wav (2.3MB)

🎥 PART 3: Video Rendering
----------------------------------------------------------------------
✅ Video rendered: output/videos/youtube_horoscope/shorts.mp4
   Size: 45.3 MB

======================================================================
✅ SUCCESS! Video generation complete
======================================================================
Project: youtube_horoscope
Format: shorts
Output: output/videos/youtube_horoscope/shorts.mp4
Size: 45.3 MB

Video is ready for:
  - YouTube Shorts (1080×1920)
  - TikTok / Instagram Reels

Next: Download from artifacts and publish to platforms
```

---

## 🚀 Как правильно запустить

### Опция 1: Вручно для Shorts

```bash
1. GitHub → Actions → Generate Horoscope Video
2. Run workflow
3. Format: shorts
4. Date: (empty = тодая)
5. Run workflow
```

### Опция 2: Вручно для Long-form

```bash
1. Format: long-form
2. Date: 2025-12-13
3. Run workflow
```

### Опция 3: Каждые день (втоматически)

```bash
# Каждый день в 06:00 UTC (09:00 MSK) для shorts:

cron: '0 6 * * *'  # (.github/workflows/generate-horoscope-video.yml)

# Отредактировать дату/наскаждение в .github/workflows/generate-horoscope-video.yml
```

---

## 📋 Ответы на главные вопросы

### ❔ "Как складывается видео?"

См. `docs/VIDEO_GENERATION_GUIDE.md` — там диаграммы, с нкы всю мозаику.

### ❔ "Как работает TTS?"

**Gemini 2.5 TTS API**:
- Ово вымос широка и более гнавым чем Edge-TTS
- Выдает MP3 → конвертируем в WAV (pydub)
- Каждый блок синтезируется отдельно

### ❔ "Как добавить свои промпты?"

На строке 49 workflow `tts_generator.synthesize()` всю инфо для TTS вытаскивается из `script` дикта.

Если модель не сделает это самом — эдить директно `core/generators/script_generator.py`.

---

## 📄 Полная документация

- **[VIDEO_GENERATION_GUIDE.md](docs/VIDEO_GENERATION_GUIDE.md)** — Полные диаграммы и объяснения
- **README.md** — Общая инфо проекта
- **.github/workflows/generate-horoscope-video.yml** — Обскрипция workflow

---

**Статус:** ✅ Ready to use  
**Версия:** 1.0  
**Дата:** 13 Дек 2025
