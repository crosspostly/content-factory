# Auto-Fix Agent Guide 🤖

## Overview

**Auto-Fix Agent is ALWAYS ENABLED** and works automatically when any workflow fails.

It uses **Gemini 2.5 Flash** to analyze failures and creates:
1. 📝 GitHub Issue with detailed analysis
2. 🔀 Pull Request with suggested fixes

You review and merge the PR manually (you're always in control!).

---

## How It Works

```
Workflow Fails
    ↓
GitHub Actions triggers auto-fix-agent.yml
    ↓
Gemini 2.5 Flash analyzes error logs
    ↓
Creates GitHub Issue with:
  - Problem description
  - Root cause analysis
  - Severity level
  - Solution steps
  - Code fix suggestion
    ↓
If auto-fix possible:
  Creates PR with code changes
    ↓
You review PR and manually merge
    ↓
Fix applied to main branch
```

---

## What You See

### When Workflow Fails

**GitHub Issue is created automatically:**
```
🔴 [HIGH] TTS Generator missing API key parameter

Problem: Test fails because api_key parameter not passed
Root Cause: Function signature changed but calls weren't updated
Severity: HIGH

Solution Steps:
- Identify all synthesize() calls without api_key
- Add api_key parameter
- Run tests to verify

Suggested Code Fix:
```

**Pull Request is created (if auto-fix possible):**
```
🔧 Auto-Fix: TTS Generator missing API key parameter

Issue: Test fails because api_key parameter not passed
Root Cause: Function signature changed but calls weren't updated
Severity: HIGH

Changes:
- tests/test_tts_generator.py (1 file changed)

[Review] [Merge] [Close]
```

### Your Actions

1. **Review the PR**
   - Check the code changes
   - Read the issue for context
   - Verify it makes sense

2. **Merge or Request Changes**
   - ✅ Click "Merge" if fix looks good
   - 📝 Request changes if you see issues
   - ❌ Close if fix is wrong

3. **Done!**
   - Branch auto-deletes
   - Issue auto-closes
   - Main branch has the fix

---

## Configuration

**File:** `.github/auto-fix-config.yml`

```yaml
auto_fix:
  enabled: true              # Always on
  create_issue: true         # Create issue + PR
  model: gemini-2.5-flash    # Using fastest Gemini model
  min_severity: low          # Fix all failures
```

**You don't need to change anything!** It's configured to work automatically.

If you want to disable it temporarily:
```yaml
auto_fix:
  enabled: false  # ← Change this
```

Then commit and push. Auto-fix will be disabled until you change it back.

---

## Examples

### Example 1: Test Failure (Low Severity)

**Workflow fails:**
```
FAILED tests/test_tts_generator.py::test_synthesize_shorts
ValueError: Missing parameter 'api_key'
```

**Auto-Fix Agent creates:**

📝 **Issue:**
```
🟡 [MEDIUM] Test failure: missing api_key parameter
```

🔀 **PR:**
```
+ result = tts_generator.synthesize(
+   config,
+   script,
+   mode,
+   api_key=api_key  # ← Added this
+ )
```

**You:**
- Review fix ✅
- Click "Merge" ✅
- Tests pass on next run ✅

### Example 2: Docker Build (Critical)

**Workflow fails:**
```
Step 5/10 : RUN pip install -r requirements.txt
Error: Conflicting versions of numpy
```

**Auto-Fix Agent creates:**

📝 **Issue:**
```
🔴 [CRITICAL] Docker build failed: numpy version conflict

Root Cause: requirements.txt has conflicting numpy versions
Solution: Pin numpy to compatible version
```

🔀 **PR:**
```
-numpy==1.24.0
+numpy==1.26.4  # Compatible with all dependencies
```

**You:**
- Read analysis ✅
- Check if version is correct ✅
- Merge if OK ✅

### Example 3: No Auto-Fix Possible

**Workflow fails:**
```
Network timeout connecting to S3 bucket
```

**Auto-Fix Agent creates:**

📝 **Issue:**
```
🟠 [HIGH] Network error: S3 bucket unreachable

Problem: Network timeout
Root Cause: AWS credentials expired or network issue
Auto-fix possible: NO

Suggested Actions:
- Check AWS credentials
- Verify network connectivity
- Re-run workflow after fix
```

❌ **No PR created** (can't auto-fix network issues)

**You:**
- Read the analysis ✅
- Fix the underlying issue (update credentials, etc.) ✅
- Re-run workflow ✅

---

## Model: Gemini 2.5 Flash

Why Gemini 2.5 Flash? 
- ✅ Fastest model (instant analysis)
- ✅ Best for code analysis
- ✅ Good at understanding errors
- ✅ Cheap (included in API quota)
- ✅ Always available

```python
# Confirmed in workflow:
model = genai.GenerativeModel('gemini-2.5-flash')
```

---

## Safety Features

✅ **You're always in control**
- PRs created, not auto-merged
- Issue is created for context
- Branch is separate from main
- You can review before merging

✅ **Audit trail**
- Every PR has issue reference
- Commits tagged with `[auto-fix-agent]`
- Workflow run linked
- Easy to track what changed

✅ **Can be disabled**
- Edit `.github/auto-fix-config.yml`
- Set `enabled: false`
- Commit and push
- Auto-fix stops immediately

---

## Troubleshooting

### PR not created but issue is
**Means:** Auto-fix determined it's not possible to fix automatically

**What to do:**
- Read the issue analysis
- Follow the suggested solution steps
- Fix manually
- Re-run workflow

### API key error in auto-fix
**Error:** `GOOGLE_AI_API_KEY not set`

**Fix:**
1. Go to GitHub repo Settings → Secrets
2. Add secret: `GOOGLE_AI_API_KEY`
3. Use your Gemini API key
4. Re-run the workflow

### PR is created but fix is wrong
**What to do:**
- Click "Request Changes" on PR
- Leave a comment explaining what's wrong
- Agent won't auto-fix again for this error
- Fix manually in separate PR
- Learn from the issue for next time

---

## Workflow Events

Auto-fix triggers on failures from these workflows:
- ✅ `Generate Content (Part 1 MVP)` - Main generation workflow
- ✅ `test` - Unit tests

Add more workflows to `.github/auto-fix-config.yml` if needed:
```yaml
workflow:
  triggers:
    - "Generate Content (Part 1 MVP)"
    - "test"
    - "build-docker"  # ← Add new workflow
```

---

## FAQ

**Q: Will this auto-merge to main?**
A: No! It creates a PR that you manually review and merge.

**Q: What if the fix is wrong?**
A: Request changes on the PR or close it. You're in control.

**Q: Can I disable it?**
A: Yes, edit `.github/auto-fix-config.yml` and set `enabled: false`

**Q: Does it cost money?**
A: Only Google Gemini API calls, which are cheap. GitHub Actions are free for public repos.

**Q: Can it fix any error?**
A: Not all errors have auto-fixable solutions. Network issues, missing credentials, etc. still require manual fixes.

**Q: How fast is it?**
A: Usually < 2 minutes from failure to PR creation.

---

## Status

✅ **Auto-Fix Agent is LIVE**
✅ **Using Gemini 2.5 Flash**
✅ **Always enabled (PR-based)**
✅ **Manual merge required**

No configuration needed - it just works! 🚀

---

**Last Updated:** 2025-12-12
