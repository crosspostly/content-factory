# 🏃 Architecture Improvements from youtube_podcast → content-factory

**Status:** 📝 Planning & Strategy  
**Date:** 13 Dec 2025  
**Context:** Adapting proven patterns from youtube_podcast (React/Gemini interactive studio) into content-factory (Python/GitHub Actions headless factory)

---

## 🎯 Executive Summary

`youtube_podcast` has **battle-tested architecture** for:
- ✅ Robust AI text generation with **fallback models** (flash-lite → 2.5-flash)
- ✅ **Retry logic** with exponential backoff + JSON error recovery
- ✅ **Length validation** for generated scripts (8.5K–10K chars)
- ✅ **Batch content planning** before per-video generation
- ✅ **Chapter-based packaging** with metadata
- ✅ **Comprehensive logging** for debugging

**Opportunity:** Port these patterns into content-factory's **headless GitHub Actions pipeline** for:
- Reliable multi-attempt generation without manual intervention
- Batch horoscope generation (N months in 1 run)
- Atomic chapter packaging + metadata export
- Crystal-clear audit trail in GitHub logs

---

## 🏗️ Part 1: Model Fallback Architecture

### Current State (youtube_podcast)

```typescript
// services/aiTextService.ts
const PRIMARY_TEXT_MODEL = 'gemini-flash-lite-latest';
const FALLBACK_TEXT_MODEL = 'gemini-2.5-flash';

export const generateContentWithFallback = async (
    params: { contents: any; config?: any; }, 
    log: LogFunction,
): Promise<GenerateContentResponse> => {
    try {
        return await withRetries(() => attemptGeneration(PRIMARY_TEXT_MODEL), log);
    } catch (primaryError) {
        log({ type: 'error', message: `Primary model failed, switching to fallback` });
        return await withRetries(() => attemptGeneration(FALLBACK_TEXT_MODEL), log);
    }
};
```

**Strengths:**
- Graceful degradation (fast → powerful)
- Each model gets full retry budget
- Clear error tracking

### Port to content-factory (Python)

**New file:** `core/utils/model_router.py` (already exists, but needs enhancement)

```python
# core/utils/model_router.py

from typing import Callable, Any, Optional
import logging
import time

logger = logging.getLogger(__name__)

# Model priorities (fast → powerful)
PRIMARY_MODELS = {
    "script": "gemini-2.5-flash",  # Fast turnaround
    "tts": "gemini-2.5-flash",      # Good quality
}

FALLBACK_MODELS = {
    "script": "gemini-2.0-flash",
    "tts": "gemini-2.0-flash",
}

MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 2  # Exponential backoff: 2, 4, 8 secs

def generate_with_fallback(
    api_key: str,
    task: str,  # "script", "tts", etc
    prompt: str,
    **kwargs
) -> str:
    """
    Generate content with fallback model support.
    
    Priority:
    1. Try PRIMARY model with retries
    2. If fails → try FALLBACK with retries
    3. If both fail → raise with detailed error
    """
    
    primary = PRIMARY_MODELS.get(task)
    fallback = FALLBACK_MODELS.get(task)
    
    for model in [primary, fallback]:
        if not model:
            continue
            
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                logger.info(f"🔄 Attempt {attempt}/{MAX_RETRIES} with model: {model} (task: {task})")
                response = _call_gemini_api(api_key, model, prompt, **kwargs)
                logger.info(f"✅ Success with {model}")
                return response
            
            except Exception as e:
                logger.warning(f"❌ Attempt {attempt} failed: {str(e)}")
                
                if attempt < MAX_RETRIES:
                    wait_time = RETRY_DELAY_SECONDS * (2 ** (attempt - 1))
                    logger.info(f"⏳ Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"❌ Model {model} exhausted all {MAX_RETRIES} retries")
    
    # Both models failed
    raise RuntimeError(
        f"All models failed for task '{task}':\n"
        f"  Primary: {primary}\n"
        f"  Fallback: {fallback}\n"
        f"  Max retries per model: {MAX_RETRIES}\n"
        f"Check API key and rate limits."
    )

def _call_gemini_api(api_key: str, model: str, prompt: str, **kwargs) -> str:
    """Actual API call (wraps genai library)"""
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    
    client = genai.GenerativeModel(model)
    response = client.generate_content(prompt, **kwargs)
    
    if not response.text:
        raise ValueError("Empty response from API")
    
    return response.text
```

