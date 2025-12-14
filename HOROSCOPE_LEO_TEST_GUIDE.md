# 🦁 HOROSCOPE LEO PROJECT - TEST GUIDE

## 🌟 OVERVIEW

This guide shows you how to **test the complete slides mode pipeline** with the `horoscope_leo` project.

```
Input (Text)
    ⬆️
[ContentProcessor]
    ⬆️
[SlideBuilder] → Split into slides
    ⬆️
[SlideRenderer] → Render to PNG images
    ⬆️
[MoviePy] → Combine with transitions
    ⬆️
Output: output/horoscope_leo/output.mp4 (🦁)
```

---

## 📋 WHAT'S CONFIGURED

**File:** `projects/horoscope_leo/config.yaml`

### Project Settings
```yaml
project:
  name: horoscope_leo
  title: Leo Horoscope Daily
  description: Daily horoscope for Leo zodiac sign
```

### Video Mode
```yaml
video_mode: slides          # Using SlidesMode
variant: carousel          # Carousel variant (slide-by-slide)
```

### Design (What You'll See)
```yaml
design:
  width: 1080              # Phone width
  height: 1920             # Phone height (vertical)
  background_color: "#2B1B3D"  # Dark purple
  text_color: "white"     # White text
  font_size: 70            # Large, readable
  transitions: fade        # Smooth fade between slides
```

### Example Content (for testing)
```yaml
example_content: |
  Leo, today is your lucky day!
  Money and career opportunities coming.
  Love is in the air for singles.
  Avoid conflicts until evening.
  Lucky numbers: 7, 13, 25.
```

---

## 🚀 HOW TO TEST

### Option 1: Quick Test (Recommended for first-time)

```bash
# Run the test script
python scripts/test_horoscope_leo.py
```

**What it does:**
1. Loads config from `projects/horoscope_leo/config.yaml`
2. Uses example content from config
3. Generates video using SlidesMode
4. Outputs to `output/horoscope_leo/output.mp4`
5. Prints detailed logs of each step

**Expected output:**
```
============================================================
🦁 TESTING HOROSCOPE LEO PROJECT WITH SLIDES MODE
============================================================

📋 Step 1: Loading configuration...
   ✅ Loaded config from projects/horoscope_leo/config.yaml
   Project: Leo Horoscope Daily
   Mode: slides (carousel)

📝 Step 2: Preparing content...
   Content length: 234 chars
   Expected slides: 5

... (more steps) ...

🎬 Step 6: Generating video...
   (This may take 30-60 seconds)

   ✅ VIDEO GENERATION SUCCESSFUL!

   📹 Video Path: output/horoscope_leo/output.mp4
   ⏱️ Duration: 10.50 seconds
   📐 Resolution: 1080x1920
   📊 Metadata: {'slides_count': 5, 'variant': 'carousel', 'fps': 30}

============================================================
✅ ALL TESTS PASSED!
============================================================
```

### Option 2: Manual Python Test

```python
import asyncio
import yaml
from pathlib import Path
from core.content_modes.slides_mode.mode import SlidesMode

# Load config
with open('projects/horoscope_leo/config.yaml') as f:
    config = yaml.safe_load(f)

# Get content
content = config['example_content'].strip()

# Setup design config
design_config = {
    'width': 1080,
    'height': 1920,
    'background_color': '#2B1B3D',
    'text_color': 'white',
    'font_size': 70,
    'fps': 30,
    'bitrate': '5000k',
    'transitions': {'type': 'fade', 'duration': 0.5},
}

# Generate
async def generate():
    mode = SlidesMode(variant='carousel')
    result = await mode.generate(
        scenario=content,
        audio_map={},
        config=design_config,
        output_dir=Path('output/horoscope_leo'),
    )
    print(f"🎯 Video: {result.video_path}")
    print(f"⏱️ Duration: {result.duration:.2f}s")
    print(f"📐 Resolution: {result.width}x{result.height}")

asyncio.run(generate())
```

### Option 3: Direct Command (if modules are importable)

```bash
cd content-factory
python scripts/test_horoscope_leo.py
```

---

## 📺 VIEWING THE OUTPUT

After successful generation, video will be at:
```
output/horoscope_leo/output.mp4
```

### On Linux/Mac:
```bash
ffplay output/horoscope_leo/output.mp4
# or
open output/horoscope_leo/output.mp4  # Mac
```

### On Windows:
```bash
wmplayer output\horoscope_leo\output.mp4
```

### What to check:
- ✅ Video is vertical (1080x1920, phone-oriented)
- ✅ Dark purple background visible
- ✅ White text centered on each slide
- ✅ 5 slides total (~2 seconds each)
- ✅ Smooth fade transitions between slides
- ✅ Total duration ~10-12 seconds

---

## 🔍 TROUBLESHOOTING

### Error: "No module named 'core'"
```bash
# Make sure you're in the project root
cd /path/to/content-factory
python scripts/test_horoscope_leo.py
```

### Error: "MoviePy not installed"
```bash
pip install moviepy
```

### Error: "Config file not found"
```bash
# Make sure config exists
ls projects/horoscope_leo/config.yaml
```

### Error: "Port 5000 already in use" (MoviePy)
This is just a warning, safe to ignore.

### Video generates but is black/empty
- Check if font is available: `fc-list | grep Arial`
- Try with different font_family in config
- Check slide rendering:
  ```bash
  ls output/horoscope_leo/slides/
  ```

---

## ✅ SUCCESS CRITERIA

Test passes if:
- [ ] Script runs without errors
- [ ] Video file is created (`output/horoscope_leo/output.mp4`)
- [ ] Video size is > 1 MB
- [ ] Video duration is 8-15 seconds
- [ ] Video opens in player
- [ ] Video has 5 slides visible
- [ ] Slides have white text on purple background
- [ ] Transitions between slides are smooth

---

## 🚁 NEXT STEPS AFTER TESTING

### Phase 2: Add TTS Audio
- Integrate Google Cloud TTS
- Generate Russian voice for each slide
- Sync audio with slide timing

### Phase 3: Upload Pipeline
- Add YouTube Shorts upload
- Add TikTok upload
- Add Instagram Reels upload

### Phase 4: Generalize
- Make it work for all zodiac signs (Aries, Taurus, etc.)
- Create Gemini content generation pipeline
- Schedule daily generation

---

## 📋 FILES INVOLVED

| File | Purpose |
|------|----------|
| `projects/horoscope_leo/config.yaml` | Project configuration |
| `core/content_modes/slides_mode/mode.py` | Main SlidesMode implementation |
| `core/content_modes/slides_mode/slide_builder.py` | Text-to-slides conversion |
| `core/content_modes/slides_mode/slide_renderer.py` | Image rendering (PIL) |
| `core/content_modes/base.py` | Base class for all modes |
| `core/content_modes/registry.py` | Mode registration |
| `scripts/test_horoscope_leo.py` | Test script |
| `output/horoscope_leo/` | Generated video output |

---

## 📧 CONTACT

If tests fail, check:
1. **Error message** - read carefully
2. **Logs** - script prints detailed logs for each step
3. **Dependencies** - run `pip install -r requirements.txt`
4. **File permissions** - make sure you can write to `output/` dir

---

**Happy testing!** 🌟
