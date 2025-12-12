# How to Test Auto-Fix Agent 🔨

## Quick Start (1 minute)

### Method 1: Run Test Workflow (Safest 🔐)

```bash
1. Go to GitHub repo → Actions tab
2. Find "Test Auto-Fix Trigger" workflow
3. Click "Run workflow"
4. Watch the magic! 🤖
```

**What happens:**
- Test workflow intentionally fails
- Auto-Fix Agent automatically starts (~1-2 min)
- Creates GitHub Issue with analysis
- Creates PR with suggested fix
- You see it in PR tab

### Method 2: Intentional Test Failure (Most Realistic)

```bash
# 1. Edit any test to make it fail
vi tests/test_tts_generator.py
# Change a line to fail:
# assert False  # Intentional failure

# 2. Commit and push
git add tests/test_tts_generator.py
git commit -m "[TEST] Trigger auto-fix agent"
git push origin main

# 3. Wait ~2 minutes

# 4. Check:
#    - GitHub Actions → auto-fix-agent.yml
#    - GitHub Issues → new issue created
#    - GitHub PRs → new PR with fix
```

---

## What to Expect 👀

### Timeline

```
00:00 - Workflow fails
00:10 - Auto-fix-agent.yml starts
00:15 - Gemini 2.5 analyzes (very fast)
00:20 - Creates GitHub Issue
00:45 - Creates Pull Request with fix
01:00 - DONE! PR ready for you to merge
```

### GitHub Issue (Auto-generated)

🔴 **Title Example:**
```
🔴 [HIGH] Test failure: missing api_key parameter
```

📝 **Content:**
```
Problem: Test fails because api_key parameter not passed
Root Cause: Function signature changed but calls weren't updated
Severity: HIGH
Solution Steps:
- Add api_key parameter to synthesize() calls
- Update test fixtures
Code Fix: [code snippet]
```

### Pull Request (Auto-generated)

🔧 **Title Example:**
```
🔧 Auto-Fix: Test failure: missing api_key parameter
```

💱 **Content:**
```
1 file changed
- old code
+ new code

[View] [Merge] [Request Changes] [Close]
```

**You just click MERGE and it's done!**

---

## Verification Checklist ✅

- [ ] Test workflow fails intentionally
- [ ] Auto-fix-agent.yml starts in Actions
- [ ] Gemini analysis appears in logs
- [ ] GitHub Issue is created
- [ ] Pull Request is created
- [ ] PR shows code changes
- [ ] You can merge the PR

---

## If It Doesn't Work 🚫

### Check These:

1. **GOOGLE_AI_API_KEY is set?**
   - Go to Repo Settings → Secrets
   - Check if GOOGLE_AI_API_KEY exists
   - If not, add it!

2. **Workflow is enabled?**
   - Check `.github/workflows/auto-fix-agent.yml` exists
   - Check it's not disabled

3. **Failure was real?**
   - Make sure workflow actually FAILED
   - Auto-fix only runs on failures!

4. **Check Action logs:**
   - Go to Actions → auto-fix-agent run
   - Scroll down to see full logs
   - Look for errors

---

## Monitor Auto-Fix Agent 📊

### Real-time Monitoring

```bash
# Watch the workflow
open "https://github.com/crosspostly/content-factory/actions"

# Check issues
open "https://github.com/crosspostly/content-factory/issues"

# Check PRs
open "https://github.com/crosspostly/content-factory/pulls"
```

### Workflow Logs

```bash
# In Actions tab:
# 1. Click "auto-fix-agent" workflow
# 2. Click the failed run
# 3. See all steps with timestamps
# 4. Click each step to expand logs
```

---

## Understanding the Output 🤭

### Gemini Analysis (JSON format)

```json
{
  "problem": "Brief description",
  "root_cause": "Why it happened",
  "severity": "critical|high|medium|low",
  "solution_steps": ["step 1", "step 2"],
  "code_fix": "actual code to fix",
  "file_to_modify": "path/to/file",
  "suggested_commit_message": "git message",
  "auto_fix_possible": true/false
}
```

### What Each Field Means

| Field | Meaning |
|-------|----------|
| **problem** | What went wrong |
| **root_cause** | Why it went wrong |
| **severity** | How serious (critical/high/medium/low) |
| **solution_steps** | Steps to fix it |
| **code_fix** | Actual code to apply |
| **file_to_modify** | Which file needs changing |
| **auto_fix_possible** | Can we auto-fix or need manual? |

---

## Dual-Model Mode (Advanced) 🤖

After adding QWEN_API_KEY to Secrets:

```
Workflow Fails
    ↓
Gemini 2.5 analyzes (50ms) ⚡
    ↓
Qwen 3 analyzes (2s) 🧠
    ↓
Compares results
    ↓
Chooses best solution
    ↓
Creates PR with BOTH analyses
```

See `.github/DUAL_MODEL_ANALYSIS.md` for setup!

---

## Success Criteria ✅

Auto-fix agent is working correctly if:

1. ✅ Workflow fails
2. ✅ Issue is created within 2 minutes
3. ✅ PR is created within 3 minutes  
4. ✅ PR has actual code changes
5. ✅ You can merge the PR
6. ✅ After merge, tests pass

---

## Still Not Working? 🣣

**Debug checklist:**

```bash
# 1. Check if auto-fix-agent.yml exists
ls -la .github/workflows/auto-fix-agent.yml

# 2. Check for syntax errors
grep -n "gemini-2.5-flash" .github/workflows/auto-fix-agent.yml

# 3. Verify secrets
gh secret list

# 4. Check Actions history
gh run list -w auto-fix-agent.yml

# 5. View latest run
gh run view <run-id>

# 6. Check GitHub API permissions
# (Settings → Actions → General → Workflow permissions)
```

---

## Next Steps

- ✅ Verify it works with test failure
- ✅ Check Issue and PR are created
- ✅ Merge the PR
- ✅ (Optional) Add Qwen for dual-model
- ✅ Let it run automatically on real failures!

---

**Status:** Auto-Fix Agent is ready to test! 🚀

**Estimated test time:** 5 minutes
