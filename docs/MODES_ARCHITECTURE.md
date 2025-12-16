# MODES_ARCHITECTURE (актуальная архитектура режимов)

**Дата обновления:** 2025-12-16  
**Источник:** текущий код (см. [`ACTUAL_STATUS.md`](./ACTUAL_STATUS.md)).

> Документация прошла «rebase»: устаревшие разделы удалены/сокращены (>50%), а существенная часть уточнена по коду (~40%).

## 0) Два «мира» в текущем репозитории

Сейчас в проекте фактически существуют **две** параллельные архитектуры генерации видео:

1. **Classic pipeline (используется в прод-скриптах/CLI):**
   - `pipeline_orchestrator` → `script_generator` → `tts_generator` → `video_renderer`
2. **Content modes (реализовано, но пока не подключено к orchestrator):**
   - `core/content_modes/*` (в т.ч. `slides`)

Это важно, потому что документация режимов должна говорить, **какой путь реально используется**.

---

## 1) Classic pipeline: modes = shorts / long_form / ad

**Точка входа:** `core/orchestrators/pipeline_orchestrator.py`

```
Config (shared + project)
   ↓
Script generator (mode: shorts|long_form|ad)
   ↓
TTS (audio_map)
   ↓
Video renderer (mode: shorts|long_form|ad)
   ↓
output/videos/... + output/metadata/...
```

### 1.1 Script modes

**Код:** `core/generators/script_generator.py`
- `generate_short(...)`
- `generate_long_form(...)`
- `generate_ad(...)`

### 1.2 Video modes

**Код:** `core/generators/video_renderer.py`
- `_render_shorts(...)` — 9:16
- `_render_long_form(...)` — 16:9, блоки love/money/health
- `_render_ad(...)` — 9:16

### 1.3 Что НЕ входит в classic pipeline

- Subtitles (нет шага генерации/встраивания).
- Реальный Upload (uploader stub).
- Slides mode (content_modes).

---

## 2) Content modes: slides

**Цель подсистемы:** дать плагиноподобный механизм разных способов генерации видео.

**Код:**
- `core/content_modes/base.py` — интерфейс режима + `GenerationResult`.
- `core/content_modes/registry.py` — registry и декоратор `register_mode(...)`.
- `core/content_modes/slides_mode/*` — реализация режима `slides`.

**Важно:**
- регистрация режима происходит при импорте `SlidesMode` (через декоратор).
- для корректного использования через registry удобнее импортировать:
  ```python
  from core.content_modes import ContentModeRegistry
  mode = ContentModeRegistry.get("slides")
  ```

---

## 3) Конфигурация

### 3.1 Как реально грузится конфиг

**Код:** `core/utils/config_loader.py`
- Загружает `projects/<project>/config.yaml|yml|json`
- Мержит с `config/shared.yaml` (если он существует)
- Даёт dot-access через `ConfigNode`

### 3.2 Что важно знать про ключи

- В `config/shared.yaml` есть блоки `subtitles`, `caching` и т.п., но на текущий момент они **не применяются** orchestrator’ом и classic renderer’ом.
- Проект `projects/horoscope_leo/config.yaml` содержит `video_mode: slides`, но orchestrator эти ключи не использует (slides запускается отдельно).

---

## 4) Что делать с «двумя мирами» дальше

Рекомендуемое направление (см. `docs/DEVELOPMENT_ROADMAP.md`):
1) стабилизировать TTS+classic pipeline (чтобы было «реальное видео»);
2) затем решить: либо переносить classic renderer в content_modes, либо постепенно подключать content_modes (slides) к orchestrator.
