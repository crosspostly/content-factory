#!/usr/bin/env python3
"""
Interactive project setup script for content-factory.

Usage:
    python3 scripts/setup_project.py

This script will:
1. Ask for project details
2. Create project directory structure
3. Generate config.yaml
4. Create prompts
5. Generate GitHub Actions workflow
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime


class ProjectSetup:
    def __init__(self):
        self.repo_root = Path(__file__).parent.parent
        self.projects_dir = self.repo_root / "projects"
        self.workflows_dir = self.repo_root / ".github" / "workflows"
        self.scripts_dir = self.repo_root / "scripts"

    def prompt(self, question: str, default: str = "") -> str:
        """Prompt user for input with optional default."""
        if default:
            return input(f"{question} [{default}]: ").strip() or default
        return input(f"{question}: ").strip()

    def prompt_choice(self, question: str, choices: list, default: str = None) -> str:
        """Prompt user to choose from a list."""
        default_str = f" [{default}]" if default else ""
        print(f"\n{question}{default_str}")
        for i, choice in enumerate(choices, 1):
            print(f"  {i}. {choice}")
        
        while True:
            selection = input("Select (1-{}): ".format(len(choices))).strip()
            if selection.isdigit() and 1 <= int(selection) <= len(choices):
                return choices[int(selection) - 1]
            print("❌ Invalid selection")

    def prompt_yes_no(self, question: str, default: str = "n") -> bool:
        """Prompt for yes/no answer."""
        default_str = "[Y/n]" if default.lower() == "y" else "[y/N]"
        answer = input(f"{question} {default_str}: ").strip().lower()
        if answer:
            return answer[0] == "y"
        return default.lower() == "y"

    def get_project_details(self) -> dict:
        """Gather project details from user."""
        print("\n" + "="*70)
        print("🚀 CONTENT-FACTORY PROJECT SETUP")
        print("="*70)

        # Project name
        while True:
            name = self.prompt("\n📝 Project name").lower().replace(" ", "_")
            if not name:
                print("❌ Project name required")
                continue
            
            project_dir = self.projects_dir / name
            if project_dir.exists():
                print(f"⚠️  Project '{name}' already exists!")
                if not self.prompt_yes_no("Override?"):
                    continue
            break

        # Description
        description = self.prompt(
            "📄 Description",
            default="AI-powered content generation"
        )

        # Content type
        content_type = self.prompt_choice(
            "🎬 Content type",
            ["shorts", "long-form", "ad", "podcast", "custom"],
            default="shorts"
        )

        # Platforms
        print("\n📺 Platforms (select with comma separation: 1,2,3)")
        platforms = ["youtube", "tiktok", "instagram", "vk", "telegram"]
        for i, p in enumerate(platforms, 1):
            print(f"  {i}. {p}")
        
        platform_input = input("Select (1-5, e.g., 1,2,3): ").strip()
        selected_platforms = []
        if platform_input:
            try:
                indices = [int(x.strip()) for x in platform_input.split(",")]
                selected_platforms = [platforms[i-1] for i in indices if 1 <= i <= len(platforms)]
            except:
                selected_platforms = ["youtube"]
        
        if not selected_platforms:
            selected_platforms = ["youtube"]
        
        print(f"✅ Selected: {', '.join(selected_platforms)}")

        # API keys
        api_keys_str = self.prompt(
            "\n🔑 API keys needed (comma-separated)",
            default="GOOGLE_AI_API_KEY"
        )
        api_keys = [k.strip() for k in api_keys_str.split(",") if k.strip()]

        # Scheduling
        enable_scheduling = self.prompt_yes_no("\n🕐 Enable scheduling?")
        
        schedule = None
        if enable_scheduling:
            schedule = self.prompt(
                "Cron schedule (0 6 * * * = daily 06:00 UTC)",
                default="0 6 * * *"
            )
            print(f"✅ Schedule: {schedule}")
            print("   (See crontab.guru for schedule syntax)")

        return {
            "name": name,
            "description": description,
            "content_type": content_type,
            "platforms": selected_platforms,
            "api_keys": api_keys,
            "scheduling_enabled": enable_scheduling,
            "schedule": schedule,
        }

    def create_config(self, project: dict) -> dict:
        """Create config.yaml structure."""
        config = {
            "project": {
                "name": project["name"],
                "description": project["description"],
                "content_type": project["content_type"],
                "platforms": project["platforms"],
                "enabled": True,
                "created_at": datetime.now().isoformat(),
            },
            "generation": {
                "primary_model": "gemini-2.5-flash",
                "fallback_models": ["gemini-2.5-pro", "openrouter-qwen"],
                "temperature": 0.7,
                "max_retries": 2,
            },
            "api_keys": project["api_keys"],
            "scheduling": {
                "enabled": project["scheduling_enabled"],
                "cron": project["schedule"],
                "timezone": "UTC",
            },
            "output": {
                "format": "video" if project["content_type"] != "podcast" else "audio",
                "video_quality": "1080p",
                "frame_rate": 30,
                "audio_quality": "320kbps",
            },
        }
        return config

    def create_content_plan(self, project: dict) -> dict:
        """Create content_plan.json structure."""
        plan = {
            "project": project["name"],
            "version": "1.0.0",
            "created_at": datetime.now().isoformat(),
            "topics": [
                "Topic 1 - Edit this",
                "Topic 2 - Edit this",
                "Topic 3 - Edit this",
            ],
            "content_style": "professional",
            "target_audience": "general",
            "publish_schedule": {
                platform: "daily" for platform in project["platforms"]
            },
        }
        return plan

    def create_prompts(self, project: dict) -> dict:
        """Create prompt templates."""
        content_type = project["content_type"]
        platforms = ", ".join(project["platforms"])
        
        script_prompt = f"""You are a professional scriptwriter for {content_type} content.

