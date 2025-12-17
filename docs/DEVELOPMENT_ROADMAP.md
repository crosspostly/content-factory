# DEVELOPMENT_ROADMAP (основано на текущем коде)

**Дата обновления:** 2025-12-16  
**Фокус:** roadmap выведен из реального состояния репозитория (см. [`ACTUAL_STATUS.md`](./ACTUAL_STATUS.md)), без исторических планов.

> Документация прошла «rebase»: устаревшие разделы удалены/сокращены (>50%), а существенная часть уточнена по коду (~40%).

## 0) Главные блокеры (P0)

1. **TTS не генерирует голос** → все видео по основному pipeline «немые».
   - Код: `core/generators/tts_generator.py` (`_synthesize_gemini_tts_async`, `_create_silent_wav`).
2. **Нет субтитров** (и нет механизма их генерации/встраивания).
   - Код: в `core/generators/video_renderer.py` отсутствуют любые subtitle-шаги.
3. **Upload не реализован** — в orchestrator есть флаги, но uploader stub.
   - Код: `core/uploaders/youtube_uploader.py`.

---

## 1) Phase 1 — Fix core pipeline to be “real video” (1–2 недели)

### 1.1 Fix TTS (P0)

**Цель:** `tts_generator.synthesize(...)` должен создавать не silent WAV, а реальный звук.

**Куда менять:**
- `core/generators/tts_generator.py`

**Definition of Done:**
- в коде нет fallback’а на “тишину” как нормального happy-path;
- smoke-run pipeline создаёт видео с голосом;
- корректные sample rate/channels сохраняются.

### 1.2 Stabilize video render (P1)

**Цель:** уменьшить вероятность падений и зависимость от окружения.

**Куда менять:**
- `core/generators/video_renderer.py`

**Идеи улучшений:**
- предсказуемое закрытие ресурсов MoviePy (`close()`);
- добавить retry (в orchestrator или внутри renderer);
- нормализовать обработку TextClip fallback (уже есть PIL fallback).

---

## 2) Phase 2 — Subtitles MVP (1–2 недели после TTS)

**Текущее состояние:** subtitles не реализованы.

**Рекомендованный MVP-подход (из текущих данных pipeline):**
- генерировать субтитры **из текста сценария**, а не из распознавания речи;
- тайминг распределять пропорционально длине текста и длительности аудио (она уже есть в `audio_map["total_duration_sec"]`).

**Куда интегрировать:**
- минимально — прямо в `core/generators/video_renderer.py` как опциональный шаг (burn-in);
- включение через конфиг (например, использовать уже существующий блок `subtitles` в `config/shared.yaml`).

---

## 3) Phase 3 — Integrate Slides mode into orchestrator (1 неделя)

**Текущее состояние:** Slides mode реализован (`core/content_modes/slides_mode/*`), но main pipeline его не использует.

**Цель:** дать возможность запускать generation через `pipeline_orchestrator` для `slides`-проекта (например, `projects/horoscope_leo`).

**Куда менять:**
- `core/orchestrators/pipeline_orchestrator.py`
- `core/utils/config_loader.py` (если потребуется нормализация ключей)

**Варианты:**
- добавить отдельный `--mode slides` (или `--video-mode slides`),
- или переключать режим через config (`video_mode: slides`) и выбирать нужный runner.

---

## 4) Phase 4 — Upload MVP (YouTube) (1–2 недели)

**Текущее состояние:**
- orchestrator умеет вызвать upload, но `core/uploaders/youtube_uploader.py` — stub.

**Цель:** реализовать YouTube upload хотя бы для локального/ручного запуска.

**Куда менять:**
- `core/uploaders/youtube_uploader.py`
- `core/orchestrators/pipeline_orchestrator.py` (обработка ошибок/результатов)

---

## 5) Phase 5 — Reliability / housekeeping (параллельно)

- Привести конфиги к фактическому использованию: `config/shared.yaml` содержит `subtitles`, `caching`, но код их не применяет.
- Удалить/переосмыслить `weekly` из `script_generator.py` либо добавить соответствующий режим в orchestrator.
- Проверить вспомогательные скрипты (например, `scripts/test_horoscope_leo.py`) на актуальность импортов/API.

---

## 6) Workflows / Auto-fix

**Факт:** workflow уже существуют (tests/code-quality/auto-fix/generation). Roadmap по ним должен опираться на текущие файлы:
- `.github/workflows/tests.yml`
- `.github/workflows/code-quality.yml`
- `.github/workflows/auto-fix-failures.yml`
- код агента: `core/auto_fix_agent.py`

Цель: не добавлять «ещё один CI», а поддерживать текущие workflow рабочими.
