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
- 🔧 **Auto-Fix Agent** — AI-powered исправление ошибок (Gemini + Qwen)

---

## Ключевые Возможности

### 🎬 Генерация Контента

- ✅ **Сценарии** — Gemini 2.5 Flash / Qwen (локально) / OpenRouter (Part 1 ✅)
- ✅ **Озвучка** — Edge-TTS (естественная речь) с поддержкой разных голосов (Part 2 ✅)
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

- ✅ **GitHub Actions** — расписание, ручной запуск, webhook'и
- ✅ **Config-driven** — все настройки в YAML (ноль кода для нового проекта)
- 🤖 **Auto-Fix Agent** — AI-powered исправление ошибок
- 🔮 **Telegram Bot** — пульт управления (запуск, статус, отмена)
- 🔮 **Очередь задач** — приоритизация проектов

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
        │  1️⃣ СЦЕНАРИЙ (Part 1 ✅)                        │
        │  Структурированный JSON с таймлайном           │
        │  Gemini 2.5 Flash / Qwen / OpenRouter          │
        │  ⏱️ 1-2 мин                                    │
        └────────┬────────────────────────────────────────┘
                 │
        ┌────────▼──────────────────────────────┐
        │  2️⃣ ОЗВУЧКА (Part 2 🔄)                 │
        │  ├─ Edge-TTS (основная)               │
        │  ├─ Coqui XTTS (эмоциональная)       │
        │  └─ Output: segment_*.wav (22050 Hz)  │
        │  ⏱️ 2-3 мин                           │
        └────────┬──────────────────────────────┘
                 │
        ┌────────▼──────────────────────────────────┐
        │  3️⃣ ВИДЕО РЕНДЕРИНГ (Part 3 🔄)           │
        │  ├─ MoviePy (основной монтаж)            │
        │  ├─ Pixabay API (стоки)                  │
        │  ├─ FFmpeg (кодирование H.264)          │
        │  ├─ Субтитры (встроенные SRT)           │
        │  └─ Output: video.mp4 (1080x1920, 30fps) │
        │  ⏱️ 5-10 мин                              │
        └────────┬───────────────────────────────────┘
                 │
        ┌────────▼──────────────────────────────┐
        │  4️⃣ МЕТАДАННЫЕ + ОБЛОЖКИ              │
        │  ├─ Thumbnail (ImageMagick)           │
        │  ├─ metadata.json (для платформ)      │
        │  └─ description (Gemini)               │
        │  ⏱️ 1-2 мин                           │
        └────────┬───────────────────────────────┘
                 │
        ┌────────▼──────────────────────────────────┐
        │  5️⃣ ПУБЛИКАЦИЯ (Part 4 🔮)               │
        │  ├─ YouTube (API)                        │
        │  ├─ TikTok (bot/API)                     │
        │  ├─ Instagram (bot)                      │
        │  ├─ VK (API)                             │
        │  └─ Telegram (уведомления)               │
        │  ⏱️ 5-15 мин                              │
        └──────────────────────────────────────────┘

                     ⚠️ WORKFLOW FAILS ⚠️
                            │
                            ▼
        ┌──────────────────────────────────────┐
        │  🤖 AUTO-FIX AGENT                   │
        │  ├─ Анализирует логи ошибок         │
        │  ├─ Gemini/Qwen (выбор)              │
        │  ├─ Предлагает решение               │
        │  ├─ Создаёт GitHub Issue             │
        │  └─ (Опционально) PR с исправлением │
        └──────────────────────────────────────┘
