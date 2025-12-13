"""Auto-Fix Agent: Automatic error analysis and fix generation.

When GitHub Actions workflows fail, this module:
1. Analyzes error logs using Qwen (primary) or Gemini (fallback)
2. Identifies the problem and root cause
3. Generates code fixes when possible
4. Creates GitHub Issues with detailed analysis
5. Creates PRs with automatic fixes
"""

import json
import logging
import os
import re
import subprocess
from typing import Optional

from core.utils.model_router import generate_text
from core.utils.config_loader import ProjectConfig

logger = logging.getLogger(__name__)


def analyze_workflow_error(
    project_name: str,
    workflow_name: str,
    error_logs: str,
    config: ProjectConfig,
) -> dict:
    """Analyze workflow error using Qwen/Gemini LLM.

    Args:
        project_name: Project identifier (youtube_horoscope, tiktok_faces, etc)
        workflow_name: Name of the failed workflow
        error_logs: Complete error logs from GitHub Actions
        config: ProjectConfig object with model settings

    Returns:
        Analysis dictionary with:
        - problem: What failed
        - root_cause: Why it failed
        - severity: critical|high|medium|low
        - auto_fix_possible: Whether we can fix it automatically
        - file_to_modify: File path to modify (or None)
        - code_fix: Fixed code (or empty string)
        - solution_steps: Manual steps if auto-fix not possible
        - suggested_commit_message: Git commit message
    """

    # Use only recent logs (most relevant)
    recent_logs = error_logs[-3000:] if len(error_logs) > 3000 else error_logs

    prompt = f"""You are an expert DevOps engineer and Python developer.
You specialize in the Content Factory project - an AI-powered video generation system.

A GitHub Actions workflow failed. Analyze the error and provide a technical solution.

**Project:** {project_name}
**Workflow:** {workflow_name}

**Error Logs:**
```
{recent_logs}
```

Analyze this error and respond with ONLY a valid JSON object (no markdown, no explanations):

{{
  "problem": "Brief description of what failed (1-2 sentences)",
  "root_cause": "Why it happened and detailed explanation",
  "severity": "critical|high|medium|low",
  "solution_steps": ["Step 1", "Step 2", "Step 3"],
  "auto_fix_possible": true or false,
  "file_to_modify": "path/to/file or null",
  "code_fix": "Complete corrected code or empty string",
  "suggested_commit_message": "Brief git commit message"
}}

Be precise and actionable. Only return JSON.
"""

    try:
        response = generate_text(config, prompt)

        # Extract JSON from response
        match = re.search(r"\{[\s\S]*\}", response)
        if not match:
            logger.error("No JSON found in LLM response")
            return _default_analysis("Could not parse LLM response")

        analysis = json.loads(match.group())

        # Validate and normalize response
        analysis = _normalize_analysis(analysis)
        logger.info(f"Analysis complete: {analysis['problem'][:100]}")
        return analysis

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return _default_analysis("Invalid JSON from LLM")
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return _default_analysis(str(e)[:100])


def _normalize_analysis(analysis: dict) -> dict:
    """Ensure analysis has all required fields with proper types."""

    return {
        "problem": analysis.get("problem", "Unknown error")[:200],
        "root_cause": analysis.get("root_cause", "Unknown")[:500],
        "severity": _validate_severity(analysis.get("severity", "medium")),
        "solution_steps": analysis.get("solution_steps", [])[:10],
        "auto_fix_possible": bool(analysis.get("auto_fix_possible", False)),
        "file_to_modify": analysis.get("file_to_modify"),
        "code_fix": analysis.get("code_fix", "")[:5000],
        "suggested_commit_message": analysis.get("suggested_commit_message", "fix: auto-fix")[:100],
    }


def _validate_severity(severity: str) -> str:
    """Ensure severity is one of allowed values."""
    valid = {"critical", "high", "medium", "low"}
    return severity if severity in valid else "medium"


def _default_analysis(error: str) -> dict:
    """Return default analysis when LLM fails."""
    return {
        "problem": f"Auto-Fix analysis failed: {error}",
        "root_cause": "Qwen/Gemini analysis could not complete",
        "severity": "high",
        "solution_steps": [
            "Check the error logs manually",
            "Review the workflow output for details",
            "Contact the project maintainer if needed",
        ],
        "auto_fix_possible": False,
        "file_to_modify": None,
        "code_fix": "",
        "suggested_commit_message": "fix: manual fix required",
    }


