# 🚧 Content Factory - Узкие места и планы улучшений

**Дата:** Декабрь 2025  
**Версия:** 1.0.0  
**Статус:** Active monitoring

---

## 🔴 КРИТИЧЕСКИЕ УЗКИЕ МЕСТА

### 1. TTS создаёт тишину вместо голоса

**Приоритет:** 🔴 CRITICAL  
**Компонент:** Part 2 (TTS Generator)  
**Файл:** `core/generators/tts_generator.py`

#### Проблема

Текущая реализация пытается использовать Gemini 2.5 Flash для text-to-speech, но API не возвращает аудио данные:

```python
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=text
)

# ❌ PROBLEM: response.audio is None
if hasattr(response, 'audio') and response.audio:
    # Этот код никогда не выполняется
    audio_data = response.audio
else:
    # Fallback: создать тишину
    _create_silent_wav(output_path, estimated_duration)
```

#### Impact

- ❌ **Видео БЕЗ озвучки** - только тишина
- ❌ **Полностью блокирует production** использование
- ❌ **Нет смысла в субтитрах** без аудио
- 📊 **Engagement: -90%** (видео без звука никто не смотрит)

#### Root Cause

**Hypothesis 1:** Gemini 2.5 Flash не поддерживает TTS через `generate_content()`
- API предназначен для текстовой генерации, а не аудио
- Нужен специальный TTS endpoint

**Hypothesis 2:** Неправильный формат запроса
- Может нужен другой метод SDK
- Или специальные параметры

**Hypothesis 3:** Feature не доступна в текущем tier
- Может TTS требует paid plan
- Или waitlist/early access

#### Solution Options

**Option A: Google Cloud Text-to-Speech API** (Recommended)

```python
from google.cloud import texttospeech

client = texttospeech.TextToSpeechClient()

synthesis_input = texttospeech.SynthesisInput(text=text)
voice = texttospeech.VoiceSelectionParams(
    language_code="ru-RU",
    name="ru-RU-Wavenet-D",  # High-quality female voice
    ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
)
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3,
    speaking_rate=1.0,  # Normal speed
    pitch=0.0,  # Normal pitch
)

response = client.synthesize_speech(
    input=synthesis_input,
    voice=voice,
    audio_config=audio_config
)

# response.audio_content contains MP3 bytes
with open(output_path, 'wb') as out:
    out.write(response.audio_content)
```

**Pros:**
- ✅ Native Google Cloud integration
- ✅ High-quality WaveNet voices
- ✅ Supports Russian (ru-RU)
- ✅ SSML support (advanced control)
- ✅ Reliable and production-ready

**Cons:**
- 💰 Paid API ($4 per 1M characters for WaveNet)
- 📄 Requires Google Cloud account + credentials
- ⚙️ More setup complexity

**Cost estimate:** 
- 1000 символов/скрипт × 50 видео/день = 50,000 символов/день
- 50,000 × 30 дней = 1.5M символов/месяц
- Cost: ~$6/месяц (acceptable)

---

**Option B: Edge-TTS** (Free alternative)

```python
import edge_tts
import asyncio

async def synthesize():
    communicate = edge_tts.Communicate(
        text=text,
        voice="ru-RU-DariyaNeural",  # Female Russian voice
        rate="+0%",  # Normal speed
        pitch="+0Hz"  # Normal pitch
    )
    await communicate.save(output_path)

asyncio.run(synthesize())
```

**Pros:**
- ✅ Completely FREE
- ✅ No API key required
- ✅ High-quality neural voices
- ✅ Supports Russian
- ✅ Simple integration

**Cons:**
- ⚠️ Unofficial API (uses Microsoft Edge TTS)
- ⚠️ May be rate-limited or blocked
- ⚠️ No SLA or reliability guarantee
- ⚠️ Legal gray area

---

**Option C: ElevenLabs** (Premium quality)

```python
from elevenlabs import generate, save, set_api_key

set_api_key(api_key)

audio = generate(
    text=text,
    voice="Bella",  # Or custom cloned voice
    model="eleven_multilingual_v2"
)

save(audio, output_path)
```

**Pros:**
- ✅ Best-in-class voice quality
- ✅ Voice cloning (custom voices)
- ✅ Multilingual support
- ✅ Emotion control

**Cons:**
- 💰 Expensive ($22-$99/month for sufficient quota)
- 📄 Requires API key
- 🌐 Russian support may be limited

---

