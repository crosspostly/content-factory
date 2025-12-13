# 📦 How to Add a New Project

> **TL;DR:** Run the setup script and answer a few questions. That's it!

## 🚀 Quick Start

```bash
python3 scripts/setup_project.py
```

Then answer the interactive questions:

```
📝 Project Name (e.g., youtube_podcast): my_project
📄 Description: AI-powered content generation for my platform
🎬 Content Type (shorts/long-form/ad): shorts
🔑 API Keys needed (comma-separated): GOOGLE_AI_API_KEY, MY_CUSTOM_API_KEY
📊 Enable scheduling? (y/n): y
🕐 Cron schedule (0 6 * * * = daily at 6:00 UTC): 0 9 * * *
```

**That's it!** Your project is ready! ✅

---

## 📁 What Gets Created

```
projects/my_project/
├── config.yaml                 # Project configuration
├── content_plan.json          # Content strategy
├── prompts/
│   ├── script.txt             # Script generation prompt
│   ├── tts.txt                # TTS synthesis prompt
│   └── video.txt              # Video rendering prompt
└── README.md                  # Project documentation

.github/workflows/
└── generate-my_project.yml    # Auto-generated workflow
```

---

## 🎯 What Each File Does

### `config.yaml` - Project Settings

```yaml
project:
  name: my_project
  description: AI-powered content generation
  content_type: shorts
  enabled: true

generation:
  primary_model: gemini-2.5-flash
  fallback_models:
    - gemini-2.5-pro
    - openrouter-qwen
  temperature: 0.7
  max_retries: 2

api_keys:
  - GOOGLE_AI_API_KEY
  - MY_CUSTOM_API_KEY

scheduling:
  enabled: true
  cron: "0 9 * * *"  # Daily at 9:00 UTC
  timezone: UTC

output:
  format: video
  video_quality: 1080p
  frame_rate: 30
```

### `content_plan.json` - Strategy

```json
{
  "project": "my_project",
  "topics": [
    "topic 1",
    "topic 2",
    "topic 3"
  ],
  "content_style": "professional",
  "target_audience": "general",
  "upload_schedule": {
    "youtube": "daily",
    "tiktok": "multiple-per-day",
    "instagram": "daily"
  }
}
```

### `prompts/` - AI Instructions

**script.txt** - How to write scripts
```
You are a professional scriptwriter for [content_type].

Create engaging scripts about [topics].
Style: [content_style]
Audience: [target_audience]
Length: [duration]

Output format:
[NARRATOR]
Scripted text here...

[VISUAL]
Visual description here...
```

**tts.txt** - How to synthesize audio
```
You are a voice director for [content_type].

Synthesize audio from scripts about [topics].
Voice: professional, engaging
Pace: [pace]
Emotions: [emotions]
```

**video.txt** - How to render video
```
You are a video editor for [content_type].

Create videos for [platform].
Style: [video_style]
Quality: [video_quality]
Format: [format]
```

---

## 🔧 Customization Examples

### Example 1: Daily Podcast Generation

```bash
python3 scripts/setup_project.py

# Answers:
Project Name: daily_podcast
Description: AI-powered daily podcast for tech news
Content Type: long-form
API Keys: GOOGLE_AI_API_KEY, ELEVENLABS_API_KEY
Scheduling: y
Cron: 0 8 * * *  # 8:00 UTC daily
```

### Example 2: Multiple Daily Shorts

```bash
python3 scripts/setup_project.py

# Answers:
Project Name: tiktok_shorts
Description: 3 TikTok shorts per day
Content Type: shorts
API Keys: GOOGLE_AI_API_KEY, PIXABAY_API_KEY
Scheduling: y
Cron: 0 6,14,22 * * *  # 3x daily (6, 14, 22 UTC)
```

### Example 3: On-Demand Ads

```bash
python3 scripts/setup_project.py

# Answers:
Project Name: ad_generator
Description: AI ad content generator
Content Type: ad
API Keys: GOOGLE_AI_API_KEY
Scheduling: n  # Manual trigger only
```

