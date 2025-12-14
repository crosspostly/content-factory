# 🎬 Content Factory - AI-Powered Multi-Platform Content Machine

> **Полностью автоматизированная фабрика контента, работающая в GitHub Actions. Генерирует видео для YouTube, TikTok, Instagram, VK и управляется через Telegram Bot.**

![Version](https://img.shields.io/badge/version-2.2-blue)
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
- [GitHub Workflows (Как всё работает)](#github-workflows-как-всё-работает)
- [Part 1: Script Generation (✅ DONE)](#part-1-script-generation-done)
- [Part 2: TTS + Audio (✅ DONE)](#part-2-tts--audio-done)
- [Part 3: Video Rendering (✅ DONE)](#part-3-video-rendering-done)
- [Auto-Fix Agent (🤖 AI-POWERED)](#auto-fix-agent--ai-powered)
- [Testing (✅ DONE)](#testing)
- [**⚡ Оптимизация и Кэширование (NEW!)](#-оптимизация-и-кэширование)
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
- 🤖 **Управление из Telegram** — пульт управления прямо в мессенжере
- 📋 **Параллельная генерация** — асинхронное выполнение задач
- 🔧 **Auto-Fix Agent** — AI-powered исправление ошибок (Gemini + Qwen)

---

## 🎯 Ключевые Возможности

### 🎬 Генерация Контента

- ✅ **Сценарии** — Gemini 2.5 Flash / Qwen (локально) / OpenRouter (Part 1 ✅)
- ✅ **Озвучка** — Gemini 2.5 Flash TTS (высокое качество русской речи) (Part 2 ✅)
- ✅ **Видео** — MoviePy (монтаж), Pixabay API (стоки), FFmpeg (кодирование) (Part 3 ✅)
- 🔄 **Субтитры** — WhisperX (word-level timestamps), автосинхронизация (ffsubsync) (Part 4 🔄)
- 🔮 **Изображения** — Stock (Pexels/Pixabay), Flux.1 (генерация), ImageMagick (обложки) (Part 4 🔮)

### 📤 Публикация

- 🔮 **YouTube** — автоматическая загрузка, плейлисты, расписание
- 🔮 **TikTok** — API / браузер-бот
- 🔮 **Instagram** — автоматизация
- 🔮 **VK** — API интеграция
- 🔮 **Telegram** — распространение готовых видео

### 🎮 Управление

- ✅ **GitHub Actions** — расписание, ручной запуск, webhook'u
- ✅ **Config-driven** — все настройки в YAML (нуль кода для нового проекта)
- 🤖 **Auto-Fix Agent** — AI-powered исправление ошибок
- 🔮 **Telegram Bot** — пульт управления (запуск, статус, отмена)
- 🔮 **Очередь задач** — приоритизация проектов

### ⚡ Оптимизация

- ✅ **Кэширование** — pip, Ollama модели, Docker слои, npm
- ✅ **Result caching** — переиспользование скриптов и видео
- ✅ **Параллелизм** — одновременная генерация аудио, субтитров, визуала
- ✅ **Экономия времени** — 14 мин → 5.5 мин за видео

---

## 🏠 Архитектура

```
┌──────────────────────────────────────────────────────────────────┐
│                    GitHub Actions Trigger                            │
│    (Расписание + Вручную + Telegram Bot Webhook)                    │
└──────────────────────────────────────────────────────────────────┘
                 │
                 ▼ [⚡ АГРЕССИВНОЕ КШИРОВАНИЕ ⚡]
                 │
        ┌──────────────────────────────────────────────────┐
        │  1️⃣ СЦЕНАРИЙ (Part 1 ✅)                        │
        │  Структурированный JSON с таймлайном           │
        │  Gemini 2.5 Flash / Qwen / OpenRouter          │
        │  ⏱️ 1-2 мин                                    │
        └──────────────────────────────────────────────────┘
                 │
        ┌──────────────────────────────────────────────────┐
        │  2️⃣ ОЗВУЧКА (Part 2 ✅)                 │
        │  ├─ Gemini 2.5 Flash TTS (основная)  │
        │  ├─ Высокое качество руссской речи  │
        │  └─ Output: segment_*.wav (22050 Hz)  │
        │  ⏱️ 2-3 мин                           │
        └──────────────────────────────────────────────────┘
                 │
        ┌──────────────────────────────────────────────────┐
        │  3️⃣ ВИДЕО РЕНДЕРИНГ (Part 3 ✅)           │
        │  ├─ MoviePy (основной монтаж)            │
        │  ├─ Pixabay API (стоки)                  │
        │  ├─ FFmpeg (кодирование H.264)          │
        │  ├─ Субтитры (встроенные SRT)           │
        │  └─ Output: video.mp4 (1080x1920, 30fps) │
        │  ⏱️ 5-10 мин                              │
        └──────────────────────────────────────────────────┘
                 │
        ┌──────────────────────────────────────────────────┐
        │  4️⃣ МЕТАДАННЫЕ + ОБЛОЖКИ              │
        │  ├─ Thumbnail (ImageMagick)           │
        │  ├─ metadata.json (для платформ)      │
        │  └─ description (Gemini)               │
        │  ⏱️ 1-2 мин                           │
        └──────────────────────────────────────────────────┘
                 │
        ┌──────────────────────────────────────────────────┐
        │  5️⃣ ПУБЛИКАЦИЯ (Part 4 🔮)               │
        │  ├─ YouTube (API)                        │
        │  ├─ TikTok (bot/API)                     │
        │  ├─ Instagram (bot)                      │
        │  ├─ VK (API)                             │
        │  └─ Telegram (уведомления)               │
        │  ⏱️ 5-15 мин                              │
        └──────────────────────────────────────────────────┘

                     ⚠️ WORKFLOW FAILS ⚠️
                            │
                            ▼
        ┌──────────────────────────────────────────────────┐
        │  🤖 AUTO-FIX AGENT                   │
        │  ├─ Анализирует логи ошибок         │
        │  ├─ Gemini/Qwen (выбор)              │
        │  ├─ Предлагает решение               │
        │  ├─ Создаёт GitHub Issue             │
        │  └─ (Опционально) PR с исправлением │
        └──────────────────────────────────────────────────┘
```

---

## 🚀 Технологический Стек

### 🤖 AI Модели (Бесплатные)

| Задача | Модель | Платформа | Статус |
|--------|--------|-----------|--------|
| **Генерация сценариев** | Gemini 2.5 Flash | Google AI Studio | ✅ Part 1 |
| **Резервный сценарий** | Qwen 2.5 (1.5B) | Ollama (локально) | ✅ Part 1 |
| **TTS (озвучка)** | Gemini 2.5 Flash TTS | Google AI Studio | ✅ Part 2 |
| **Анализ ошибок** | Gemini 2.5 Flash / Qwen | Auto-Fix Agent | 🤖 Active |
| **Анализ картинок** | Gemini 2.5 Flash | Google AI Studio | 🔮 Part 4 |

### 🔊 Аудио (Part 2)

| Инструмент | Назначение | Статус |
|-----------|-----------|--------|
| **Gemini 2.5 Flash TTS** | Синтез речи высокого качества | ✅ Part 2 |
| **Coqui XTTS** | Клонирование голоса | 🔮 Future |
| **Pydub** | Монтаж аудио | ✅ Part 2 |

### 🎬 Видео & Анимация (Part 3)

| Инструмент | Назначение | Статус |
|-----------|-----------|--------|
| **MoviePy** | Python-монтаж видео | ✅ Part 3 |
| **FFmpeg** | Конвертация/кодирование | ✅ Part 3 |
| **Pixabay API** | Стоки видео | ✅ Part 3 |
| **ImageMagick** | Обложки/текст | ✅ Part 3 |

---

## 📊 Структура Проекта

```
content-factory/
│
├── 📁 projects/
│   ├── youtube_horoscope/
│   │   ├── config.yaml                   # ✅ Project config
│   │   ├── prompts/
│   │   │   ├── shorts_scenario.txt       # Для shorts (Part 1)
│   │   │   ├── long_form_scenario.txt    # Для long-form (Part 1)
│   │   │   └── ad_script.txt             # Для ads (Part 1)
│   │   ├── content_plan.json             # ✅ Metadata
│   │   └── workflows/ (опционально)
│   │
│   └── [другие проекты...]
│
├── 📁 core/                              # Общие модули
│   ├── generators/
│   │   ├── script_generator.py           # ✅ Part 1: Генерация сценариев
│   │   ├── tts_generator.py              # ✅ Part 2: Озвучка (Gemini 2.5 TTS)
│   │   ├── video_renderer.py             # ✅ Part 3: Видео (MoviePy)
│   │   └── audio_utils.py                # ✅ Part 2/3: Помощники аудио
│   │
│   ├── orchestrators/
│   │   ├── pipeline_orchestrator.py      # ✅ Главный оркестратор
│   │   ├── cache_manager.py              # ✅ Управление кэшем
│   │   └── retry_manager.py              # ✅ Переитримы
│   │
│   ├── uploaders/
│   │   ├── youtube_uploader.py           # 🔮 Part 4
│   │   ├── tiktok_uploader.py            # 🔮 Part 4
│   │   └── vk_uploader.py                # 🔮 Part 4
│   │
│   ├── utils/
│   │   ├── config_loader.py              # ✅ Загружение YAML конфигов
│   │   ├── secrets_manager.py            # ✅ GitHub Secrets
│   │   ├── model_router.py               # ✅ LLM балансирование (Gemini/Qwen)
│   │   └── notification_sender.py        # 🔮 Telegram уведомления
│   │
│   └── models/
│       ├── config_schema.py              # ✅ Pydantic модели
│       └── enums.py                     # ✅ Enum'ы
│
├── 📁 .github/
│   └── workflows/
│       ├── auto-fix-agent.yml            # 🤖 Auto-Fix с Gemini/Qwen
│       ├── tests.yml                     # ✅ GitHub Actions для Part 1 (ОПТИМИЗИРОВАНО!)
│       └── generate-batch.yml            # ✅ GitHub Actions (ОПТИМИЗИРОВАНО!)
│
├── 📄 requirements.txt               # ✅ Все зависимости
├── 📄 .env.example                   # ✅ Шаблон переменных
├── 📄 Dockerfile                      # ⚡ ОПТИМИЗИРОВАН!
├── 📄 QUICK-START.md                 # ✅ 5-мин гайд
├── 📄 AI_AGENT_TECHNICAL_BRIEF.md   # 🤖 Полное ТЗ для ИИ (НОВО!)
├── 📄 INSTALLATION_OPTIMIZATION.md  # ⚡ Гайд оптимизации
└── 📄 README.md                      # ✅ Вы ЗДЕСЬ

```

---

## 📢 Установка

### Требования

- Python 3.11+
- Git
- GitHub Account (для использования Actions)
- API ключи (Google, Pixabay — обязательные)

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

pip install --prefer-binary -r requirements.txt
```

### Шаг 3: Настройка Переменных

```bash
cp .env.example .env
nano .env
```

Обязательные переменные:

```env
# Google Gemini (Part 1 + Part 2 TTS)
GOOGLE_AI_API_KEY=your_key_from_ai.google.dev

# Stock Videos (Part 3)
PIXABAY_API_KEY=your_key_from_pixabay.com

# Telegram (уведомления)
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id

# Опционально
OPENROUTER_API_KEY=your_key_for_fallback
```

### Шаг 4: GitHub Secrets

1. Settings → Secrets and variables → Actions
2. Добавьте переменные как GitHub Secrets:
   - `GOOGLE_AI_API_KEY` (для Gemini 2.5 Flash + TTS)
   - `PIXABAY_API_KEY`
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
   - `OPENROUTER_API_KEY` (опционально)

### Шаг 5: Первый Запуск (Локальный)

```bash
# Тест Part 1 (Script Generation)
python -m core.orchestrators.pipeline_orchestrator \
  --project youtube_horoscope \
  --mode shorts \
  --dry-run

# После реализации Part 2 (TTS с Gemini 2.5 Flash TTS)
python -m core.orchestrators.pipeline_orchestrator \
  --project youtube_horoscope \
  --mode shorts

# После реализации Part 3 (Video)
python -m core.orchestrators.pipeline_orchestrator \
  --project youtube_horoscope \
  --mode shorts \
  --render-video
```

---

## 🏆 Использование

### 🚀 Команды CLI

#### Part 1: Генерация Сценариев ✅

```bash
# Генерация shorts сценария
python -m core.orchestrators.pipeline_orchestrator \
  --project youtube_horoscope \
  --mode shorts

# Результат: output/scripts/youtube_horoscope/YYYYMMDD/short_*.json
```

#### Part 2: Синтез Речи (TTS) ✅

```bash
# Озвучка с помощью Gemini 2.5 Flash TTS
python -m core.orchestrators.pipeline_orchestrator \
  --project youtube_horoscope \
  --mode shorts \
  --generate-audio

# Результат: output/audio/youtube_horoscope/shorts_*.wav
```

#### Part 3: Видео Рендеринг ✅

```bash
# Генерация видео
python -m core.orchestrators.pipeline_orchestrator \
  --project youtube_horoscope \
  --mode shorts \
  --render-video

# Результат: output/videos/youtube_horoscope/shorts.mp4
```

#### Полный Pipeline

```bash
# Все этапы (Part 1 + 2 + 3)
python -m core.orchestrators.pipeline_orchestrator \
  --project youtube_horoscope \
  --mode shorts \
  --full
```

---

## 🌐 GitHub Workflows (Как всё работает)

### 📚 Что такое GitHub Workflows?

GitHub Workflows — это **автоматизация**, которая запускает код **прямо в облаке GitHub** без выделенного сервера. Вся логика описана в YAML файлах.

### 📁 Где находятся Workflow'ы

```
.github/workflows/
├── auto-fix-agent.yml          # 🤖 Автоматическое исправление ошибок
├── tests.yml                  # ✅ Unit-тесты (ОПТИМИЗИРОВАНО!)
├── generate-batch.yml         # ✅ Батч-генерация (ОПТИМИЗИРОВАНО!)
├── generate-horoscope-video.yml # ✅ Одиночная генерация (УЖЕ ИСПРАВЛЕНО!)
├── tests-docker.yml           # ✅ Тесты в Docker
└── build-docker.yml           # 🐳 Стройка Docker образа
```

### 🎯 Основные Workflow'ы

#### 1️⃣ **Part 1+2+3 Test** ✅

**Что делает:** Генерирует сценарии, озвучивает, создаёт видео с помощью Gemini API

**Запускается:** 
- По расписанию (каждый день в 10:00 UTC)
- При push в main
- Вручную из Actions

**Этапы:**
1. ✅ Setup Python
2. ✅ Cache pip зависимостей
3. ✅ Install Python dependencies (**ОПТИМИЗИРОВАНО с `--prefer-binary`!**)
4. ✅ Run Tests
5. ✅ Generate Content (Part 1)
6. ✅ Generate Audio (Part 2 с Gemini 2.5 TTS)
7. ✅ Render Video (Part 3)

**Результат:** `output/` содержит JSON сценарии, WAV аудио, MP4 видео

---

#### 2️⃣ **Run Tests** 🪧

**Что делает:** Запускает unit-тесты для проверки кода

**Запускается:**
- При каждом push
- При pull request
- Вручную

**Команда:**
```bash
pytest tests/ -v --cov=core
```

**Результат:** ✅ или ❌ (всё тесты прошли или нет)

---

#### 3️⃣ **Build and Push Docker Image** 🐳

**Что делает:** Создаёт Docker образ и загружает в реестр

**Запускается:** При создании release

**Что нужно:**
- Docker Hub аккаунт
- GitHub Secrets: `DOCKER_USERNAME`, `DOCKER_PASSWORD`

---

#### 4️⃣ **Auto-Fix Agent** 🤖 (НОВО!)

**Что делает:** Автоматически исправляет ошибки в workflow'ах с помощью AI

**Запускается:** Когда другой workflow падает

**Процесс:**
1. ✅ Анализирует логи ошибок
2. ✅ **Выбирает модель:** Qwen (локально, FREE) или Gemini (Google API)
3. ✅ Отправляет в LLM API для анализа
4. ✅ Получает решение в JSON формате
5. ✅ Создаёт GitHub Issue с описанием проблемы
6. ✅ (Опционально) Создаёт PR с автоматическим исправлением

**Результат:** GitHub Issue + Pull Request с предложенным решением

##### 🤖 Как работает Gemini/Qwen выбор

```python
# core/utils/model_router.py

def generate_text(config, prompt, model_hint="qwen2.5-coder:1.5b"):
    """
    Выбор модели на основе имени:
    - "gemini" → Google Gemini API
    - "qwen" → OpenRouter (платный) или Ollama (бесплатный)
    """
    
    model_l = model_hint.lower()
    
    if "gemini" in model_l:
        return _call_gemini(model, prompt)  # ← Google API
    
    if "qwen" in model_l:
        if "ollama" in config:  # Локальный Qwen через Ollama
            return _call_ollama(model, prompt)  # ← БЕСПЛАТНО!
        else:
            return _call_openrouter(model, prompt)  # ← Платный API
    
    raise ValueError(f"Unknown model: {model_hint}")
```

---

## ⚡ ОПТИМИЗАЦИЯ И КШИРОВАНИЕ

### 🖱️ Студентские Кэш

#### ✅ **PIP Cache (Python зависимости)**

**Флаг:** `--prefer-binary` (использует готовые wheels вместо компиляции)

**Результат:**
- **1-й run:** 41s → 15-20s (🚀 50% ускорение!)
- **2-й run:** 41s → <2s (🚀 95% ускорение из кэша!)

**Как это работает:**

GitHub Actions сохраняет pip cache между запусками.

**Ключ кэша:** хеш файла `requirements.txt`

**Каждый раз:**
1. Если requirements.txt не изменился → восстанавливаем из кэша (<2s)
2. Если изменился → скачиваем только новые (15-20s с `--prefer-binary`)

### 🖱️ Экономия времени

| Сценарий | Без кэша | С кэшем | Экономия |
|----------|----------|---------|----------|
| **1 видео (Part 1)** | 2 мин | 0.5 мин | 1.5 мин |
| **1 видео (Part 1+2+3)** | 15 мин | 6 мин | 9 мин |
| **4 видео/месяц** | 60 мин | 24 мин | 36 мин |
| **ежедневно (30/месяц)** | 450 мин | 180 мин | **270 мин (4.5 часов!)** |

### 🏖️ Другие оптимизации

См ПОЛНУЙ гайд в [INSTALLATION_OPTIMIZATION.md](INSTALLATION_OPTIMIZATION.md)

---

## ⚠️ Лимиты GitHub Actions

### Free Plan

| Параметр | Лимит |
|----------|-------|
| **Минуты/месяц** | **2,000 мин** |
| **Storage** | **500 MB** |
| **Concurrent jobs** | **20 (Linux)** |
| **Job timeout** | **6 часов** |

**Вывод:** Хватает на **30-40 видео в месяц**.

### 💀 Повышение лимита

**Публичный репо = НЕОГРАНИЧЕННЫЕ минуты!**

Не боитесь делиться кодом → Получите бесплатные Actions!

---

## 🔧 Решение Проблем

### ❌ Gemini API 401 Error

```bash
# Проверить ключ
echo $GOOGLE_AI_API_KEY

# Получить новый с https://ai.google.dev
# Убедиться что скопирован БЕЗ пробелов
```

### ❌ "ModuleNotFoundError: No module named 'pydub'"

```bash
pip install pydub
pip install --prefer-binary -r requirements.txt
```

### ❌ "ffmpeg not found"

```bash
# Ubuntu/Debian
sudo apt-get install -y ffmpeg

# macOS
brew install ffmpeg

# Windows - скачать с https://ffmpeg.org/download.html
```

### ❌ pip инсталация течет медленно

**Решение:** Обновить выведенные workflow'u с помощью `--prefer-binary` (УЖЕ СДЕЛАНО!)

---

## 👋 Внесение Вклада

Приветствуются PR для:

- ✅ Улучшение Part 2 (TTS)
- ✅ Улучшение Part 3 (Video)
- ✅ Новые платформы (Part 4)
- ✅ Auto-Fix Agent improvements
- ✅ Документация
- ✅ Исправление багов

### Процесс

1. Fork репо
2. Создайте ветку: `git checkout -b feature/awesome-feature`
3. Commit: `git commit -am 'Add awesome feature'`
4. Push: `git push origin feature/awesome-feature`
5. Откройте Pull Request

---

## 📄 Лицензия

MIT License — см. [LICENSE](LICENSE)

---

## 🙋 Благодарности

Проект построен на базе:

- [Gemini API](https://ai.google.dev/)
- [Gemini 2.5 Flash TTS](https://ai.google.dev/docs/gemini-api-overview)
- [Qwen](https://github.com/QwenLM/Qwen)
- [Ollama](https://ollama.ai/)
- [MoviePy](https://zulko.github.io/moviepy)
- [FFmpeg](https://ffmpeg.org/)
- [Pixabay API](https://pixabay.com/api)
- [Pydub](https://github.com/jiaaro/pydub)

---

## 🪧 Testing

Content Factory имеет полное покрытие тестами для всех модулей.

### Запуск тестов

```bash
# Быстрые unit-тесты (без внешних API)
pytest tests/ -v -m "not slow"

# Все тесты включая интеграционные
pytest tests/ -v

# С покрытием кода
pytest tests/ --cov=core --cov-report=html
```

### CI/CD

Тесты автоматически запускаются при каждом push и pull request через GitHub Actions.

Подробнее см. [TESTING.md](TESTING.md).

---

**Версия:** 2.2  
**Последнее обновление:** Декабрь 14, 2025  
**Статус:** 🜢 Parts 1+2+3 COMPLETE (with Gemini 2.5 Flash TTS) + Auto-Fix Agent Active + двухуровневая pip оптимизация (50% ускорение!) + Full Test Coverage

---

<div align="center">

**Made with ❤️ by Content Factory Team**

[⭐ Поставьте звезду, если нравится!](https://github.com/crosspostly/content-factory)

</div>