#### Recommended Solution

**Phase 1 (Immediate):** Use **Edge-TTS** for quick fix
- Free, fast implementation
- Good enough quality для MVP
- Risk: может перестать работать

**Phase 2 (Production):** Migrate to **Google Cloud TTS**
- More reliable
- Better quality
- Acceptable cost (~$6/month)
- Official API with SLA

#### Implementation Plan

**Week 1:**
- [ ] Research & prototype Edge-TTS integration
- [ ] Test Russian voices quality
- [ ] Update `tts_generator.py`
- [ ] Test full pipeline (script → audio → video)

**Week 2:**
- [ ] Update unit tests
- [ ] Add error handling
- [ ] Deploy & monitor

**Week 3-4:**
- [ ] Setup Google Cloud TTS
- [ ] Implement fallback: Edge-TTS → Google Cloud TTS
- [ ] Cost monitoring
- [ ] Production deployment

#### Effort Estimate

- **Edge-TTS implementation:** 1-2 дня
- **Google Cloud TTS implementation:** 2-3 дня
- **Testing & deployment:** 2-3 дня
- **Total:** 1 неделя (с запасом)

#### Success Metrics

- [ ] 100% videos have real voice (not silence)
- [ ] <2% TTS generation failures
- [ ] Voice quality rating: 8+/10 (user surveys)
- [ ] Cost per video: <$0.10 for TTS

---

### 2. Нет встроенных субтитров

**Приоритет:** 🔴 CRITICAL  
**Компонент:** Part 3 (Video Renderer) + Part 4 (Not implemented)  
**Impact:** -30% engagement

#### Проблема

Видео не подходит для:
- 📱 **Мобильного просмотра без звука** (70% YouTube Shorts смотрят без звука)
- 🦻 **Пользователей с нарушениями слуха** (accessibility)
- 🔍 **SEO** (нет текста для индексирования)
- 🌍 **Международной аудитории** (нет переводов)

Примерная потеря engagement:
- YouTube Shorts without subs: -30% views
- TikTok without subs: -40% views
- Long-form without subs: -20% views

#### Impact

📊 **Engagement loss:**
- Current: 1000 views/video
- With subtitles: 1300-1400 views/video (+30-40%)
- Revenue impact: +$5-10/video (ads)

#### Solution

См. `SUBTITLE_IMPLEMENTATION_PLAN.md` для детального плана.

**Summary:**
1. Use WhisperX для transcription
2. Generate SRT files с word-level timestamps
3. Embed subtitles via ffmpeg (burn-in)
4. Add styling (font, color, position)

#### Effort

- **Implementation:** 2-3 недели
- **Testing:** 1 неделя
- **Total:** 3-4 недели

#### Priority

🔴 **CRITICAL** - should be done immediately after TTS fix

---

### 3. Медленный рендеринг видео

**Приоритет:** 🟠 HIGH  
**Компонент:** Part 3 (Video Renderer)  
**Impact:** Cannot scale production

#### Проблема

**Current performance:**
- Shorts (30-60 sec): 5-10 минут
- Long-form (10-12 min): 15-20 минут
- Ad (15-30 sec): 3-5 минут

**Why slow:**
1. MoviePy is single-threaded (no parallelization)
2. FFmpeg без GPU acceleration
3. No caching of stock videos
4. Redundant re-encoding

**Impact:**

GitHub Actions free tier: 2000 minutes/month
- Can generate: ~100-200 shorts/month (2000 / 10 = 200)
- Need: 50 videos/day = 1500/month
- Gap: **7.5x недостаточно capacity**

Без оптимизации невозможно масштабировать на production volumes.

#### Root Causes

**1. MoviePy architecture**
- Python-based (GIL bottleneck)
- Single-threaded by design
- Inefficient memory management

**2. FFmpeg configuration**
- Using default preset (medium) - медленный
- No GPU encoding (NVENC/VCE)
- No multi-threading

**3. No parallelization**
- Long-form renders 3 blocks sequentially
- Could render in parallel (3x speedup)

**4. Redundant work**
- Stock videos downloaded каждый раз
- No caching

#### Solution Options

**Option A: Parallelize block rendering** (Quick win)

```python
import asyncio
from concurrent.futures import ProcessPoolExecutor

async def render_blocks_parallel(blocks):
    with ProcessPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(render_block, block)
            for block in blocks
        ]
        results = [f.result() for f in futures]
    return results
```