---

## 📊 Part 2: Length Validation Loop

### Current State (youtube_podcast)

```typescript
// Validate script meets minimum length before accepting
while (attempt < MAX_REGENERATION_ATTEMPTS) {
    const response = await generateContentWithFallback(...);
    const data = parseGeminiJsonResponse(response.text);
    
    if (!validateScriptLength(data.script, chapterNumber, log)) {
        if (attempt < MAX_REGENERATION_ATTEMPTS) {
            const deficit = MIN_SCRIPT_LENGTH - currentLength;
            log({ type: 'warning', message: `Retrying with +${deficit} chars needed` });
            continue; // Retry generation
        }
    }
    
    // Success
    return data;
}
```

**Key insight:** AI can miss target length. **Don't accept first pass.** Validate → reject if short → regenerate with stricter prompt.

### Port to content-factory

**Update:** `core/generators/script_generator.py`

```python
# core/generators/script_generator.py

MIN_SCRIPT_LENGTH = 300  # 3-4 minutes of horoscope
MAX_SCRIPT_LENGTH = 800  # 8-10 minutes
MAX_LENGTH_ATTEMPTS = 3

def _calculate_text_length(script_dict: dict) -> int:
    """Calculate non-SFX text length"""
    if isinstance(script_dict.get('script'), str):
        return len(script_dict['script'])
    return 0

def _validate_script_length(script_dict: dict, attempt: int) -> tuple[bool, str]:
    """
    Validate script meets length requirements.
    Returns (is_valid, reason)
    """
    length = _calculate_text_length(script_dict)
    
    if length < MIN_SCRIPT_LENGTH:
        return False, f"Too short: {length} < {MIN_SCRIPT_LENGTH} (deficit: {MIN_SCRIPT_LENGTH - length})"
    
    if length > MAX_SCRIPT_LENGTH:
        return False, f"Too long: {length} > {MAX_SCRIPT_LENGTH} (excess: {length - MAX_SCRIPT_LENGTH})"
    
    return True, f"✅ Valid length: {length} chars"

def generate_horoscope_script(
    config: ProjectConfig,
    target_date: str,
    format: str,  # "shorts", "long_form", "ad"
    api_key: str
) -> dict:
    """
    Generate horoscope script with length validation.
    """
    
    for attempt in range(1, MAX_LENGTH_ATTEMPTS + 1):
        logger.info(f"📝 Attempt {attempt}/{MAX_LENGTH_ATTEMPTS} to generate {format} script")
        
        try:
            # Generate
            prompt = _get_horoscope_prompt(format, target_date, config.project.language)
            raw_response = generate_with_fallback(
                api_key,
                task="script",
                prompt=prompt
            )
            
            # Parse JSON
            script_dict = json.loads(raw_response)
            
            # Validate length
            is_valid, reason = _validate_script_length(script_dict, attempt)
            logger.info(f"Length check: {reason}")
            
            if is_valid:
                logger.info(f"✅ Script generation complete after attempt {attempt}")
                return script_dict
            
            # Not valid - retry with enforced length in prompt
            if attempt < MAX_LENGTH_ATTEMPTS:
                logger.warning(f"🔄 Retrying with length enforcement...")
                length = _calculate_text_length(script_dict)
                deficit = MAX(0, MIN_SCRIPT_LENGTH - length)
                
                # Append strict instruction to prompt
                prompt += f"\n\n**CRITICAL**: Output MUST be at least {MIN_SCRIPT_LENGTH} characters. "\
                          f"Current: {length}. Add {deficit} more characters of detailed horoscope text."
                
                # Retry with same logic
                raw_response = generate_with_fallback(api_key, task="script", prompt=prompt)
                script_dict = json.loads(raw_response)
                
                is_valid, reason = _validate_script_length(script_dict, attempt)
                if is_valid:
                    logger.info(f"✅ Script valid after length-enforced retry")
                    return script_dict
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON (attempt {attempt}): {e}")
            if attempt == MAX_LENGTH_ATTEMPTS:
                raise
    
    # All attempts exhausted
    raise RuntimeError(
        f"Failed to generate valid {format} script after {MAX_LENGTH_ATTEMPTS} attempts. "
        f"Check prompt quality and API responses."
    )
```

