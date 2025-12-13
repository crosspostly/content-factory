# 🎬 Content Modes System - Полный гайд

## 📖 Содержание

1. [Суть системы](#-суть-системы)
2. [Как это работает](#-как-это-работает)
3. [Встроенные режимы](#-встроенные-режимы)
4. [Использование](#-использование)
5. [Добавление нового режима](#-добавление-нового-режима)
6. [Архитектура](#-архитектура)
7. [FAQ](#-faq)

---

## 💡 Суть системы

**Content Modes** — это модульная система для автоматической генерации видео разного типа.

### Проблема ❌
```
- Ручное управление каждый день
- Один способ генерации для всех
- Сложно добавлять новые типы
- Много параметров в workflow
```

### Решение ✅
```yaml
# Один раз указываешь в конфиге:
generation:
  mode: "shorts_carousel"

# Система автоматически:
# - Выбирает нужный режим
# - Генерирует видео каждый день
# - Легко добавлять новые типы
```

---

## 🔄 Как это работает

### Шаг 1: Ты указываешь тип контента
```yaml
# projects/youtube_horoscope/config.yaml
project:
  name: "YouTube Horoscope"

generation:
  mode: "shorts_carousel"          # ← Выбираешь один раз
  duration: 15
  resolution: "1080x1920"

content_config:
  slides_count: 5
  transition: "fade"
  text_animation: "slideIn"
```

### Шаг 2: Система находит режим
```python
from core.content_modes import get_mode

# Автоматически находит ShortsCarouselMode
mode = get_mode("shorts_carousel")
```

### Шаг 3: Генерирует видео по логике режима
```python
# Каждый режим знает как генерировать:
result = mode.generate(scenario, audio_map, config)

# Выход: /output/video.mp4
```

---

## 🎥 Встроенные режимы

### 1️⃣ `shorts_carousel` — Карусель слайдов

**Лучше всего для:**
- YouTube Shorts (60 сек)
- TikTok Reels
- Instagram Reels
- Быстрые видео (5-20 слайдов)

**Примеры:**
- 📅 Гороскопы (знаки зодиака)
- 💡 Советы/Tips (5-10 советов)
- 📰 Новости (каждая новость = слайд)
- 😂 Мемы/Приколы
- 🎓 Топы/Рейтинги

**Конфиг:**
```yaml
generation:
  mode: "shorts_carousel"
  duration: 15
  resolution: "1080x1920"

content_config:
  slides_count: 5
  transition: "fade"           # fade, slide, zoom, bounce
  text_animation: "slideIn"    # fadeIn, slideIn, bounce, none
  background_type: "solid"     # solid, gradient, image
  slide_duration: 3            # сек на слайд
```

**Скорость:** 5-10 сек рендеринга

---

### 2️⃣ `animation_ai` — Анимированные видео

**Лучше всего для:**
- Красивые анимированные видео
- Демонстрация процессов
- Сложные визуализации
- Интерактивные элементы

**Примеры:**
- 🎨 Дизайн-демонстрации
- 📊 Диаграммы и графики
- 🎬 Интро/Outro
- 🎮 Визуальные эффекты
- ✨ Анимированные истории

**Конфиг:**
```yaml
generation:
  mode: "animation_ai"
  duration: 20
  resolution: "1080x1920"

content_config:
  animation_style: "bounce"    # bounce, fade, slide, zoom
  scene_count: 3               # сцены
  scene_duration: 5            # сек на сцену
  background: "gradient"       # solid, gradient, video
```

**Скорость:** 10-30 сек рендеринга

---

### 3️⃣ `text_stock` — Текст + Стоковое видео

**Лучше всего для:**
- Статейные видео (5-15 минут)
- Новостные видео
- Обзоры с фоновым видео
- Образовательный контент

**Примеры:**
- 📰 Новостные сюжеты
- 🎓 Образовательные видео
- 📚 Чтение статей
- 💼 Бизнес-презентации
- 🌍 Туристические гайды

**Конфиг:**
```yaml
generation:
  mode: "text_stock"
  duration: 60
  resolution: "1080x1920"

content_config:
  background_source: "pexels"  # pexels, pixabay, unsplash
  text_position: "bottom"      # top, bottom, center
  text_size: "large"           # small, medium, large
  text_color: "#FFFFFF"
```

**Скорость:** 20-60 сек

---

## 💻 Использование

### Способ 1: Автоматическая генерация (Рекомендуется)

Просто добавь в конфиг:
```yaml
generation:
  mode: "shorts_carousel"

content_config:
  slides_count: 5
  transition: "fade"
```

✅ Видео генерируется автоматически каждый день в 6:00 UTC

---

### Способ 2: CLI

```bash
# Список режимов
python -m core.content_modes.cli list

# Информация о режиме
python -m core.content_modes.cli info shorts_carousel

# Генерировать видео
python -m core.content_modes.cli generate \
  --project youtube_horoscope \
  --mode shorts_carousel \
  --date 2025-12-13
```

---

### Способ 3: GitHub Actions (вручную)

Actions → Run workflow → Run

---

### Способ 4: Python код

```python
from core.content_modes import get_mode
from core.utils.config_loader import ProjectConfig

config = ProjectConfig.load("youtube_horoscope")
mode = get_mode(config.generation.mode)
result = mode.generate(scenario, audio_map, config)

print(f"✅ Готово: {result['video_path']}")
```

---

## 🚀 Добавление нового режима (10 минут)

### Шаг 1: Создать класс

```python
# core/content_modes/my_mode/mode.py
from core.content_modes.base_mode import BaseContentMode

class MyCustomMode(BaseContentMode):
    mode_id = "my_custom_mode"
    display_name = "My Custom Mode"
    
    def validate(self, config) -> None:
        """Проверить конфиг"""
        pass
    
    def generate(self, scenario, audio_map, config):
        """Основной метод генерации"""
        # 1. Генерировать контент
        # 2. Подготовить визуалы
        # 3. Собрать видео
        return {
            "video_path": "...",
            "duration": config.generation.duration,
            "resolution": config.generation.resolution,
        }
    
    def get_schema(self):
        """Схема конфига"""
        return {"my_param": {"type": "string"}}
    
    def get_required_apis(self):
        """Требуемые API"""
        return ["GOOGLE_AI_API_KEY"]
    
    def get_required_tools(self):
        """Требуемые инструменты"""
        return ["ffmpeg", "nodejs"]
```

### Шаг 2: Зарегистрировать

```python
# core/content_modes/__init__.py
from core.content_modes.my_mode.mode import MyCustomMode

register_mode(MyCustomMode())
```

### Шаг 3: Использовать

```yaml
generation:
  mode: "my_custom_mode"

content_config:
  my_param: "value"
```

### Шаг 4: Готово! 🎉

```bash
python -m core.content_modes.cli info my_custom_mode
python -m core.content_modes.cli generate --project X --mode my_custom_mode
```

---

## 🏗️ Архитектура

### Поток данных

```
Config (YAML)
    ↓
ContentModeRegistry.get(mode_id)
    ↓
Mode.validate(config)
    ↓
Mode.generate(scenario, audio, config)
    ↓
VideoFile (MP4)
```

### Класс иерархия

```
BaseContentMode (ABC)
├── ShortsCarouselMode
├── AnimationAIMode
├── TextStockMode
└── YourCustomMode
```

---

## ❓ FAQ

**Q: Один проект = один режим?**
A: Да, один проект использует один режим. Разные видео = разные проекты.

**Q: Как добавить кастомные параметры?**
A: Добавь в `content_config` и опиши в `get_schema()`.

**Q: Можно ли комбинировать режимы?**
A: Нет, но можно создать новый режим, объединяющий логику нескольких.

**Q: Как отладить?**
A: Используй `--verbose`:
```bash
python -m core.content_modes.cli generate --project X --mode Y --verbose
```

**Q: Что если генерация падает?**
A: Проверь логи в `logs/`, API ключи, системные инструменты, конфиг.

**Q: Как отключить автоматическую генерацию?**
A: Удали или отключи workflow в `.github/workflows/auto-generate-videos.yml`

**Q: Как интегрировать с публикацией?**
A: После `mode.generate()` используй YouTube/TikTok API:
```python
result = mode.generate(...)
publish_to_youtube(result["video_path"], title, description)
```

---

## 📚 Документация

- **Issue #24** — Полное описание: https://github.com/crosspostly/content-factory/issues/24
- **IMPLEMENTATION_COMPLETE.md** — Статус реализации
- **core/content_modes/README.md** — Техническое описание

---

**Готово к использованию!** 🚀
