"""Auto-Fix Agent: Automatic error analysis and fix generation.

When GitHub Actions workflows fail, this module:
1. Analyzes error logs using Qwen (primary) or Gemini (fallback)
2. Identifies the problem and root cause
3. Generates code fixes when possible
4. Creates GitHub Issues with detailed technical specs
5. Creates PRs with automatic fixes
"""

import json
import logging
import os
import re
import subprocess
from typing import Optional

from core.utils.model_router import get_router
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
        - technical_notes: Detailed technical analysis
    """

    # Use only recent logs (most relevant)
    recent_logs = error_logs[-3000:] if len(error_logs) > 3000 else error_logs

    prompt = f"""You are an expert DevOps engineer and Python developer.
You specialize in the Content Factory project - an AI-powered video generation system.

A GitHub Actions workflow failed. Analyze the error and provide a comprehensive technical solution.

**Project:** {project_name}
**Workflow:** {workflow_name}

**Error Logs:**
```
{recent_logs}
```

Analyze this error DEEPLY and respond with ONLY a valid JSON object (no markdown, no explanations):

{{
  "problem": "Brief clear description of what failed (1-2 sentences)",
  "root_cause": "Detailed analysis: WHY it failed, what went wrong, which line/component",
  "severity": "critical|high|medium|low",
  "technical_notes": "Detailed technical explanation for developers. Include: error type, affected components, patterns of failure, what was expected vs what happened",
  "solution_steps": ["Step 1: exact action", "Step 2: code changes needed", "Step 3: verification"],
  "files_to_check": ["path/to/file1.py", "path/to/file2.yaml"],
  "auto_fix_possible": true or false,
  "file_to_modify": "path/to/file or null",
  "code_fix": "Complete corrected code or empty string",
  "suggested_commit_message": "Brief git commit message",
  "testing_instructions": "How to verify the fix works (run these commands/tests)"
}}

Be VERY detailed and precise. Only return JSON.
"""

    try:
        # Get API key from environment
        api_key = os.environ.get("GOOGLE_AI_API_KEY")
        if not api_key:
            logger.error("GOOGLE_AI_API_KEY not found in environment")
            return _default_analysis("Missing GOOGLE_AI_API_KEY")

        router = get_router(api_key)
        response = router.generate(task="error_analysis", prompt=prompt)

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
        "root_cause": analysis.get("root_cause", "Unknown")[:800],
        "technical_notes": analysis.get("technical_notes", "")[:2000],
        "severity": _validate_severity(analysis.get("severity", "medium")),
        "solution_steps": analysis.get("solution_steps", [])[:15],
        "files_to_check": analysis.get("files_to_check", [])[:10],
        "auto_fix_possible": bool(analysis.get("auto_fix_possible", False)),
        "file_to_modify": analysis.get("file_to_modify"),
        "code_fix": analysis.get("code_fix", "")[:5000],
        "suggested_commit_message": analysis.get("suggested_commit_message", "fix: auto-fix")[:100],
        "testing_instructions": analysis.get("testing_instructions", "")[:1000],
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
        "technical_notes": "Manual review required",
        "severity": "high",
        "solution_steps": [
            "Check the error logs manually",
            "Review the workflow output for details",
            "Contact the project maintainer if needed",
        ],
        "files_to_check": [],
        "auto_fix_possible": False,
        "file_to_modify": None,
        "code_fix": "",
        "suggested_commit_message": "fix: manual fix required",
        "testing_instructions": "Run: pytest tests/ -v",
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
    """Create GitHub Issue with detailed technical task description.

    Args:
        project_name: Project identifier
        workflow_id: GitHub workflow run ID
        workflow_run_number: GitHub workflow run number
        analysis: Analysis dictionary from analyze_workflow_error()

    Returns:
        Issue URL if successful, None otherwise
    """

    title = f"[{project_name}] 🔴 [{analysis['severity'].upper()}] {analysis['problem'][:60]}"

    # Build comprehensive issue body
    body = f"""## 🚨 Workflow Failure - Technical Task

**Severity:** {analysis['severity'].upper()}
**Project:** {project_name}
**Workflow Run:** #{workflow_run_number}

---

## 📋 Problem Statement

{analysis['problem']}

---

## 🔍 Root Cause Analysis

{analysis['root_cause']}

---

## 📌 Technical Details

{analysis['technical_notes']}

### Files Involved
"""

    if analysis.get('files_to_check'):
        for file_path in analysis['files_to_check']:
            body += f"\n- `{file_path}`"
    else:
        body += "\n- Check logs for affected files"

    body += f"""\n\n---

## ✅ Solution: Task Description

"""

    if analysis['auto_fix_possible']:
        body += "**Auto-Fix Available:** Yes ✅\n\n"
        body += "An automated PR has been created with the suggested fix.\n"
        body += "Review the PR and merge if the fix looks correct.\n\n"
    else:
        body += "**Manual Fix Required:** This needs manual attention\n\n"

    body += "### Steps to Fix\n\n"
    for i, step in enumerate(analysis.get('solution_steps', []), 1):
        body += f"{i}. {step}\n"

    body += f"""\n### Testing Instructions

