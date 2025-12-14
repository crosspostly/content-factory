# 🎬 DEMO: Slides Mode Video Generation

## 📸 VISUAL EXAMPLES (5 SLIDES)

Вот как выглядят **реальные слайды** при генерации видео для гороскопа Льва!

### Slide 1: Lucky Day
![Slide 1](https://user-gen-media-assets.s3.amazonaws.com/seedream_images/8c94c318-c3e4-4fda-9609-4d79afb9061d.png)

**Text:** "Leo, today is your lucky day!"
**Duration:** ~2 seconds
**Audio:** Google Cloud TTS (Russian, Neural2-D voice)

---

### Slide 2: Money & Career
![Slide 2](https://user-gen-media-assets.s3.amazonaws.com/seedream_images/62f9980f-1c1a-4c08-ae10-cbef301b0fa9.png)

**Text:** "Money and career opportunities coming."
**Duration:** ~2.5 seconds
**Transition:** FADE (0.5s overlap)

---

### Slide 3: Love
![Slide 3](https://user-gen-media-assets.s3.amazonaws.com/seedream_images/8fcd14eb-a0bf-4493-95bc-1c37ab2aac76.png)

**Text:** "Love is in the air for singles."
**Duration:** ~2.5 seconds
**Animation:** Text slides in from left

---

### Slide 4: Avoid Conflicts
![Slide 4](https://user-gen-media-assets.s3.amazonaws.com/seedream_images/05dbb48f-85c8-425d-848f-ded3a9fe2e13.png)

**Text:** "Avoid conflicts until evening."
**Duration:** ~2 seconds
**Background:** Dark purple gradient

---

### Slide 5: Lucky Numbers
![Slide 5](https://user-gen-media-assets.s3.amazonaws.com/seedream_images/cd9e-49f7-8efc-6db069256812.png)

**Text:** "Lucky numbers: 7, 13, 25."
**Duration:** ~1.5 seconds
**Final Frame Duration:** +1 second (pause at end)

---

## 🎯 OUTPUT VIDEO SPECS

```
📹 Final Video (output.mp4)
├─ Resolution: 1080x1920 (vertical - YouTube Shorts/TikTok)
├─ Duration: ~10-11 seconds
├─ FPS: 30
├─ Video Codec: H.264
├─ Audio Codec: AAC
├─ Bitrate: 5000 kbps
└─ File Size: ~5-8 MB
```

---

## 🔊 AUDIO TIMELINE

```
0.0s ─────────────── 2.0s ─────────────── 4.5s ─────────────── 7.0s ─────────────── 9.5s ─ 11.0s
│                      │                      │                      │                      │     │
Slide 1             Slide 2               Slide 3               Slide 4              Slide 5  END
"Leo, today"      "Money and"           "Love is"            "Avoid"              "Lucky"
(2s TTS)           (2.5s TTS)             (2.5s TTS)           (2s TTS)             (1.5s TTS)

[====== TTS Audio Stream ======]
Russian voice: "Лев, сегодня твой счастливый день!..."
```

---

## 🖼️ DESIGN BREAKDOWN

### Colors Used:
- **Background:** #2B1B3D (Dark purple)
- **Text:** #FFFFFF (White)
- **Shadow:** #000000 (Black, 3px offset)

### Typography:
- **Font:** Arial Bold
- **Size:** 70px
- **Line Height:** 1.4
- **Alignment:** Center (both horizontal & vertical)
- **Shadow:** Yes (drop shadow for readability)

### Layout:
- **Safe Area:** 40px horizontal padding, 200px top padding
- **Text Position:** Centered in middle 60% of screen
- **Aspect Ratio:** 9:16 (vertical)

---

## 🚀 HOW TO GENERATE THIS VIDEO

### Option 1: Quick Test (Using Example Code)

```python
import asyncio
from core.content_modes.registry import ContentModeRegistry
import yaml

# Load config
with open('projects/horoscope_leo/config.yaml') as f:
    config = yaml.safe_load(f)

# Get mode
mode = ContentModeRegistry.get('slides')

# Content
scenario = config['example_content']

# Generate!
result = await mode.generate(
    scenario=scenario,
    audio_map={},
    config=config['design']
)

print(f"✅ Video: {result.video_path}")
print(f"Duration: {result.duration}s")
```

### Option 2: Full Pipeline (From Gemini API)

```bash
# 1. Generate horoscope content using Gemini
python scripts/generate_horoscope.py --sign leo

# 2. Create video
python scripts/create_video.py --project horoscope_leo --mode slides

# 3. Upload to social media (optional)
python scripts/upload_social.py --platform youtube_shorts horoscope_leo/output.mp4
```

### Option 3: Direct Python Command

```bash
python -c "
import asyncio
from core.content_modes.slides_mode.mode import SlidesMode

async def main():
    mode = SlidesMode(variant='carousel')
    result = await mode.generate(
        scenario='Leo, today is your lucky day! Money and career opportunities coming. Love is in the air for singles. Avoid conflicts until evening. Lucky numbers: 7, 13, 25.',
        audio_map={},
        config={
            'background_color': '#2B1B3D',
            'font_size': 70,
            'text_color': 'white',
            'slides_count': 5,
            'tts_voice': 'ru-RU-Neural2-D'
        }
    )
    print(f'Generated: {result.video_path}')

asyncio.run(main())
"
```

---

## 📁 FILES TO SEND TO AI AGENT

### ✅ What to Send:

1. **Configuration File** (already created)
   - 📄 `projects/horoscope_leo/config.yaml`
   - What it contains: All design settings, TTS voice, transitions

2. **Technical Specification** (already in Issue #43)
   - 📖 Full implementation guide with code
   - Link: https://github.com/crosspostly/content-factory/issues/43

3. **This Demo File**
   - 📸 Visual examples of what output looks like
   - Helps AI Agent understand the goal

4. **Existing Code** (if any)
   - Any base classes or utilities already in repo

### 📝 How to Share with AI Agent:

```bash
# Option 1: Share GitHub Issue
"Here's the tech spec: https://github.com/crosspostly/content-factory/issues/43
And config: https://github.com/crosspostly/content-factory/blob/main/projects/horoscope_leo/config.yaml"

# Option 2: Copy Full Task
Copy the technical specification comment from Issue #43 and paste to AI Agent

# Option 3: Create Summary Document
python scripts/generate_ai_brief.py > AI_AGENT_BRIEF.md
Then send the file
```

---

## ✅ CHECKLIST FOR AI AGENT

Before AI Agent starts, ensure they have:

- [ ] **Tech Spec Document** (Issue #43)
- [ ] **Config File** (projects/horoscope_leo/config.yaml)
- [ ] **Demo Images** (5 slide examples above)
- [ ] **Python Environment Setup**
  - [ ] Pillow==10.0.0
  - [ ] ffmpeg-python==0.2.1
  - [ ] google-cloud-texttospeech==2.14.0
- [ ] **System Tools Installed**
  - [ ] FFmpeg
  - [ ] ImageMagick
- [ ] **Google Cloud Setup**
  - [ ] GOOGLE_APPLICATION_CREDENTIALS environment variable set
  - [ ] Service account with TTS API access

---

## 🎬 EXPECTED OUTPUT

When AI Agent successfully completes implementation, they should be able to run:

```bash
python -m pytest tests/test_slides_mode_e2e.py -v
```

And get:

```
✅ test_end_to_end PASSED

✅ Video generated: /tmp/content-factory/output.mp4
   Duration: 10.50s
   Resolution: 1080x1920
   File Size: 6.2 MB
```

Then the video can be played with:

```bash
ffplay /tmp/content-factory/output.mp4
```

---

## 📊 PERFORMANCE METRICS

| Metric | Expected | Actual |
|--------|----------|--------|
| Generation Time | 30-60s | - |
| Slide Render Time (each) | 2-3s | - |
| TTS Generation Time (5 slides) | 15-20s | - |
| FFmpeg Assembly Time | 10-20s | - |
| **Total Time** | **~1 minute** | - |
| Output File Size | 5-8 MB | - |
| Video Quality | 1080p vertical | - |
| Audio Quality | 128 kbps AAC | - |

---

## 🐛 DEBUGGING TIPS

If something goes wrong:

1. **No audio generated?**
   ```bash
   # Check Google Cloud credentials
   echo $GOOGLE_APPLICATION_CREDENTIALS
   gcloud auth list
   ```

2. **FFmpeg error?**
   ```bash
   # Test FFmpeg installation
   ffmpeg -version
   ffmpeg -encoders | grep h264
   ```

3. **PIL can't render text?**
   ```bash
   # Check fonts installed
   fc-list | grep Arial
   ```

4. **Memory issues with large images?**
   ```bash
   # Reduce resolution or use PIL's optimize mode
   image.save(path, optimize=True)
   ```

---

## 🎯 NEXT STEPS

1. **AI Agent implements** the 8 stages from Issue #43
2. **Runs E2E test** to verify
3. **Creates PR** with implementation
4. **Get code review** before merge
5. **Deploy** to production

---

## 📞 SUPPORT

If you need to explain this to AI Agent:

1. **Share this file:** DEMO_SLIDES_MODE.md
2. **Link to Issue:** #43 (tech spec)
3. **Reference config:** projects/horoscope_leo/config.yaml
4. **Show examples:** The 5 slide images above

**Key Message for AI Agent:**
"Your job is to implement the components described in Issue #43 to make videos that look like the examples shown in DEMO_SLIDES_MODE.md"
