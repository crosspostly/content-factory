# Content Factory - Technical Requirements for AI Agent

## Current Status: Part 1 MVP (Scripts + TTS) ✅ DONE

---

## ✅ COMPLETED

### 1. Script Generation (Part 1) ✅
- Horoscope script generation using Gemini 2.5
- Three modes: `shorts`, `long_form`, `ad`
- Output format: JSON with structured content
- **Status:** PRODUCTION READY

### 2. TTS Integration (Part 1) ✅ UPDATED
- **Engine:** Gemini 2.5 TTS (switched from Edge-TTS)
- **Why Gemini?** Works in GitHub Actions (Edge-TTS gets 403 blocked)
- **API Key:** `GOOGLE_AI_API_KEY` from environment
- **Voices:** Google Cloud Neural2 voices
  - Female warm: `ru-RU-Neural2-C`
  - Female neutral: `ru-RU-Neural2-A`
  - Male: `ru-RU-Neural2-B`
- **Status:** ✅ PRODUCTION READY

### 3. Testing ✅ FIXED
- ✅ Updated tests for Gemini 2.5 TTS
- ✅ All tests use real `GOOGLE_AI_API_KEY` from environment
- ✅ Tests skip if API key not available (no fake mocks)
- ✅ 45/45 tests passing
- **Coverage:** 35% (acceptable for MVP)

---

## 🔧 REQUIREMENTS TO IMPLEMENT

### Priority 1: CRITICAL (Next 24 hours)

#### 1. Apt Caching in GitHub Actions

**Problem:**
```
sudo apt-get install -y ffmpeg imagemagick  # Takes 30 seconds EVERY RUN
```

**Solution:** Add to `.github/workflows/main.yml`

```yaml
- name: Cache apt packages
  uses: awalsh128/cache-apt-pkgs-action@latest
  with:
    packages: ffmpeg imagemagick
    version: 1.0
```

**Expected Result:**
- First run: 30s
- Subsequent runs: 2s (93% faster)

#### 2. Docker Image for CI/CD

**Create `Dockerfile` in repo root:**

```dockerfile
FROM ubuntu:24.04
LABEL maintainer="Pavel Shekhov <shekhovpavel@gmail.com>"
LABEL description="Content Factory runtime environment"

# Avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.11 \
    python3-pip \
    ffmpeg \
    imagemagick \
    ghostscript \
    fonts-dejavu-core \
    ca-certificates \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set Python 3.11 as default
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Run tests by default
CMD ["python", "-m", "pytest", "-v"]
```

**Expected Result:**
- Zero apt installation time in CI/CD
- Consistent environment across local/CI/CD
- ~5 minute build time (one-time)

### Priority 2: BUILD AUTOMATION (Next 48 hours)

#### 1. Docker Build Workflow

**Create `.github/workflows/build-docker.yml`:**

```yaml
name: Build and Push Docker Image

on:
  push:
    branches: [main]
    paths: ['Dockerfile', 'requirements.txt', '.github/workflows/build-docker.yml']
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            ghcr.io/${{ github.repository }}:latest
            ghcr.io/${{ github.repository }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

#### 2. Update Main Workflow to Use Docker

**In `.github/workflows/main.yml`, replace apt-get with container:**

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    container:
      image: ghcr.io/crosspostly/content-factory:latest
    
    steps:
      - uses: actions/checkout@v4
      
      # No apt-get needed! All tools pre-installed in Docker image
      
      - name: Run tests
        run: |
          python -m pytest tests/ -v --cov=core
        env:
          GOOGLE_AI_API_KEY: ${{ secrets.GOOGLE_AI_API_KEY }}
```

**Expected Result:**
- 30s saved per run (apt installation eliminated)
- Consistent environment across all runs
- Reproducible builds

### Priority 3: OPTIMIZATION (Next week)

#### 1. Performance Benchmarking

```bash
# Track build times
# Target: < 3 minutes total (currently ~5-7 minutes)
```

#### 2. Parallel Testing

```bash
pytest -n auto  # Use pytest-xdist for parallel execution
```

---

## 📋 ENVIRONMENT VARIABLES

**GitHub Actions Secrets Required:**

```
GOOGLE_AI_API_KEY          ✅ Set (Gemini API)
PIXABAY_API_KEY            ⚠️ Optional (Part 2)
TELEGRAM_BOT_TOKEN         ✅ Set (Notifications)
TELEGRAM_CHAT_ID           ✅ Set (Notifications)
GHCR_PAT                   ⚠️ Needed for Docker push (optional)
```

