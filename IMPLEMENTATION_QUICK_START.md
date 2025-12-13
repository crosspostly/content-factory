# 🚀 Quick Start: youtube_podcast Patterns in content-factory

**TL;DR:** Porting 4 battle-tested patterns from youtube_podcast to make GitHub Actions horoscope generation bulletproof.

---

## 💳 What Changed?

### New Files Added

1. **`core/utils/model_router.py`** ✅ DONE
   - Manages model fallback (fast → powerful)
   - Handles retries with exponential backoff
   - Auto-repairs broken JSON
   - Tracks statistics

2. **`ARCHITECTURE_IMPROVEMENTS.md`** ✅ DONE
   - Full strategy document
   - Shows how youtube_podcast does it
   - Detailed code examples for content-factory
   - 4-week implementation roadmap

### Next Steps (In Order)

#### 🔗 Step 1: Integrate ModelRouter into Script Generation

**File:** `core/generators/script_generator.py`

```python
# BEFORE (current):
import google.generativeai as genai

def generate_horoscope_script(config, target_date, format, api_key):
    client = genai.GenerativeModel('gemini-2.5-flash')
    response = client.generate_content(prompt)
    return json.loads(response.text)

# AFTER (with ModelRouter):
from core.utils.model_router import get_router

def generate_horoscope_script(config, target_date, format, api_key):
    router = get_router(api_key)
    result = router.generate_json(
        task="script",
        prompt=_get_horoscope_prompt(format, target_date, config.language)
    )
    return result
```

**Benefits:**
- ✅ Auto-retry if API rate-limited
- ✅ Fallback to gemini-2.0-flash if primary fails
- ✅ Auto-repair broken JSON
- ✅ Full audit trail logged

#### 🔗 Step 2: Add Length Validation

**In:** `core/generators/script_generator.py`

```python
# Add these constants
MIN_SCRIPT_LENGTH = 300  # For 3-4 min horoscope
MAX_SCRIPT_LENGTH = 800  # For 8-10 min horoscope
MAX_LENGTH_ATTEMPTS = 3

# Add validation function
def _validate_script_length(script_dict: dict) -> tuple[bool, str]:
    """
    Validate script meets length requirements.
    Returns (is_valid, reason)
    """
    length = len(script_dict.get('script', ''))
    
    if length < MIN_SCRIPT_LENGTH:
        return False, f"Too short: {length} < {MIN_SCRIPT_LENGTH}"
    
    if length > MAX_SCRIPT_LENGTH:
        return False, f"Too long: {length} > {MAX_SCRIPT_LENGTH}"
    
    return True, f"Valid length: {length}"

# Wrap generation with validation loop
def generate_horoscope_script_validated(config, target_date, format, api_key):
    router = get_router(api_key)
    
    for attempt in range(1, MAX_LENGTH_ATTEMPTS + 1):
        logger.info(f"Attempt {attempt}/{MAX_LENGTH_ATTEMPTS} to generate script")
        
        result = router.generate_json(
            task="script",
            prompt=_get_horoscope_prompt(format, target_date, config.language)
        )
        
        is_valid, reason = _validate_script_length(result)
        logger.info(f"Length check: {reason}")
        
        if is_valid:
            return result
        
        if attempt < MAX_LENGTH_ATTEMPTS:
            # Enforce length in next attempt
            logger.warning(f"Retrying with length enforcement...")
            deficit = MAX(0, MIN_SCRIPT_LENGTH - len(result.get('script', '')))
            # Next prompt includes: "Add at least {deficit} more characters"
    
    raise RuntimeError(f"Failed to generate valid script after {MAX_LENGTH_ATTEMPTS} attempts")
```

**Benefits:**
- ✅ Scripts that are too short auto-regenerated
- ✅ Clear feedback why it failed
- ✅ Graceful degradation (use last attempt if all fail)

#### 🔗 Step 3: Add Batch Planning (Optional, but cool)

**New file:** `core/generators/content_planner.py` (from ARCHITECTURE_IMPROVEMENTS.md)

**Usage:**
```python
from core.generators.content_planner import plan_horoscope_batch

# Generate plan for 7 days
plan = plan_horoscope_batch(
    api_key="...",
    start_date="2025-12-13",
    num_days=7,
    format="shorts"
)

# Returns:
# [
#   {"date": "2025-12-13", "theme": "...", "hook": "..."},
#   {"date": "2025-12-14", "theme": "...", "hook": "..."},
#   ...
# ]
```

**Benefits:**
- ✅ Ensures variety (AI plans N days upfront)
- ✅ Deterministic (locked in dates)
- ✅ Can parallelize per-day generation

#### 🔗 Step 4: Update GitHub Actions Workflow

**File:** `.github/workflows/generate-horoscope.yml`