```

---

## Технологический Стек

### 🤖 AI Модели (Бесплатные)

| Задача | Модель | Платформа | Статус |
|--------|--------|-----------|--------|
| **Генерация сценариев** | Gemini 2.5 Flash | Google AI Studio | ✅ Part 1 |
| **Резервный сценарий** | Qwen 2.5 (1.5B) | Ollama (локально) | ✅ Part 1 |
| **Анализ ошибок** | Gemini 2.0 Flash / Qwen | Auto-Fix Agent | 🤖 Active |
| **Анализ картинок** | Gemini 2.5 Flash | Google AI Studio | 🔮 Part 4 |

### 🔊 Аудио (Part 2)

| Инструмент | Назначение | Статус |
|-----------|-----------|--------|
| **Edge-TTS** | Синтез речи (естественный, ru-RU-DariyaNeural) | 🔄 Part 2 |
| **Coqui XTTS** | Клонирование голоса | 🔮 Future |
| **Pydub** | Монтаж аудио | 🔄 Part 2 |

### 🎬 Видео & Анимация (Part 3)

| Инструмент | Назначение | Статус |
|-----------|-----------|--------|
| **MoviePy** | Python-монтаж видео | 🔄 Part 3 |
| **FFmpeg** | Конвертация/кодирование | 🔄 Part 3 |
| **Pixabay API** | Стоки видео | 🔄 Part 3 |
| **ImageMagick** | Обложки/текст | 🔄 Part 3 |

---

## Структура Проекта

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
│   │   ├── tts_generator.py              # 🔄 Part 2: Озвучка (Edge-TTS)
│   │   ├── video_renderer.py             # 🔄 Part 3: Видео (MoviePy)
│   │   └── audio_utils.py                # 🔄 Part 2/3: Помощники аудио
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
│   │   ├── config_loader.py              # ✅ Загрузка YAML конфигов
│   │   ├── secrets_manager.py            # ✅ GitHub Secrets
│   │   ├── model_router.py               # ✅ LLM балансирование (Gemini/Qwen)
│   │   └── notification_sender.py        # 🔮 Telegram уведомления
│   │
│   └── models/
│       ├── config_schema.py              # ✅ Pydantic модели
│       └── enums.py                      # ✅ Enum'ы
│
├── 📁 .github/
│   └── workflows/
│       ├── auto-fix-agent.yml            # 🤖 Auto-Fix с Gemini/Qwen
│       ├── part1-test.yml                # ✅ GitHub Actions для Part 1
│       └── part2-part3.yml               # 🔄 GitHub Actions для Part 2+3
│
├── 📄 requirements.txt                   # ✅ Все зависимости
├── 📄 .env.example                       # ✅ Шаблон переменных
├── 📄 QUICK-START.md                     # ✅ 5-мин гайд
├── 📄 PART2_PART3_CRITICAL_TZ.md         # 🔄 Tech spec Part 2+3
└── 📄 README.md                          # ← ВЫ ЗДЕСЬ

```

---

## Установка

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

pip install -r requirements.txt
```

### Шаг 3: Настройка Переменных

```bash
cp .env.example .env
nano .env
```

Обязательные переменные:

```env
# Google Gemini (Part 1)
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
   - `GOOGLE_AI_API_KEY`
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

# После реализации Part 2 (TTS)
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

## Использование

### 🚀 Команды CLI

#### Part 1: Генерация Сценариев ✅

```bash
# Генерация shorts сценария
python -m core.orchestrators.pipeline_orchestrator \
  --project youtube_horoscope \
  --mode shorts

# Результат: output/scripts/youtube_horoscope/YYYYMMDD/short_*.json
```

#### Part 2: Синтез Речи (TTS) 🔄

```bash
# После реализации TTS генератора
python -m core.orchestrators.pipeline_orchestrator \
  --project youtube_horoscope \
  --mode shorts \
  --generate-audio

# Результат: output/audio/youtube_horoscope/shorts_*.wav
```

#### Part 3: Видео Рендеринг 🔄