**Expected improvement:** 3x faster для long-form (15 min → 5 min)

---

**Option B: GPU-accelerated FFmpeg**

```bash
ffmpeg -hwaccel cuda -i input.mp4 \
  -c:v h264_nvenc -preset fast \
  -b:v 5000k output.mp4
```

**Requirements:**
- NVIDIA GPU (CUDA support)
- FFmpeg compiled with NVENC support

**Expected improvement:** 2-3x faster (5 min → 2 min для shorts)

**Cost:** Need GPU runner на GitHub Actions или cloud GPU ($0.50-1/hour)

---

**Option C: Optimize FFmpeg preset**

Current:
```python
clip.write_videofile(
    codec="libx264",
    preset="medium"  # Slow
)
```

Optimized:
```python
clip.write_videofile(
    codec="libx264",
    preset="fast",  # 2x faster, minimal quality loss
    threads=4  # Use all CPU cores
)
```

**Expected improvement:** 2x faster, free

---

**Option D: Cache stock videos**

```python
def get_stock_video(keywords):
    cache_key = hashlib.md5(keywords.encode()).hexdigest()
    cache_path = Path("cache/stock") / f"{cache_key}.mp4"
    
    if cache_path.exists():
        return str(cache_path)  # Instant
    
    # Download & cache
    video_url = pixabay_api(keywords)
    download(video_url, cache_path)
    return str(cache_path)
```

**Expected improvement:** Save 30-60 seconds per video

---

#### Recommended Solution

**Phase 1 (Quick wins - 1 week):**
1. ✅ Optimize FFmpeg preset (fast instead of medium)
2. ✅ Enable multi-threading (`threads=4`)
3. ✅ Cache stock videos

**Expected:** 2x faster (10 min → 5 min для shorts)

**Phase 2 (Parallelization - 2 weeks):**
4. ✅ Parallelize long-form block rendering
5. ✅ Async pipeline

**Expected:** 3x faster для long-form (15 min → 5 min)

**Phase 3 (GPU acceleration - 1 month):**
6. ✅ Setup GPU runner
7. ✅ Implement NVENC encoding
8. ✅ Benchmark & compare

**Expected:** 2-3x additional speedup (5 min → 2 min)

#### Total Expected Improvement

- Shorts: 10 min → 2 min (5x faster)
- Long-form: 20 min → 3 min (6.5x faster)
- Ad: 5 min → 1 min (5x faster)

**New capacity:**
- 2000 minutes / 2 min per short = 1000 shorts/month
- 50 videos/день × 30 = 1500/month
- Still need more (1.5x), but much closer

**Alternative:** Use cloud GPU runners ($0.50/hour)
- Cost: 1500 videos × 2 min / 60 = 50 hours/month
- Cost: 50 × $0.50 = $25/month (acceptable)

---

### 4. Нет мониторинга + логирования

**Приоритет:** 🟠 HIGH  
**Impact:** Impossible to debug production issues

#### Проблема

**Current state:**
- ✅ Basic logging (print statements)
- ❌ No structured logs (JSON)
- ❌ No centralized logging
- ❌ No error tracking
- ❌ No performance metrics
- ❌ No alerting

**Impact:**

When something breaks:
1. No visibility что именно сломалось
2. No historical data для анализа
3. Нужно manually inspect logs
4. Cannot track performance degradation
5. No alerts → delayed response

**Example scenario:**
```
[ERROR] Video rendering failed
```

Questions:
- Which component failed? (script/TTS/video?)
- Which video? (date, project, mode?)
- How often does this happen? (1% или 50%?)
- Is this a new issue or ongoing?
- What's the root cause?

**Cannot answer without proper monitoring!**

#### Solution

**Phase 1: Structured Logging**

```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "component": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, 'request_id', None),
            "project": getattr(record, 'project', None),
            "mode": getattr(record, 'mode', None),
            "duration_ms": getattr(record, 'duration_ms', None),
            "error": getattr(record, 'error', None),
        })

logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.FileHandler("logs/app.json"),
        logging.StreamHandler()
    ]
)
logging.getLogger().handlers[0].setFormatter(JSONFormatter())
```

**Benefits:**
- ✅ Machine-readable logs
- ✅ Easy to query & analyze
- ✅ Integration with log aggregators (CloudWatch, Datadog)

---

**Phase 2: Error Tracking**

