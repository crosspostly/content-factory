# NEXT_STEPS (на базе текущего кода)

**Дата обновления:** 2025-12-16  
**Источник:** фактический код (см. [`ACTUAL_STATUS.md`](./ACTUAL_STATUS.md)).

> Документация прошла «rebase»: устаревшие разделы удалены/сокращены (>50%), а существенная часть уточнена по коду (~40%).

## 0) Цель ближайших 1–2 недель

Сделать так, чтобы основной pipeline генерировал **реальное озвученное** видео, а не silent placeholders, и подготовить основу для субтитров/публикации.

---

## 1) P0 — Исправить TTS (блокер)

**Почему:** сейчас `tts_generator` создаёт тишину → все видео по orchestrator «немые».

**Где:** `core/generators/tts_generator.py`

**Подзадачи:**
- [ ] Выделить текущую «точку поломки»: `_synthesize_gemini_tts_async(...)` никогда не получает `response.audio`.
- [ ] Выбрать реальный TTS backend и корректный формат ответа (байты аудио).
- [ ] Удалить silent WAV как default-path (оставить только как last-resort).
- [ ] Smoke-test: `python -m core.orchestrators --project youtube_horoscope --mode shorts` → видео с голосом.

---

## 2) P1 — Стабилизировать video_renderer

**Где:** `core/generators/video_renderer.py`

**Подзадачи:**
- [ ] Проверить закрытие ресурсов MoviePy (в идеале `close()` для клипов).
- [ ] Привести обработку Pixabay к предсказуемому поведению (при отсутствии ключа — чистый fallback).
- [ ] Добавить retry/cleanup стратегию (можно начать в orchestrator).

---

## 3) P1 — Subtitles MVP (без распознавания речи)

**Текущее состояние:** субтитров нет.

**Реалистичный MVP из текущих входных данных:**
- Генерировать субтитры из текста сценария.
- Тайминг распределять по длительности аудио (`audio_map["total_duration_sec"]`) и длине строк.
- Встраивать как burn-in (самый простой путь для Shorts).

**Где внедрять:** начать с `core/generators/video_renderer.py` (как опциональный шаг), позже вынести в отдельный модуль.

---

## 4) P2 — Подключить Slides mode к orchestrator

**Почему:** Slides mode реализован и протестирован, но не используется основным pipeline.

**Где:**
- `core/orchestrators/pipeline_orchestrator.py`
- `core/content_modes/slides_mode/*`

**Подзадачи:**
- [ ] Определиться с интерфейсом запуска (новый `--mode slides` или выбор по config).
- [ ] В orchestrator добавить ветку, которая использует `from core.content_modes import ContentModeRegistry`.

---

## 5) P2 — Upload MVP (YouTube)

**Текущее состояние:** `core/uploaders/youtube_uploader.py` — stub.

**Подзадачи:**
- [ ] Реализовать `upload(...)` или временно убрать `--upload` из пользовательских инструкций.
- [ ] В orchestrator явно логировать, что upload недоступен, если uploader не реализован.

---

## 6) Контроль актуальности документации

- [ ] При изменениях в pipeline обновлять `docs/ACTUAL_STATUS.md` как источник правды.
- [ ] Не добавлять в `/docs` ссылки на несуществующие модули/файлы: сначала код → потом документация.