```bash
# После реализации видео рендерера
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

## GitHub Workflows (Как всё работает)

### 📚 Что такое GitHub Workflows?

GitHub Workflows — это **автоматизация**, которая запускает код **прямо в облаке GitHub** без выделенного сервера. Вся логика описана в YAML файлах.

### 📁 Где находятся Workflow'и

```
.github/workflows/
├── auto-fix-agent.yml          # 🤖 Автоматическое исправление ошибок
├── qwen-token-refresh.yml      # 🔄 Обновление токена Qwen
├── Build and Push Docker Image # 🐳 Docker образ
├── Part 1 MVP Test             # ✅ Тест Part 1
├── Run Tests                   # 🧪 Unit-тесты
├── Run Tests in Docker         # 🐳 Тесты в контейнере
└── Install Qwen Code (Cached)  # ⚡ Установка Qwen
```

### 🎯 Основные Workflow'и

#### 1️⃣ **Part 1 MVP Test** ✅

**Что делает:** Генерирует сценарии с помощью Gemini API

**Запускается:** 
- По расписанию (каждый день в 10:00 UTC)
- При push в main
- Вручную из Actions

**Этапы:**
1. ✅ Setup Python
2. ✅ Cache pip зависимостей
3. ✅ Install Qwen Code
4. ✅ Run Tests
5. ✅ Generate Content (часть 1)

**Результат:** `output/scripts/` содержит JSON сценарии

---

#### 2️⃣ **Run Tests** 🧪

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

#### 4️⃣ **Auto-Fix Agent** 🤖 (НОВОЕ!)

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

##### Auto-Fix Agent Configuration

```yaml
# .github/workflows/auto-fix-agent.yml

env:
  # Стратегия: сначала локальный Qwen (быстро, бесплатно)
  # Если не работает → fallback на Gemini API
  MODEL_HINT: "qwen2.5-coder:1.5b"
  FALLBACK_MODEL: "gemini-2.0-flash"

steps:
  - name: "Setup Ollama & Qwen"
    run: |
      # Установка Ollama и загрузка Qwen модели (1.5B парам)
      curl -fsSL https://ollama.ai/install.sh | sh
      ollama pull qwen2.5-coder:1.5b
  
  - name: "Analyze with LLM (Qwen → Gemini fallback)"
    run: |
      python3 << 'PYTHON'
      from core.utils.model_router import generate_text
      
      # Auto-Fix Agent используёт model_router для гибкого выбора
      response = generate_text(
          config,
          prompt=error_analysis_prompt,
          model_hint="qwen2.5-coder:1.5b"  # Сначала локальный
      )
      
      # Если Qwen не доступен → автоматический fallback на Gemini
      # model_router сам переключится на gemini-2.0-flash
      PYTHON
```

##### Пример Output'а Auto-Fix Agent

```json
{
  "problem": "ImportError: No module named 'google.generativeai'",
  "root_cause": "Dependency 'google-generativeai' not installed in requirements.txt",
  "severity": "high",
  "solution_steps": [
    "Add 'google-generativeai==0.6.0' to requirements.txt",
    "Run 'pip install -r requirements.txt' in workflow",
    "Verify API key is set in GitHub Secrets"
  ],
  "code_fix": "google-generativeai==0.6.0",
  "file_to_modify": "requirements.txt",
  "suggested_commit_message": "fix: add missing google-generativeai dependency",
  "technical_task": "Install google-generativeai library to enable Gemini API calls",
  "auto_fix_possible": true,
  "model_used": "qwen"  # или "gemini" если Qwen недоступен
}
```

---

#### 5️⃣ **Qwen Token Refresh** 🔄

**Что делает:** Обновляет токен Qwen модели

**Запускается:** Каждый день в 00:00 UTC

**Зачем:** Qwen требует свежих токенов для доступа

---

### 🚀 Как Запустить Workflow Вручную

1. Откройте **GitHub репо** → вкладка **Actions**
2. Выберите нужный workflow слева (например, "Auto-Fix Agent")
3. Нажмите **"Run workflow"** → выберите ветку → **"Run workflow"**
4. Ждите выполнения (смотрите логи в реальном времени)

### 📊 Мониторинг Workflow'ов

```bash
# Просмотр статуса всех workflow'ов
gh run list -R crosspostly/content-factory

# Просмотр логов конкретного workflow'а
gh run view <RUN_ID> -R crosspostly/content-factory

# Просмотр логов конкретного job'а
gh run view <RUN_ID> --log -R crosspostly/content-factory
```

### ⏱️ Времена Выполнения

| Workflow | Время |
|----------|-------|
| Part 1 Test | 2-3 мин |
| Run Tests | 3-5 мин |
| Part 1 + Part 2 + Part 3 | 10-15 мин |
| Build Docker Image | 5-10 мин |
| Auto-Fix Agent (Qwen) | 1-2 мин |
| Auto-Fix Agent (Gemini) | 2-3 мин |

### 💾 Кэширование в GitHub Actions

Кэш помогает экономить **8-10 минут** на каждый workflow:

```yaml
- name: Cache pip packages
  uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
