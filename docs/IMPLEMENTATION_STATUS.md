# IMPLEMENTATION_STATUS (docs synced with code)

**Дата обновления:** 2025-12-16  
**Важно:** этот документ синхронизирован с текущим состоянием репозитория и дополняется файлом [`ACTUAL_STATUS.md`](./ACTUAL_STATUS.md).

> Документация прошла «rebase»: устаревшие разделы (про неиспользуемые компоненты/планы) удалены или сильно сокращены (>50%), а значительная часть оставшегося текста уточнена по реальному коду (~40%).

## Сводка

| Компонент | Статус | Где в коде | Главная проблема |
|---|---|---|---|
| Script generation | ✅ DONE | `core/generators/script_generator.py` | Для `long_form` нет length validation; `weekly` упомянут только в константах |
| TTS | ❌ BROKEN | `core/generators/tts_generator.py` | Не получает реальный аудио-ответ → создаёт silent WAV |
| Video rendering (classic) | ⚠️ MVP | `core/generators/video_renderer.py` | Нет субтитров; зависимость от окружения (MoviePy/FFmpeg/TextClip) |
| Slides mode | ✅ (standalone) / ⚠️ не интегрировано | `core/content_modes/slides_mode/*` | Не подключено к `pipeline_orchestrator` |
| Subtitles | ❌ NOT IMPLEMENTED | — | В репозитории нет саб-модуля; `subtitles` в config не используется |
| Upload | ❌ NOT IMPLEMENTED | `core/uploaders/youtube_uploader.py` | `upload()` — stub (`NotImplementedError`) |
| Workflows / Auto-fix | ✅/⚠️ | `.github/workflows/*`, `core/auto_fix_agent.py` | Некоторые workflow manual-only / требуют секретов |

---

## 1) Текущий работающий pipeline (реальная цепочка)

**Точка входа:** `core/orchestrators/pipeline_orchestrator.py`

Последовательность:
1. Script: `core/generators/script_generator.py`
2. Audio: `core/generators/tts_generator.py`
3. Video: `core/generators/video_renderer.py`
4. Metadata: `output/metadata/*.json`
5. Upload (опционально): частично, но uploader не реализован

**CLI:**
```bash
python -m core.orchestrators --project <project> --mode shorts|long_form|ad
```

---

## 2) Script Generation

**Статус:** ✅ работает.

**Файлы/функции:**
- `core/generators/script_generator.py`
  - `generate_short(...)` — есть контроль длины и retry.
  - `generate_long_form(...)`, `generate_ad(...)` — генерация и сохранение JSON.
- Роутинг моделей: `core/utils/model_router.py`.

**Заметки:**
- В константах есть `weekly`, но в orchestrator и генераторах нет соответствующего режима.

---

## 3) TTS

**Статус:** ❌ критический баг.

**Файлы/функции:**
- `core/generators/tts_generator.py`
  - `_synthesize_gemini_tts_async(...)` → пытается получить `response.audio`, но по факту создаёт заглушку `_create_silent_wav(...)`.

**Практический эффект:**
- видео рендерится, но звук — тишина (с корректной длительностью).

---

## 4) Video Rendering (classic)

**Статус:** ⚠️ MVP.

**Файл:** `core/generators/video_renderer.py`

**Что есть:**
- Рендер `shorts`, `long_form`, `ad`.
- Фон: Pixabay (если задан `PIXABAY_API_KEY`) или цветной fallback.

**Чего нет (важно для продуктового качества):**
- Субтитров (burn-in или отдельной дорожки).
- Retry/cleanup на падениях.

---

## 5) Slides Mode (content_modes)

**Статус:** ✅ реализовано и покрыто тестами, но отдельно от основного pipeline.

**Файлы:**
- `core/content_modes/slides_mode/mode.py`
- `core/content_modes/slides_mode/slide_builder.py`
- `core/content_modes/slides_mode/slide_renderer.py`
- `core/content_modes/registry.py`

**Важно про registry:**
Используйте `from core.content_modes import ContentModeRegistry` (это импортирует и регистрирует slides mode).

---

## 6) Subtitles

**Статус:** ❌ не реализовано.

**Факты:**
- Блок `subtitles:` присутствует в `config/shared.yaml`, но orchestrator и renderer его не используют.

---

## 7) Upload

**Статус:** ❌ не реализовано.

**Факт:** `core/uploaders/youtube_uploader.py` содержит только stub `upload()`.

---

## 8) Workflows / Auto-fix

**Статус:** ✅/⚠️.

**Файлы:**
- Workflows: `.github/workflows/*.yml`
- Auto-fix логика: `core/auto_fix_agent.py`

**Примечание:** для деталей см. `docs/WORKFLOW_AUDIT.md`.