```bash
{analysis.get('testing_instructions', 'pytest tests/ -v')}
```

---

## 📝 Notes for Developer

- Make sure to run the testing instructions before creating a PR
- Follow the solution steps in order
- Reference this issue in your PR: `Fixes #{workflow_run_number}`
- Auto-Fix Agent will verify the fix works ✅

---

*Generated by Auto-Fix Agent 🤖*
*[View Workflow Run](https://github.com/crosspostly/content-factory/actions/runs/{workflow_id})*
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

### Solution Implemented
{analysis['root_cause']}

### Changes
See diff below for code changes.

### How to Review
1. Check the diff to understand the fix
2. Verify it solves the issue
3. Run: `{analysis.get('testing_instructions', 'pytest tests/ -v')}`
4. Merge if approved

---
*Created by Auto-Fix Agent 🤖*
*Auto-generated to fix workflow failure*
*Close this PR if the fix is incorrect - will create a new analysis*
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


def create_github_issue(
    project_name: str,
    workflow_id: str,
    workflow_run_number: str,
    analysis: dict,
) -> Optional[str]:
    """Alias for create_issue() - for backward compatibility with workflows.
    
    Args:
        project_name: Project identifier
        workflow_id: GitHub workflow run ID
        workflow_run_number: GitHub workflow run number
        analysis: Analysis dictionary from analyze_workflow_error()
    
    Returns:
        Issue URL if successful, None otherwise
    """
    return create_issue(project_name, workflow_id, workflow_run_number, analysis)


def classify_error_complexity(analysis: dict) -> str:
    """Classify error as SIMPLE (auto-fixable) or COMPLEX (needs manual work).
    
    Args:
        analysis: Analysis dictionary from analyze_workflow_error()
    
    Returns:
        "SIMPLE" or "COMPLEX"
    """
    # Check if LLM already marked it as auto-fixable
    if analysis.get('auto_fix_possible', False):
        # Additional validation: check if we have actual code fix
        if analysis.get('code_fix') and analysis.get('file_to_modify'):
            return "SIMPLE"
    
    # Check error patterns that are typically simple
    problem_lower = analysis.get('problem', '').lower()
    root_cause_lower = analysis.get('root_cause', '').lower()
    
    simple_patterns = [
        'missing import',
        'modulenotfounderror',
        'importerror',
        'syntax error',
        'indentation',
        'missing attribute',
        'attributeerror',
        'file not found',
        'permissionerror',
        'yaml syntax',
    ]
    
    for pattern in simple_patterns:
        if pattern in problem_lower or pattern in root_cause_lower:
            # But only if we have a fix
            if analysis.get('code_fix') and analysis.get('file_to_modify'):
                return "SIMPLE"
    
    # Everything else is complex
    return "COMPLEX"


def apply_auto_fix(
    analysis: dict,
    branch_name: str,
    commit_message: Optional[str] = None,
) -> bool:
    """Apply automatic fix: modify file, commit, push to branch.
    
    Args:
        analysis: Analysis dictionary with code_fix and file_to_modify
        branch_name: Branch name to create and push
        commit_message: Custom commit message (optional)
    
    Returns:
        True if successful, False otherwise
    """
    file_to_modify = analysis.get('file_to_modify')
    code_fix = analysis.get('code_fix')
    
    if not file_to_modify or not code_fix:
        logger.error("No file_to_modify or code_fix in analysis")
        return False
    
    try:
        # Create and checkout new branch
        result = subprocess.run(
            ['git', 'checkout', '-b', branch_name],
            capture_output=True,
            text=True,
            timeout=10,
        )
        
        if result.returncode != 0:
            # Branch might already exist, try to checkout
            result = subprocess.run(
                ['git', 'checkout', branch_name],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode != 0:
                logger.error(f"Failed to checkout branch: {result.stderr}")
                return False
        
        logger.info(f"Checked out branch: {branch_name}")
        
        # Apply the fix to file
        if not apply_fix_to_file(file_to_modify, code_fix):
            logger.error(f"Failed to apply fix to {file_to_modify}")
            return False
        
        # Format code with black (optional, ignore errors)
        subprocess.run(
            ['black', file_to_modify],
            capture_output=True,
            timeout=10,
        )
        
        # Git add
        result = subprocess.run(
            ['git', 'add', file_to_modify],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            logger.error(f"Git add failed: {result.stderr}")
            return False
        
        # Git commit
        msg = commit_message or analysis.get('suggested_commit_message', 'fix: auto-fix')
        result = subprocess.run(
            ['git', 'commit', '-m', msg],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            logger.error(f"Git commit failed: {result.stderr}")
            return False
        
        logger.info(f"Committed changes: {msg}")
        
        # Git push
        result = subprocess.run(
            ['git', 'push', '-u', 'origin', branch_name],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            logger.error(f"Git push failed: {result.stderr}")
            return False
        
        logger.info(f"Pushed to branch: {branch_name}")
        return True
        
    except Exception as e:
        logger.error(f"Exception in apply_auto_fix: {e}")
        return False