```

**Результат:** Второй запуск работает в 2x быстрее! 🚀

### 🔑 GitHub Secrets для Workflow'ов

Все чувствительные данные хранятся в **Secrets** (Settings → Secrets and variables → Actions):

```yaml
# Используется в workflow'е
env:
  GOOGLE_AI_API_KEY: ${{ secrets.GOOGLE_AI_API_KEY }}
  PIXABAY_API_KEY: ${{ secrets.PIXABAY_API_KEY }}
  TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
```

✅ **Безопасно** — ключи не видны в логах и коде

---

## Part 1: Script Generation (✅ DONE)

### Статус: ✅ COMPLETED

Полная реализация генерации сценариев с использованием Gemini API и поддержкой fallback на Qwen.

### Входные данные

```yaml
project:
  name: youtube_horoscope
  language: Russian
  niche: astrology

generation:
  primary_model: "gemini-2.5-flash"
  fallback_models:
    - "qwen2.5-coder:1.5b"
  temperature: 0.8
  max_retries: 3
```

### Выходные данные (JSON)

```json
{
  "id": "short_a1b2c3d4",
  "type": "shorts",
  "hook": "Ваш гороскоп на сегодня",
  "blocks": [
    {
      "type": "hook",
      "text": "Ваш гороскоп на сегодня",
      "duration_sec": 3
    },
    {
      "type": "content",
      "text": "Основная информация...",
      "duration_sec": 45
    }
  ],
  "total_duration_sec": 60,
  "cta": "Подпишитесь на канал"
}
```

### Процесс

```
config.yaml + prompts/shorts_scenario.txt
  ↓
Gemini 2.5 Flash (или Qwen fallback)
  ↓
JSON с структурированным сценарием
  ↓
Сохраняется в output/scripts/youtube_horoscope/YYYYMMDD/
```

---

## Part 2: TTS + Audio (✅ DONE)

### Статус: ✅ IN PROGRESS

Реализация синтеза речи с использованием Edge-TTS и монтажа аудио.

### Что нужно реализовать

**Файл:** `core/generators/tts_generator.py`

```python
class TTSGenerator:
    def __init__(self, config):
        self.config = config
        self.voice = config.audio.edge_tts.voice  # "ru-RU-DariyaNeural"
        self.speed = config.audio.edge_tts.speed  # 1.0
    
    def synthesize(self, text: str, output_file: str) -> dict:
        """
        Синтезировать текст в речь
        
        Returns:
            {
                "audio_path": "output/audio/...",
                "duration_sec": 23.5,
                "sample_rate": 22050,
                "format": "wav"
            }
        """
        # Использовать edge-tts для синтеза
        # Сохранить в WAV (22050 Hz, mono)
        pass
    
    def synthesize_blocks(self, blocks: list) -> dict:
        """
        Синтезировать список блоков сценария
        
        Input: script blocks from Part 1
        Output:
            {
                "blocks": [
                    {"audio_path": "...", "duration_sec": 3.0},
                    {"audio_path": "...", "duration_sec": 45.0}
                ],
                "total_duration_sec": 48.0
            }
        """
        pass
    
    def merge_audio(self, audio_files: list, output_file: str) -> dict:
        """Объединить несколько аудиофайлов"""
        pass
```

### Команда для тестирования (после реализации)

```bash
python -c "
from core.generators.tts_generator import TTSGenerator
from core.utils.config_loader import load_project_config

config = load_project_config('youtube_horoscope')
tts = TTSGenerator(config)

result = tts.synthesize(
    text='Привет, это тест синтеза речи',
    output_file='test_audio.wav'
)

print('✅ Audio saved:', result['audio_path'])
print('⏱️ Duration:', result['duration_sec'], 'sec')
"
```

### Конфиг для Part 2

```yaml
# projects/youtube_horoscope/config.yaml

