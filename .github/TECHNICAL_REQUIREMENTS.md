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

### 4. Auto-Fix Agent ✅ NEW!
- **Status:** DEPLOYED & READY
- Automatically analyzes workflow failures
- Creates GitHub issues with technical tasks
- Optionally auto-commits fixes (configurable)
- Uses Gemini 2.5 for analysis

---

## 🤖 AUTO-FIX AGENT (NEW FEATURE)

### How It Works

```
[Workflow Fails]
        ↓
[GitHub Actions triggers auto-fix-agent.yml]
        ↓
[Fetches workflow logs]
        ↓
[Gemini 2.5 analyzes error]
        ↓
[Creates detailed GitHub Issue]
        ↓
[IF auto-fix enabled in config]
  → Auto-commits fix to repo
[ELSE]
  → Manual review required
```

### Configuration File

**Location:** `.github/auto-fix-config.yml`

```yaml
auto_fix:
  # MAIN SWITCH: Enable/disable auto-commit
  auto_commit: false  # ← Change to 'true' to enable auto-fixes!
  
  # Create GitHub issues
  create_issue: true
  
  # Minimum severity to trigger fix
  min_severity: medium  # critical, high, medium, low
  
  # Only fix on these branches
  allowed_branches:
    - main
    - develop
  
  # Gemini model to use
  model: gemini-2.5-flash
```

### Enable Auto-Fix in 2 Steps

**Step 1:** Edit `.github/auto-fix-config.yml`
```yaml
auto_fix:
  auto_commit: true  # ← Change this!
```

**Step 2:** Push to main
```bash
git add .github/auto-fix-config.yml
git commit -m "Enable auto-fix agent"
git push origin main
```

**Done!** Next workflow failure will be auto-fixed. ✨

### What the Agent Does

#### 1. Analyzes Failure
- Reads GitHub Actions logs
- Uses Gemini to understand the error
- Identifies root cause

#### 2. Creates GitHub Issue
- **Title:** 🔴 [CRITICAL] Error description
- **Body:**
  - Problem description
  - Root cause analysis
  - Severity level (critical/high/medium/low)
  - Solution steps
  - Suggested code fix
  - Link to failing workflow run

#### 3. Auto-Commits (If Enabled)
- Applies Gemini's suggested code fix
- Creates git commit with message
- Pushes to original branch
- Closes related issues automatically

### Example Workflow

**Test fails:**
```
FAILED tests/test_tts_generator.py::TestSynthesizeModes::test_synthesize_shorts
ValueError: Missing required parameter 'api_key'
```

**Auto-Fix Agent (1 minute later):**

1. ✅ **Creates Issue:**
   ```
   Title: 🔴 [HIGH] TTS Generator missing API key parameter
   
   Problem: Test fails because api_key parameter not passed
   Root Cause: Refactoring missed one function call
   
   Solution:
   - Add api_key parameter to synthesize() call
   - Update test fixtures
   
   Code Fix:
   result = tts_generator.synthesize(
     config,
     script,
     mode,
     api_key=api_key  # ← Added this
   )
   ```

2. 🔧 **Auto-commits (if enabled):**
   ```
   [auto-fix-agent] Fix TTS Generator: missing api_key parameter
   
   - Add api_key parameter to synthesize() calls
   - Update test fixtures to pass real API key
   - All tests now pass
   ```

### Gemini Analysis Output

Each run generates detailed analysis:

```json
{
  "problem": "Test fails due to missing api_key parameter",
  "root_cause": "Function signature changed but call sites not updated",
  "severity": "high",
  "solution_steps": [
    "Identify all synthesize() calls",
    "Add api_key parameter",
    "Run tests to verify"
  ],
  "code_fix": "result = tts_generator.synthesize(config, script, mode, api_key=api_key)",
  "file_to_modify": "tests/test_tts_generator.py",
  "suggested_commit_message": "Fix TTS Generator: missing api_key parameter",
  "auto_fix_possible": true
}
```

### Safety Features

