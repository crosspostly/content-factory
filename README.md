# 🎬 Content Factory - AI-Powered Multi-Platform Content Machine

> **Фабрика контента, работающая на GitHub Actions. Генерирует видео и контент для YouTube, TikTok, Instagram, VK с поддержкой Gemini API, Edge-TTS, стоками видео и масштабируемыми проектами.**

![Version](https://img.shields.io/badge/version-2.2-blue)
![Status](https://img.shields.io/badge/status-Part%202%20TTS%20%2B%20Video-yellowgreen)
![License](https://img.shields.io/badge/license-MIT-orange)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)

---

## 📚 START HERE

1. **[QUICK-START.md](./QUICK-START.md)** - 5 мин установка (все секреты и команды)
2. **[PART2_PART3_CRITICAL_TZ.md](./PART2_PART3_CRITICAL_TZ.md)** - Tech spec для AI агента (Part 2 + 3)

---

## 🚀 FULL SETUP & INSTALLATION

### Шаг 1: Clone & Install

```bash
# Clone repo
git clone https://github.com/crosspostly/content-factory.git
cd content-factory

# Create Python venv (опционально, но рекомендуется)
python3.11 -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Шаг 2: Setup GitHub Secrets

Перейти: https://github.com/crosspostly/content-factory/settings/secrets/actions

Добавить **5 секретов** (все обязательные для Part 2 + 3):

```bash
# Secret 1: Gemini API Key
Name: GOOGLE_AI_API_KEY
Value: <Получить с https://ai.google.dev>

# Secret 2: Fallback LLM (OpenRouter)
Name: OPENROUTER_API_KEY
Value: <Получить с https://openrouter.ai>

# Secret 3: Stock Videos API
Name: PIXABAY_API_KEY
Value: <Получить с https://pixabay.com/api>

# Secret 4: Telegram Bot для уведомлений
Name: TELEGRAM_BOT_TOKEN
Value: <Получить от @BotFather в Telegram>

# Secret 5: Telegram Chat для сообщений
Name: TELEGRAM_CHAT_ID
Value: <Получить от @userinfobot в Telegram>
```

### Шаг 3: Create .env File (локальное тестирование)

```bash
cp .env.example .env
```

Отредактировать `.env`:

```env
GOOGLE_AI_API_KEY=<your-gemini-key>
OPENROUTER_API_KEY=<your-openrouter-key>
PIXABAY_API_KEY=<your-pixabay-key>
TELEGRAM_BOT_TOKEN=<your-telegram-bot-token>
TELEGRAM_CHAT_ID=<your-telegram-chat-id>
```

---

## 📋 USAGE COMMANDS (Copy-Paste Ready)

### Part 1: Generate Scripts (WORKING ✅)

```bash
# Dry-run (no files created)
python -m core.orchestrators.pipeline_orchestrator \
  --project youtube_horoscope \
  --mode shorts \
  --dry-run

# Generate shorts scripts
python -m core.orchestrators.pipeline_orchestrator \
  --project youtube_horoscope \
  --mode shorts

# Generate long-form scripts  
python -m core.orchestrators.pipeline_orchestrator \
  --project youtube_horoscope \
  --mode long_form

# Generate ads scripts
python -m core.orchestrators.pipeline_orchestrator \
  --project youtube_horoscope \
  --mode ad
```

**Результат:** Scripts сохраняются в `output/scripts/youtube_horoscope/{date}/`

### Part 2: Test TTS Generator (IN PROGRESS 🔜)

```bash
# После реализации AI агентом:
python -c "
from core.generators.tts_generator import TTSGenerator
from core.utils.config_loader import load_project_config

config = load_project_config('youtube_horoscope')
tts = TTSGenerator(config)

# Simple test
result = tts.synthesize(
    text='Привет, это тест синтеза речи',
    output_file='test_audio.wav'
)
print('✅ Audio saved:', result['audio_path'])
print('⏱️  Duration:', result['duration_sec'], 'sec')
"
```

### Part 3: Test Video Renderer (IN PROGRESS 🔜)

```bash
# После реализации AI агентом:
python -c "
from core.generators.video_renderer import VideoRenderer
from core.utils.config_loader import load_project_config

config = load_project_config('youtube_horoscope')
renderer = VideoRenderer(config)

# Generate simple shorts
result = renderer.render_shorts(
    audio_path='test_audio.wav',
    script_data={'hook': 'Тестовое видео!'},
    output_path='test_shorts.mp4'
)
print('✅ Video saved:', result['video_path'])
print('📺 Resolution:', result['resolution'])
print('⏱️  Duration:', result['duration_sec'], 'sec')
"
```

---

## 📁 PROJECT STRUCTURE

```
content-factory/
├── core/
│   ├── generators/
│   │   ├── script_generator.py          ✅ DONE (Part 1)
│   │   ├── tts_generator.py             🔜 IN PROGRESS (Part 2)
│   │   └── video_renderer.py            🔜 IN PROGRESS (Part 3)
│   │
│   ├── orchestrators/
│   │   ├── __main__.py
│   │   └── pipeline_orchestrator.py     ✅ DONE (CLI interface)
│   │
│   └── utils/
│       ├── config_loader.py             ✅ (YAML parsing)
│       ├── model_router.py              ✅ (LLM selection)
│       ├── secrets_manager.py           ✅ (env handling)
│       └── yaml_loader.py               ✅ (stdlib YAML)
│
├── projects/
│   └── youtube_horoscope/
│       ├── config.yaml                  ✅ (Russian voice configured)
│       ├── prompts/
│       │   ├── shorts_scenario.txt      (Gemini prompt для shorts)
│       │   ├── long_form_scenario.txt   (Gemini prompt для long-form)
│       │   └── ad_script.txt            (Gemini prompt для ads)
│       └── content_plan.json            (Metadata)
│
├── .github/workflows/
│   └── part1-test.yml                   ✅ (GitHub Actions CI/CD)
│
├── requirements.txt                     (Dependencies)
├── .env.example                         (Environment template)
├── QUICK-START.md                       (5-min setup guide)
├── PART2_PART3_CRITICAL_TZ.md          (AI agent tech spec)
│
└── output/                              (Auto-created)
    ├── scripts/
    │   └── youtube_horoscope/
    │       └── 20251212/
    │           ├── short_a1b2c3d4.json
    │           ├── long_form_x9y8z7w6.json
    │           └── ad_p1q2r3s4.json
    │
    ├── audio/
    │   └── youtube_horoscope/
    │       ├── shorts_main.wav
    │       ├── long_form_love.wav
    │       ├── long_form_money.wav
    │       └── long_form_health.wav
    │
    ├── videos/
    │   └── youtube_horoscope/
    │       ├── shorts.mp4  (1080x1920, 30fps, H.264)
    │       ├── long_form.mp4 (1920x1080, 30fps, H.264)
    │       └── ad.mp4  (1080x1920, 30fps, H.264)
    │
    └── logs/
        └── youtube_horoscope/
            └── 20251212.log
```

---

## ⚙️ CONFIGURATION

### `projects/youtube_horoscope/config.yaml`

```yaml
project:
  name: youtube_horoscope
  language: Russian
  niche: astrology
  description: "Horoscope content for YouTube Shorts, Long-form, and Ads"

generation:
  primary_model: "gemini-2.5-flash"      # ✅ Актуальная модель Dec 2025
  fallback_models:
    - "gemini-2.5-flash-lite"            # Дешёвая альтернатива
    - "gemini-2.5-pro"                   # Умнее, медленнее
  temperature: 0.8                       # Творческость (0.0-1.0)
  max_retries: 3                         # Повторы при ошибке

audio:
  enabled: true
  engines:
    edge-tts:
      enabled: true
      voice: "ru-RU-DariyaNeural"        # Русский женский голос (бесплатный!)
      speed: 1.0                         # Скорость (0.5-2.0)
    gemini-tts:
      enabled: false

video:
  fps: 30                                # Frames per second
  codec: libx264                         # H.264 кодек
  audio_codec: aac                       # Audio codec
  quality: high                          # Качество (low/medium/high)
  
  shorts:                                # 9:16 вертикально
    width: 1080
    height: 1920
    preferred_source: pixabay_video      # Источник видео (pixabay/pexels/none)
    max_duration_sec: 60                 # Макс. длительность
  
  long_form:                             # 16:9 горизонтально
    width: 1920
    height: 1080
    preferred_source: pixabay_video
    max_duration_sec: 600                # 10 минут макс
  
  ad:                                    # 9:16 вертикально
    width: 1080
    height: 1920
    preferred_source: pixabay_video
    max_duration_sec: 60

subtitles:
  enabled: true
  font: Arial
  font_size: 24
  color: white                           # RGB
  shadow: true                           # Тень для читаемости

output:
  base_dir: "output"                     # Базовая папка для результатов
  keep_intermediates: false              # Сохранять временные файлы?
```

---

## 🧪 TESTING & DEBUGGING

### Check Script Generation

```bash
# Локально тестировать скрипт-генератор
ls -lah output/scripts/youtube_horoscope/
cat output/scripts/youtube_horoscope/*/short_*.json | head -50
```

### Check Logs

```bash
# Локально смотреть логи
ls -lah output/logs/youtube_horoscope/
tail -f output/logs/youtube_horoscope/$(date +%Y%m%d).log
```

### GitHub Actions Logs

```
1. https://github.com/crosspostly/content-factory/actions
2. Выбрать последний workflow run
3. Смотреть "Generate Content" job
4. Expand шаги для деталей ошибок
```

### Upload Artifacts from Actions

```bash
# Скачать результаты из GitHub Actions
# Artifacts автоматически сохраняются после каждого запуска
# Доступны в "Artifacts" секции каждого workflow run
```

---

## 📊 ROADMAP

```
┌─ Part 1: Foundation ✅ DONE
│  ├─ Config loader (stdlib YAML)
│  ├─ LLM routing (Gemini + fallbacks)
│  ├─ CLI orchestrator
│  ├─ Script generator + saving
│  └─ GitHub Actions workflow
│
├─ Part 2: TTS Implementation 🔜 IN PROGRESS
│  ├─ Edge-TTS integration (ru-RU-DariyaNeural)
│  ├─ WAV generation (22050 Hz, mono)
│  ├─ Audio block synthesis
│  └─ Duration validation
│
├─ Part 3: Video Rendering 🔜 NEXT
│  ├─ moviepy/ffmpeg integration
│  ├─ Pixabay video API
│  ├─ Text overlay + shadows
│  ├─ Shorts (1080x1920)
│  ├─ Long-form (1920x1080)
│  └─ Ad (1080x1920)
│
├─ Part 4: Platform Uploaders 🔮 FUTURE
│  ├─ YouTube API v3
│  ├─ TikTok API
│  ├─ VK API
│  └─ Instagram API
│
└─ Part 5: Scheduling & Automation 🔮 FUTURE
   ├─ Cron jobs
   ├─ GitHub Actions scheduler
   └─ Telegram bot control
```

---

## 🔐 API KEYS & SERVICES

| Сервис | Ключ | Где получить | Что нужно |
|--------|------|------------|----------|
| **Google Gemini** | `GOOGLE_AI_API_KEY` | [ai.google.dev](https://ai.google.dev) | API Key (бесплатно) |
| **Fallback LLM** | `OPENROUTER_API_KEY` | [openrouter.ai](https://openrouter.ai) | API Key (опционально) |
| **Stock Videos** | `PIXABAY_API_KEY` | [pixabay.com/api](https://pixabay.com/api) | API Key (бесплатно) |
| **Telegram Bot** | `TELEGRAM_BOT_TOKEN` | [@BotFather](https://t.me/BotFather) | /newbot → get token |
| **Telegram Chat** | `TELEGRAM_CHAT_ID` | [@userinfobot](https://t.me/userinfobot) | /start → get chat_id |

### Все остальное БЕСПЛАТНО:

- ✅ **Edge-TTS** - бесплатный синтез речи (Microsoft Azure)
- ✅ **moviepy** - бесплатная библиотека для видео
- ✅ **GitHub Actions** - бесплатные минуты для публичных репозиториев
- ✅ **Gemini API** - 60 запросов/мин бесплатно

---

## 🎯 GOOGLE GEMINI MODELS (Dec 2025 - ACTUAL)

| Модель | Код | Статус | Используется для |
|--------|------|--------|------------------|
| **Gemini 2.5 Flash** | `gemini-2.5-flash` | ✅ ACTIVE | **РЕКОМЕНДУЕТСЯ** - баланс скорости и качества |
| Gemini 2.5 Flash-Lite | `gemini-2.5-flash-lite` | ✅ ACTIVE | Дешевле, для простых задач |
| Gemini 2.5 Pro | `gemini-2.5-pro` | ✅ ACTIVE | Медленнее, но умнее |
| Gemini 3 Pro Preview | `gemini-3-pro-preview` | ⚠️ PREVIEW | Новейшая (ограниченный доступ) |

### ❌ DEPRECATED (НЕ РАБОТАЮТ):

- ❌ `gemini-2.0-flash` - shutdown Feb 2026
- ❌ `gemini-1.5-flash` - retired April 2025
- ❌ `gemini-1.5-pro` - retired April 2025
- ❌ `gemini-exp-1206` - никогда не существовала
- ❌ `gemini-2.0-flash-exp` - удалена из API

**Источник:** https://ai.google.dev/gemini-api/docs/models

---

## 📱 WORKFLOW FILES & SCRIPTS

### GitHub Actions Workflow

Файл: `.github/workflows/part1-test.yml`

```yaml
name: Generate Content (Part 1 MVP)

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  workflow_dispatch:  # Manual trigger

jobs:
  generate-content:
    runs-on: ubuntu-24.04
    
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'  # ← КЕШИРОВАНИЕ!
      
      - name: Install system dependencies
        run: |
          sudo apt-get update -qq
          sudo apt-get install -y ffmpeg imagemagick
      
      - name: Install Python dependencies
        run: |
          pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: Generate content (Part 1)
        env:
          GOOGLE_AI_API_KEY: ${{ secrets.GOOGLE_AI_API_KEY }}
          OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}
          PIXABAY_API_KEY: ${{ secrets.PIXABAY_API_KEY }}
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
        run: |
          python -m core.orchestrators.pipeline_orchestrator \
            --project youtube_horoscope \
            --mode shorts
      
      - name: Upload artifacts
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: content-factory-output
          path: |
            output/
            logs/
          retention-days: 30
```

---

## 🔗 LINKS & RESOURCES

- **Google AI Studio:** https://ai.google.dev
- **Gemini Models Docs:** https://ai.google.dev/gemini-api/docs/models
- **Gemini Deprecations:** https://ai.google.dev/gemini-api/docs/deprecations
- **Edge-TTS GitHub:** https://github.com/rany2/edge-tts
- **moviepy Docs:** https://zulko.github.io/moviepy
- **Pixabay API:** https://pixabay.com/api/documentation
- **Pexels API:** https://www.pexels.com/api

---

## 💬 TROUBLESHOOTING

### Gemini API 401/403 Error

```bash
# Проверить ключ
echo $GOOGLE_AI_API_KEY

# Переполучить с https://ai.google.dev
# Убедиться что key скопирован БЕЗ пробелов
```

### ffmpeg not found

```bash
# Linux/Ubuntu
sudo apt-get install -y ffmpeg imagemagick

# macOS
brew install ffmpeg imagemagick

# Windows - скачать с https://ffmpeg.org/download.html
```

### Python venv issues

```bash
# Пересоздать venv
rm -rf venv
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### GitHub Actions timeout

```yaml
# Увеличить timeout в .github/workflows/part1-test.yml
jobs:
  generate-content:
    runs-on: ubuntu-24.04
    timeout-minutes: 30  # ← Добавить
```

---

## 📞 SUPPORT

- **Ошибка?** Смотри логи: `output/logs/youtube_horoscope/`
- **Вопрос?** Открой Issue
- **PR?** Добро пожаловать! 🚀

---

**Status:** 🔜 Part 2 TTS + Part 3 Video In Progress
**Last Updated:** Dec 12, 2025 (All processes, workflows, and configs restored)
