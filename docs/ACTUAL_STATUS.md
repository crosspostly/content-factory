# ACTUAL_STATUS (sync with code)

**Дата обновления:** 2025-12-16  
**Источник правды:** текущий репозиторий (ветка/код), а не исторические планы.

> Документация прошла «rebase»: устаревшие разделы про неиспользуемые компоненты удалены/сокращены (>50%), а существенная часть оставшегося текста уточнена по реальному коду (~40%).

## TL;DR (по подсистемам)

| Подсистема | Статус | Что именно (файлы/точки входа) | Блокеры / заметки |
|---|---|---|---|
| Scripts | ✅ Работает | `core/generators/script_generator.py` (`generate_short`, `generate_long_form`, `generate_ad`) | Для `long_form` нет проверки длины; в константах есть `weekly`, но режима/CLI нет |
| Orchestrator | ✅ Работает | `core/orchestrators/pipeline_orchestrator.py` (`main`, CLI) | Поддерживает только `--mode shorts|long_form|ad`; content-modes не подключены |
| TTS | ❌ Баг (реального голоса нет) | `core/generators/tts_generator.py` (`synthesize`, `_synthesize_gemini_tts_async`) | `generate_content()` не возвращает `response.audio` → создаётся **silent WAV** как заглушка |
| Video (classic renderer) | ⚠️ MVP (рендерит, но без субтитров) | `core/generators/video_renderer.py` (`render`, `_render_shorts/_render_long_form/_render_ad`) | Субтитров нет; высокая зависимость от окружения (MoviePy/FFmpeg/TextClip/ImageMagick); качество/стабильность Pixabay ограничены |
| Slides mode | ✅ Работает (standalone) / ⚠️ не интегрировано | `core/content_modes/slides_mode/*`, регистрация через `core/content_modes/registry.py` | В main pipeline не используется; для использования registry нужно импортировать `core.content_modes` (см. ниже) |
| Subtitles | ❌ Не реализовано | В репозитории нет генератора/встраивания субтитров | В `config/shared.yaml` есть блок `subtitles`, но pipeline его не читает |
| Upload | ❌ Не реализовано (stub) | `core/uploaders/youtube_uploader.py` | `upload()` всегда `raise NotImplementedError`; в orchestrator есть флаги `--upload/--platforms`, но YouTube сломан |
| Batch | ✅ Работает (поверх текущего pipeline) | `core/generators/batch_generator.py` (`generate_batch`) | Унаследует проблемы TTS/Video |
| Workflows | ✅/⚠️ (зависит от workflow) | `.github/workflows/*.yml` + `core/auto_fix_agent.py` | `ai-code-review.yml` фактически manual-only; автофикс требует API key |

---

## 1) Scripts (генерация сценариев)

**Статус:** ✅ работает.

**Код:**
- `core/generators/script_generator.py`
  - `generate_short(...)` — есть retry по длине (`MAX_LENGTH_ATTEMPTS`) и контроль MIN/MAX.
  - `generate_long_form(...)` — генерирует JSON и сохраняет, но без length validation.
  - `generate_ad(...)` — аналогично.
- Использует `core/utils/model_router.py` (`get_router(...).generate_json(...)`).

**Артефакты:**
- Скрипты сохраняются в `output/scripts/<project>/<YYYYMMDD>/*.json`.

**Реальные проблемы:**
- Константы `MIN_SCRIPT_LENGTH/MAX_SCRIPT_LENGTH` содержат `weekly`, но orchestrator/CLI режима `weekly` не имеют.

---

## 2) Orchestrator (основной пайплайн)

**Статус:** ✅ работает.

**Код:**
- `core/orchestrators/pipeline_orchestrator.py`
  - Step 1: script
  - Step 2: tts
  - Step 3: video
  - Step 4: metadata в `output/metadata/*.json`
  - Опционально: upload (частично, см. ниже)

**CLI:**
- `python -m core.orchestrators --project <name> --mode shorts|long_form|ad [--upload] [--platforms youtube,...]`

**Ограничения:**
- Никак не использует `core/content_modes/*` (slides mode не подключён).
- Не читает/не применяет `config.shared.yaml: subtitles`.

---

## 3) TTS

**Статус:** ❌ баг (видео получается без голоса).

**Код:**
- `core/generators/tts_generator.py`
  - `synthesize(...)` — синхронная обёртка над async.
  - `_synthesize_gemini_tts_async(...)` — пытается получить `response.audio` из `client.models.generate_content(...)`.

**Фактическое поведение:**
- При отсутствии аудио в ответе создаётся заглушка: `_create_silent_wav(...)`.

**Блокер:**
- Нужна замена/исправление интеграции TTS так, чтобы реально получать байты аудио и конвертировать их в WAV.

---

## 4) Video (classic renderer)

**Статус:** ⚠️ MVP.

**Код:**
- `core/generators/video_renderer.py`
  - `render(config, script, audio_map, mode)`
  - `_render_shorts`, `_render_long_form`, `_render_ad`

**Фактические ограничения:**
- Субтитров нет.
- Частично зависит от внешнего окружения (MoviePy/FFmpeg, шрифты, иногда ImageMagick для `TextClip`).
- Pixabay используется опционально (по `PIXABAY_API_KEY`), иначе fallback на цветной фон.

---

## 5) Slides mode (content_modes)

**Статус:** ✅ реализовано и тестируемо, но **не подключено** к основному orchestrator.

**Код:**
- `core/content_modes/slides_mode/slide_builder.py` — разбиение текста и расчёт длительности.
- `core/content_modes/slides_mode/slide_renderer.py` — рендер PNG слайдов.
- `core/content_modes/slides_mode/mode.py` — сборка видео (MoviePy).
- `core/content_modes/registry.py` — registry; регистрация происходит через декоратор `@register_mode("slides")` в `SlidesMode`.

**Правильный импорт для использования registry:**
```python
from core.content_modes import ContentModeRegistry  # важно: импортирует slides_mode и регистрирует
mode = ContentModeRegistry.get("slides")
```

---

## 6) Subtitles

**Статус:** ❌ не реализовано.

**Факты:**
- В коде нет шага генерации/встраивания субтитров.
- В `config/shared.yaml` есть блок `subtitles`, но он не используется orchestrator’ом.

---

## 7) Upload

**Статус:** ❌ не реализовано.

**Код:**
- `core/uploaders/youtube_uploader.py` — `upload(...)` всегда `raise NotImplementedError`.
- `core/orchestrators/pipeline_orchestrator.py` умеет дергать uploader при `--upload`, но это приведёт к исключению.

---

## 8) Workflows / Auto-fix

**Статус:** ✅/⚠️ зависит от workflow.

**Код:**
- `core/auto_fix_agent.py` — анализ логов, создание issue/PR через `gh` CLI.

**Workflows (файлы):**
- `.github/workflows/tests.yml`, `code-quality.yml` — базовые проверки.
- `.github/workflows/auto-fix-failures.yml` — автоанализ падений (требует корректных секретов/ключей).
- `.github/workflows/generate-batch.yml`, `generate-horoscope-video.yml` — генерация контента (manual).

---

## Что делать дальше (из текущего кода)

См.:
- [`docs/NEXT_STEPS.md`](./NEXT_STEPS.md)
- [`docs/DEVELOPMENT_ROADMAP.md`](./DEVELOPMENT_ROADMAP.md)