```python
def create_error_issue(error, context):
    """Auto-create GitHub Issue on error."""
    title = f"[AUTO] {type(error).__name__}: {str(error)[:50]}"
    body = f"""
## Error Details
- **Component:** {context['component']}
- **Project:** {context['project']}
- **Mode:** {context['mode']}
- **Timestamp:** {context['timestamp']}

## Error Message
```
{str(error)}
```

## Stack Trace
```
{context['traceback']}
```

## Context
- Request ID: {context['request_id']}
- Config: {context['config']}

## Reproducibility
Run with:
```bash
python main.py --project {context['project']} --mode {context['mode']} --date {context['date']}
```
"""
    
    gh_api.create_issue(
        repo="owner/content-factory",
        title=title,
        body=body,
        labels=["bug", "auto-created", context['component']]
    )
```

**Benefits:**
- ✅ Auto-triage errors
- ✅ Historical error tracking
- ✅ Duplicate detection
- ✅ Prioritization

---

**Phase 3: Performance Monitoring**

```python
import time
from functools import wraps

def track_performance(component):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            request_id = kwargs.get('request_id', 'unknown')
            
            try:
                result = func(*args, **kwargs)
                duration = (time.time() - start) * 1000
                
                logger.info(
                    f"{component} success",
                    extra={
                        'request_id': request_id,
                        'component': component,
                        'duration_ms': duration,
                        'status': 'success'
                    }
                )
                
                # Send to metrics system
                metrics.gauge(f"{component}.duration", duration)
                metrics.increment(f"{component}.success")
                
                return result
            
            except Exception as e:
                duration = (time.time() - start) * 1000
                
                logger.error(
                    f"{component} failed",
                    extra={
                        'request_id': request_id,
                        'component': component,
                        'duration_ms': duration,
                        'status': 'error',
                        'error': str(e)
                    }
                )
                
                metrics.increment(f"{component}.error")
                raise
        
        return wrapper
    return decorator

# Usage
@track_performance("script_generator")
def generate_short(config, date, request_id=None):
    ...
```

**Metrics to track:**
- `script_generator.duration` (ms)
- `script_generator.success` (count)
- `script_generator.error` (count)
- `tts_generator.duration` (ms)
- `video_renderer.duration` (ms)
- `pipeline.total_duration` (ms)
- `pipeline.success_rate` (%)

---

**Phase 4: Alerting**

```python
class AlertManager:
    def __init__(self):
        self.thresholds = {
            'error_rate': 0.05,  # 5%
            'avg_duration': 600000,  # 10 minutes
        }
    
    def check_alerts(self):
        error_rate = metrics.get('pipeline.error_rate')
        avg_duration = metrics.get('pipeline.avg_duration')
        
        if error_rate > self.thresholds['error_rate']:
            self.send_alert(
                severity='high',
                message=f"Error rate {error_rate:.1%} exceeds threshold"
            )
        
        if avg_duration > self.thresholds['avg_duration']:
            self.send_alert(
                severity='medium',
                message=f"Average duration {avg_duration/1000:.1f}s exceeds threshold"
            )
    
    def send_alert(self, severity, message):
        # Email
        send_email(
            to="tech-lead@company.com",
            subject=f"[{severity.upper()}] Content Factory Alert",
            body=message
        )
        
        # Telegram (optional)
        if severity == 'high':
            telegram_bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=f"🚨 {message}"
            )
```

---

#### Implementation Plan

**Week 1: Structured Logging**
- [ ] Implement JSON formatter
- [ ] Add request ID tracking
- [ ] Log all pipeline stages
- **Effort:** 2-3 дня

**Week 2: Error Tracking**
- [ ] GitHub Issue auto-creation
- [ ] Error categorization
- [ ] Duplicate detection
- **Effort:** 2-3 дня

**Week 3: Performance Monitoring**
- [ ] Add performance decorators
- [ ] Integrate metrics system (Prometheus/CloudWatch)
- [ ] Create dashboards
- **Effort:** 2-3 дня

**Week 4: Alerting**
- [ ] Implement alert manager
- [ ] Email integration
- [ ] Telegram integration (optional)
- **Effort:** 1-2 дня

#### Success Metrics

- [ ] 100% errors tracked
- [ ] <5 minutes MTTR (Mean Time To Repair)
- [ ] Performance regressions detected within 1 hour
- [ ] Zero unnoticed production failures

---

### 5. Pixabay rate limiting

**Приоритет:** 🟡 MEDIUM  
**Impact:** Cannot scale beyond 50 videos/день

#### Проблема