Project: {project['name']}
Description: {project['description']}
Platforms: {platforms}
Content Type: {content_type}

Your task:
1. Write engaging scripts about the provided topics
2. Keep it concise and attention-grabbing
3. Use professional language
4. Include visual cues and transitions
5. Optimize for target audience

Output format:
[TITLE]
Your title here

[NARRATOR]
Narration text...

[VISUAL]
Visual description...

[MUSIC]
Music suggestions...

Start writing:
"""

        tts_prompt = f"""You are a voice director for {content_type} content.

Project: {project['name']}
Platforms: {platforms}

Your task:
1. Create natural, engaging voice direction
2. Specify tone: professional, energetic, calm, etc.
3. Add emotional cues
4. Suggest pacing: fast, medium, slow
5. Include pronunciation guides if needed

For each section:
[VOICE_SETTINGS]
- Tone: professional
- Pace: medium
- Emotion: engaging
- Energy: high

[NARRATION]
Text with delivery cues (pause: 2s, emphasis: WORD, etc.)
"""

        video_prompt = f"""You are a professional video editor for {content_type} content.

Project: {project['name']}
Platforms: {platforms}
Quality: 1080p @ 30fps

Your task:
1. Create visually appealing video sequences
2. Match pacing to audio
3. Use platform-appropriate aspect ratios
4. Add text overlays and graphics
5. Suggest color grading and effects

For each scene:
[SCENE]
Duration: Xs
Visuals: description
Transition: cut/fade/zoom
Text: overlay text
Effects: suggested effects
Color: color tone
"""

        return {
            "script.txt": script_prompt,
            "tts.txt": tts_prompt,
            "video.txt": video_prompt,
        }

    def create_workflow(self, project: dict) -> str:
        """Create GitHub Actions workflow."""
        project_name = project["name"]
        schedule_str = ""
        
        if project["scheduling_enabled"]:
            schedule_str = f"""
  schedule:
    - cron: '{project["schedule"]}'"""

        workflow = f"""name: Generate {project_name}

on:
  workflow_dispatch:
    inputs:
      format:
        description: 'Content format'
        required: false
        default: '{project["content_type"]}'
      date:
        description: 'Target date (YYYY-MM-DD, optional)'
        required: false
{schedule_str}

jobs:
  generate:
    runs-on: ubuntu-22.04
    timeout-minutes: 60

    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 1

      - name: Setup Python 3.11
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install dependencies
        run: |
          sudo apt-get update -qq
          sudo apt-get install -y ffmpeg imagemagick ghostscript fonts-dejavu-core
          python -m pip install --upgrade pip
          pip install -r requirements.txt -q

      - name: Generate content
        env:
          PROJECT: {project_name}
          FORMAT: ${{{{ github.event.inputs.format || '{project["content_type"]}' }}}}
          TARGET_DATE: ${{{{ github.event.inputs.date }}}}
          GH_TOKEN: ${{{{ github.token }}}}
          GOOGLE_AI_API_KEY: ${{{{ secrets.GOOGLE_AI_API_KEY }}}}
        run: |
          python3 << 'PYTHON_SCRIPT'
          import os
          import sys
          from pathlib import Path

          sys.path.insert(0, '.')
          
          try:
              from core.orchestrators.pipeline_orchestrator import generate_content
              from core.utils.config_loader import ProjectConfig
              
              project_name = os.getenv('PROJECT')
              fmt = os.getenv('FORMAT')
              target_date = os.getenv('TARGET_DATE')
              
              print(f"\\n🚀 Generating content for {{project_name}}")
              print(f"Format: {{fmt}}")
              if target_date:
                  print(f"Date: {{target_date}}")
              
              # Load project config
              config = ProjectConfig.load(f'projects/{{project_name}}/config.yaml')
              
              # Generate content
              result = generate_content(
                  project_name=project_name,
                  format=fmt,
                  target_date=target_date,
                  config=config
              )
              
              print(f"\\n✅ Content generated successfully!")
              print(f"Output: {{result}}")
              
          except Exception as e:
              print(f"\\n❌ Generation failed: {{e}}")
              import traceback
              traceback.print_exc()
              sys.exit(1)
          PYTHON_SCRIPT

      - name: Upload artifacts
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: {project_name}-output-${{{{ github.run_number }}}}
          path: output/
          retention-days: 7
          if-no-files-found: warn

      - name: Notify result
        if: always()
        run: |
          STATUS="${{{{ job.status }}}}"
          if [ "$STATUS" = "success" ]; then
            echo "✅ Content generated successfully"
          else
            echo "❌ Generation failed"
          fi
