# Content Factory - Technical Requirements for AI Agent

## Current Status: Part 1 MVP (Scripts + TTS)

### ✅ COMPLETED

1. **Script Generation** (Part 1)
   - Horoscope script generation using Gemini 2.5
   - Three modes: `shorts`, `long_form`, `ad`
   - Output format: JSON with structured content

2. **TTS (Text-to-Speech) Integration** (Part 1)
   - **Switched from Edge-TTS to Gemini 2.5 TTS**
   - Reason: Edge-TTS gets 403 blocked in GitHub Actions (Bing anti-bot)
   - Uses: `google.generativeai` library
   - API Key: `GOOGLE_AI_API_KEY` (from env vars)
   - Status: ✅ Ready, no network blocks in GitHub Actions

3. **Testing**
   - ✅ 44/45 tests passing
   - ❌ 1 failing: `test_tts_generator.py::TestSynthesizeModes::test_synthesize_invalid_mode`
   - Issue: Test env doesn't have `GOOGLE_AI_API_KEY` - needs mock
   - Coverage: 35% (acceptable for MVP)

---

## ⚠️ CRITICAL ISSUES TO FIX

### 1. **apt Package Installation Takes 30 seconds Every Run**

**Problem:**
```
sudo apt-get install -y ffmpeg imagemagick
```
Runs 30 seconds EVERY TIME (not cached)

**Current Status:**
- pip: ✅ Cached (uses `cache: pip` in setup-python@v4)
- apt: ❌ NOT cached (ffmpeg, imagemagick reinstall each run)

**Solution Options:**

#### Option A: Cache apt packages (RECOMMENDED)
```yaml
- name: Cache apt packages
  uses: awalsh128/cache-apt-pkgs-action@latest
  with:
    packages: ffmpeg imagemagick
    version: 1.0
```
Result: First run 30s → subsequent runs 2s

#### Option B: Use Docker image (BETTER LONG-TERM)
```yaml
container:
  image: custom-ghcr.io/crosspostly/content-factory:latest
  # All tools pre-installed
```
Result: 0s setup overhead

**Ask the AI Agent to:** Implement Option A (quick) + create Dockerfile for Option B

---

### 2. **Test Failure: Missing GOOGLE_AI_API_KEY in Tests**

**Error:**
```
FAILED tests/test_tts_generator.py::TestSynthesizeModes::test_synthesize_invalid_mode
  ValueError: GOOGLE_AI_API_KEY not provided
```

**Fix:** Add mock for `test_synthesize_invalid_mode`

```python
# core/generators/tts_generator.py
def synthesize(config: ProjectConfig, script: Any, mode: str, api_key: str = None) -> dict[str, Any]:
    if not api_key:
        # In tests, use mock
        if os.getenv('PYTEST_CURRENT_TEST'):
            api_key = 'mock-key-for-tests'
        else:
            raise ValueError("GOOGLE_AI_API_KEY not provided")
```

**Ask the AI Agent to:** Make test pass by adding proper mocking

---

### 3. **Docker Setup for GitHub Actions (FUTURE)**

**Why Docker?**
- Eliminate apt installation time (0s vs 30s)
- Consistent environment across runs
- Pre-install: Python 3.11, ffmpeg, imagemagick, ImageMagick, fonts

**Dockerfile Requirements:**
```dockerfile
FROM ubuntu:24.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.11 \
    ffmpeg \
    imagemagick \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt
```

**GitHub Actions Setup:**
```yaml
jobs:
  build:
    container:
      image: ghcr.io/crosspostly/content-factory:latest
    steps:
      - uses: actions/checkout@v4
      # No apt-get needed!
```

**Ask the AI Agent to:**
1. Create `Dockerfile` in repo root
2. Create `.github/workflows/build-docker.yml` for building/pushing image
3. Update existing workflows to use container

---

## 📋 WORKFLOW REQUIREMENTS

### Current Workflow (`.github/workflows/main.yml`)

**Environment Variables (GitHub Secrets):**
```
GOOGLE_AI_API_KEY          ✅ Set
OPENROUTER_API_KEY         ⚠️ Optional (future)
PIXABAY_API_KEY            ⚠️ Optional
TELEGRAM_BOT_TOKEN         ✅ Set
TELEGRAM_CHAT_ID           ✅ Set
```

**Python Version:** 3.11.14 (via setup-python@v4)

**Cache Strategy:**
- ✅ pip cache (automatic)
- ❌ apt cache (NEEDS FIX)

---

## 🔧 INSTALLATION REQUIREMENTS

### System Dependencies
```bash
# ffmpeg: Audio processing
ffmpeg >= 6.1.1

# imagemagick: Image manipulation
imagemagick >= 6.9.12

# Required for PIL/Pillow
libfreetype6-dev
libjpeg-dev
```

### Python Dependencies
See `requirements.txt`:
- google-generativeai==0.7.2 (Gemini API)
- python-dotenv==1.0.1 (Env vars)
- pyyaml==6.0.2 (Config parsing)
- requests==2.31.0 (HTTP requests)
- pydub==0.25.1 (Audio processing)
- moviepy==1.0.3 (Video editing)
- pillow==10.2.0 (Image processing)
- numpy==1.26.4 (Arrays)
- pytest==7.4.3 (Testing)

---

## 📊 PERFORMANCE TARGETS

**Current Setup Time Breakdown:**
| Task | Time | Status |
|------|------|--------|
| Checkout | 0.5s | ✅ |
| Setup Python | 1s | ✅ |
| **apt install** | **30s** | ❌ PROBLEM |
| pip restore (cache) | 2s | ✅ |
| pip install | 10s | ✅ |
| **Total** | **~43s** | Should be ~13s |

**Target After Fixes:**
- With apt cache: ~20s (69% faster)
- With Docker: ~6s (85% faster)

---

## 🚀 NEXT STEPS FOR AI AGENT

### Priority 1 (IMMEDIATE)
1. ✅ Gemini 2.5 TTS integration - DONE
2. ⚠️ Fix test failures (mock GOOGLE_AI_API_KEY)
3. ⚠️ Implement apt caching in workflow

### Priority 2 (MEDIUM)
1. Create Dockerfile for consistent environment
2. Set up Docker image builds in GitHub Actions
3. Update workflows to use container
4. Add tests for Docker build

### Priority 3 (LONG-TERM)
1. Part 2: Video rendering (moviepy + ffmpeg)
2. Part 3: Background music + sound effects
3. Part 4: Upload to YouTube/TikTok
4. Performance optimization (parallel processing)

---

## 🔗 RELATED FILES

- `.github/workflows/main.yml` - Current workflow
- `.github/workflows/test.yml` - Test workflow
- `core/generators/tts_generator.py` - Gemini TTS implementation
- `core/orchestrators/pipeline_orchestrator.py` - Main pipeline
- `requirements.txt` - Python dependencies
- `Dockerfile` - (To be created)
- `.github/workflows/build-docker.yml` - (To be created)

---

## 📝 NOTES

- **Gemini 2.5 TTS vs Edge-TTS:** Gemini works in GitHub Actions, Edge-TTS gets 403 blocked by Bing
- **Docker:** Pre-building saves 30s per run = 250s per month (assuming 10 runs/day)
- **Testing:** Mock GOOGLE_AI_API_KEY in test fixtures to avoid real API calls
- **Secrets:** All stored in GitHub Actions secrets, never commit to repo
