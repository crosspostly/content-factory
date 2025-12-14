# 🎬 Slides Mode Implementation Guide

## Overview

Slides Mode is a content generation pipeline that converts text content into carousel-style videos. It's part of the modular content_modes system for flexible video rendering.

## Architecture

```
Text Content
     ↓
SlideBuilder (Split text into slides)
     ↓
SlideRenderer (Render each slide as image)
     ↓
SlidesMode (Combine with audio and create video)
     ↓
MP4 Video Output
```

## Components

### 1. SlideBuilder
Intelligently splits text into slides with automatic duration calculation.

**Key Features:**
- Sentence-aware splitting (periods, exclamation marks)
- Character limit per slide (configurable)
- Automatic duration calculation based on character count
- Minimum/maximum duration clamping

**Usage:**
```python
from core.content_modes.slides_mode.slide_builder import SlideBuilder

builder = SlideBuilder(
    max_chars_per_slide=200,
    min_duration=1.5,
    max_duration=5.0,
)

slides = builder.build_slides("Your text content here...")
```

### 2. SlideRenderer
Renders individual slides as images with customizable design.

**Key Features:**
- Customizable background and text colors
- Configurable font size and family
- Text wrapping and centering
- Drop shadow for readability
- Support for hex and named colors

**Usage:**
```python
from core.content_modes.slides_mode.slide_renderer import SlideRenderer
from pathlib import Path

renderer = SlideRenderer(
    width=1080,
    height=1920,
    background_color="#2B1B3D",
    text_color="white",
    font_size=70,
)

image_path = renderer.render_slide(
    "Slide text here",
    Path("output/slide_001.png")
)
```

### 3. SlidesMode
Main orchestrator that combines all components to generate videos.

**Key Features:**
- Full video generation pipeline
- Audio synchronization
- Transition effects (fade, slide, zoom)
- Async/await support
- Metadata output

**Usage:**
```python
import asyncio
from core.content_modes.registry import ContentModeRegistry

async def generate():
    mode = ContentModeRegistry.get("slides")
    
    result = await mode.generate(
        scenario="Your text content",
        audio_map={},  # Optional: text -> audio_file mappings
        config={
            "width": 1080,
            "height": 1920,
            "background_color": "#2B1B3D",
            "text_color": "white",
            "font_size": 70,
            "fps": 30,
            "bitrate": "5000k",
            "transitions": {
                "type": "fade",
                "duration": 0.5,
            },
        },
        output_dir=Path("output")
    )
    
    print(f"Video: {result.video_path}")
    print(f"Duration: {result.duration}s")

asyncio.run(generate())
```

## Configuration

Slides mode is configured via YAML config files in project directories.

### Example Configuration

```yaml
# projects/horoscope_leo/config.yaml

video_mode: "slides"
variant: "carousel"

design:
  width: 1080
  height: 1920
  background_color: "#2B1B3D"
  background_secondary: "#1a0f2e"
  
  text_color: "white"
  text_shadow: true
  shadow_color: "#000000"
  shadow_offset: 3
  
  font_size: 70
  font_family: "Arial Bold"
  line_height: 1.4
  
  padding_horizontal: 40
  padding_vertical: 200

transitions:
  type: "fade"
  duration: 0.5
  easing: "ease-in-out"

output:
  format: "mp4"
  fps: 30
  codec: "h264"
  audio_codec: "aac"
  bitrate: "5000k"
```

## Duration Calculation

Slide duration is calculated based on character count:

- Formula: `duration = char_count / 2.5` seconds
  - Assumes ~150 characters per minute (average reading speed)
  - ~2.5 characters per second

- Clamped to range: `[min_duration, max_duration]`
  - Default: 1.5s to 5.0s

### Examples:
- 30 chars: 1.5s (clamped to min)
- 100 chars: 2.7s
- 200 chars: 5.0s (clamped to max)

## Text Splitting Strategy

The SlideBuilder splits text using the following priority:

1. **Periods (`.`)** - Most natural sentence boundaries
2. **Exclamation marks (`!`)** - Emphatic sentences
3. **Newlines (`\n`)** - Line break separated content
4. **Whole text** - If no delimiters found, single slide

Each sentence is stripped of whitespace and combined with subsequent sentences until reaching the character limit.

## Video Output Specifications

### Default Output Format:
- **Resolution**: 1080x1920 (vertical, 9:16)
- **FPS**: 30
- **Codec**: H.264 (video), AAC (audio)
- **Bitrate**: 5000 kbps
- **File Format**: MP4

### Generated Files:
```
output/
├── output.mp4          # Final video
└── slides/
    ├── slide_000.png
    ├── slide_001.png
    └── ...
```

## Audio Integration

### Optional Audio Map
If you have pre-generated TTS audio files, you can sync them with slides:

```python
audio_map = {
    "First slide text": "/path/to/audio1.wav",
    "Second slide": "/path/to/audio2.wav",
    # ...
}

result = await mode.generate(
    scenario=text,
    audio_map=audio_map,
    config=config,
)
```