---

## 🎬 Part 3: Batch Content Planning

### Current State (youtube_podcast)

```typescript
export const generateContentPlan = async (
    count: number,
    log: LogFunction
): Promise<DetailedContentIdea[]> => {
    // AI generates N unique ideas FIRST
    // Then each idea becomes a separate video
    const prompt = getContentPlanPrompt(count);
    const response = await generateContentWithFallback({ contents: prompt });
    return parseGeminiJsonResponse(response.text);
};

// Usage:
const ideas = await generateContentPlan(5);  // 5 unique topics
for (const idea of ideas) {
    generatePodcastBlueprint(idea.topic);  // Each gets full treatment
}
```

**Why it works:** AI can hallucinate/repeat ideas. **Ask upfront for N ideas → validate diversity → lock them in.** Then generate each one deterministically.

### Port to content-factory

**New feature:** Batch horoscope planning for multiple dates/zodiac signs

**New file:** `core/generators/content_planner.py`

```python
# core/generators/content_planner.py

from datetime import datetime, timedelta
from typing import List
import json
import logging

logger = logging.getLogger(__name__)

def plan_horoscope_batch(
    api_key: str,
    start_date: str,  # YYYY-MM-DD
    num_days: int,
    format: str  # "shorts", "long_form", "weekly"
) -> List[dict]:
    """
    Plan batch horoscope generation.
    
    Example:
        plan_horoscope_batch(api_key, "2025-12-13", 7, "shorts")
        → [
            {"date": "2025-12-13", "zodiac": "Aries", "theme": "..."},
            {"date": "2025-12-14", "zodiac": "Taurus", "theme": "..."},
            ...
          ]
    """
    
    logger.info(f"📅 Planning batch: {num_days} days starting {start_date}")
    
    # Generate N unique plans
    prompt = f"""
    Create a detailed content plan for {num_days} horoscope {format} videos.
    
    For format '{format}':
    - shorts: 15-30 sec, hook + main prediction + CTA
    - long_form: 10-15 min, intro + 3 zodiac signs deep dives + outro
    - weekly: 5-10 min, week overview + key events
    
    Return JSON:
    {{
        "plan": [
            {{
                "day": 1,
                "date": "2025-12-13",
                "theme": "Cosmic Alignment & Career Moves",
                "hook": "Mercury's influence brings clarity...",
                "key_points": ["Point 1", "Point 2", ...],
                "tone": "inspiring"
            }},
            ...
        ]
    }}
    """
    
    try:
        response = generate_with_fallback(api_key, "script", prompt)
        plan_data = json.loads(response)
        
        # Validate
        if not plan_data.get('plan') or len(plan_data['plan']) < num_days:
            logger.warning(f"Plan has {len(plan_data.get('plan', []))} items, expected {num_days}")
        
        # Lock dates
        start = datetime.strptime(start_date, "%Y-%m-%d")
        for i, item in enumerate(plan_data['plan'][:num_days]):
            item['date'] = (start + timedelta(days=i)).strftime("%Y-%m-%d")
        
        logger.info(f"✅ Plan created for {len(plan_data['plan'])} days")
        return plan_data['plan'][:num_days]
    
    except Exception as e:
        logger.error(f"❌ Failed to plan batch: {e}")
        
        # Fallback: generate simple plan locally
        logger.info("Generating fallback plan...")
        fallback_plan = []
        start = datetime.strptime(start_date, "%Y-%m-%d")
        
        themes = [
            "New Beginnings",
            "Relationships & Love",
            "Career & Growth",
            "Health & Wellness",
            "Finance & Abundance",
            "Spiritual Awakening",
            "Adventure & Discovery"
        ]
        
        for i in range(num_days):
            fallback_plan.append({
                "day": i + 1,
                "date": (start + timedelta(days=i)).strftime("%Y-%m-%d"),
                "theme": themes[i % len(themes)],
                "hook": f"Your horoscope for {(start + timedelta(days=i)).strftime('%B %d')}",
                "key_points": ["Personal growth", "Positive energy", "Take action"],
                "tone": "inspiring"
            })
        
        return fallback_plan

def generate_batch(
    api_key: str,
    pixabay_key: str,
    start_date: str,
    num_days: int,
    format: str,
    project: str = "youtube_horoscope"
):
    """
    Main batch generation orchestrator.
    """
    
    logger.info(f"\n" + "="*70)
    logger.info(f"🚀 BATCH HOROSCOPE GENERATION START")
    logger.info(f"="*70)
    logger.info(f"Dates: {start_date} → +{num_days} days")
    logger.info(f"Format: {format}")
    logger.info(f"Project: {project}\n")
    
    # Step 1: Plan
    plan = plan_horoscope_batch(api_key, start_date, num_days, format)
    
    # Step 2: Generate each
    results = []
    for i, day_plan in enumerate(plan, 1):
        logger.info(f"\n📺 [{i}/{num_days}] Generating {day_plan['date']} - {day_plan['theme']}")
        
        try:
            # Generate full pipeline for this date
            # (script → tts → video → metadata)
            result = generate_full_pipeline(
                api_key=api_key,
                pixabay_key=pixabay_key,
                date=day_plan['date'],
                format=format,
                theme=day_plan['theme'],
                project=project
            )
            
            results.append(result)
            logger.info(f"✅ Complete: {result['video_path']}")
        
        except Exception as e:
            logger.error(f"❌ Failed for {day_plan['date']}: {e}")
            results.append({
                "date": day_plan['date'],
                "status": "failed",
                "error": str(e)
            })
    
    # Step 3: Summary
    successful = sum(1 for r in results if r.get('status') != 'failed')
    logger.info(f"\n" + "="*70)
    logger.info(f"✅ Batch complete: {successful}/{num_days} successful")
    logger.info(f"="*70 + "\n")
    
    return results
```