def apply_fix_to_file(file_path: str, code_fix: str) -> bool:
    """Apply code fix to a file.

    Args:
        file_path: Full path to file to modify
        code_fix: New code content

    Returns:
        True if successful, False otherwise
    """
    if not code_fix or not file_path:
        return False

    try:
        import shutil

        # Create backup
        backup_path = f"{file_path}.backup"
        shutil.copy(file_path, backup_path)
        logger.info(f"Created backup: {backup_path}")

        # Write fix
        with open(file_path, "w") as f:
            f.write(code_fix)

        logger.info(f"Applied fix to {file_path}")
        return True

    except Exception as e:
        logger.error(f"Failed to apply fix: {e}")
        return False


def create_issue(
    project_name: str,
    workflow_id: str,
    workflow_run_number: str,
    analysis: dict,
) -> Optional[str]:
    """Create GitHub Issue with error analysis.

    Args:
        project_name: Project identifier
        workflow_id: GitHub workflow run ID
        workflow_run_number: GitHub workflow run number
        analysis: Analysis dictionary from analyze_workflow_error()

    Returns:
        Issue URL if successful, None otherwise
    """

    title = f"[{project_name}] 🔴 [{analysis['severity'].upper()}] {analysis['problem'][:60]}"

    body = f"""## 🚨 Workflow Failure Analysis

**Project:** {project_name}
**Run:** #{workflow_run_number}
**Severity:** {analysis['severity'].upper()}

### Problem
{analysis['problem']}

### Root Cause
{analysis['root_cause']}

### Solution Steps
{_format_steps(analysis.get('solution_steps', []))}

### Auto-Fix Status
- Can be auto-fixed: {'✅ Yes' if analysis['auto_fix_possible'] else '❌ No (manual fix needed)'}

---
*Generated by Auto-Fix Agent 🤖 at GitHub Actions*
[View Workflow Run](https://github.com/crosspostly/content-factory/actions/runs/{workflow_id})
"""

    try:
        result = subprocess.run(
            [
                "gh",
                "issue",
                "create",
                "--title",
                title,
                "--body",
                body,
                "--label",
                f"bug,auto-generated,ai-analyzed,project:{project_name}",
            ],
            capture_output=True,
            text=True,
            env={**os.environ},
            timeout=30,
        )

        if result.returncode == 0:
            issue_url = result.stdout.strip()
            logger.info(f"Created issue: {issue_url}")
            return issue_url
        else:
            logger.error(f"Failed to create issue: {result.stderr}")
            return None

    except Exception as e:
        logger.error(f"Exception creating issue: {e}")
        return None


def create_pr(
    project_name: str,
    branch_name: str,
    analysis: dict,
    issue_url: str,
) -> Optional[str]:
    """Create GitHub PR with auto-fix code.

    Args:
        project_name: Project identifier
        branch_name: Branch with the fix (must already be pushed)
        analysis: Analysis dictionary
        issue_url: URL of the related GitHub Issue

    Returns:
        PR URL if successful, None otherwise
    """

    title = f"[{project_name}] 🔧 Auto-Fix: {analysis['problem'][:50]}"

    body = f"""## Auto-Fix PR

**Related Issue:** {issue_url}

### Problem
{analysis['problem']}

### Solution
{analysis['root_cause']}

### How to Review
1. Check the diff below to understand the fix
2. Verify it solves the issue mentioned above
3. Merge if approved, or request changes

---
*Created by Auto-Fix Agent 🤖*
*This PR was automatically generated to fix a workflow failure*
"""

    try:
        result = subprocess.run(
            [
                "gh",
                "pr",
                "create",
                "--base",
                "main",
                "--head",
                branch_name,
                "--title",
                title,
                "--body",
                body,
                "--label",
                f"auto-generated,ai-generated,project:{project_name}",
            ],
            capture_output=True,
            text=True,
            env={**os.environ},
            timeout=30,
        )

        if result.returncode == 0:
            pr_url = result.stdout.strip()
            logger.info(f"Created PR: {pr_url}")
            return pr_url
        else:
            logger.error(f"Failed to create PR: {result.stderr}")
            return None

    except Exception as e:
        logger.error(f"Exception creating PR: {e}")
        return None


def _format_steps(steps: list) -> str:
    """Format solution steps as markdown list."""
    if not steps:
        return "- No specific steps provided"
    return "\n".join(f"- {step}" for step in steps)