Pixabay Free tier:
- 50 API requests/день
- 1 request per video
- Limit: 50 videos/день

Current production needs:
- Target: 50+ videos/день
- Already at limit

Future needs:
- Growth: 100+ videos/день
- Gap: 2x недостаточно

#### Solution Options

**Option A: Premium Pixabay Account**
- Cost: $29/месяц
- Limit: 20,000 requests/month (666/день)
- **ROI:** Acceptable для commercial use

**Option B: Cache stock videos**
```python
def get_cached_stock(keywords):
    # Reuse stock videos for same keywords
    cache_key = hash(keywords)
    if cache_exists(cache_key):
        return cache_path
    
    # Download once, reuse forever
    download_and_cache(keywords)
```

**Expected:** 10x reduction в API calls (5 videos/день вместо 50)

**Option C: Alternative APIs**
- Pexels (free, 200/hour)
- Unsplash (free, 50/hour)
- Burst by Shopify (free, unlimited)

**Option D: Custom stock library**
- Build own library (100-200 videos)
- Rotate randomly
- Cost: $100-200 one-time

---

#### Recommended Solution

**Phase 1 (Immediate):**
- Implement caching (Option B)
- Reduce API calls 10x

**Phase 2 (If needed):**
- Add alternative APIs (Pexels, Unsplash)
- Fallback chain: Pixabay → Pexels → Gradient

**Phase 3 (Production):**
- Upgrade to Pixabay Premium ($29/month)
- Build custom stock library

---

## 🟡 СРЕДНИЕ УЗКИЕ МЕСТА

### 6. Нет кэширования скриптов

**Приоритет:** 🟡 MEDIUM  
**Impact:** Лишние API calls

#### Проблема

Если запустить `python main.py` дважды в день:
- Generates 2 different scripts
- Wastes API calls
- Inconsistent content

#### Solution

```python
def get_or_generate_script(project, date, mode):
    cache_path = Path(f"output/scripts/{project}/{date}/{mode}_*.json")
    
    if cache_path.exists():
        logger.info("Using cached script")
        return json.loads(cache_path.read_text())
    
    logger.info("Generating new script")
    return generate_script(project, date, mode)
```

**Effort:** 2-3 часа

---

### 7. Нет retry логики для видео

**Приоритет:** 🟡 MEDIUM  
**Impact:** Manual intervention required

#### Проблема

If video rendering fails:
- No automatic retry
- Need manual restart
- Wastes time

#### Solution

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=16)
)
def render_video(script, audio, mode):
    try:
        return _render_video_impl(script, audio, mode)
    except Exception as e:
        logger.warning(f"Render attempt failed: {e}")
        raise
```

**Effort:** 2-3 часа

---

### 8. Нет unit тестов для видео

**Приоритет:** 🟡 MEDIUM  
**Impact:** Fear to refactor

#### Проблема

Current tests:
- ✅ Mock-based tests exist
- ❌ No real rendering tests
- ❌ No visual regression tests
- ❌ Coverage unknown

Cannot safely refactor без tests.

#### Solution

**Phase 1: Unit tests**
```python
def test_shorts_rendering():
    script = load_fixture("shorts_script.json")
    audio = load_fixture("shorts_audio.wav")
    
    video_path = render_video(script, audio, "shorts")
    
    assert video_path.exists()
    assert get_video_duration(video_path) == audio.duration
    assert get_video_resolution(video_path) == (1080, 1920)
```

**Phase 2: Visual regression**
```python
def test_visual_regression():
    video = render_shorts(test_script)
    
    # Compare frames
    current_frames = extract_frames(video, [0, 5, 10])
    expected_frames = load_baseline("shorts_baseline_frames.png")
    
    similarity = compare_images(current_frames, expected_frames)
    assert similarity > 0.95  # 95% similar
```

**Effort:** 1 неделя

---

## 🟢 МЕЛКИЕ УЗКИЕ МЕСТА

### 9. Нет thumbnail generation

**Effort:** 2-3 часа  
**Impact:** Manual work required

#### Solution

```python
def generate_thumbnail(video_path, script):
    # Option 1: Extract first frame
    clip = VideoFileClip(video_path)
    frame = clip.get_frame(0)
    
    # Option 2: Generate custom thumbnail
    img = create_thumbnail_image(
        title=script['hook'],
        background=gradient,
        overlay=text
    )
    
    img.save(video_path.replace('.mp4', '_thumb.jpg'))