---

## 📦 Part 4: Chapter-Based Packaging & Metadata

### Current State (youtube_podcast)

```typescript
// services/chapterPackager.ts
// Generates:
// ├── chapter_01/
// │   ├── script.json
// │   ├── audio/
// │   │   ├── narration.wav
// │   │   ├── music.mp3
// │   │   └── sfx/
// │   ├── images/
// │   │   ├── bg_01.png
// │   │   └── text_overlay.png
// │   └── metadata.json
// ├── chapter_02/ ...
// └── assemble_video.bat  ← FFmpeg script
```

### Port to content-factory

**Create:** `core/orchestrators/package_manager.py`

```python
# core/orchestrators/package_manager.py

from pathlib import Path
import json
import shutil
from datetime import datetime

class HoroscopePackage:
    """
    Structure for complete horoscope generation output.
    """
    
    def __init__(self, project: str, date: str, format: str):
        self.project = project
        self.date = date
        self.format = format
        
        # Base: output/packages/youtube_horoscope/2025-12-13_shorts/
        self.base_dir = Path("output/packages") / project / f"{date}_{format}"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Subdirs
        self.script_dir = self.base_dir / "script"
        self.audio_dir = self.base_dir / "audio"
        self.video_dir = self.base_dir / "video"
        self.images_dir = self.base_dir / "images"
        
        for d in [self.script_dir, self.audio_dir, self.video_dir, self.images_dir]:
            d.mkdir(exist_ok=True)
    
    def save_script(self, script_data: dict, filename: str = "script.json"):
        """Save generated script"""
        path = self.script_dir / filename
        with open(path, 'w') as f:
            json.dump(script_data, f, indent=2, ensure_ascii=False)
        return path
    
    def save_audio(self, audio_path: Path, format: str = "wav"):
        """Save TTS audio"""
        dest = self.audio_dir / f"narration.{format}"
        shutil.copy(audio_path, dest)
        return dest
    
    def save_image(self, image_path: Path, index: int = 0):
        """Save background image"""
        ext = Path(image_path).suffix
        dest = self.images_dir / f"bg_{index:02d}{ext}"
        shutil.copy(image_path, dest)
        return dest
    
    def save_video(self, video_path: Path):
        """Save final video"""
        dest = self.video_dir / "horoscope.mp4"
        shutil.copy(video_path, dest)
        return dest
    
    def create_metadata(self, script_data: dict, video_info: dict):
        """
        Create comprehensive metadata.
        """
        metadata = {
            "generated_at": datetime.now().isoformat(),
            "project": self.project,
            "date": self.date,
            "format": self.format,
            "script": {
                "hook": script_data.get('hook'),
                "cta": script_data.get('engagement_cta'),
                "duration_target_sec": script_data.get('duration_sec_target')
            },
            "video": {
                "resolution": video_info.get('resolution'),
                "duration_sec": video_info.get('duration_sec'),
                "fps": video_info.get('fps'),
                "file_size_mb": video_info.get('file_size_mb')
            },
            "files": {
                "script": str(self.script_dir / "script.json"),
                "audio": str(self.audio_dir / "narration.wav"),
                "video": str(self.video_dir / "horoscope.mp4"),
                "images": str(self.images_dir)
            }
        }
        
        meta_path = self.base_dir / "metadata.json"
        with open(meta_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return metadata
    
    def export_to_zip(self, output_name: str = None) -> Path:
        """
        Package everything into ZIP for download.
        """
        if output_name is None:
            output_name = f"{self.date}_{self.format}"
        
        zip_path = Path("output") / f"{output_name}.zip"
        
        shutil.make_archive(
            str(zip_path.with_suffix('')),  # Without .zip
            'zip',
            self.base_dir
        )
        
        return zip_path
```

