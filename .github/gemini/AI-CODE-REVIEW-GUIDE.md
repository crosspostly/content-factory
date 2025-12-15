# 🤖 AI Code Review Workflow Guide

## Overview

This repository includes an automated **AI Code Review** workflow powered by **Gemini 2.5 Flash** that:

- ✅ Automatically reviews pull requests against GitHub issue requirements
- ✅ Identifies code quality issues, missing tests, and documentation gaps
- ✅ Auto-commits improvements and fixes to the PR branch
- ✅ Posts comprehensive review summaries as PR comments

## How It Works

### Automatic Trigger (Pull Request)
The workflow runs automatically when:
- A new PR is opened against `main` or `develop` branches
- A PR is updated (new commits pushed)
- A PR is reopened

### Manual Trigger (Workflow Dispatch)
You can manually trigger the review via GitHub Actions UI with:
- **pr_number** (optional): Specific PR to review
- **base_ref** (optional): Base branch for comparison (default: `main`)

## Setup & Configuration

### 1. API Key Configuration

The workflow requires a Gemini API key. Add it to your repository secrets:

**Option A:** Using `GOOGLE_AI_API_KEY` (Recommended)
```bash
# Go to: Settings → Secrets and variables → Actions
# Add a new repository secret:
# Name: GOOGLE_AI_API_KEY
# Value: <your-gemini-api-key>
```

**Option B:** Using `GEMINI_API_KEY` (Legacy)
```bash
# Name: GEMINI_API_KEY
# Value: <your-gemini-api-key>
```

The workflow checks both keys in this order: `GOOGLE_AI_API_KEY` → `GEMINI_API_KEY`

### 2. Link Issues to PRs

For the AI Agent to analyze requirements, **link the GitHub issue in the PR description**:

```markdown
## Description
This PR implements the new feature...

Fixes #43
Resolves #44
Related to #45
```