---

## 🚀 After Setup

### 1. Edit the Configuration

```bash
vi projects/my_project/config.yaml
```

Customize:
- API models and parameters
- Output formats and quality
- Scheduling (if enabled)

### 2. Customize Content Plan

```bash
vi projects/my_project/content_plan.json
```

Set:
- Your topics and themes
- Content style and tone
- Publishing schedule

### 3. Fine-tune Prompts

```bash
vi projects/my_project/prompts/script.txt
vi projects/my_project/prompts/tts.txt
vi projects/my_project/prompts/video.txt
```

Adjust AI instructions for your brand/style.

### 4. Test Locally

```bash
cd projects/my_project
python3 ../../core/orchestrators/pipeline_orchestrator.py \
  --project my_project \
  --test
```

### 5. Manual Trigger (Optional)

```bash
gh workflow run generate-my_project.yml \
  -f format=shorts \
  -f date=2025-12-14
```

---

## 📊 Generated Workflow

Autоматически создается `.github/workflows/generate-my_project.yml`:

```yaml
name: Generate my_project

on:
  schedule:
    - cron: "0 9 * * *"  # Your schedule
  workflow_dispatch:     # Manual trigger

jobs:
  generate:
    runs-on: ubuntu-22.04
    steps:
      # Uses your config.yaml
      # Loads your prompts/
      # Follows your content_plan.json
```

---

## ✅ Checklist

- [ ] Ran `python3 scripts/setup_project.py`
- [ ] Edited `projects/my_project/config.yaml`
- [ ] Customized `projects/my_project/content_plan.json`
- [ ] Updated prompts in `projects/my_project/prompts/`
- [ ] Tested locally with `--test` flag
- [ ] Triggered workflow manually: `gh workflow run generate-my_project.yml`
- [ ] Checked GitHub Actions logs
- [ ] Project is live! 🎉

---

## 🆘 Troubleshooting

**Q: Script doesn't find my project config**
- A: Make sure `projects/my_project/config.yaml` exists

**Q: API keys not found**
- A: Add secrets to GitHub: Settings → Secrets → New repository secret

**Q: Workflow doesn't show up**
- A: Wait 1-2 minutes for GitHub to sync, or manually trigger

**Q: Want to disable a project?**
- A: Set `enabled: false` in `config.yaml`, or delete the directory

---

## 📚 Full Project Structure

```
content-factory/
├── core/
│   ├── generators/
│   │   ├── script_generator.py
│   │   ├── tts_generator.py
│   │   └── video_renderer.py
│   ├── orchestrators/
│   │   └── pipeline_orchestrator.py
│   └── utils/
│       └── config_loader.py
│
├── projects/
│   ├── youtube_horoscope/
│   │   ├── config.yaml
│   │   ├── content_plan.json
│   │   └── prompts/
│   │
│   └── my_project/          ← YOUR NEW PROJECT
│       ├── config.yaml
│       ├── content_plan.json
│       └── prompts/
│
├── .github/workflows/
│   ├── generate-youtube_horoscope.yml
│   └── generate-my_project.yml  ← AUTO-GENERATED
│
└── scripts/
    └── setup_project.py     ← YOU ARE HERE
```

---

## 🎓 Next Steps

1. **Learn the Config Format**: Read `projects/youtube_horoscope/config.yaml`
2. **Check Prompts**: Look at `projects/youtube_horoscope/prompts/` for examples
3. **Customize**: Copy structure to your new project
4. **Test**: Run locally first
5. **Deploy**: Push to GitHub and watch it go! 🚀

---

## 💡 Pro Tips

✨ **Reuse configs**: Copy a working project's config and customize it
✨ **Test prompts locally**: Edit and test before committing
✨ **Use cron generator**: [crontab.guru](https://crontab.guru) for schedule syntax
✨ **Monitor runs**: Check GitHub Actions for logs
✨ **Add to README.md**: Document your project's specifics

---

**Questions?** Check the example projects in `projects/` directory!