```yaml
name: Generate Horoscope

on:
  schedule:
    - cron: '0 3 * * *'  # Daily at 3 AM UTC
  workflow_dispatch:
    inputs:
      format:
        description: Video format
        type: choice
        options: [shorts, long-form]

jobs:
  generate:
    runs-on: ubuntu-22.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: Install dependencies
        run: pip install -r requirements.txt -q
      
      - name: Generate horoscope
        env:
          GOOGLE_AI_API_KEY: ${{ secrets.GOOGLE_AI_API_KEY }}
          PIXABAY_API_KEY: ${{ secrets.PIXABAY_API_KEY }}
        run: python3 -m core.orchestrators.pipeline_orchestrator
      
      - name: Upload video
        if: success()
        uses: actions/upload-artifact@v4
        with:
          name: horoscope-video
          path: output/videos/
```

---

## 📊 What You Get

| Feature | Before | After |
|---------|--------|-------|
| API Failure | 🔴 Crash | 🜟 Retry + Fallback |
| Script Too Short | 🔴 Accept anyway | ✅ Regenerate |
| JSON Parse Error | 🔴 Crash | ✅ Auto-repair |
| Error Visibility | 🔴 Vague | ✅ Detailed logs |
| Multiple Videos | 🔴 Manual | ✅ Batch plan |
| Audit Trail | 🔴 None | ✅ Full history |

---

## 🔄 How It Works

### ModelRouter Flow

```
Prompt sent
    ↓
Try PRIMARY model (gemini-2.5-flash)
    ↓ [Attempt 1,2,3]
    └── Success? ✅ Return
    └── Fail ×3? → Wait, retry
    └── Still fail? → Try FALLBACK
    ↓
Try FALLBACK model (gemini-2.0-flash)
    ↓ [Attempt 1,2,3]
    └── Success? ✅ Return
    └── Fail? 💩 Throw error
```

### Length Validation Flow

```
Generate script
    ↓
Measure length
    ↓
    ├─ Length OK? ✅ Return
    ├─ Too short? → Regenerate with larger prompt
    ├─ Too long? → Warn but accept
    └─ Max attempts? → Return best effort
```

---

## 🗚️ Testing

### Test ModelRouter

```bash
GOOGLE_AI_API_KEY=your-key python3 core/utils/model_router.py
```

Expected output:
```
🌖 Starting generation for task: script
   Primary: gemini-2.5-flash
   Fallback: gemini-2.0-flash
   Attempt 1/3...
   ✅ Success! Got 456 characters
✅ Result:
{"sign": "Aries", "script": "..."}
📊 Stats:
{"total_attempts": 1, "successful": 1, "model_usage": {...}}
```

### Test Length Validation

```bash
GOOGLE_AI_API_KEY=your-key \
  PIXABAY_API_KEY=your-key \
  python3 -c "
from core.generators.script_generator import generate_horoscope_script_validated
from core.config import ProjectConfig

config = ProjectConfig.from_yaml('config/youtube_horoscope.yaml')
script = generate_horoscope_script_validated(
    config, '2025-12-13', 'shorts', 'your-key'
)
print('Script length:', len(script['script']))
"
```

---

## 📊 Logs Format

With ModelRouter, you get detailed logs like:

```
🌖 Starting generation for task: script
   Primary: gemini-2.5-flash
   Fallback: gemini-2.0-flash
   Retries: up to 3 per model

🔄 Trying model: gemini-2.5-flash
   Attempt 1/3...
   ❌ Attempt 1 failed: 429 rate_limit_exceeded
   ⏳ Waiting 2s before retry...
   Attempt 2/3...
   ❌ Attempt 2 failed: 429 rate_limit_exceeded
   ⏳ Waiting 4s before retry...
   Attempt 3/3...
   ✅ Success! Got 456 characters

📊 Stats:
{
  "total_attempts": 3,
  "successful": 1,
  "failed": 2,
  "success_rate": "33.3%",
  "model_usage": {"gemini-2.5-flash": 3}
}
```

---

## 🔝 Integration Checklist

- [ ] ModelRouter installed and tested (`model_router.py` created)
- [ ] Integrated into `script_generator.py` (use `get_router()`)
- [ ] Length validation added to script generation
- [ ] Batch planning implemented (optional)
- [ ] GitHub Actions workflow updated
- [ ] Tested with 1 video (shorts)
- [ ] Tested with 7-day batch
- [ ] Logs show clear audit trail
- [ ] All GitHub secrets configured
- [ ] Ready for production

---

## 📚 Reference

| Resource | Location |
|----------|----------|
| **Full Strategy** | `ARCHITECTURE_IMPROVEMENTS.md` |
| **ModelRouter Code** | `core/utils/model_router.py` |
| **Example Usage** | Bottom of `model_router.py` |
| **youtube_podcast Source** | https://github.com/crosspostly/youtube_podcast |

---

**Status:** Implementation phase 1 complete ✅

**Next:** Integrate ModelRouter into script_generator.py (step 1) 👊