✅ **Default: Safe Mode**
- Auto-fix is DISABLED by default
- Issues created with manual review required
- No automatic commits

✅ **Controlled Enable**
- Must explicitly set `auto_commit: true` in config
- Only works on specified branches (default: main, develop)
- Minimum severity threshold (default: medium)

✅ **Audit Trail**
- Every auto-fix creates a GitHub Issue (for review)
- Commits include `[auto-fix-agent]` tag
- Analysis saved to artifacts

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

**Create `Dockerfile` in repo root**
- Zero apt installation time
- Consistent environment
- Pre-install: Python 3.11, ffmpeg, imagemagick, fonts

### Priority 2: BUILD AUTOMATION (Next 48 hours)

#### 1. Docker Build Workflow

**Create `.github/workflows/build-docker.yml`**
- Builds Docker image on changes
- Pushes to GitHub Container Registry
- Uses buildx for caching

#### 2. Update Main Workflow

**Update `.github/workflows/main.yml`**
- Use Docker container
- Remove apt-get install
- Saves 30 seconds per run

### Priority 3: OPTIMIZATION (Next week)

#### 1. Performance Benchmarking
- Target: < 3 minutes total (currently ~5-7 minutes)

#### 2. Parallel Testing
```bash
pytest -n auto  # Use pytest-xdist
```

---

## 📝 ENVIRONMENT VARIABLES

**GitHub Actions Secrets Required:**

```
GOOGLE_AI_API_KEY          ✅ Set (Gemini API)
PIXABAY_API_KEY            ⚠️ Optional (Part 2)
TELEGRAM_BOT_TOKEN         ✅ Set (Notifications)
TELEGRAM_CHAT_ID           ✅ Set (Notifications)
GHCR_PAT                   ⚠️ Needed for Docker push (optional)
```

---

## 📦 DEPENDENCIES

### System Dependencies
```bash
ffmpeg >= 6.1.1
imagemagick >= 6.9.12
ghostscript >= 10.02.1
fonts-dejavu-core
```

### Python Dependencies
```
google-generativeai==0.7.2   # Gemini API
python-dotenv==1.0.1
pyyaml==6.0.2
requests==2.31.0
pydub==0.25.1
moviepy==1.0.3
pillow==10.2.0
numpy==1.26.4
pytest==7.4.3
```

---

## 📊 PERFORMANCE TARGETS

| Step | Current | With apt cache | With Docker |
|------|---------|----------------|-------------|
| Checkout | 0.5s | 0.5s | 0.5s |
| Python setup | 1s | 1s | 0s |
| **apt install** | **30s** | **2s** | **0s** |
| pip restore | 2s | 2s | 0s |
| pip install | 10s | 0s | 0s |
| Tests | 5s | 5s | 5s |
| **Total** | **~48s** | **~10s** | **~5s** |

**Savings:** 79% faster (apt cache) → 90% faster (Docker)

---

## 🧪 TEST REQUIREMENTS

```bash
# Set API key
export GOOGLE_AI_API_KEY="your-key"

# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=core --cov-report=html

# Skip slow tests
python -m pytest tests/ -v -m "not slow"
```

**Target Coverage:** 70% (MVP acceptable at 35%)

---

## 📄 WORKFLOW FILES

- `.github/workflows/main.yml` - CI/CD tests & builds
- `.github/workflows/auto-fix-agent.yml` - Auto-fix on failures (NEW!)
- `.github/workflows/build-docker.yml` - Docker builds (to create)
- `.github/auto-fix-config.yml` - Auto-fix configuration (NEW!)

---

## 🚀 NEXT MILESTONES

### Part 2: Video Rendering (2 weeks)
- Use moviepy for video creation
- Combine script + TTS + background video + subtitles

### Part 3: Audio Enhancement (1 week)
- Background music (Pixabay API)
- Sound effects & mixing

### Part 4: Upload & Distribution (2 weeks)
- YouTube, TikTok, Instagram integration

---

**Last Updated:** 2025-12-12
**Status:** Part 1 MVP Complete + Auto-Fix Agent Deployed ✨
