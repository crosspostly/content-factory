# 🎬 Content Factory - AI-Powered Multi-Platform Content Machine

> **Фабрика контента, работающая на GitHub Actions. Генерирует видео и контент для YouTube, TikTok, Instagram, VK с поддержкой Gemini, Edge-TTS, стоками и масштабируемыми проектами.**

![Version](https://img.shields.io/badge/version-2.2-blue)
![Status](https://img.shields.io/badge/status-Part%202%20TTS%20Implementation-yellowgreen)
![License](https://img.shields.io/badge/license-MIT-orange)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)

---

## 🚀 STATUS: Part 2 TTS Implementation 🔜

### Current Phase: **Edge-TTS + Video Rendering**

✅ **COMPLETED:**
- [x] Config loader (stdlib YAML parser - zero dependencies!)
- [x] LLM routing (Gemini → Ollama → OpenRouter with fallbacks)
- [x] Pipeline orchestrator (CLI interface, dry-run mode)
- [x] Logging & error handling (file + console + Telegram alerts)
- [x] Script generator with file saving ✅
- [x] GitHub Actions workflow (fixed YAML syntax)

🔜 **IN PROGRESS (Part 2 + 3):**
- [ ] TTS Generator (Edge-TTS integration) — реальное создание аудио
- [ ] Video Renderer (moviepy + ffmpeg) — композиция видео
- [ ] Pixabay/Pexels API интеграция — стоки видео

❌ **TODO (Part 4 + 5):**
- [ ] YouTube/TikTok/VK uploaders
- [ ] Scheduling & automation
- [ ] Real LLM script generation (Part 3)

---

## 🛣️ Roadmap

```
┌─ Part 1: Foundation ✅ DONE
│  ├─ Config system ✅
│  ├─ LLM/TTS routing ✅
│  ├─ CLI orchestrator ✅
│  ├─ Script generator + saving ✅
│  └─ GitHub Actions ✅
│
├─ Part 2: TTS Implementation 🔜 IN PROGRESS
│  ├─ Edge-TTS (ru-RU-DariyaNeural)
│  ├─ WAV generation (22050 Hz, mono)
│  └─ Audio block synthesis
│
├─ Part 3: Video Rendering 🔜 NEXT
│  ├─ moviepy/ffmpeg integration
│  ├─ Pixabay video API
│  ├─ Shorts (1080x1920)
│  ├─ Long-form (1920x1080)
│  └─ Ad (1080x1920)
│
├─ Part 4: Platform Uploaders 🔮 FUTURE
│  ├─ YouTube API v3
│  ├─ TikTok API
│  ├─ VK API
│  └─ Instagram API
│
└─ Part 5: Scheduling & Automation 🔮 FUTURE
   ├─ Cron jobs
   ├─ GitHub Actions scheduler
   └─ Telegram bot control
```

---

## 📋 QUICK START

### Setup (5 мин)

```bash
# 1. Clone repo
git clone https://github.com/crosspostly/content-factory.git
cd content-factory

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file
cp .env.example .env
# Edit .env with your API keys

# 4. Run dry-run test
python -m core.orchestrators.pipeline_orchestrator \
  --project youtube_horoscope \
  --mode shorts \
  --dry-run
```

### Full Pipeline

```bash
# Generate shorts with all steps: script → audio → video
python -m core.orchestrators.pipeline_orchestrator \
  --project youtube_horoscope \
  --mode shorts

# Generate long-form
python -m core.orchestrators.pipeline_orchestrator \
  --project youtube_horoscope \
  --mode long_form

# Check output
ls -lah output/videos/youtube_horoscope/
ls -lah output/audio/youtube_horoscope/
```

---

## 🔐 GitHub Secrets (Требуемые)

### ОБЯЗАТЕЛЬНЫЕ для Part 2 + 3

| Secret Name | Значение | Где получить | Для чего |
|------------|---------|-------------|----------|
| `GOOGLE_AI_API_KEY` | API Key | [ai.google.dev](https://ai.google.dev) | Gemini LLM (текст скриптов) |
| `OPENROUTER_API_KEY` | API Key | [openrouter.ai](https://openrouter.ai) | Fallback LLM (если Gemini недоступен) |
| `PIXABAY_API_KEY` | API Key | [pixabay.com/api](https://pixabay.com/api) | Стоки видео для shorts/фона |
| `TELEGRAM_BOT_TOKEN` | Token | [@BotFather](https://t.me/BotFather) в Telegram | Уведомления об ошибках |
| `TELEGRAM_CHAT_ID` | Chat ID | [@userinfobot](https://t.me/userinfobot) в Telegram | Куда отправлять уведомления |

### ОПЦИОНАЛЬНЫЕ для Part 4 (YouTube/TikTok/VK)

| Secret Name | Значение | Где получить | Для чего |
|------------|---------|-------------|----------|
| `YOUTUBE_API_KEY` | API Key | Google Cloud Console | YouTube upload |
| `TIKTOK_ACCESS_TOKEN` | Token | TikTok Developer | TikTok upload |
| `VK_SERVICE_TOKEN` | Token | VK App Admin | VK upload |
| `INSTAGRAM_ACCESS_TOKEN` | Token | Meta Developer | Instagram upload |

### Как добавить Secrets

1. Перейти: **Settings → Secrets and variables → Actions**
2. Нажать **"New repository secret"**
3. Заполнить Name и Value для каждого secret
4. После добавления автоматически доступны в `${{ secrets.SECRET_NAME }}`

---

## 🎬 Project Structure

```
content-factory/
├── core/
│   ├── orchestrators/
│   │   ├── __main__.py
│   │   └── pipeline_orchestrator.py
│   ├── generators/
│   │   ├── script_generator.py       ✅ DONE
│   │   ├── tts_generator.py          🔜 IN PROGRESS (Edge-TTS)
│   │   └── video_renderer.py         🔜 IN PROGRESS (moviepy)
│   └── utils/
│       ├── config_loader.py
│       ├── model_router.py
│       ├── yaml_loader.py
│       └── secrets_manager.py
├── projects/
│   └── youtube_horoscope/
│       ├── config.yaml              ✅ Russian voice configured
│       ├── prompts/
│       │   ├── shorts_scenario.txt
│       │   ├── long_form_scenario.txt
│       │   └── ad_script.txt
│       └── content_plan.json
├── .github/workflows/
│   └── part1-test.yml               ✅ Fixed YAML syntax
├── requirements.txt
├── .env.example
└── output/                          (auto-created)
    ├── scripts/
    ├── audio/
    ├── videos/
    └── logs/
```

---

## 📝 Configuration

### `projects/youtube_horoscope/config.yaml`

```yaml
project:
  name: youtube_horoscope
  language: Russian
  niche: astrology

generation:
  primary_model: "gemini-1.5-flash"        # ✅ Актуальная модель Dec 2025
  fallback_models:
    - "gemini-exp-1206"                   # Экспериментальная
  temperature: 0.8
  max_retries: 3

audio:
  enabled: true
  engines:
    edge-tts:
      enabled: true
      voice: "ru-RU-DariyaNeural"          # Русский женский голос (бесплатный!)
      speed: 1.0
    gemini-tts:
      enabled: false

video:
  fps: 30
  codec: libx264
  audio_codec: aac
  quality: high
  shorts:
    width: 1080
    height: 1920                           # Vertical 9:16
    preferred_source: pixabay_video
  long_form:
    width: 1920
    height: 1080                           # Horizontal 16:9

subtitles:
  enabled: true
  font: Arial
  font_size: 24
  color: white
```

---

## 🤖 Gemini Models (Декабрь 2025)

### АКТУАЛЬНЫЕ модели

```
✅ gemini-1.5-flash (РЕКОМЕНДУЕТСЯ)
   - Быстрая, стабильная
   - Хорошее качество текста
   - Бесплатный tier доступен
   - Низкая латенция

✅ gemini-1.5-pro
   - Более мощная, медленнее
   - Лучше для сложных задач
   - Платная ($)

✅ gemini-2.0-flash (НОВЕЙШАЯ, если доступна)
   - Экспериментальная
   - Может быть нестабильной
   - Используйте как fallback
```

### ❌ УСТАРЕВШИЕ (НЕ ИСПОЛЬЗУЙТЕ)

```
❌ gemini-2.0-flash-exp       (Удалена в Dec 2025)
❌ gemini-exp-1206             (Удалена в Dec 2025)
❌ gemini-pro                  (Архивная)
❌ gemini-pro-vision           (Архивная)
```

---

## 📊 Output Files

После запуска pipeline создаются:

```
output/
├── scripts/youtube_horoscope/20251212/
│   ├── short_a1b2c3d4.json
│   ├── long_form_x9y8z7w6.json
│   └── ad_p1q2r3s4.json
│
├── audio/youtube_horoscope/
│   ├── shorts_main.wav            (22050 Hz, mono)
│   ├── long_form_love.wav
│   ├── long_form_money.wav
│   ├── long_form_health.wav
│   └── ad_main.wav
│
└── videos/youtube_horoscope/
    ├── shorts.mp4                 (1080x1920, 30fps, H.264)
    ├── long_form.mp4              (1920x1080, 30fps, H.264)
    └── ad.mp4                     (1080x1920, 30fps, H.264)
```

---

## 🧪 Testing

### Part 1 (Script Generator) — Already Working ✅

```bash
python -c "
from core.utils.config_loader import load_project_config
from core.generators.script_generator import generate_short

config = load_project_config('youtube_horoscope')
script = generate_short(config)
print('✅ Script generated:', script['_script_path'])
"
```

### Part 2 (TTS) — In Progress 🔜

```bash
python -c "
from core.utils.config_loader import load_project_config
from core.generators.script_generator import generate_short
from core.generators.tts_generator import synthesize

config = load_project_config('youtube_horoscope')
script = generate_short(config)
audio = synthesize(config, script, 'shorts')
print('✅ TTS:', audio['blocks']['main'])
print('Duration:', audio['total_duration_sec'], 'sec')
"
```

### Full Pipeline

```bash
python -m core.orchestrators.pipeline_orchestrator \
  --project youtube_horoscope \
  --mode shorts \
  --dry-run

# Check results
ls -lah output/
```

---

## 🔧 Troubleshooting

### Edge-TTS не работает

```bash
# Проверить установку
pip install edge-tts==6.1.0

# Тест
python -c "import edge_tts; print('✅ edge-tts installed')"
```

### Gemini API ошибка (401/403)

```bash
# Проверить ключ
echo $GOOGLE_AI_API_KEY

# Переполучить с https://ai.google.dev/
```

### GitHub Actions падает

1. Проверить `.github/workflows/part1-test.yml` синтаксис
2. Убедиться все secrets добавлены
3. Смотреть Actions tab → logs

---

## 📚 Documentation

- **FULL-IMPLEMENTATION-TZ.md** — Полное техническое задание для Part 2 + 3
- **QUICK-START.md** — Быстрый старт
- **GITHUB-SECRETS-GUIDE.md** — Гайд по секретам

---

## 📞 Support

- **Проблема?** Смотри логи: `output/logs/{project}/{date}.log`
- **Вопрос?** Открой Issue
- **PR?** Добро пожаловать! 🚀

---

**Status:** 🔜 Part 2 TTS Implementation In Progress  
**Next:** Merge Part 2 + 3 → Part 4 YouTube upload → Part 5 Scheduling