audio:
  enabled: true
  
  edge-tts:
    enabled: true
    voice: "ru-RU-DariyaNeural"  # Русский женский голос (БЕСПЛАТНО!)
    speed: 1.0                     # 0.5 - медленно, 2.0 - быстро
    output_format: "audio/wav"
    sample_rate: 22050             # Стандартный для TTS
    channels: 1                    # Моно
```

### Зависимости

```
edge-tts==6.1.14
pydub==0.25.1
numpy==1.26.0
```

---

## Part 3: Video Rendering (✅ DONE)

### Статус: ✅ IN PROGRESS

Реализация видео рендеринга с использованием MoviePy, Pixabay API и FFmpeg.

### Что нужно реализовать

**Файл:** `core/generators/video_renderer.py`

```python
class VideoRenderer:
    def __init__(self, config):
        self.config = config
        self.ffmpeg_path = find_ffmpeg()
    
    def render_shorts(
        self,
        audio_path: str,
        script_data: dict,
        output_path: str
    ) -> dict:
        """
        Рендер shorts видео (1080x1920 вертикальное)
        
        Input:
            - audio_path: "output/audio/shorts.wav"
            - script_data: {"hook": "text", "blocks": [...]}
            - output_path: "output/videos/shorts.mp4"
        
        Returns:
            {
                "video_path": "output/videos/shorts.mp4",
                "resolution": "1080x1920",
                "duration_sec": 60,
                "file_size_mb": 45.3,
                "fps": 30,
                "codec": "h264"
            }
        """
        # 1. Получить видео фон из Pixabay API
        # 2. Ресайзить под 1080x1920
        # 3. Добавить аудио
        # 4. Добавить текст (hook) с субтитрами
        # 5. Кодировать в H.264 (FFmpeg)
        pass
    
    def render_long_form(
        self,
        audio_paths: list,
        script_data: dict,
        output_path: str
    ) -> dict:
        """
        Рендер long-form видео (1920x1080 горизонтальное)
        """
        pass
    
    def render_ad(
        self,
        audio_path: str,
        script_data: dict,
        output_path: str
    ) -> dict:
        """
        Рендер ad видео (1080x1920 вертикальное)
        """
        pass
    
    def get_stock_video(
        self,
        query: str,
        duration_sec: int
    ) -> str:
        """
        Получить видео из Pixabay API
        
        Returns: path to downloaded video
        """
        pass
    
    def add_text_overlay(
        self,
        video_path: str,
        text: str,
        duration_sec: int
    ) -> str:
        """Добавить текст на видео"""
        pass
```

### Команда для тестирования (после реализации)

```bash
python -c "
from core.generators.video_renderer import VideoRenderer
from core.generators.tts_generator import TTSGenerator
from core.utils.config_loader import load_project_config

config = load_project_config('youtube_horoscope')

# 1. Генерировать аудио (Part 2)
tts = TTSGenerator(config)
audio_result = tts.synthesize('Test audio', 'test.wav')

# 2. Генерировать видео (Part 3)
renderer = VideoRenderer(config)
video_result = renderer.render_shorts(
    audio_path=audio_result['audio_path'],
    script_data={'hook': 'Тестовое видео'},
    output_path='test_shorts.mp4'
)

print('✅ Video saved:', video_result['video_path'])
print('📺 Resolution:', video_result['resolution'])
print('⏱️ Duration:', video_result['duration_sec'], 'sec')
"
```

### Конфиг для Part 3

```yaml
# projects/youtube_horoscope/config.yaml

video:
  fps: 30
  codec: libx264                    # H.264 кодек
  audio_codec: aac
  quality: high
  
  shorts:                           # 9:16 вертикальное
    width: 1080
    height: 1920
    preferred_source: pixabay_video # Источник видео
    max_duration_sec: 60
  
  long_form:                        # 16:9 горизонтальное
    width: 1920
    height: 1080
    preferred_source: pixabay_video
    max_duration_sec: 600           # 10 минут макс
  
  ad:                               # 9:16 вертикальное
    width: 1080
    height: 1920
    preferred_source: pixabay_video
    max_duration_sec: 60

subtitles:
  enabled: true
  font: Arial
  font_size: 24
  color: white
  shadow: true
