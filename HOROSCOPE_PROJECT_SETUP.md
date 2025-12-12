# 🎬 YouTube Гороскопы - ПУЛНОЕ РУКОВОДСТВО

> Комплексная инструкция по настройке портала YouTube с автоматическим генерированием гороскопного контента

## 📋 Оглавление

- [Общие Сведения](#общие-сведения)
- [Предпосылки](#предпосылки)
- [Настройка API Ключей](#настройка-api-ключей)
- [Настройка GitHub Secrets](#настройка-github-secrets)
- [Настройка Прожекта](#настройка-прожекта)
- [Остановка Всех Утилит](#остановка-всех-утилит)
- [Запуск Генератора](#запуск-генератора)
- [Торовление](#торовление)

---

## Общие Сведения

- **Проект**: YouTube Гороскопы
- **Папка**: `projects/youtube_horoscope/`
- **Стратегия**: Шорты 2x в день + длинные 1x в неделю
- **Конфигурация**: `projects/youtube_horoscope/config.yaml`

---

## Предпосылки

- Python 3.11+
- Git
- GitHub Account с GitHub Actions вактивным
- YouTube Channel (Developer account)
- API ключи (see below)

---

## Настройка API Ключей

### 1️⃣ YouTube Data API v3

**Нужно для**: Уплоад видео, управление плейлистами, оптимизация SEO

**Шагы**:

1. Перейди на [Google Cloud Console](https://console.cloud.google.com/)
2. Создай ровый проект
3. Активируй **YouTube Data API v3**
4. Создай **OAuth 2.0 Desktop Application** credentials
5. Скачай JSON файл креденциалов

**ГитХуб Секрет**:

```
name: YOUTUBE_API_KEY
value: [OAuth 2.0 Client ID JSON - скодирован в base64]
```

---

### 2️⃣ Google AI (Gemini API)

**Нужно для**: Генерация сценариев, голоса (TTS), анализ картинок

**Шагы**:

1. Перейди на [Google AI Studio](https://aistudio.google.com/)
2. Нажми **Get API Key**
3. Создай новый ключ **Google AI API**
4. Копируй ключ

**ГитХуб Секрет**:

```
name: GOOGLE_AI_API_KEY
value: [API Key]

name: GEMINI_TTS_ENABLED
value: "true"

name: GEMINI_TTS_QUOTA_DAILY
value: "150"  # Примерные лимиты - проверить в доку
```

**Лимиты**:
- TTS: ~100-200 запросов/день бесплатно (Проверить!)
- Анализ картинок: 15 реквестов/мин

---

### 3️⃣ Telegram Bot (optional)

**Нужно для**: Нотификации, ротация вынуждающая генерацию видео

**Шагы**:

1. Талк с [@BotFather](https://t.me/botfather) в Telegram
2. Нажми `/newbot`
3. Открутий твоё чат с ботом (даются инструкции)
4. Копируй **Chat ID** (бери из URL чата)
5. Копируй **Bot Token** от @BotFather

**ГитХуб Секрет**:

```
name: TELEGRAM_BOT_TOKEN
value: [Bot Token from @BotFather]

name: TELEGRAM_CHAT_ID
value: [Your Chat ID]
```

---

## Настройка GitHub Secrets

1. Перейди в **Settings → Secrets and variables → Actions**
2. Нажми **New repository secret**
3. Добавь все секреты из таблицы выше

### НОРМАЛЬНЫЕ НАСТРОЙКИ (Secrets)

| Name | Description | Example |
|------|-------------|----------|
| `YOUTUBE_API_KEY` | YouTube OAuth 2.0 credentials (base64) | `{"client_id": "...", "client_secret": "..."}` |
| `GOOGLE_AI_API_KEY` | Gemini API key | `AIzaSyDxxxxxxxxxxxxxx` |
| `GEMINI_TTS_ENABLED` | Enable Gemini TTS | `true` |
| `GEMINI_TTS_QUOTA_DAILY` | Daily quota for Gemini TTS | `150` |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token | `123456789:ABCDxxxxxxxxxxxx` |
| `TELEGRAM_CHAT_ID` | Telegram chat ID for notifications | `987654321` |
| `EDGE_TTS_ENABLED` | Enable Edge-TTS as fallback | `true` |
| `GITHUB_TOKEN` | GitHub token for API access | `ghp_xxxxxxxxxxxx` |

---

## Настройка Прожекта

### Папка ЕЮче в готовности

```
projects/youtube_horoscope/
├── config.yaml                 # Главная конфигурация
├── prompts/
│   ├── shorts_scenario.txt        # Генератор для шортов
│   ├── shorts_hooks.txt           # Набор хуков
│   ├── shorts_visual_hints.txt    # Визуальные навстки
│   ├── long_form_scenario.txt     # Людгосрочные видео
│   └── ads_product_script.txt     # Реклама в контенте
├── ads/                       # Папка рекламы
│   ├── products.yaml              # Список рекламируемых продуктов
│   └── assets/                    # Картинки/видео для рекламы
├── content_plan.json           # План контента на неделю
└── requirements.txt             # Python зависимости (доп за этот проект)
```

### Остановка Проякта Локально

```bash
# Клонируем
 git clone https://github.com/crosspostly/content-factory.git
 cd content-factory

# Останавливаем зависимости
 pip install -r requirements.txt

# Копируем .env.example в .env
 cp .env.example .env

# Открываем и заполняем все секреты
 nano .env
```

---

## Остановка Всех Утилит

### Основные зависимости

```bash
# AI/LLM
pip install google-generativeai ollama-python openai

# Аудио
 pip install pydub librosa edge-tts google-cloud-texttospeech

# Видео
pip install moviepy opencv-python imageio imageio-ffmpeg pillow

# Стоки
pip install pexels-api pixabay requests

# Субтитры
pip install openai-whisper faster-whisper ffsubsync

# YouTube
 pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client

# Утилиты
pip install pyyaml python-dotenv pydantic

# Telegram
pip install python-telegram-bot
```

### Системные утилиты

```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg imagemagick sox

# macOS
brew install ffmpeg imagemagick sox

# Windows (Chocolatey)
choco install ffmpeg imagemagick sox
```

---

## Запуск Генератора

### Локально

```bash
# Генерация сценария для шорта
python3 core/generators/script_generator.py --project youtube_horoscope --type shorts

# Генерация длинного видео
python3 core/generators/script_generator.py --project youtube_horoscope --type long_form
```

### GitHub Actions

Перейди в **Actions → Generate Video → Run Workflow**

---

## Торовление

### Проблема: Gemini TTS квота закончилась

**Решение**: Обратно свитчение на Edge-TTS (see config.yaml `fallback_if_gemini_quota_exceeded`)

### Проблема: YouTube upload error

**Решение**: Проверить OAuth 2.0 креденциалы, аутентификация

### Проблема: Video encoding takes too long

**Решение**: Уменьшите качество видео в config.yaml

---

## Следующие Шаги

1. Полная реализация Python-генератора (на следующем этапе)
2. Настройка GitHub Actions workflows
3. Тестирование в режиме dry-run
4. Первый запуск живого продукциа (жди Петя КО МОМ)

---

**Понравилось? ⭐ Ставь звезду!**