"""
        return workflow

    def save_files(self, project: dict, config: dict, content_plan: dict, prompts: dict, workflow: str) -> bool:
        """Save all generated files."""
        project_name = project["name"]
        project_dir = self.projects_dir / project_name
        prompts_dir = project_dir / "prompts"

        try:
            # Create directories
            project_dir.mkdir(parents=True, exist_ok=True)
            prompts_dir.mkdir(parents=True, exist_ok=True)

            # Save config.yaml
            import yaml
            config_path = project_dir / "config.yaml"
            with open(config_path, "w") as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)
            print(f"✅ Created {config_path}")

            # Save content_plan.json
            plan_path = project_dir / "content_plan.json"
            with open(plan_path, "w") as f:
                json.dump(content_plan, f, indent=2)
            print(f"✅ Created {plan_path}")

            # Save prompts
            for prompt_name, prompt_content in prompts.items():
                prompt_path = prompts_dir / prompt_name
                with open(prompt_path, "w") as f:
                    f.write(prompt_content)
                print(f"✅ Created {prompt_path}")

            # Save workflow
            workflow_path = self.workflows_dir / f"generate-{project_name}.yml"
            self.workflows_dir.mkdir(parents=True, exist_ok=True)
            with open(workflow_path, "w") as f:
                f.write(workflow)
            print(f"✅ Created {workflow_path}")

            # Create README
            readme_path = project_dir / "README.md"
            readme = f"""# {project_name}

{project['description']}

## Configuration

Edit `config.yaml` to customize:
- API models and parameters
- Output formats and quality
- Scheduling (if enabled)

## Content Plan

Edit `content_plan.json` to set:
- Topics and themes
- Content style and tone
- Publishing schedule

## Prompts

Customize AI instructions in `prompts/`:
- `script.txt` - Script generation
- `tts.txt` - Audio synthesis
- `video.txt` - Video rendering

## Manual Generation

```bash
gh workflow run generate-{project_name}.yml \\
  -f format={project['content_type']} \\
  -f date=2025-12-14
```

## Scheduling

Schedule: {project['schedule'] if project['scheduling_enabled'] else 'Manual trigger only'}

Edit cron schedule in `config.yaml` under `scheduling.cron`.

---

Generated by setup_project.py on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            with open(readme_path, "w") as f:
                f.write(readme)
            print(f"✅ Created {readme_path}")

            return True
        except Exception as e:
            print(f"❌ Error saving files: {e}")
            return False

    def run(self):
        """Run the setup process."""
        # Check for required packages
        try:
            import yaml
        except ImportError:
            print("\n⚠️  PyYAML not found. Installing...")
            os.system("pip install pyyaml")

        # Get project details
        project = self.get_project_details()
        
        # Generate structures
        config = self.create_config(project)
        content_plan = self.create_content_plan(project)
        prompts = self.create_prompts(project)
        workflow = self.create_workflow(project)

        # Save files
        print(f"\n{'='*70}")
        print("📝 Creating project files...")
        print(f"{'='*70}")
        
        success = self.save_files(project, config, content_plan, prompts, workflow)

        if success:
            print(f"\n{'='*70}")
            print("✅ PROJECT SETUP COMPLETE!")
            print(f"{'='*70}")
            print(f"\n📁 Project directory: projects/{project['name']}/")
            print(f"\n🎯 Next steps:")
            print(f"  1. Edit projects/{project['name']}/config.yaml")
            print(f"  2. Customize projects/{project['name']}/content_plan.json")
            print(f"  3. Update prompts in projects/{project['name']}/prompts/")
            print(f"  4. Test: python3 core/orchestrators/pipeline_orchestrator.py --project {project['name']} --test")
            print(f"  5. Deploy: git push origin main")
            print(f"\n✨ Your workflow will run{' on schedule: ' + project['schedule'] if project['scheduling_enabled'] else ' on manual trigger'}")
            print(f"\n📚 Read ADD_PROJECT.md for more details\n")
        else:
            print(f"\n❌ Setup failed. Check the errors above.\n")
            sys.exit(1)


if __name__ == "__main__":
    setup = ProjectSetup()
    setup.run()
