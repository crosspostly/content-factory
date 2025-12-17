# Slides Mode Guide (актуально по коду)

**Дата обновления:** 2025-12-16  
**Статус реализации:** Slides mode реализован в `core/content_modes/slides_mode/*`, но **не подключён** к `core/orchestrators/pipeline_orchestrator.py`.

> Документация прошла «rebase»: устаревшие разделы удалены/сокращены (>50%), а существенная часть уточнена по коду (~40%).

## 1) Что такое Slides mode

Slides mode — это режим генерации видео, который:
1) разбивает текст на «слайды»,
2) рендерит каждый слайд в PNG,
3) склеивает PNG в MP4 (MoviePy),
4) (опционально) подмешивает аудио на уровне отдельных слайдов.

**Код:**
- `core/content_modes/slides_mode/slide_builder.py`
- `core/content_modes/slides_mode/slide_renderer.py`
- `core/content_modes/slides_mode/mode.py`

---

## 2) Быстрый старт

### 2.1 Использование через registry

Важно: чтобы режим `slides` был зарегистрирован, удобнее импортировать registry через пакет `core.content_modes` (он импортирует реализации режимов).

```python
from pathlib import Path
from core.content_modes import ContentModeRegistry

mode = ContentModeRegistry.get("slides", variant="carousel")
result = await mode.generate(
    scenario="Текст для слайдов. Второе предложение. Третье.",
    audio_map={},
    config={
        "width": 1080,
        "height": 1920,
        "background_color": "#2B1B3D",
        "text_color": "white",
        "font_size": 70,
        "fps": 30,
        "bitrate": "5000k",
        "transitions": {"type": "fade", "duration": 0.5},
    },
    output_dir=Path("output/slides_demo"),
)
print(result.video_path)
```

### 2.2 Использование напрямую

```python
from pathlib import Path
from core.content_modes.slides_mode.mode import SlidesMode

mode = SlidesMode(variant="carousel")
result = await mode.generate(
    scenario="...",
    audio_map={},
    config={...},
    output_dir=Path("output/slides_demo"),
)
```

---

## 3) Компоненты

### 3.1 SlideBuilder

**Файл:** `core/content_modes/slides_mode/slide_builder.py`

- Разбиение текста на части по `.`, `!`, `\n`.
- Ограничение `max_chars_per_slide`.
- Расчёт длительности: `duration = char_count / 2.5`, затем clamp в `[min_duration, max_duration]`.

### 3.2 SlideRenderer

**Файл:** `core/content_modes/slides_mode/slide_renderer.py`

- Рендер PNG с переносами строк, выравниванием и цветами.

### 3.3 SlidesMode

**Файл:** `core/content_modes/slides_mode/mode.py`

- Склейка PNG в видео.
- Поддержка простой transition `fade`.

---

## 4) Конфигурация

Проектный пример (существует в репозитории): `projects/horoscope_leo/config.yaml`.

Ключи, которые реально использует `SlidesMode.generate(...)`, передаются через аргумент `config`:

- `width`, `height`
- `background_color`, `text_color`
- `font_size`, `font_family`
- `fps`, `bitrate`
- `transitions: {type, duration}`

---

## 5) Аудио

`audio_map` — словарь вида `{ "текст_слайда": "/path/to/audio.wav" }`.

Поведение:
- если для слайда найден аудиофайл, длительность слайда становится `max(slide.duration, audio.duration)`.
- если аудио не найдено, используется рассчитанная длительность.

---

## 6) Ограничения / Known issues

- Slides mode не подключён к основному CLI orchestrator.
- Transition’ы кроме `fade` не реализованы.
- Нет встроенного TTS внутри Slides mode (ожидается внешний генератор).

См. также:
- [`docs/ISSUE_43_IMPLEMENTATION.md`](./ISSUE_43_IMPLEMENTATION.md)
- [`docs/MODES_ARCHITECTURE.md`](./MODES_ARCHITECTURE.md)
