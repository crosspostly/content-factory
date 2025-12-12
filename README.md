# 🎬 Content Factory - AI-Powered Multi-Platform Content Machine

> **Полностью автоматизированная фабрика контента, работающая в GitHub Actions. Генерирует видео для YouTube, TikTok, Instagram, VK и управляется через Telegram Bot.**

![Version](https://img.shields.io/badge/version-2.1-blue)
![Status](https://img.shields.io/badge/status-active-green)
![License](https://img.shields.io/badge/license-MIT-orange)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)

---

## 📋 Содержание

- [О Проекте](#о-проекте)
- [Ключевые Возможности](#ключевые-возможности)
- [Архитектура](#архитектура)
- [Технологический Стек](#технологический-стек)
- [Установка](#установка)
- [Структура Проекта](#структура-проекта)
- [Использование](#использование)
- [Оптимизация и Кэширование](#оптимизация-и-кэширование)
- [Лимиты GitHub Actions](#лимиты-github-actions)
- [Решение Проблем](#решение-проблем)
- [Внесение Вклада](#внесение-вклада)

---

## О Проекте

**Content Factory** — это масштабируемая, полностью автоматизированная система для генерации, производства и публикации видео-контента. Проект спроектирован для работы исключительно в GitHub Actions без необходимости в выделенном сервере.

### Идеология

- 🎯 **Проект-ориентированная архитектура** — каждый канал/бот = отдельная папка с конфигом
- 🔄 **Переиспользование кода** — общие модули в `core/` используются всеми проектами
- ⚡ **Оптимизация** — агрессивное кэширование экономит 8+ минут на видео
- 🤖 **Управление из Telegram** — пульт управления прямо в мессенджере
- 📊 **Параллельная генерация** — асинхронное выполнение задач

---

## Ключевые Возможности

### 🎬 Генерация Контента

- ✅ **Сценарии** — Gemini 2.5 / Ollama (Gemma 3, Qwen) / OpenRouter
- ✅ **Озвучка** — Edge-TTS (естественная речь), Coqui XTTS (клонирование голоса)
- ✅ **Субтитры** — WhisperX (word-level timestamps), автосинхронизация (ffsubsync)
- ✅ **Визуал** — Manim (математика), Remotion (React-видео), MoviePy (монтаж)
- ✅ **Изображения** — Stock (Pexels/Pixabay), Flux.1 (генерация), ImageMagick (обложки)

### 📤 Публикация

- ✅ **YouTube** — автоматическая загрузка, плейлисты, расписание
- ✅ **TikTok** — API / браузер-бот
- ✅ **Instagram** — автоматизация
- ✅ **VK** — API интеграция
- ✅ **Telegram** — распространение готовых видео

### 🎮 Управление

- ✅ **Telegram Bot** — пульт управления (запуск, статус, отмена)
- ✅ **GitHub Actions** — расписание, ручной запуск, webhook'и
- ✅ **Config-driven** — все настройки в YAML (ноль кода для нового проекта)
- ✅ **Очередь задач** — приоритизация проектов

### ⚡ Оптимизация

- ✅ **Кэширование** — pip, Ollama модели, Docker слои, npm
- ✅ **Result caching** — переиспользование скриптов и видео
- ✅ **Параллелизм** — одновременная генерация аудио, субтитров, визуала
- ✅ **Экономия времени** — 14 мин → 5.5 мин за видео

---

## Архитектура

```
┌──────────────────────────────────────────────────────────────────────┐
│                    GitHub Actions Trigger                            │
│    (Расписание + Вручную + Telegram Bot Webhook)                    │
└────────────────┬──────────────────────────────────────────────────────┘
                 │
                 ▼ [⚡ АГРЕССИВНОЕ КЭШИРОВАНИЕ ⚡]
                 │
        ┌─────────────────────────────────────────────────┐
        │  1. СЦЕНАРИЙ + ТАЙМЛАЙН JSON                   │
        │  (Структурированный скрипт)                    │
        │  Gemma 3 / Qwen / Gemini / GPT                 │
        │  ⏱️ 1-2 мин                                    │
        └────────┬────────────────────────────────────────┘
                 │
        ┌────────▼──────────────────────────────┐
        │  2. ОЗВУЧКА (параллельно)             │
        │  ├─ Edge-TTS (основная)               │
        │  └─ Coqui XTTS (эмоциональная)       │
        │  Output: segment_*.mp3                 │
        │  ⏱️ 2-3 мин                           │
        └────────┬──────────────────────────────┘
                 │
        ┌────────▼──────────────────────────────────┐
        │  3. СУБТИТРЫ (параллельно)                │
        │  ├─ WhisperX (word-level timestamps)     │
        │  ├─ ffsubsync (автосинхронизация)        │
        │  └─ Output: subtitles.srt                 │
        │  ⏱️ 2-3 мин                               │
        └────────┬───────────────────────────────────┘
                 │
        ┌────────▼──────────────────────────────┐
        │  4. ВИЗУАЛЬНЫЙ КОНТЕНТ                │
        │  (параллельно на 4+ workers)          │
        │  ├─ Manim анимация                    │
        │  ├─ Remotion (React видео)            │
        │  ├─ MoviePy (Python монтаж)           │
        │  ├─ Flux.1 (картинки)                 │
        │  ├─ Stock (Pexels/Pixabay)            │
        │  ├─ ImageMagick (обложки)             │
        │  └─ Gemini Vision анализ              │
        │  ⏱️ 5-15 мин                          │
        └────────┬───────────────────────────────┘
                 │
        ┌────────▼──────────────────────────────┐
        │  5. МОНТАЖ (FFmpeg + MoviePy)         │
        │  ├─ video.mp4 (основное видео)        │
        │  ├─ subtitles.srt (встроенные)        │
        │  ├─ thumbnail.jpg (обложка)           │
        │  └─ metadata.json (для платформ)      │
        │  ⏱️ 2-5 мин                           │
        └────────┬───────────────────────────────┘
                 │
        ┌────────▼──────────────────────────────────┐
        │  6. ПУБЛИКАЦИЯ (параллельно)              │
        │  ├─ YouTube (через API)                   │
        │  ├─ TikTok (через bot/API)                │
        │  ├─ Instagram (через bot)                 │
        │  └─ VK (через API)                        │
        │  + Telegram bot (уведомления)             │
        │  ⏱️ 5-15 мин                              │
        └──────────────────────────────────────────┘
```

---

## Технологический Стек

### 🤖 AI Модели (Бесплатные)

| Задача | Модель | Платформа | Лимиты |
|--------|--------|-----------|--------|
| **Генерация сценариев** | Gemma 3 4B + Qwen 2.5 72B | GitHub Actions + Ollama | ∞ |
| **Резервный сценарий** | DeepSeek R1 :free | OpenRouter | 50/день |
| **Анализ картинок** | Gemini 2.5 Flash | Google AI Studio | 15 RPM |
| **Видео-анализ** | Claude 3.5 Sonnet | via Portkey | Зависит от плана |

### 🔊 Аудио

| Инструмент | Назначение | Цена |
|-----------|-----------|------|
| **Edge-TTS** | Синтез речи (естественный) | Бесплатно |
| **Coqui XTTS** | Клонирование голоса | Бесплатно |
| **Pydub** | Монтаж аудио | Бесплатно |
| **ffsubsync** | Синхронизация субтитров | Бесплатно |

### 🎬 Видео & Анимация

| Инструмент | Назначение | Работает в GA |
|-----------|-----------|---------------|
| **Manim** | Математическая анимация | ✅ Docker |
| **Remotion** | React-видео (HTML/CSS) | ✅ npm |
| **MoviePy** | Python-монтаж | ✅ pip |
| **FFmpeg** | Конвертация/монтаж | ✅ Встроено |
| **OpenCV** | Обработка картинок | ✅ pip |
| **ImageMagick** | Обложки/текст | ✅ apt |

---

## Структура Проекта

```
content-factory/
│
├── 📁 projects/                          # Проекты (каналы/боты)
│   ├── youtube_podcast/
│   │   ├── config.yaml                  # Конфигурация проекта
│   │   ├── prompts/                     # Кастомные промпты
│   │   │   ├── scenario.txt
│   │   │   ├── video_hints.txt
│   │   │   └── seo_keywords.txt
│   │   ├── workflows/                   # Проект-специфичный workflow
│   │   │   └── generate.yml
│   │   ├── requirements.txt              # Опциональные зависимости
│   │   └── content_plan.json             # План контента
│   │
│   ├── tiktok_shorts/
│   │   ├── config.yaml
│   │   ├── prompts/
│   │   └── content_plan.json
│   │
│   └── telegram_bot/
│       ├── config.yaml
│       ├── handlers/
│       └── templates/
│
├── 📁 core/                              # Общие модули (оркестраторы)
│   ├── generators/
│   │   ├── script_generator.py          # Генерация сценариев
│   │   ├── audio_generator.py           # TTS
│   │   ├── subtitle_generator.py        # WhisperX
│   │   ├── video_generator.py           # Manim/MoviePy/Remotion
│   │   └── image_generator.py           # Stock/Flux
│   │
│   ├── orchestrators/
│   │   ├── pipeline_orchestrator.py     # Главный оркестратор
│   │   ├── cache_manager.py             # Управление кэшем
│   │   ├── retry_manager.py             # Переитримы и ошибки
│   │   └── event_logger.py              # Логирование для Telegram
│   │
│   ├── uploaders/
│   │   ├── youtube_uploader.py
│   │   ├── tiktok_uploader.py
│   │   ├── instagram_uploader.py
│   │   └── vk_uploader.py
│   │
│   ├── utils/
│   │   ├── config_loader.py             # Загрузка конфигов
│   │   ├── secrets_manager.py           # GitHub Secrets
│   │   ├── api_router.py                # Балансирование ключей
│   │   └── notification_sender.py       # Telegram уведомления
│   │
│   └── models/
│       ├── config_schema.py             # Pydantic-модели
│       └── enums.py                     # Enum'ы
│
├── 📁 .github/
│   ├── workflows/
│   │   ├── generate-video.yml           # Основной workflow
│   │   ├── bulk-generate.yml            # Массовая генерация
│   │   ├── retry-failed.yml             # Переитримы
│   │   └── cleanup.yml                  # Уборка кэша
│   │
│   └── scripts/
│       └── setup_cache.sh               # Инициализация
│
├── 📄 main.py                           # Entry point
├── 📄 requirements.txt                  # Глобальные зависимости
├── 📄 .env.example                      # Шаблон переменных
└── 📄 README.md                         # Этот файл
```

---

## Установка

### Требования

- Python 3.11+
- Git
- GitHub Account (для использования Actions)
- API ключи (Google, OpenAI/DeepSeek — опционально)

### Шаг 1: Клонирование

```bash
git clone https://github.com/crosspostly/content-factory.git
cd content-factory
```

### Шаг 2: Установка Зависимостей

```bash
python3.11 -m venv venv
source venv/bin/activate  # Linux/macOS
# или
venv\\Scripts\\activate  # Windows

pip install -r requirements.txt
```

### Шаг 3: Настройка Переменных

```bash
cp .env.example .env
nano .env
```

Требуемые переменные:

```env
# YouTube API
YOUTUBE_API_KEY=your_key_here
YOUTUBE_CLIENT_ID=your_client_id
YOUTUBE_CLIENT_SECRET=your_secret

# Google AI (для Gemini)
GOOGLE_API_KEY=your_key_here

# OpenAI/DeepSeek (опционально)
OPENAI_API_KEY=your_key_here
OPENROUTER_API_KEY=your_key_here

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id

# GitHub
GITHUB_TOKEN=ghp_your_token_here
GITHUB_REPO=crosspostly/content-factory

# Ollama
OLLAMA_MODEL=gemma3:4b
```

### Шаг 4: GitHub Secrets

1. Settings → Secrets and variables → Actions
2. Добавьте все переменные из `.env` как GitHub Secrets
3. Пример для `YOUTUBE_API_KEY`:
   - Name: `YOUTUBE_API_KEY`
   - Value: `your_actual_key`

### Шаг 5: Первый Запуск (Локальный)

```bash
# Тестируем генерацию сценария
python3 main.py --project youtube_podcast --mode generate-script

# Тестируем озвучку
python3 main.py --project youtube_podcast --mode generate-audio

# Полный pipeline
python3 main.py --project youtube_podcast --mode full
```

### Шаг 6: Запуск в GitHub Actions

1. Actions → Generate Video
2. Run workflow
3. Выберите проект: `youtube_podcast`
4. Run workflow

---

## Использование

### 🚀 Запуск из CLI

```bash
# Генерация скрипта
python3 main.py --project youtube_podcast --mode generate-script

# Генерация аудио
python3 main.py --project youtube_podcast --mode generate-audio

# Генерация субтитров
python3 main.py --project youtube_podcast --mode generate-subtitles

# Генерация визуала
python3 main.py --project youtube_podcast --mode generate-video

# Монтаж
python3 main.py --project youtube_podcast --mode assemble

# Загрузка
python3 main.py --project youtube_podcast --mode upload

# ВСЕ в одном
python3 main.py --project youtube_podcast --mode full

# С параметрами
python3 main.py --project youtube_podcast --mode full --force-rerender --skip-upload
```

### 🤖 Управление через Telegram Bot

```
/start                           # Запуск бота
/generate youtube_podcast        # Запустить генерацию
/status                          # Статус всех проектов
/list                            # Список доступных проектов
/cancel <workflow_id>            # Отменить запуск
/cache_status                    # Статус кэша
/help                            # Справка
```

### 📅 Автоматическое Расписание

Отредактируйте `.github/workflows/bulk-generate.yml`:

```yaml
on:
  schedule:
    - cron: '0 10 * * *'         # Каждый день в 10:00
    - cron: '0 18 * * 1,3,5'     # Пн, Ср, Пт в 18:00
```

---

## Оптимизация и Кэширование

### ⚡ Уровни Кэширования

#### 1️⃣ PIP Cache (Python зависимости)

```yaml
- name: Setup Python
  uses: actions/setup-python@v4
  with:
    python-version: '3.11'
    cache: 'pip'  # ← Волшебная строка!
```

**Экономия:** 90 сек → 10 сек

#### 2️⃣ Ollama Models Cache (AI модели)

```yaml
- name: Cache Ollama
  uses: actions/cache@v4
  with:
    path: ~/.ollama/models
    key: ollama-${{ runner.os }}-gemma3-v1
    restore-keys: ollama-${{ runner.os }}-
```

**Экономия:** 180 сек → 3 сек

#### 3️⃣ Docker Layer Cache

```yaml
- uses: docker/build-push-action@v5
  with:
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

**Экономия:** 240 сек → 20 сек

#### 4️⃣ NPM Cache (Remotion)

```yaml
- name: Setup Node
  uses: actions/setup-node@v4
  with:
    node-version: '18'
    cache: 'npm'
```

**Экономия:** 45 сек → 3 сек

### 📊 Итоговая Экономия

| Сценарий | Без Кэша | С Кэшем | Экономия |
|----------|----------|---------|----------|
| **1 видео/неделя** | 14 мин | 5.5 мин | 8.5 мин |
| **4 видео/месяц** | 56 мин | 22 мин | 34 мин |
| **ежедневно (30/месяц)** | 420 мин | 165 мин | **255 мин (4.25 часов!)** |

---

## Лимиты GitHub Actions

### Free Plan (Приватный репо)

| Параметр | Лимит | Рекомендация |
|----------|-------|--------------|
| **Минуты/месяц** | **2,000 мин** | Хватает на 30-40 видео |
| **Storage** | **500 MB** | Используйте S3 для больших файлов |
| **Concurrent jobs** | **20 (Linux)** | Запускайте 2-3 параллельно |
| **Job timeout** | **6 часов** | Хватит даже для сложного видео |

### Pro Plan

| Параметр | Лимит |
|----------|-------|
| **Минуты/месяц** | 3,000 мин |
| **Storage** | 1 GB |
| **Concurrent** | 40 (Linux) |

### 💡 Совет по Оптимизации Лимитов

**Публичный репозиторий = НЕОГРАНИЧЕННЫЕ минуты!**

Если не боитесь видимости кода → создайте публичный репо и получите бесплатные минуты без ограничений.

---

## Решение Проблем

### ❌ Проблема: "Workflow заканчивается через 6 часов"

**Причина:** GitHub Actions job timeout = 6 часов

**Решение:**
- Разделите видео на части (генерируйте несколько коротких вместо одного длинного)
- Используйте параллельные jobs
- Кэшируйте еще более агрессивно

### ❌ Проблема: "Кэш не восстанавливается"

**Причина:** Хеш зависимостей изменился

**Решение:**
```bash
gh actions-cache list -R crosspostly/content-factory
gh actions-cache delete-all -R crosspostly/content-factory
```

### ❌ Проблема: "Ollama модель скачивается очень долго"

**Причина:** Первый раз скачивается полная модель (~5GB)

**Решение:**
- Используйте меньшую модель (`gemma3:2b` вместо `gemma3:7b`)
- Или используйте публичный репо (неограниченный кэш)
- Или кэшируйте в S3

### ❌ Проблема: "GitHub Actions минуты закончились"

**Причина:** Free plan = 2,000 мин/месяц

**Решение:**
- Используйте публичный репо (неограниченные минуты!)
- Или оптимизируйте кэширование еще больше
- Или используйте Self-hosted runner (ваш сервер)

### ❌ Проблема: "Видео генерируется очень долго"

**Причина:** Рендеринг Manim/Remotion медленный

**Решение:**
```yaml
# В config.yaml используйте более легкий стиль
video:
  style: "moviepy"  # Быстрее чем Manim
  quality: "medium"  # Вместо "high"
```

### ❌ Проблема: "Субтитры не синхронизируются"

**Причина:** ffsubsync плохо подогнал таймкоды

**Решение:**
```python
# core/generators/subtitle_generator.py
engine = "whisperx"  # Точнее на word-level
```

---

## Расширение на Новые Платформы

### Создание Нового Проекта (Например, Instagram)

#### Шаг 1: Создайте Папку

```bash
mkdir projects/instagram_reels
```

#### Шаг 2: Создайте `config.yaml`

```yaml
# projects/instagram_reels/config.yaml

name: Instagram Reels
platform: instagram
priority: 2

generation:
  model: "gemma3:4b"
  prompt_file: "prompts/scenario.txt"
  
audio:
  engine: "edge-tts"
  voice: "ru-RU-DariyaNeural"

video:
  style: "remotion"
  resolution: "1080x1920"  # Вертикальное видео!
  duration: "30-60sec"

upload:
  platform: "instagram"
  hashtags: ["reels", "AI", "tech"]
```

#### Шаг 3: Готово!

```bash
python3 main.py --project instagram_reels --mode full
```

---

## Примеры Конфигураций

### 📺 YouTube Podcast

```yaml
# projects/youtube_podcast/config.yaml

name: YouTube Podcast
platform: youtube
priority: 1

generation:
  model: "gemma3:4b"
  temperature: 0.7

audio:
  engine: "edge-tts"
  voice: "ru-RU-DariyaNeural"

video:
  style: "manim"
  resolution: "1920x1080"
  duration: "10-15min"

upload:
  platform: "youtube"
  playlist_id: "PLxxxxx"
  tags: ["podcast", "educational", "AI"]
```

### 🎵 TikTok Shorts

```yaml
# projects/tiktok_shorts/config.yaml

name: TikTok Shorts
platform: tiktok
priority: 2

generation:
  model: "qwen:72b"
  temperature: 0.9

audio:
  engine: "coqui-xtts"
  voice: "sample.wav"

video:
  style: "remotion"
  resolution: "1080x1920"
  duration: "15-60sec"

upload:
  platform: "tiktok"
  draft: false
```

---

## Внесение Вклада

Приветствуются PR для:

- ✅ Новые платформы (YouTube Shorts, Bluesky, Mastodon)
- ✅ Улучшение качества генерации
- ✅ Оптимизация производительности
- ✅ Документация
- ✅ Исправление багов

### Процесс

1. Fork репо
2. Создайте ветку: `git checkout -b feature/awesome-feature`
3. Commit: `git commit -am 'Add awesome feature'`
4. Push: `git push origin feature/awesome-feature`
5. Откройте Pull Request

---

## Лицензия

MIT License — см. [LICENSE](LICENSE)

---

## Контакты и Ссылки

- 👤 GitHub: [@crosspostly](https://github.com/crosspostly)
- 📧 Email: [contact@example.com](mailto:contact@example.com)
- 💬 Telegram: [@yourprofile](https://t.me/yourprofile)

---

## Благодарности

Проект построен на базе:

- [Gemini API](https://ai.google.dev/)
- [OpenAI Whisper](https://github.com/openai/whisper)
- [Manim Community](https://www.manim.community/)
- [FFmpeg](https://ffmpeg.org/)
- [Edge-TTS](https://github.com/rany2/edge-tts)
- [Remotion](https://www.remotion.dev/)

---

**Версия:** 2.1  
**Последнее обновление:** Декабрь 2025  
**Статус:** 🟢 В активной разработке

---

<div align="center">

**Made with ❤️ by AI Video Factory**

[⭐ Поставьте звезду, если нравится!](https://github.com/crosspostly/content-factory)

</div>