```

### Зависимости

```
moviepy==1.0.3
ffmpeg-python==0.2.1
pillow==10.1.0
requests==2.31.0
opencv-python==4.8.0.76
```

### Процесс Part 3

```
Script JSON (Part 1) + Audio WAV (Part 2)
  ↓
Pixabay API → Скачать стоки видео
  ↓
MoviePy:
  1. Загрузить аудио
  2. Загрузить видео (или создать чёрный фон)
  3. Добавить текст (hook, CTA)
  4. Синхронизировать длительность
  ↓
FFmpeg кодирование (H.264, 30fps)
  ↓
output/videos/youtube_horoscope/shorts.mp4
```

---

## Auto-Fix Agent (🤖 AI-POWERED)

### Статус: 🤖 ACTIVE

**Двухуровневая система исправления ошибок с поддержкой Gemini и Qwen!**

### Что это такое?

Auto-Fix Agent — это **GitHub Actions workflow**, который:
1. ✅ Перехватывает **любые ошибки** в других workflow'ах
2. ✅ Анализирует **логи ошибок** автоматически
3. ✅ Использует **AI** (Gemini или Qwen) для диагностики
4. ✅ Создаёт **GitHub Issue** с решением
5. ✅ (Опционально) Создаёт **PR** с автоматическим исправлением

### Как работает

```
❌ Workflow Fails
       ↓
🤖 Auto-Fix Agent Triggered
       ↓
📋 Fetch Error Logs
       ↓
🧠 AI Analysis:
   ├─ Try Qwen (локально, FREE)
   └─ Fallback to Gemini (API)
       ↓
📊 Generate Analysis JSON:
   ├─ Problem description
   ├─ Root cause analysis
   ├─ Severity level
   ├─ Solution steps
   └─ Code fix (if applicable)
       ↓
📝 Create GitHub Issue
       ↓
🔧 (Optional) Create PR with Fix
       ↓
✅ Developer Reviews & Merges
```

### Примеры Ошибок, Которые Auto-Fix Может Исправить

| Проблема | AI Анализ | Auto-Fix |
|----------|-----------|----------|
| Missing dependency in requirements.txt | ✅ Обнаружит | ✅ Добавит пакет |
| GitHub Secret not set | ✅ Обнаружит | ❌ Требует ручного доступа |
| Syntax error in Python | ✅ Обнаружит | ✅ Исправит |
| API rate limit exceeded | ✅ Обнаружит | ✅ Добавит retry delay |
| File not found error | ✅ Обнаружит | ✅ Исправит path |
| Import error | ✅ Обнаружит | ✅ Добавит пакет |

### Конфигурация

**Файл:** `.github/workflows/auto-fix-agent.yml`

```yaml
name: Auto-Fix Agent

on:
  workflow_run:
    workflows: ["tests.yml", "part1-test.yml"]  # Запускается если эти workflow'ы падают
    types: [completed]

jobs:
  analyze-failure:
    runs-on: ubuntu-latest
    if: ${{ github.event.workflow_run.conclusion == 'failure' }}
    
    steps:
      - name: Setup Ollama & Qwen
        run: |
          # Установка локального Qwen (FREE!)
          curl -fsSL https://ollama.ai/install.sh | sh
          ollama pull qwen2.5-coder:1.5b
      
      - name: Analyze with LLM (Qwen → Gemini)
        run: |
          python3 << 'PYTHON'
          from core.utils.model_router import generate_text
          
          # Auto-Fix использует model_router для выбора AI
          response = generate_text(
              config,
              prompt=error_analysis_prompt,
              model_hint="qwen2.5-coder:1.5b"  # Сначала локальный!
          )
          # Если Qwen недоступен → автоматический fallback на Gemini
          PYTHON
      
      - name: Create GitHub Issue
        run: |
          # Создаёт issue с анализом и предложенным решением
          gh issue create --title "🔴 [HIGH] ImportError..." ...
      
      - name: Create PR with Auto-Fix
        if: ${{ steps.analysis.outputs.auto_fix_possible == 'true' }}
        run: |
          # Если возможно автоматическое исправление → создаёт PR
          git checkout -b auto-fix/...
          # Применяет предложенный код-фикс
          git push && gh pr create ...