---

## 🔄 Part 5: GitHub Actions Integration

### New Workflow: Batch Generation

**File:** `.github/workflows/generate-horoscope-batch.yml`

```yaml
name: Generate Horoscope Batch

on:
  workflow_dispatch:
    inputs:
      start_date:
        description: 'Start date (YYYY-MM-DD)'
        required: true
        default: '2025-12-13'
        type: string
      num_days:
        description: 'Number of days to generate'
        required: false
        default: '7'
        type: choice
        options:
          - '1'
          - '7'
          - '30'
          - '90'
      format:
        description: 'Video format'
        required: false
        default: 'shorts'
        type: choice
        options:
          - shorts
          - long-form
          - weekly

jobs:
  batch-generate:
    runs-on: ubuntu-22.04
    timeout-minutes: 240  # 4 hours for 30 days of videos
    
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: Install dependencies
        run: pip install -r requirements.txt -q
      
      - name: Generate batch
        env:
          GOOGLE_AI_API_KEY: ${{ secrets.GOOGLE_AI_API_KEY }}
          PIXABAY_API_KEY: ${{ secrets.PIXABAY_API_KEY }}
        run: |
          python3 << 'PYTHON'
          from datetime import datetime
          from core.generators.content_planner import generate_batch
          
          results = generate_batch(
              api_key="${{ env.GOOGLE_AI_API_KEY }}",
              pixabay_key="${{ env.PIXABAY_API_KEY }}",
              start_date="${{ inputs.start_date }}",
              num_days=int("${{ inputs.num_days }}"),
              format="${{ inputs.format }}"
          )
          
          # Summary
          successful = sum(1 for r in results if r.get('status') != 'failed')
          print(f"\n✅ Batch complete: {successful}/{len(results)} successful")
          PYTHON
      
      - name: Upload batch artifacts
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: horoscope-batch-${{ inputs.start_date }}
          path: output/packages/
          retention-days: 14
```

---

## 📋 Part 6: Logging & Audit Trail

### Current State (youtube_podcast)