The agent will automatically:
1. Extract issue number (#43, #44, #45)
2. Fetch the issue details and checklist
3. Verify PR implements all requirements

## Workflow Structure

### Step 1: Checkout & Context
- Clones repository with full history
- Determines PR context (auto vs manual trigger)
- Extracts SHAs for diff generation

### Step 2: Prepare Materials
- **Issue**: Fetches GitHub issue linked in PR
- **Diff**: Generates code changes (max 8000 chars)
- **Files**: Lists all modified files
- **Description**: Saves PR description

All materials saved to `.gemini/` directory for processing.

### Step 3: Setup Tools
- Installs Node.js v18
- Installs/verifies Gemini CLI
- Prepares environment for API calls

### Step 4: Run Review
Sends comprehensive prompt to Gemini API containing:
- System prompt (from `.github/gemini/code-review-prompt.md`)
- Issue details and checklist
- PR description
- Code diff
- Changed files list

### Step 5: Process Results
- Parses JSON response from Gemini
- Extracts: rating, issues, improvements, files modified
- Prepares commit message

### Step 6: Auto-Fix
If improvements detected:
- Stages all changes: `git add -A`
- Commits with message: `fix: auto-improvements by Gemini CLI AI Agent`
- Pushes to PR branch: `git push origin <branch>`

### Step 7: Post Comment
Creates comprehensive PR comment with:
- Overall rating (✅ APPROVE, ⚠️ REVIEW, ❌ REQUEST_CHANGES)
- Issue checklist status
- Found issues with severity levels
- Suggested improvements
- Files modified by AI Agent
- Summary and recommendations

### Step 8: Debug Info
- Shows JSON review results
- Displays raw Gemini response for troubleshooting

## Review Criteria

The AI Agent checks against:

### Code Quality
- ✅ Architecture compliance (follows ARCHITECTURE.md patterns)
- ✅ Error handling (proper try/except, retry logic)
- ✅ Configuration usage (config_loader, no hardcoded values)
- ✅ Logging (sufficient logging for debugging)
- ✅ Testing (unit tests for new functionality)
- ✅ Documentation (updated docs for changes)

### Critical Model Checks
- ✅ **ONLY** `gemini-2.5-flash` or `gemini-2.5-flash-lite` allowed
- ❌ **NEVER** use: gemini-2.0-flash, gemini-1.5-flash, or older versions

### Common Issues Fixed
- 🔴 Wrong Gemini model versions → Update to 2.5 Flash
- 🔴 Hardcoded API keys → Use `os.getenv()`
- 🔴 Missing tests → Add unit tests
- 🔴 Insufficient logging → Add logging calls
- 🟡 Code style issues → Fix formatting
- 🟡 Missing docstrings → Add documentation

## PR Comment Format

Example output in your PR:

```markdown
## 🤖 AI Code Review Summary

**Issue:** #43 - Implement Slides Mode

**Overall Rating:** ✅ APPROVE

**Summary:** PR successfully implements all required features with good test coverage.

### ✅ Checklist Status
✅ Introduce content_modes package - Completed
✅ Implement SlidesMode - Completed
✅ Create tests - Completed
⚠️ Update docs - Partially (README needs section)

### 🚨 Issues Found
🟡 **WARNING** in `core/content_modes/slides_mode.py:42`
> Missing docstring for SlideRenderer.render() method
💡 Add docstring: """Renders slide data to image using Pillow."""

### 💡 Improvements Suggested
- Add type hints to all function parameters
- Consider caching slide renders for performance
- Add integration tests with real Pixabay API

### 📝 Files Modified by AI Agent
- `core/content_modes/slides_mode.py`
- `README.md`
- `tests/test_slides_mode.py`

### ℹ️ AI Agent Status
- Auto-fixes applied: ✅ Yes
- Commit: fix: auto-improvements by Gemini CLI AI Agent

---
*Auto-generated by Gemini CLI AI Agent*
```

## Best Practices

### For PR Authors

1. **Link the Issue**
   ```markdown
   Fixes #NUMBER
   ```

2. **Follow the Checklist**
   - Review the issue checklist before submitting
   - Implement all required items
   - Add tests for new functionality

3. **Write Clear Descriptions**
   - Explain what changed and why
   - Reference issue numbers
   - List any breaking changes

4. **Include Tests**
   - Unit tests for new functions
   - Edge case testing
   - Integration tests if applicable

### For Project Maintainers

1. **Create Issues with Checklists**
   ```markdown
   ## Details
   
   ### Tasks
   - [ ] Task 1 description
   - [ ] Task 2 description
   - [ ] Task 3 description
   
   ### Notes
   - Any special requirements
   - Known limitations
   - Warnings for reviewers
   ```

2. **Monitor Review Results**
   - Review AI feedback
   - Ensure all critical issues addressed
   - Request changes if necessary

3. **Merge After Fixes**
   - Run tests locally
   - Verify AI-suggested changes
   - Approve and merge when ready

## Troubleshooting

### API Key Issues
**Error:** `GEMINI_API_KEY is not set`

**Solution:** Add `GOOGLE_AI_API_KEY` to repository secrets:
1. Go to Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `GOOGLE_AI_API_KEY`
4. Paste your API key

### No Issue Found
**Message:** ⚠️ No issue number found in PR description

**Solution:** Link the issue in PR:
```markdown
Fixes #NUMBER
```

### Large Diff
**Warning:** Diff truncated to first 8000 chars

**Info:** This is normal. Larger PRs will have truncated diffs.
**Fix:** Break large PRs into smaller, focused changes.

### Failed to Push
**Error:** Failed to push changes

**Cause:** Usually permission issues

**Solution:** 
- Ensure workflow has `contents: write` permission
- Check branch protection rules
- Verify token has access

## Configuration Files

### `.github/workflows/ai-code-review.yml`
Main workflow file with all steps and logic.

**Key Inputs:**
- `pr_number`: PR to review (workflow_dispatch only)
- `base_ref`: Base branch for diff (default: main)

**Permissions Required:**
- `contents: write` - Create commits
- `pull-requests: write` - Create comments
- `checks: write` - Report checks

### `.github/gemini/code-review-prompt.md`
System prompt sent to Gemini API.

**Contains:**
- Role definition
- Code review guidelines
- Checklist items
- Output format requirements

## Advanced Usage

### Manual Review on Specific Branch
1. Go to Actions → AI Code Review with Gemini CLI
2. Click "Run workflow"
3. Enter PR number (if exists)
4. Or use base_ref for non-PR comparisons

### Disable for Specific PRs
Add to PR description:
```markdown
<!-- AI_REVIEW_SKIP -->
```

(Not implemented - would need workflow update)

### Customize Review Criteria
Edit `.github/gemini/code-review-prompt.md` to:
- Add project-specific checks
- Change severity levels
- Update model version requirements
- Add new code standards

## Security Considerations

### API Key Protection
- ✅ Keys stored in repository secrets
- ✅ Not logged in workflow output
- ✅ Rotated via Settings page

### Code Review Safety
- ✅ No automatic merging (manual approval required)
- ✅ Only commits to PR branch, not main
- ✅ All changes reviewable in PR

### Limitations
- ⚠️ AI reviews are suggestions, not ground truth
- ⚠️ Manual review by humans still required
- ⚠️ Security-critical code needs expert review

## Support & Feedback

### Issues with Workflow
1. Check workflow logs in Actions tab
2. Review error messages in step output
3. Verify API key is set correctly
4. Check GitHub API permissions

### Feature Requests
- Update code-review-prompt.md
- Add custom checks
- Enhance commit logic

### Reporting Issues
Include:
- Workflow run URL
- Step that failed
- Error messages
- PR number (if applicable)

## Related Documentation

- [ARCHITECTURE.md](../../ARCHITECTURE.md) - Project architecture
- [README.md](../../README.md) - Project overview
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Gemini API Docs](https://ai.google.dev/docs)

---

**Last Updated:** December 2025
**Version:** 1.0
**Maintained By:** AI Team
