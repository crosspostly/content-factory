# 📦 Multi-Project Setup

This document explains how content-factory supports multiple projects.

## Quick Start

```bash
# Add new project
python3 scripts/setup_project.py

# List all projects
python3 core/utils/config_loader.py

# Load specific project
python3 core/utils/config_loader.py youtube_horoscope
```

## Project Structure

```
projects/
├── youtube_horoscope/
│   ├── config.yaml              # Project settings
│   ├── content_plan.json        # Content strategy
│   ├── prompts/                 # AI instructions
│   │   ├── script.txt
│   │   ├── tts.txt
│   │   └── video.txt
│   └── README.md
├── my_podcast/                  # Your new project
│   └── ...
└── another_project/             # Another project
    └── ...
```

## Adding Projects

### Interactive Setup (Recommended)

```bash
python3 scripts/setup_project.py

# Answer these questions:
# - Project name
# - Description
# - Content type (shorts/long-form/ad/podcast)
# - Platforms (youtube/tiktok/instagram/vk/telegram)
# - API keys needed
# - Enable scheduling? (y/n)
```

### Manual Setup

1. Create directory:
   ```bash
   mkdir projects/my_project
   ```

2. Copy config template:
   ```bash
   cp projects/youtube_horoscope/config.yaml projects/my_project/
   vi projects/my_project/config.yaml
   ```

3. Copy prompts:
   ```bash
   cp -r projects/youtube_horoscope/prompts projects/my_project/
   vi projects/my_project/prompts/*.txt
   ```

4. Create content plan:
   ```bash
   vi projects/my_project/content_plan.json
   ```

5. Create workflow:
   ```bash
   vi .github/workflows/generate-my_project.yml
   ```

## Configuration Format

### config.yaml

```yaml
project:
  name: youtube_horoscope
  description: Daily horoscope videos for YouTube
  content_type: shorts          # shorts, long-form, ad, podcast, custom
  platforms: [youtube, tiktok]  # Target platforms
  enabled: true                 # Disable to skip this project

generation:
  primary_model: gemini-2.5-flash
  fallback_models:
    - gemini-2.5-pro
    - openrouter-qwen
  temperature: 0.7              # 0-1: Lower = more deterministic
  max_retries: 2                # Retry failed generations

api_keys:
  - GOOGLE_AI_API_KEY
  - PIXABAY_API_KEY

scheduling:
  enabled: true
  cron: "0 6 * * *"             # Daily at 6:00 UTC
  timezone: UTC

output:
  format: video                 # video, audio, text
  video_quality: 1080p
  frame_rate: 30
  audio_quality: 320kbps
```

### content_plan.json

```json
{
  "project": "youtube_horoscope",
  "topics": [
    "Daily horoscope",
    "Zodiac signs",
    "Astrology insights"
  ],
  "content_style": "professional",
  "target_audience": "astrology enthusiasts",
  "publish_schedule": {
    "youtube": "daily",
    "tiktok": "daily"
  }
}
```

## Using Multiple Projects

### Run All Projects

```bash
python3 scripts/run_all_projects.py
```

### Run Specific Project

```bash
python3 core/orchestrators/pipeline_orchestrator.py \
  --project youtube_horoscope \
  --format shorts \
  --date 2025-12-14
```

### GitHub Actions

Each project gets its own workflow:

```
.github/workflows/
├── generate-youtube_horoscope.yml
├── generate-my_podcast.yml
├── generate-ad_generator.yml
└── ...
```

Manually trigger:

```bash
gh workflow run generate-my_podcast.yml
```

## Examples

### Example 1: YouTube Shorts (Daily)

```bash
python3 scripts/setup_project.py

# Answers:
Project Name: youtube_shorts
Description: Daily YouTube shorts
Content Type: shorts
Platforms: youtube,tiktok,instagram
API Keys: GOOGLE_AI_API_KEY
Scheduling: y
Cron: 0 9 * * *
```

Result: Video generated daily at 9:00 UTC

### Example 2: Podcast (Weekly)

```bash
python3 scripts/setup_project.py

# Answers:
Project Name: tech_podcast
Description: Weekly tech podcast
Content Type: long-form
Platforms: youtube,spotify,podcast
API Keys: GOOGLE_AI_API_KEY,ELEVENLABS_API_KEY
Scheduling: y
Cron: 0 10 * * 1  # Mondays at 10:00 UTC
```

Result: Podcast generated every Monday

### Example 3: Ads (On-Demand)

```bash
python3 scripts/setup_project.py

# Answers:
Project Name: ad_generator
Description: AI ad content
Content Type: ad
Platforms: youtube,instagram,tiktok
API Keys: GOOGLE_AI_API_KEY
Scheduling: n  # Manual only
```

Result: Manual trigger via GitHub Actions

## File Organization

```
project_name/
├── config.yaml
│   └── Project settings and API keys
├── content_plan.json
│   └── Topics and strategy
├── prompts/
│   ├── script.txt      - "How to write scripts"
│   ├── tts.txt         - "How to synthesize audio"
│   └── video.txt       - "How to render video"
└── README.md
    └── Project documentation
```

## Loading Configs Programmatically

```python
from core.utils.config_loader import ProjectConfig, ConfigManager

# Load single project
config = ProjectConfig.load('projects/youtube_horoscope/config.yaml')
print(f"Project: {config.name}")
print(f"Type: {config.content_type}")
print(f"Models: {config.generation['primary_model']}")

# Load all projects
manager = ConfigManager()
projects = manager.list_projects()
print(f"Available: {projects}")

# Get specific project
config = manager.get('youtube_horoscope')
if config.scheduling['enabled']:
    print(f"Scheduled: {config.scheduling['cron']}")

# List only enabled projects
enabled = manager.list_enabled()
print(f"Enabled: {enabled}")
```

## Best Practices

✅ **DO:**
- One project per directory
- Use descriptive names (youtube_shorts, tech_podcast, etc.)
- Keep config.yaml and content_plan.json in sync
- Test prompts locally before deployment
- Document your project in README.md
- Use environment variables for sensitive data

❌ **DON'T:**
- Store API keys in config files (use GitHub Secrets)
- Share workflow files between projects
- Leave projects in disabled state without comment
- Mix multiple content types in one project

## Troubleshooting

### Project not found
```bash
# Check projects directory
ls projects/

# Verify config exists
ls projects/my_project/config.yaml
```

### Config loading error
```bash
# Validate YAML
python3 -m yaml projects/my_project/config.yaml

# Load with debug info
python3 core/utils/config_loader.py my_project
```

### Workflow not running
```bash
# List workflows
gh workflow list

# Check for syntax errors
gh workflow view generate-my_project.yml

# View recent runs
gh run list --workflow generate-my_project.yml
```

## Next Steps

1. Read `ADD_PROJECT.md` for detailed instructions
2. Check example projects in `projects/`
3. Customize prompts for your brand
4. Test locally before deploying
5. Monitor GitHub Actions for results

---

**Questions?** Check the project examples or run `python3 scripts/setup_project.py --help`