```typescript
type LogEntry = {
    timestamp: Date,
    type: 'info' | 'warning' | 'error' | 'request' | 'response',
    message: string,
    data?: any
};

// UI shows colored logs in real-time
// Users can export full journal
```

### Port to content-factory

**Create:** `core/utils/detailed_logger.py`

```python
# core/utils/detailed_logger.py

import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Any, Optional

class DetailedLogger:
    """
    Structured logging for batch generation.
    Logs to both console and JSON file.
    """
    
    def __init__(self, log_dir: str = "output/logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # JSON log file
        self.log_file = self.log_dir / f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.entries = []
        
        # Console logger
        self.logger = logging.getLogger(__name__)
    
    def log(self, level: str, message: str, data: Optional[Any] = None):
        """
        Log structured entry.
        
        Levels: info, warning, error, request, response
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
            "data": data if data is None else self._serialize(data)
        }
        
        self.entries.append(entry)
        
        # Console output with color
        color_map = {
            "info": "\033[94m",  # Blue
            "warning": "\033[93m",  # Yellow
            "error": "\033[91m",  # Red
            "request": "\033[92m",  # Green
            "response": "\033[92m",  # Green
        }
        reset = "\033[0m"
        color = color_map.get(level, "")
        
        print(f"{color}[{level.upper()}]{reset} {message}")
        if data:
            print(f"  {self._serialize(data)[:200]}...")
    
    def save(self):
        """
        Save all entries to JSON.
        """
        with open(self.log_file, 'w') as f:
            json.dump(self.entries, f, indent=2, ensure_ascii=False)
        print(f"\n📋 Logs saved: {self.log_file}")
    
    def _serialize(self, obj: Any) -> str:
        if isinstance(obj, (dict, list)):
            return json.dumps(obj, ensure_ascii=False)
        return str(obj)
```

**Usage in workflow:**
```python
logger = DetailedLogger()
logger.log("info", f"Generating {date}...")
logger.log("response", f"Script length: {len(script)}")
logger.save()  # Save at end
```

---

## 🎯 Implementation Roadmap

### Phase 1: Foundation (Week 1)
- [ ] Implement `model_router.py` with fallback + retry logic
- [ ] Add length validation to `script_generator.py`
- [ ] Create `content_planner.py` for batch planning

### Phase 2: Packaging (Week 2)
- [ ] Create `package_manager.py` for chapter-based structure
- [ ] Implement `detailed_logger.py`
- [ ] Create batch generation workflow `.github/workflows/generate-horoscope-batch.yml`

### Phase 3: Integration (Week 3)
- [ ] Test 1-day batch (shorts + long-form + metadata)
- [ ] Test 7-day batch end-to-end
- [ ] Add GitHub Actions artifact upload
- [ ] Write batch generation documentation

### Phase 4: Polish (Week 4)
- [ ] Performance optimizations (parallel generation?)
- [ ] Error recovery strategies
- [ ] Pre-publish checklist (like youtube_podcast)

---

## ✅ Success Criteria

- ✅ Generate 7 horoscope videos in single GitHub Actions run
- ✅ All videos properly packaged with metadata
- ✅ Full audit trail in logs
- ✅ Automatic artifact upload for download
- ✅ Zero manual intervention needed
- ✅ Clear error messages if anything fails
- ✅ Fallback models used if primary fails
- ✅ Scripts meet minimum length requirements

---

## 📚 Reference: youtube_podcast Patterns

| Pattern | File | Key Learning |
|---------|------|---------------|
| **Model Fallback** | `aiTextService.ts` | Try fast → then powerful, each with retries |
| **Length Validation** | `generateNextChapterScript()` | Reject short scripts, regenerate with stricter prompt |
| **Batch Planning** | `generateContentPlan()` | Plan N ideas upfront, then generate each |
| **Chapter Packaging** | `chapterPackager.ts` | Atomic ZIP export with metadata |
| **Logging** | `App.tsx`, `LogEntry` | Structured logs with types (info/error/request/response) |
| **Error Recovery** | `generateContentWithFallback()` | Comprehensive error handling at each stage |

---

**Next:** Pick up Phase 1 items and start implementing! 🚀
