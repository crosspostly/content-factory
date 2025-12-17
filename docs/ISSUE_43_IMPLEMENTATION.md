# Issue #43 Implementation — Slides Mode (fact check)

**Дата обновления:** 2025-12-16  

> Документация прошла «rebase»: устаревшие разделы удалены/сокращены (>50%), а существенная часть уточнена по коду (~40%).

## Что просила задача

Реализовать «Slides Mode» — модульный режим генерации видео-карусели из текста.

## Что реально реализовано в репозитории

### 1) Система content_modes (минимальный plugin-скелет)

**Код:**
- `core/content_modes/base.py` — базовый интерфейс и `GenerationResult`.
- `core/content_modes/registry.py` — registry + декоратор `register_mode(...)`.

### 2) Slides mode

**Код:**
- `core/content_modes/slides_mode/slide_builder.py` — текст → список слайдов с длительностью.
- `core/content_modes/slides_mode/slide_renderer.py` — слайд → PNG.
- `core/content_modes/slides_mode/mode.py` — PNG + (опционально) аудио → MP4.

Режим регистрируется декоратором:
- `@register_mode("slides")` в `SlidesMode`.

### 3) Тесты

Есть тесты для Slides mode:
- `tests/test_slides_mode.py`

---

## Что НЕ сделано (важно)

- Slides mode **не интегрирован** в основной orchestrator (`core/orchestrators/pipeline_orchestrator.py`).
- Нет встроенного TTS в Slides mode (а основной TTS в classic pipeline сейчас сломан — создаёт тишину).
- Transition’ы кроме `fade` не реализованы.

---

## Как корректно использовать registry

Чтобы режим `slides` был зарегистрирован, импортируйте registry через пакет `core.content_modes`:

```python
from core.content_modes import ContentModeRegistry

mode = ContentModeRegistry.get("slides", variant="carousel")
```

Если импортировать только `core.content_modes.registry`, вы можете не получить зарегистрированный `slides` (в зависимости от порядка импортов).

---

## Связанные документы

- [`docs/SLIDES_MODE_GUIDE.md`](./SLIDES_MODE_GUIDE.md)
- [`docs/MODES_ARCHITECTURE.md`](./MODES_ARCHITECTURE.md)
- [`docs/ACTUAL_STATUS.md`](./ACTUAL_STATUS.md)