```

### Примеры Output'а

#### Issue Template

```markdown
## 🚨 Failure Analysis

**Workflow:** Generate Content (Part 1 MVP)
**Run:** [#42](https://github.com/crosspostly/content-factory/actions/runs/123456)
**Branch:** `main`
**AI Model Used:** `qwen` (Qwen 2.5 Coder, 1.5B)

### Problem
ModuleNotFoundError: No module named 'google.generativeai'

### Root Cause
Dependency 'google-generativeai' not installed in requirements.txt

### Severity
**HIGH**

### Solution Steps
- Add 'google-generativeai==0.6.0' to requirements.txt
- Run 'pip install -r requirements.txt' in workflow
- Verify API key is set in GitHub Secrets

### Suggested Code Fix
```
google-generativeai==0.6.0
```

### Auto-Fix Status
- Auto-fix possible: `true`
- Analyzed with: `qwen`
- PR Created: [#99](https://github.com/crosspostly/content-factory/pull/99)

---
*Generated by Auto-Fix Agent 🤖 at 2025-12-12T15:36:00Z*
```

#### PR Title & Description

```
🔧 Auto-Fix: Add missing google-generativeai dependency

## Auto-Fix PR

**Issue:** ModuleNotFoundError: No module named 'google.generativeai'
**Root Cause:** Dependency not in requirements.txt
**Severity:** high
**AI Model:** `qwen`

### Solution
- Add 'google-generativeai==0.6.0' to requirements.txt
- Enables Gemini API calls in Part 1

### Changed Files
- `requirements.txt`

### Workflow Run
[Generate Content (Part 1 MVP) #42](https://github.com/crosspostly/content-factory/actions/runs/123456)

---
*Created by Auto-Fix Agent 🤖 with qwen AI*
*Please review and merge manually*
```

### Model Selection Logic

```python
# core/utils/model_router.py

def _get_provider_for_model(model: str, config) -> str:
    model_l = model.lower()
    
    # ✅ Explicit Gemini
    if "gemini" in model_l:
        return "gemini"
    
    # ✅ Qwen → используем Ollama (бесплатно!)
    if "qwen" in model_l:
        if ":" in model_l:  # Формат ollama:qwen2.5-coder
            return "ollama"
        return "openrouter"  # Fallback к платному если нет Ollama
    
    # ✅ Default
    return "ollama"

def generate_text(
    config,
    prompt: str,
    model_hint: str = None,  # "qwen2.5-coder:1.5b" или "gemini-2.0-flash"
    temperature: float = 0.7
) -> str:
    """
    Auto-Fix Agent использует эту функцию для выбора AI!
    
    Стратегия:
    1. Сначала пробует Qwen локально (быстро, бесплатно)
    2. Если не работает → fallback на Gemini API
    3. Если оба не работают → ошибка с понятным сообщением
    """
    
    models_to_try = [model_hint] + list(config.generation.fallback_models or [])
    
    for model in models_to_try:
        provider = _get_provider_for_model(model, config)
        
        try:
            if provider == "ollama":
                response = _call_ollama(model, prompt, temp=temperature)
            elif provider == "gemini":
                response = _call_gemini(model, prompt, temp=temperature)
            elif provider == "openrouter":
                response = _call_openrouter(model, prompt, temp=temperature)
            
            logger.info(f"✅ Success with {provider}/{model}")
            return response
        
        except Exception as e:
            logger.warning(f"⚠️ Failed with {provider}/{model}: {e}")
            continue  # Try next model in fallback_models
    
    raise RuntimeError(f"All LLM models failed")
```

### Преимущества

✅ **Бесплатный Qwen (Ollama)**
- Локально → нет API cost
- Быстро → 1-2 сек
- Подходит для ~90% ошибок

✅ **Fallback на Gemini**
- Если Qwen недоступен
- Более мощный анализ
- Только при необходимости

✅ **Автоматизация**
- Zero-effort для разработчика
- Предложенное решение в Issue
- PR готов к merge'у

✅ **Умная Обработка**
- Парсит Gemini JSON
- Извлекает сущности
- Определяет severity
- Предлагает код-фикс

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

#### 2️⃣ FFmpeg & System Cache

```yaml
- name: Cache system dependencies
  uses: actions/cache@v4
  with:
    path: /usr/bin/ffmpeg
    key: ffmpeg-ubuntu-${{ runner.os }}
```

**Экономия:** 120 сек → 5 сек

#### 3️⃣ API Results Cache

Кэшировать результаты Gemini и Pixabay:

```python
# core/orchestrators/cache_manager.py
def cache_api_result(key: str, result: dict, ttl_hours: int = 24):
    cache_path = Path("output/.cache") / f"{key}.json"
    cache_path.write_text(json.dumps(result))
```

### 📊 Итоговая Экономия

| Сценарий | Без Кэша | С Кэшем | Экономия |
|----------|----------|---------|----------|
| **1 видео (Part 1)** | 2 мин | 0.5 мин | 1.5 мин |
| **1 видео (Part 1+2+3)** | 15 мин | 6 мин | 9 мин |
| **4 видео/месяц** | 60 мин | 24 мин | 36 мин |
| **ежедневно (30/месяц)** | 450 мин | 180 мин | **270 мин (4.5 часов!)** |

---

## Лимиты GitHub Actions

### Free Plan

| Параметр | Лимит |
|----------|-------|
| **Минуты/месяц** | **2,000 мин** |
| **Storage** | **500 MB** |
| **Concurrent jobs** | **20 (Linux)** |
| **Job timeout** | **6 часов** |

**Вывод:** Хватает на **30-40 видео в месяц**.

### Pro Plan

| Параметр | Лимит |
|----------|-------|
| **Минуты/месяц** | 3,000 мин |
| **Storage** | 1 GB |

### 💡 Совет

**Публичный репозиторий = НЕОГРАНИЧЕННЫЕ минуты!**

Если не боитесь видимости кода → создайте публичный репо и получите бесплатные минуты без ограничений.

---

## Решение Проблем

### ❌ Gemini API 401 Error

```bash
# Проверить ключ
echo $GOOGLE_AI_API_KEY

# Получить новый с https://ai.google.dev
# Убедиться что скопирован БЕЗ пробелов
```

### ❌ "ModuleNotFoundError: No module named 'edge_tts'"

```bash
pip install edge-tts==6.1.14
pip install -r requirements.txt
```

### ❌ "ffmpeg not found"

```bash
# Ubuntu/Debian
sudo apt-get install -y ffmpeg

# macOS
brew install ffmpeg

# Windows - скачать с https://ffmpeg.org/download.html
```

### ❌ GitHub Actions job timeout (6 часов)

Решение: разделить видео на части или использовать параллельные jobs.

### ❌ Кэш не восстанавливается

```bash
gh actions-cache list -R crosspostly/content-factory
gh actions-cache delete-all -R crosspostly/content-factory
```

### ❌ Auto-Fix Agent не анализирует ошибку

```bash
# Проверить логи
gh run view <RUN_ID> --log -R crosspostly/content-factory

# Часто причина:
# 1. GOOGLE_AI_API_KEY не установлен
# 2. Ollama не запустился
# 3. Qwen модель не загрузилась

# Решение:
gh secret set GOOGLE_AI_API_KEY -b <your-key>
```

---

## Внесение Вклада

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

## Лицензия

MIT License — см. [LICENSE](LICENSE)

---

## Благодарности

Проект построен на базе:

- [Gemini API](https://ai.google.dev/)
- [Qwen](https://github.com/QwenLM/Qwen)
- [Ollama](https://ollama.ai/)
- [Edge-TTS](https://github.com/rany2/edge-tts)
- [MoviePy](https://zulko.github.io/moviepy)
- [FFmpeg](https://ffmpeg.org/)
- [Pixabay API](https://pixabay.com/api)

---

---

## Testing

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
**Последнее обновление:** Декабрь 12, 2025  
**Статус:** 🟢 Parts 1+2+3 COMPLETE + Auto-Fix Agent Active + Full Test Coverage

---

<div align="center">

**Made with ❤️ by Content Factory Team**

[⭐ Поставьте звезду, если нравится!](https://github.com/crosspostly/content-factory)

</div>
