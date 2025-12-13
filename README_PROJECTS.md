# 📦 Multi-Project Architecture

## Overview

```
content-factory/
│
├── core/                       ← GLOBAL: Video/TTS/Models (used by ALL)
│   ├── generators/
│   │   ├── script_generator.py
│   │   ├── tts_generator.py
│   │   └── video_renderer.py
│   ├── utils/
│   │   ├── model_router.py    ← Model fallback logic
│   │   └── config_loader.py
│   └── orchestrators/
│       └── pipeline.py         ← Main pipeline
│
└── projects/                   ← PROJECT-SPECIFIC: Configs & Prompts
    ├── youtube_horoscope/
    │   ├── config.yaml         ← When to run, which models
    │   ├── content_plan.json   ← Topics, strategy
    │   └── prompts/            ← AI instructions
    │       ├── script.txt      ← "Write horoscope scripts like..."
    │       ├── tts.txt         ← "Use calm, mystical voice..."
    │       └── video.txt       ← "Starry background, slow zoom..."
    │
    └── my_project/             ← Your new project
        └── (same structure)
```

---

## Global vs Project-Specific

| What | Where | Scope |
|------|-------|-------|
| **Video rendering** | `core/generators/video_renderer.py` | ALL projects |
| **TTS synthesis** | `core/generators/tts_generator.py` | ALL projects |
| **Model router** | `core/utils/model_router.py` | ALL projects |
| **Caching** | `core/utils/cache.py` | ALL projects |
| | | |
| **Which models to use** | `projects/X/config.yaml` | THIS project |
| **Schedule (cron)** | `projects/X/config.yaml` | THIS project |
| **AI instructions** | `projects/X/prompts/*.txt` | THIS project |
| **Topics/strategy** | `projects/X/content_plan.json` | THIS project |

---

## How It Works

### 1. Workflow Triggers

```yaml
# .github/workflows/generate-my_project.yml

on:
  schedule:
    - cron: "0 9 * * *"      # ← From config.yaml

env:
  PROJECT: my_project        # ← Your project name
```

### 2. Pipeline Loads Config

```python
# core/orchestrators/pipeline.py

from core.utils.config_loader import ProjectConfig

project_name = os.getenv('PROJECT')
config = ProjectConfig.load(f'projects/{project_name}/config.yaml')

# Now pipeline knows:
# - Which models to use
# - Which prompts to load
# - Output settings
```

### 3. Pipeline Uses Global Tools

```python
# Uses GLOBAL tools (same for all projects)
from core.generators import script_generator
from core.generators import tts_generator
from core.generators import video_renderer

# But loads PROJECT-SPECIFIC prompts
prompt = open(f'projects/{project_name}/prompts/script.txt').read()

# And uses PROJECT-SPECIFIC settings
model = config.generation['primary_model']
temp = config.generation['temperature']
```

---

## Adding Projects

See `ADD_PROJECT.md` for instructions.

**Summary:**
1. Copy `projects/youtube_horoscope` → `projects/my_project`
2. Edit `config.yaml` and `prompts/`
3. Copy workflow and change `PROJECT: my_project`
4. Push to GitHub

---

## Examples

### Project 1: Daily Horoscope

```yaml
# projects/youtube_horoscope/config.yaml

project:
  name: youtube_horoscope
  content_type: shorts

generation:
  primary_model: gemini-2.5-flash
  temperature: 0.7

scheduling:
  cron: "0 6 * * *"           # Daily 6:00 UTC
```

```
# projects/youtube_horoscope/prompts/script.txt

Write a mystical horoscope for today.
Tone: calm, professional
Length: 60 seconds
...
```

### Project 2: Tech News Podcast

```yaml
# projects/tech_podcast/config.yaml

project:
  name: tech_podcast
  content_type: long-form

generation:
  primary_model: gemini-2.5-pro
  temperature: 0.8

scheduling:
  cron: "0 10 * * 1"          # Monday 10:00 UTC
```

```
# projects/tech_podcast/prompts/script.txt

Write a 10-minute tech news podcast.
Tone: energetic, informative
Cover: AI, startups, crypto
...
```

---

## Key Points

✅ **Core tools are shared** - video rendering, TTS, models  
✅ **Configs are isolated** - each project has own settings  
✅ **Prompts are isolated** - each project has own AI instructions  
✅ **Easy to add projects** - just copy folder and edit  
✅ **No conflicts** - projects don't affect each other  

---

## File Roles

| File | Purpose | Edit When |
|------|---------|----------|
| `core/generators/*.py` | Video/TTS/Script generation logic | Changing HOW things work |
| `core/utils/model_router.py` | Fallback between models | Changing model selection logic |
| `projects/X/config.yaml` | Settings for project X | Adding/configuring project |
| `projects/X/prompts/*.txt` | AI instructions for project X | Changing content style |
| `.github/workflows/generate-X.yml` | Schedule for project X | Changing when it runs |

---

## Questions?

Read `ADD_PROJECT.md` for step-by-step guide.