The audio is matched using:
1. Exact text match first
2. Prefix/partial match fallback
3. If no match, slide uses calculated duration without audio

### Audio Timing:
- Slide duration is set to max of calculated duration and audio duration
- Ensures audio plays completely
- Next slide starts after audio + slide duration

## Transition Effects

Supported transitions:

| Type | Duration | Effect |
|------|----------|--------|
| `fade` | 0.0-2.0s | Fade in/out between slides |
| `slide` | 0.0-2.0s | Slide from side to side |
| `zoom` | 0.0-2.0s | Zoom in/out effect |

**Note**: Slide and zoom transitions not yet implemented. Default is fade.

## Integration with ContentModeRegistry

The registry pattern allows runtime selection of content modes:

```python
from core.content_modes.registry import ContentModeRegistry

# Get slides mode
mode = ContentModeRegistry.get("slides")

# List all available modes
modes = ContentModeRegistry.list_modes()
for mode_name, description in modes.items():
    print(f"{mode_name}: {description}")

# Get with variant
mode = ContentModeRegistry.get("slides", variant="carousel")
```

## Testing

Comprehensive test suite includes:

- `TestSlideBuilder`: Text splitting and duration calculation
- `TestSlideRenderer`: Image rendering and color parsing
- `TestSlidesMode`: Full pipeline generation
- `TestContentModeRegistry`: Mode registration and retrieval

Run tests:
```bash
python -m pytest tests/test_slides_mode.py -v
```

## Performance Characteristics

### Generation Times (estimated):
- Text splitting: < 100ms
- Image rendering (5 slides): 1-2 seconds
- Audio processing: depends on TTS
- Video encoding: 10-30 seconds (depends on duration & bitrate)
- **Total: 15-60 seconds** for typical video

### Resource Usage:
- Memory: ~200-500MB (depends on video resolution & duration)
- Disk: ~5-10MB per video
- CPU: Single-threaded, can be optimized with parallel rendering

## Known Limitations

1. **Transitions**: Only fade is implemented. Slide/zoom are stubs.
2. **Audio**: Text-to-speech must be pre-generated and provided
3. **Animations**: Text doesn't animate, just appears on slides
4. **Subtitles**: Not integrated (planned for future release)
5. **Background Music**: Not yet implemented
6. **Custom Fonts**: Hardcoded system font paths (DejaVu/Liberation)

## Future Enhancements

- [ ] Implement slide and zoom transitions
- [ ] Add built-in TTS generation
- [ ] Support custom fonts from config
- [ ] Parallel slide rendering for better performance
- [ ] Background music and sound effects
- [ ] Animated text (slide in, bounce, etc.)
- [ ] Multiple color schemes/themes
- [ ] Gradient backgrounds
- [ ] Image backgrounds instead of solid colors

## Troubleshooting

### Issue: "No module named moviepy"
**Solution**: Install requirements: `pip install -r requirements.txt`

### Issue: Font rendering looks wrong
**Solution**: Ensure TrueType fonts are installed:
```bash
# Ubuntu/Debian
sudo apt-get install fonts-dejavu fonts-liberation

# macOS: Already included
# Windows: Use system fonts in C:\Windows\Fonts\
```

### Issue: Video is silent
**Solution**: Provide audio_map with pre-generated TTS files, or implement TTS integration

### Issue: Slides look cramped
**Solution**: Reduce font_size or increase padding/dimensions in config

### Issue: Video encoding is slow
**Solution**: Lower bitrate or reduce resolution in config

## Example: Full Horoscope Video Pipeline

```python
import asyncio
from pathlib import Path
from core.content_modes.registry import ContentModeRegistry
import yaml

async def generate_horoscope_video():
    # Load config
    with open("projects/horoscope_leo/config.yaml") as f:
        config = yaml.safe_load(f)
    
    # Get mode
    mode = ContentModeRegistry.get(config["video_mode"])
    
    # Sample horoscope content
    horoscope_text = """
    Leo, today is your lucky day!
    Money and career opportunities coming.
    Love is in the air for singles.
    Avoid conflicts until evening.
    Lucky numbers: 7, 13, 25.
    """
    
    # Generate video
    result = await mode.generate(
        scenario=horoscope_text,
        audio_map={},
        config=config["design"],
        output_dir=Path("output/horoscope_leo")
    )
    
    print(f"✅ Video generated: {result.video_path}")
    print(f"   Duration: {result.duration:.2f}s")
    print(f"   Resolution: {result.width}x{result.height}")
    print(f"   Slides: {result.metadata['slides_count']}")

asyncio.run(generate_horoscope_video())
```

## See Also

- [MODES_ARCHITECTURE.md](./MODES_ARCHITECTURE.md) - Overall architecture
- [IMPLEMENTATION_STATUS.md](./IMPLEMENTATION_STATUS.md) - Project status
- [test_slides_mode.py](../tests/test_slides_mode.py) - Test examples