```

---

### 10. Нет description generation

**Effort:** 1-2 часа  
**Impact:** Manual work required

#### Solution

```python
def generate_description(script, project):
    template = """
{hook}

{content}

📅 Дата: {date}
✨ Тип: {mode}

👉 Подпишись: {channel_url}
💬 Комментируй: Какой твой знак зодиака?

#гороскоп #астрология #{zodiac_tag}
"""
    
    return template.format(
        hook=script['hook'],
        content=script['script'][:100] + "...",
        date=script['date'],
        mode=script['mode'],
        channel_url=project['channel_url'],
        zodiac_tag=extract_zodiac(script)
    )
```

---

### 11. Hardcoded цвета

**Effort:** 1 час  
**Impact:** Limited customization

#### Solution

Move to config:
```yaml
video:
  colors:
    mystical: [20, 10, 40]
    intro: [30, 15, 50]
    love: [150, 30, 60]
    money: [50, 150, 50]
    health: [100, 150, 255]
```

---

## 📊 Priority Matrix

```
┌─────────────────────────────────────────────────────────────┐
│  IMPACT vs EFFORT MATRIX                                     │
└─────────────────────────────────────────────────────────────┘

High Impact │ 
            │  #1 TTS Fix         #2 Subtitles
            │  (1 week)           (3 weeks)
            │  
            │  #4 Monitoring      #3 Performance
            │  (2 weeks)          (1 month)
            │
            │
Medium      │  #6 Caching         #5 Pixabay
Impact      │  (3 hours)          (1 week)
            │
            │  #7 Retry           #8 Tests
            │  (3 hours)          (1 week)
            │
Low Impact  │  #9 Thumbnails      #10 Description    #11 Colors
            │  (3 hours)          (2 hours)          (1 hour)
            │
            └────────────────────────────────────────────────────
              Low Effort          Medium             High Effort
                (1-2 days)        (1 week)           (2+ weeks)
```

---

## 🎯 Рекомендуемый порядок выполнения

### Sprint 1 (Week 1-2): Quick wins
1. ✅ #1 TTS Fix (CRITICAL)
2. ✅ #6 Script caching (3 hours)
3. ✅ #7 Video retry (3 hours)

**Impact:** Unblock production, reduce API calls

---

### Sprint 2 (Week 3-4): Stability
4. ✅ #4 Monitoring & logging (2 weeks)

**Impact:** Visibility, debugging ability

---

### Sprint 3 (Month 2): Critical features
5. ✅ #2 Subtitles (3 weeks)

**Impact:** +30% engagement

---

### Sprint 4 (Month 2-3): Performance
6. ✅ #3 Performance optimization (1 month)
7. ✅ #5 Pixabay alternatives (1 week)

**Impact:** Scale to 50+ videos/день

---

### Sprint 5 (Month 3-4): Quality
8. ✅ #8 Unit tests (1 week)
9. ✅ #9 Thumbnails (3 hours)
10. ✅ #10 Description (2 hours)
11. ✅ #11 Colors config (1 hour)

**Impact:** Production quality

---

## 📈 Expected ROI

| Fix | Effort | Impact | ROI |
|-----|--------|--------|-----|
| #1 TTS | 1 week | Unblock production | ∞ (critical) |
| #2 Subtitles | 3 weeks | +30% engagement | Very High |
| #3 Performance | 1 month | 5x capacity | High |
| #4 Monitoring | 2 weeks | -50% debug time | High |
| #5 Pixabay | 1 week | Scale to 100+/день | Medium |
| #6 Caching | 3 hours | -50% API calls | Very High |
| #7 Retry | 3 hours | -80% manual work | High |
| #8 Tests | 1 week | Confidence to refactor | Medium |
| #9-11 Polish | 1 day | Better UX | Low |

---

## 🚀 Next Actions

1. **Create GitHub Issues** для каждого bottleneck
2. **Assign owners** (Tech Lead, Backend Dev, DevOps)
3. **Add to GitHub Project** (Kanban board)
4. **Start Sprint 1** (TTS fix + quick wins)
5. **Weekly review** прогресса

---

**Последнее обновление:** Декабрь 2025  
**Владелец:** Tech Lead  
**Следующий review:** Конец каждого спринта

**См. также:**
- DEVELOPMENT_ROADMAP.md - долгосрочный план
- NEXT_STEPS.md - immediate actions
- IMPLEMENTATION_STATUS.md - current state
