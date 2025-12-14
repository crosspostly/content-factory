# 🎬 Content Factory

## Что это?

Полностью автоматизированная система генерации видео-контента с помощью AI. Создаёт гороскопы для YouTube Shorts, длинные видео и рекламу. Работает в GitHub Actions без выделенного сервера.

## Установка

### 1. Клонирование проекта
```bash
git clone https://github.com/crosspostly/content-factory.git
cd content-factory
```

### 2. Установка зависимостей
```bash
python3.11 -m venv venv
source venv/bin/activate  # Linux/macOS
# или venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 3. Настройка API ключей
Добавьте в GitHub Secrets:
- `GOOGLE_AI_API_KEY` - ключ от https://ai.google.dev (для Gemini 2.5 Flash)
- `PIXABAY_API_KEY` - ключ от https://pixabay.com/api
- `TELEGRAM_BOT_TOKEN` - токен от @BotFather (опционально)
- `TELEGRAM_CHAT_ID` - ваш Telegram ID (опционально)

## Быстрый старт

### Генерация одного видео
```bash
python -m core.orchestrators.pipeline_orchestrator \
  --project youtube_horoscope \
  --mode shorts \
  --date 2025-12-13
```

### Пакетная генерация
```bash
python -m core.generators.batch_generator \
  --project youtube_horoscope \
  --start-date 2025-12-13 \
  --num-days 7 \
  --mode shorts
```

## Конфигурация

Создайте проект в папке `projects/`:

```yaml
# projects/youtube_horoscope/config.yaml
project:
  name: "YouTube Гороскопы"
  folder: "youtube_horoscope"
  language: "russian"
  target_audience: "Женщины 18-45"

generation:
  models:
    primary: "gemini-2.0-flash-exp"
    fallback: "gemini-1.5-flash"
  prompt_files:
    shorts_script: "prompts/shorts_scenario.txt"
    long_form_script: "prompts/long_form_scenario.txt"

audio:
  engines:
    edge-tts:
      voice: "ru-RU-SvetlanaNeural"
      speed: 1.0

upload:
  platforms:
    youtube:
      enabled: true
    telegram:
      enabled: true
```

## CLI команды

### Основные команды

| Команда | Описание | Пример |
|---------|----------|--------|
| `--project` | Название проекта | `youtube_horoscope` |
| `--mode` | Тип контента | `shorts`, `long_form`, `ad` |
| `--date` | Дата контента | `2025-12-13` |
| `--product-id` | ID продукта (для рекламы) | `horoscope_premium` |

### Полный pipeline
```bash
# Создание видео полного цикла
python -m core.orchestrators.pipeline_orchestrator \
  --project youtube_horoscope \
  --mode shorts \
  --date 2025-12-13
```

### Только генерация скриптов
```bash
# Для тестирования
python -m core.generators.script_generator \
  --project youtube_horoscope \
  --mode shorts \
  --date 2025-12-13
```

## Выходные файлы

После генерации получите:

### Скрипты
- `output/scripts/{project}/{date}/script_{uuid}.json`
- Содержит текст, хуки, визуальные подсказки

### Аудио
- `output/audio/{project}/{mode}.wav`
- 22050Hz, моно, русские голоса Edge-TTS

### Видео
- `output/videos/{project}/{mode}.mp4`
- Shorts: 1080x1920 (9:16)
- Long-form: 1920x1080 (16:9)

### Метаданные
- `output/metadata/{date}_{mode}.json`
- Статистика API, длительность, пути к файлам

## Решение проблем

### Топ-3 ошибки:

#### 1. `GOOGLE_AI_API_KEY not set`
**Решение**: Проверьте GitHub Secrets в настройках репозитория

#### 2. `Config file is empty`
**Решение**: Убедитесь что `projects/{project}/config.yaml` существует и не пустой

#### 3. `Project name is required`
**Решение**: Добавьте `project.name` в конфигурацию проекта

### Логи и отладка
```bash
# Просмотр логов
tail -f output/logs/{project}/{date}.log

# Проверка конфигурации
python -c "
from core.utils.config_loader import load
config = load('youtube_horoscope')
print(config.project.name)
"
```

### GitHub Actions
- Проверьте вкладку `Actions` для статуса
- Скачайте артефакты с логами
- Убедитесь что все API ключи добавлены

---

**Поддержка**: Создайте Issue в репозитории для помощи