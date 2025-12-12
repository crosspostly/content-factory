# 🎬 Content Factory - AI-Powered Multi-Platform Content Machine

> **Фабрика контента, работающая на GitHub Actions. Генерирует видео и контент для YouTube, TikTok, Instagram, VK с поддержкой Gemini, Edge-TTS, стоками и масштабируемыми проектами.**

![Version](https://img.shields.io/badge/version-2.2-blue)
![Status](https://img.shields.io/badge/status-Part%202%20TTS%20%2B%20Video-yellowgreen)
![License](https://img.shields.io/badge/license-MIT-orange)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)

---

## 📖 Documentation (START HERE)

1. **[QUICK-START.md](./QUICK-START.md)** - 5-minute setup guide
2. **[PART2_PART3_CRITICAL_TZ.md](./PART2_PART3_CRITICAL_TZ.md)** - Technical spec for Part 2 + 3 (AI agent)

---

## 🚀 Status

✅ **COMPLETED (Part 1):**
- Config loader (stdlib YAML)
- LLM routing (Gemini + fallbacks)
- Pipeline orchestrator (CLI)
- Script generator + file saving
- GitHub Actions workflow

🔜 **IN PROGRESS (Part 2 + 3):**
- Edge-TTS integration (ru-RU-DariyaNeural)
- moviepy video rendering
- Pixabay API for background videos

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

## 🔐 GitHub Secrets (Required for Part 2 + 3)

| Secret | Value | Source |
|--------|-------|--------|
| `GOOGLE_AI_API_KEY` | API Key | [ai.google.dev](https://ai.google.dev) |
| `OPENROUTER_API_KEY` | API Key | [openrouter.ai](https://openrouter.ai) (fallback) |
| `PIXABAY_API_KEY` | API Key | [pixabay.com/api](https://pixabay.com/api) |
| `TELEGRAM_BOT_TOKEN` | Token | [@BotFather](https://t.me/BotFather) |
| `TELEGRAM_CHAT_ID` | Chat ID | [@userinfobot](https://t.me/userinfobot) |

**Setup:** Settings → Secrets and variables → Actions → New repository secret

---

## 📝 Google Gemini Models (Dec 2025 - Official)

**ACTUAL (Supported):**

| Model | Code | Best For |
|-------|------|----------|
| Gemini 2.5 Flash | `gemini-2.5-flash` | **RECOMMENDED** - fast, balanced |
| Gemini 2.5 Flash-Lite | `gemini-2.5-flash-lite` | Cost-optimized |
| Gemini 2.5 Pro | `gemini-2.5-pro` | Complex reasoning |
| Gemini 3 Pro Preview | `gemini-3-pro-preview` | Newest (experimental) |

**NOT SUPPORTED (Deprecated/Removed):**
- ❌ `gemini-2.0-flash` (shutdown Feb 2026)
- ❌ `gemini-1.5-flash` (retired April 2025)
- ❌ `gemini-1.5-pro` (retired April 2025)
- ❌ `gemini-exp-1206` (never existed)
- ❌ `gemini-2.0-flash-exp` (removed from API)

Source: [ai.google.dev/gemini-api/docs/models](https://ai.google.dev/gemini-api/docs/models)

---

## 📋 Quick Start

```bash
# 1. Clone
git clone https://github.com/crosspostly/content-factory.git
cd content-factory

# 2. Install
pip install -r requirements.txt

# 3. Configure
cp .env.example .env
# Add your API keys to .env

# 4. Test
python -m core.orchestrators.pipeline_orchestrator \
  --project youtube_horoscope \
  --mode shorts \
  --dry-run

# 5. Generate
python -m core.orchestrators.pipeline_orchestrator \
  --project youtube_horoscope \
  --mode shorts
```

---

## 🎬 Project Structure

```
content-factory/
├── core/
│   ├── generators/
│   │   ├── script_generator.py       ✅ DONE
│   │   ├── tts_generator.py          🔜 Edge-TTS
│   │   └── video_renderer.py         🔜 moviepy
│   ├── orchestrators/
│   │   └── pipeline_orchestrator.py  ✅ DONE
│   └── utils/
│       ├── config_loader.py
│       ├── model_router.py
│       └── secrets_manager.py
├── projects/
│   └── youtube_horoscope/
│       ├── config.yaml
│       ├── prompts/
│       └── content_plan.json
├── .github/workflows/
│   └── part1-test.yml
├── requirements.txt
├── QUICK-START.md                 ← START HERE
├── PART2_PART3_CRITICAL_TZ.md     ← For AI agent
└── output/                         (auto-created)
```

---

## 🧪 Testing

```bash
# Part 1 (Script generation) - Working ✅
python -c "
from core.generators.script_generator import generate_short
from core.utils.config_loader import load_project_config

config = load_project_config('youtube_horoscope')
script = generate_short(config)
print('✅ Script generated')
"

# Part 2 (TTS) - In progress 🔜
# See QUICK-START.md

# Part 3 (Video) - In progress 🔜
# See QUICK-START.md
```

---

## 🔗 Links

- **Google AI Studio:** [ai.google.dev](https://ai.google.dev)
- **Models Documentation:** [ai.google.dev/gemini-api/docs/models](https://ai.google.dev/gemini-api/docs/models)
- **Deprecations:** [ai.google.dev/gemini-api/docs/deprecations](https://ai.google.dev/gemini-api/docs/deprecations)
- **Edge-TTS:** [github.com/rany2/edge-tts](https://github.com/rany2/edge-tts)
- **moviepy:** [zulko.github.io/moviepy](https://zulko.github.io/moviepy)

---

## 📞 Support

- **Issue?** Check `output/logs/`
- **Question?** Open an issue
- **PR?** Welcome! 🚀

---

**Status:** 🔜 Part 2 TTS + Part 3 Video In Progress  
**Last Updated:** Dec 12, 2025 (Gemini models verified from official docs)
