# ⚡ QUICK ACTION LIST

## ШАГ 1: Добавить GitHub Secrets (5 мин)

Перейти: **https://github.com/crosspostly/content-factory/settings/secrets/actions**

Нажать **"New repository secret"** для каждого:

### ОБЯЗАТЕЛЬНЫЕ (Part 2 + 3):

```
Secret 1:
Name: GOOGLE_AI_API_KEY
Value: [Получить с https://ai.google.dev → API Keys]

Secret 2:
Name: OPENROUTER_API_KEY
Value: [Получить с https://openrouter.ai → API Keys (fallback)]

Secret 3:
Name: PIXABAY_API_KEY
Value: [Получить с https://pixabay.com/api → API Documentation]

Secret 4:
Name: TELEGRAM_BOT_TOKEN
Value: [Получить от @BotFather в Telegram]

Secret 5:
Name: TELEGRAM_CHAT_ID
Value: [Получить от @userinfobot в Telegram]
```

---

## ШАГ 2: Запустить AI агента на Part 2 + 3

**ПРОЧИТАЙ ФАЙЛ:** `PART2_PART3_CRITICAL_TZ.md` в репозитории

**ДАЙ АГЕНТУ ЭТОТ ПРОМПТ:**

```
Задача: Реализовать Part 2 (TTS) и Part 3 (Video Rendering) для Content Factory.

Полное техническое задание находится в файле: PART2_PART3_CRITICAL_TZ.md

ОБЯЗАТЕЛЬНО ИЗУЧИ:
1. Раздел "GOOGLE GEMINI API - РЕАЛЬНЫЕ МОДЕЛИ (Dec 2025)"
2. Раздел "GITHUB ACTIONS: Кеширование зависимостей"
3. Раздел "REQUIREMENTS.TXT - ОБНОВИТЬ"

Требуется обновить 4 файла:

1️⃣ requirements.txt
   - Добавить: edge-tts, moviepy, imageio-ffmpeg, pillow
   
2️⃣ projects/youtube_horoscope/config.yaml
   - ТОЛЬКО эти модели (NO DEPRECATED!):
     * gemini-2.5-flash (основная, быстрая)
     * gemini-2.5-flash-lite (самая дешевая)
     * gemini-2.5-pro (самая умная, медленнее)
   
3️⃣ core/generators/tts_generator.py
   - Edge-TTS интеграция (ru-RU-DariyaNeural)
   - Асинхронный синтез (asyncio)
   - Сохранение в WAV (22050 Hz, mono)
   
4️⃣ core/generators/video_renderer.py
   - moviepy для композиции видео
   - Pixabay API для фоновых видео
   - Shorts (1080x1920), long_form (1920x1080), ad (1080x1920)
   - H.264 кодец, 30fps

5️⃣ .github/workflows/part1-test.yml
   - Добавить кеширование pip
   - FFmpeg кеш между запусками

Все детали в PART2_PART3_CRITICAL_TZ.md!
```

---

## ШАГ 3: После AI агента - локальный тест

```bash
# 1. Пулл изменений
git pull origin main

# 2. Обновить зависимости
pip install -r requirements.txt

# 3. Тест Part 2 (TTS)
python -c "
from core.generators.tts_generator import TTSGenerator
from core.utils.config_loader import load_project_config

config = load_project_config('youtube_horoscope')
tts = TTSGenerator(config)

result = tts.synthesize(
    text='Привет, это тест синтеза речи на русском языке',
    output_file='test_audio.wav'
)
print('✅ TTS результат:', result)
"

# 4. Тест Part 3 (Video)
python -c "
from core.generators.video_renderer import VideoRenderer
from core.utils.config_loader import load_project_config

config = load_project_config('youtube_horoscope')
renderer = VideoRenderer(config)

result = renderer.render_shorts(
    audio_path='test_audio.wav',
    script_data={'hook': 'Тестовое видео!'},
    output_path='test_video.mp4'
)
print('✅ Video результат:', result)
"

# 5. Полный pipeline
python -m core.orchestrators.pipeline_orchestrator \
  --project youtube_horoscope \
  --mode shorts

# 6. Проверить результаты
ls -lah output/videos/youtube_horoscope/
ls -lah output/audio/youtube_horoscope/
```

---

## 🎬 ОЖИДАЕМЫЕ РЕЗУЛЬТАТЫ

После всех шагов:

```
✅ output/scripts/youtube_horoscope/20251212/short_*.json
   (Скрипты от Gemini)

✅ output/audio/youtube_horoscope/shorts_main.wav
   (Реальное аудио 22050 Hz, mono, женский русский голос)

✅ output/videos/youtube_horoscope/shorts.mp4
   (1080x1920 вертикальное видео, 30fps, H.264)
```

---

**Статус:** 🔴 IN PROGRESS (ждём AI агента на Part 2 + 3)
