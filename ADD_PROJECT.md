# 📦 How to Add a New Project

## TL;DR

```bash
# 1. Copy existing project
cp -r projects/youtube_horoscope projects/my_new_project

# 2. Edit config
vi projects/my_new_project/config.yaml

# 3. Copy workflow
cp .github/workflows/generate-horoscope-video.yml .github/workflows/generate-my_new_project.yml

# 4. Edit workflow (change project name)
vi .github/workflows/generate-my_new_project.yml

# Done! ✅
```

---

## Project Structure

```
projects/
├── youtube_horoscope/          ← Example project
│   ├── config.yaml            ← Settings (models, API keys, schedule)
│   ├── content_plan.json      ← Topics and strategy
│   └── prompts/               ← AI instructions
│       ├── script.txt
│       ├── tts.txt
│       └── video.txt
│
└── my_new_project/            ← Your project (copy youtube_horoscope)
    ├── config.yaml
    ├── content_plan.json
    └── prompts/
```

---

## What Goes Where?

### 🌍 Global Settings (used by ALL projects)

**File:** `core/` directory
- Video rendering engine
- TTS synthesis
- Model routing (fallback logic)
- Cache management
- Publishing APIs

**Do NOT edit** unless you're changing how the whole system works.

### 🎯 Project-Specific Settings

**File:** `projects/YOUR_PROJECT/config.yaml`

```yaml
project:
  name: my_new_project        # ← Your project name
  description: My content     # ← What it does
  content_type: shorts        # ← shorts/long-form/ad
  platforms: [youtube]        # ← Where to publish

generation:
  primary_model: gemini-2.5-flash
  temperature: 0.7

scheduling:
  enabled: true
  cron: "0 9 * * *"           # ← When to run (9:00 UTC daily)
```

**File:** `projects/YOUR_PROJECT/prompts/*.txt`

```
script.txt   ← How to write scripts for THIS project
tts.txt      ← Voice style for THIS project
video.txt    ← Visual style for THIS project
```

---

## Step-by-Step

### 1. Copy Existing Project

```bash
cp -r projects/youtube_horoscope projects/my_new_project
```

### 2. Edit config.yaml

```bash
vi projects/my_new_project/config.yaml
```

Change:
- `project.name` → your project name
- `project.description` → what it does
- `scheduling.cron` → when to run (or disable)

### 3. Edit Prompts

```bash
vi projects/my_new_project/prompts/script.txt
```

Write instructions for AI:
- How to write scripts
- What tone to use
- What topics to cover

### 4. Copy & Edit Workflow

```bash
cp .github/workflows/generate-horoscope-video.yml \
   .github/workflows/generate-my_new_project.yml
```

Change ONE line:
```yaml
env:
  PROJECT: my_new_project  # ← Your project name here
```

### 5. Push to GitHub

```bash
git add projects/my_new_project
git add .github/workflows/generate-my_new_project.yml
git commit -m "add: my_new_project"
git push
```

**Done!** ✅

---

## Example: Add Daily Podcast

```bash
# 1. Copy
cp -r projects/youtube_horoscope projects/daily_podcast

# 2. Edit config
vi projects/daily_podcast/config.yaml
# Change: name → daily_podcast, cron → 0 8 * * *

# 3. Edit prompts
vi projects/daily_podcast/prompts/script.txt
# Write: "Create 10-minute podcast about tech news..."

# 4. Copy workflow
cp .github/workflows/generate-horoscope-video.yml \
   .github/workflows/generate-daily_podcast.yml

# 5. Edit workflow
vi .github/workflows/generate-daily_podcast.yml
# Change: PROJECT: daily_podcast

# 6. Push
git add .
git commit -m "add: daily_podcast project"
git push
```

---

## What Happens?

1. **Core tools** (video, TTS, models) work for ALL projects
2. **Your config** controls:
   - Which models to use
   - When to run
   - What prompts to load
3. **Your prompts** tell AI what to create

---

## That's It!

- ✅ Copy folder
- ✅ Edit config.yaml
- ✅ Edit prompts/
- ✅ Copy workflow
- ✅ Push

No scripts. No wizards. Just files.