**Local Development:**

```bash
# .env file (never commit!)
GOOGLE_AI_API_KEY="your-api-key-here"
PIXABAY_API_KEY="your-key-here"
TELEGRAM_BOT_TOKEN="your-token-here"
TELEGRAM_CHAT_ID="your-chat-id"
```

---

## 📦 DEPENDENCIES

### System Dependencies
```bash
# ffmpeg: Audio/video processing (7:6.1.1-3ubuntu5)
ffmpeg

# imagemagick: Image manipulation (6.9.12+)
imagemagick

# ghostscript: PDF rendering (10.02.1+)
ghostscript

# Fonts
fonts-dejavu-core
```

### Python Dependencies (see `requirements.txt`)
```
google-generativeai==0.7.2   # Gemini API
python-dotenv==1.0.1          # Environment variables
pyyaml==6.0.2                 # Config parsing
requests==2.31.0              # HTTP
pydub==0.25.1                 # Audio processing
moviepy==1.0.3                # Video editing (Part 2)
pillow==10.2.0                # Image processing
numpy==1.26.4                 # Numerical operations
pytest==7.4.3                 # Testing
```

---

## 📊 PERFORMANCE TARGETS

### Build Time Breakdown

| Step | Current | With apt cache | With Docker |
|------|---------|----------------|-------------|
| Checkout | 0.5s | 0.5s | 0.5s |
| Python setup | 1s | 1s | 0s |
| **apt install** | **30s** | **2s** | **0s** |
| pip restore | 2s | 2s | 0s |
| pip install | 10s | 0s (cached) | 0s |
| Tests | 5s | 5s | 5s |
| **Total** | **~48s** | **~10s** | **~5s** |

### Savings
- With apt cache: **79% faster** (38 seconds saved per run)
- With Docker: **90% faster** (43 seconds saved per run)

---

## 🧪 TEST REQUIREMENTS

### Running Tests Locally

```bash
# Set API key
export GOOGLE_AI_API_KEY="your-key"

# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=core --cov-report=html

# Skip slow tests
python -m pytest tests/ -v -m "not slow"

# Run specific test
python -m pytest tests/test_tts_generator.py::TestSynthesizeModes::test_synthesize_shorts -v
```

### Test Coverage

- **Target:** 70% (MVP acceptable at 35%)
- **Critical paths:** Script generation, TTS synthesis, error handling
- **Optional:** Video rendering, upload (Part 2+)

---

## 📊 WORKFLOW FILES

### Main Workflow
**File:** `.github/workflows/main.yml`
- Runs on: Push to main, Manual trigger
- Jobs: Test, Build Docker (optional)
- Outputs: Test reports, Coverage, Docker image

### Build Docker Workflow
**File:** `.github/workflows/build-docker.yml` (to create)
- Builds Docker image
- Pushes to GitHub Container Registry
- Uses buildx for caching

---

## 🚀 NEXT MILESTONES

### Part 2: Video Rendering
- Use `moviepy` for video creation
- Combine: Script + TTS audio + background video + subtitles
- Estimated: 2 weeks

### Part 3: Audio Enhancement
- Add background music (Pixabay API)
- Sound effects
- Audio mixing
- Estimated: 1 week

### Part 4: Upload & Distribution
- YouTube API integration
- TikTok upload
- Instagram Reels
- Estimated: 2 weeks

---

## 📄 CONFIGURATION FILES

- `projects/youtube_horoscope/config.yaml` - Project config
- `requirements.txt` - Python dependencies
- `Dockerfile` - Docker image (to create)
- `.github/workflows/main.yml` - CI/CD workflow
- `.github/workflows/build-docker.yml` - Docker build (to create)
- `.github/TECHNICAL_REQUIREMENTS.md` - This file

---

## 📃 NOTES FOR AI AGENT

1. **No Mocks!** Tests use real `GOOGLE_AI_API_KEY` from environment
   - Tests skip gracefully if API key not available
   - No fake/mock data

2. **Gemini 2.5 TTS** is the correct choice
   - Edge-TTS blocks GitHub Actions (403 Forbidden)
   - Gemini works everywhere (API-based)

3. **Docker is production-ready**
   - 90% performance improvement
   - Eliminates 30 seconds of apt installation
   - Ensures consistency

4. **All code must be async-compatible**
   - TTS synthesis uses async/await
   - Pipeline uses asyncio.run()
   - Tests marked with @pytest.mark.asyncio

---

**Last Updated:** 2025-12-12
**Status:** Part 1 MVP Complete, Ready for Part 2
