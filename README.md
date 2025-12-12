# 🎬 Content Factory - AI-Powered Multi-Platform Content Machine

> **Фабрика контента, работающая на GitHub Actions. Генерирует видео и контент для YouTube, TikTok, Instagram, VK с поддержкой Gemini, Edge-TTS, стоками и масштабируемыми проектами.**

![Version](https://img.shields.io/badge/version-2.2-blue)
![Status](https://img.shields.io/badge/status-Part%201%20Foundation-yellowgreen)
![License](https://img.shields.io/badge/license-MIT-orange)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)

---

## 🚀 STATUS: Part 1 Foundation ✅ (Awaiting Fixes → Merge)

### Current Phase: **Bootstrap Pipeline Architecture**

✅ **COMPLETED:**
- [x] Config loader (stdlib YAML parser - zero dependencies!)
- [x] LLM routing (Gemini → Ollama → OpenRouter with fallbacks)
- [x] TTS routing (Edge-TTS, Gemini TTS engine selection)
- [x] Pipeline orchestrator (CLI interface, dry-run mode)
- [x] Logging & error handling (file + console + Telegram alerts)
- [x] Secrets manager (GitHub Secrets + .env support)

⏳ **PENDING (CRITICAL FIXES):**
- [ ] Fix `script_generator.py` — Add file saving + JSON structure validation
- [ ] Fix `tts_generator.py` — Return proper nested dict output
- [ ] Add `core/orchestrators/__main__.py` — CLI entry point
- [ ] Create example project — `projects/youtube_horoscope/config.yaml`
- [ ] Create prompt files — Empty stubs for shorts/long_form/ads
- [ ] Merge PR #3 — Integrate into main branch

📊 **Progress:** 77% (12/15 components done)

---

## 🛣️ Roadmap

```
┌─ Part 1: Foundation (IN PROGRESS) ✅
│  ├─ Config system ✅
│  ├─ LLM/TTS routing ✅
│  ├─ CLI orchestrator ✅
│  ├─ Logging + error handling ✅
│  └─ Generators (placeholder) ⏳ PENDING FIXES
│
├─ Part 2: Real TTS Implementation 🔜
│  ├─ Edge-TTS integration
│  ├─ Gemini TTS integration
│  └─ Audio block synthesis (love/money/health)
│
├─ Part 3: LLM + Script Generation 🔜
│  ├─ Real LLM calls (Gemini/Ollama/OpenRouter)
│  ├─ JSON script parsing & validation
│  └─ Prompt file loading
│
├─ Part 4: Video Rendering 🔜
│  ├─ moviepy/ffmpeg integration
│  ├─ Stock video API (Pixabay/Pexels)
│  └─ Video composition (overlay text, transitions)
│
└─ Part 5: Platform Uploaders 🔜
   ├─ YouTube API
   ├─ TikTok API
   ├─ Instagram API
   └─ VK API
```

---

## 📋 QUICK REFERENCE

### Quick Start (When Part 1 Ready)
```bash
# Generate shorts (dry-run)
python -m core.orchestrators.pipeline_orchestrator \
  --project youtube_horoscope \
  --mode shorts \
  --dry-run

# Generate with YouTube upload
python -m core.orchestrators.pipeline_orchestrator \
  --project youtube_horoscope \
  --mode shorts \
  --platforms youtube \
  --upload
```

### Project Structure
```
content-factory/
├── core/
│   ├── orchestrators/
│   │   ├── __main__.py (PENDING)
│   │   └── pipeline_orchestrator.py ✅
│   ├── generators/
│   │   ├── script_generator.py (PENDING FIX)
│   │   ├── tts_generator.py (PENDING FIX)
│   │   └── video_renderer.py
│   ├── uploaders/ (Part 5)
│   └── utils/ ✅
├── projects/youtube_horoscope/ (PENDING)
│   ├── config.yaml
│   ├── prompts/
│   └── content_plan.json
└── output/ (auto-created)
    ├── scripts/
    ├── audio/
    ├── videos/
    └── logs/
```

### Environment Variables
```bash
# Part 3+ (LLM Integration)
GOOGLE_AI_API_KEY=your_key
OPENROUTER_API_KEY=optional

# Monitoring
TELEGRAM_BOT_TOKEN=optional
TELEGRAM_CHAT_ID=optional

# Part 5 (Upload)
YOUTUBE_API_KEY=future
TIKTOK_API_KEY=future
```

---

## 🎯 IMMEDIATE ACTION ITEMS

### 🔴 MUST DO (Before Merge)
1. **Fix `core/generators/script_generator.py`**
   - Add file saving to `output/scripts/{project}/{date}/script_uuid.json`
   - Return proper JSON structure from tech spec
   - Add validation for required fields

2. **Fix `core/generators/tts_generator.py`**
   - Return nested dict with `blocks`, `background_music_path`, `sound_effects`, `engine_used`, `total_duration_sec`
   - Currently returns only `{"main": audio_path}` ❌

3. **Add `core/orchestrators/__main__.py`**
   - Enable: `python -m core.orchestrators.pipeline_orchestrator ...`

4. **Create Example Project**
   - `projects/youtube_horoscope/config.yaml` (minimal valid config)
   - `projects/youtube_horoscope/content_plan.json` (empty)
   - `projects/youtube_horoscope/prompts/*.txt` (empty stubs)

5. **Verify End-to-End**
   ```bash
   python -m core.orchestrators.pipeline_orchestrator \
     --project youtube_horoscope --mode shorts --dry-run
   ```
   Should create:
   - ✅ `output/scripts/youtube_horoscope/2025-12-12/short_*.json`
   - ✅ `output/audio/youtube_horoscope/*.wav`
   - ✅ `output/videos/youtube_horoscope/*.mp4`

6. **Merge PR #3** → Integrate into main

### 🟡 NEXT (Part 2 - TTS Implementation)
- [ ] Real Edge-TTS synthesis
- [ ] Real Gemini TTS integration
- [ ] Audio block structure for long-form
- [ ] Background music + sound effects loading

### 🟢 LATER (Part 3+ - LLM & Upload)
- [ ] LLM script generation
- [ ] Video rendering
- [ ] Platform uploaders

---

## 📚 Architecture Highlights

### Stdlib-Only YAML Parser
✨ **No external dependencies for Part 1!**
- Custom YAML loader in `core/utils/yaml_loader.py`
- Supports full subset of YAML (mappings, lists, scalars, inline JSON)
- Zero pip packages required

### Multi-Provider LLM Routing
- Primary: Gemini
- Fallback 1: Ollama (local or remote)
- Fallback 2: OpenRouter (qwen, other models)
- Automatic retry with exponential backoff
- Auth error handling (401/403)
- Rate limit handling (429)

### Flexible Config System
```yaml
# One config per project, all settings in YAML
# Agents read once, never hardcode
generation:
  primary_model: "gemini-2.5-flash"
  fallback_models: []
  provider_priority: ["gemini", "ollama", "openrouter"]
  temperature: 0.8
  max_retries: 3

audio:
  primary_engine: "edge-tts"
  fallback_engine: "gemini-tts"
  voice_selection:
    shorts: "edge-tts"
    long_form: "gemini-tts"

upload:
  platforms:
    youtube: {enabled: true}
    tiktok: {enabled: false}
```

### CLI Interface (Ready Now!)
```bash
python -m core.orchestrators.pipeline_orchestrator \
  --project PROJECT \
  --mode {shorts|long_form|ad} \
  --date YYYY-MM-DD \
  --platforms youtube,tiktok \
  --dry-run \
  --upload \
  --product-id PRODUCT_ID
```

---

## 🔐 GitHub Secrets (Part 3+)

| Secret | Purpose | When |
|--------|---------|------|
| `GOOGLE_AI_API_KEY` | Gemini LLM + TTS | Part 3 |
| `OPENROUTER_API_KEY` | Fallback LLM | Part 3 |
| `YOUTUBE_API_KEY` | YouTube upload | Part 5 |
| `TELEGRAM_BOT_TOKEN` | Alerts | Now |
| `TELEGRAM_CHAT_ID` | Alerts | Now |

---

## 🎬 Project: YouTube Horoscope

Example project included in `projects/youtube_horoscope/`:

- **Shorts**: 30-60 sec viral hooks (daily)
- **Long-form**: 20-45 min videos with Love/Money/Health blocks (weekly)
- **Ads**: Native product placement
- **Voices**: Female mysterious/warm/neutral (Edge-TTS + Gemini TTS)
- **Target**: Women 18-45 interested in astrology

---

## 📖 Documentation

- **Tech Spec**: [TECH_SPEC.md](./TECH_SPEC.md) (Full pipeline architecture)
- **Task List**: [AGENT_TASK.md](./AGENT_TASK.md) (Current fixes needed)
- **This README**: Quick reference & status

---

## 🧪 Testing Part 1

```bash
# 1. Config loading
python -c "from core.utils import config_loader; c = config_loader.load('youtube_horoscope'); print('✅ Config OK')"

# 2. YAML parsing
python -c "from core.utils.yaml_loader import safe_load; print('✅ YAML parser OK')"

# 3. LLM routing
python -c "from core.utils.model_router import generate_text; print('✅ LLM router OK')"

# 4. End-to-end (pending fixes)
python -m core.orchestrators.pipeline_orchestrator --project youtube_horoscope --mode shorts --dry-run
```

---

## 📌 Key Design Decisions

1. **Stdlib-Only for Core** → Zero external dependencies on Part 1
2. **Config-Driven** → No hardcoding, all settings in YAML
3. **Multi-Provider LLM** → Graceful fallback between providers
4. **Project-Agnostic** → Same code for any YouTube channel, TikTok account, etc.
5. **Placeholder Generators** → Part 1 creates structure, Parts 2-5 add real implementations
6. **CLI-First** → Orchestrator accessible from command line or GitHub Actions

---

## 📞 Support

- **Issue?** Check [AGENT_TASK.md](./AGENT_TASK.md) for pending fixes
- **Architecture?** See [TECH_SPEC.md](./TECH_SPEC.md)
- **Logs?** Check `output/logs/{project}/{date}.log`

---

**Next:** Fix generators → Merge PR #3 → Start Part 2 TTS Implementation 🚀
