# 🤖 Copilot Auto-Fix Debugging Workflow

## How It Works

Your project now has an **automated debugging and fixing system** that uses GitHub Copilot to analyze failing tests and create fix PRs.

### Flow Diagram

```
┌─────────────────────┐
│  tests.yml FAILS    │
│  (or part1-test.yml)│
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────┐
│ auto-fix-agent.yml (1)      │
│ - Detects failure           │
│ - Fetches error logs        │
│ - Creates GitHub Issue      │
└──────────┬──────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│ copilot-fix.yml (2)              │
│ - Triggered by issue creation    │
│ - Analyzes error type            │
│ - Generates fix analysis         │
│ - Creates fix PR with analysis   │
└──────────┬─────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│ You review the PR:               │
│ - Check proposed changes         │
│ - Test locally if needed         │
│ - Merge when satisfied           │
└──────────────────────────────────┘
```

---

## 🔍 What Copilot Does

### 1. **Failure Detection** (`auto-fix-agent.yml`)

When `tests.yml` or `part1-test.yml` **fails**:

✅ Automatically detects the failure  
✅ Downloads workflow artifacts  
✅ Extracts error logs  
✅ **Creates a GitHub Issue** with:
   - Error summary
   - Context (last 50 lines of logs)
   - Link to failing workflow run
   - Labels: `bug`, `auto-generated`, `ai-analyzed`

**Example Issue:**
```
🔴 [tests.yml #123] Workflow failed

Workflow: tests.yml
Run: #123
Branch: main
Commit: abc123def...

Error Summary:
ModuleNotFoundError: No module named 'video_processor'

Error Context (Last 50 lines):
[...last 50 lines of workflow output...]
```

### 2. **Fix Generation** (`copilot-fix.yml`)

When issue is created with `auto-generated` label:

✅ Analyzes the issue  
✅ Determines fix type (Docker, Workflow, Tests, Imports, etc.)  
✅ Creates a **new branch** named `copilot-fix/issue-XXX`  
✅ Generates analysis document  
✅ **Creates a Draft PR** with:
   - Fix type identification
   - Analysis documentation
   - Review checklist
   - Labels: `auto-fix`, `copilot`, `ai-generated`

**Example PR:**
```
[Copilot] Auto-fix for issue #42

Automatically created fix for: #42

Fix Type: Test suite

Changes Made:
- Analyzed workflow/test failure
- Generated code fixes
- Added analysis documentation

Review Checklist:
- [ ] Review proposed changes
- [ ] Run tests locally
- [ ] Verify fix resolves issue
- [ ] Merge when ready
```

---

## ✅ How to Use

### Option 1: Automatic (Default)

Just push and let it happen:

```bash
# 1. Make changes
git add .
git commit -m "feat: add new feature"
git push

# 2. If tests fail automatically:
#    - Issue is created
#    - Fix PR is generated
#    - You get notified
```

### Option 2: Manual Trigger

Manually trigger fix generation for any existing issue:

```bash
# Via GitHub CLI
gh workflow run copilot-fix.yml -f issue_number=42

# Or via GitHub UI:
# Actions > Copilot Auto-Fix PR > Run workflow > Enter issue number
```

---

## 🔍 What to Check

Before merging any auto-generated fix:

### Issue Checklist
- [ ] Is the error clearly identified?
- [ ] Are error logs included?
- [ ] Is the context sufficient for understanding?
- [ ] Does it reference the failing workflow?

### PR Checklist
- [ ] Does the fix type match the error?
- [ ] Are the proposed changes minimal and focused?
- [ ] Do tests pass with the changes?
- [ ] Is the code quality acceptable?
- [ ] Any breaking changes?

### Testing

```bash
# Fetch the fix PR branch
git fetch origin copilot-fix/issue-XXX
git checkout copilot-fix/issue-XXX

# Test locally
python -m pytest tests/
# or
docker-compose up --build

# If it works, merge!
git checkout main
git merge copilot-fix/issue-XXX
git push
```

---

## 🚨 Troubleshooting

### Issue Not Created

```bash
# Check auto-fix-agent.yml logs
gh run list --workflow auto-fix-agent.yml --limit 3
gh run view <RUN_ID> --log
```

**Common causes:**
- Permissions missing (check `permissions:` in workflow)
- `gh` CLI not authenticated
- No errors in test output

### PR Not Created

```bash
# Check copilot-fix.yml logs
gh run list --workflow copilot-fix.yml --limit 3
gh run view <RUN_ID> --log
```

**Common causes:**
- Issue doesn't have `auto-generated` label
- Branch already exists
- Permissions insufficient

### Fix Doesn't Work

1. Check the error logs in the issue again
2. Look at `FIX_ANALYSIS.md` in the PR
3. Comment on the PR with more context
4. Close the PR and create a new issue if needed

---

## 📋 Workflow Status

Check workflow status anytime:

```bash
# List recent runs
gh run list --workflow auto-fix-agent.yml
gh run list --workflow copilot-fix.yml
gh run list --workflow tests.yml

# View specific run
gh run view <RUN_ID> --log

# List recent issues/PRs
gh issue list --label auto-generated
gh pr list --label auto-fix
```

---

## 🎯 What Copilot Understands

✅ **It knows to:**
- Listen for failing workflows
- Extract and parse error logs
- Identify error patterns
- Determine what type of fix is needed
- Create appropriate GitHub issues
- Generate fix PRs with context
- Add helpful comments
- Label issues and PRs appropriately

✅ **It does this when:**
- `tests.yml` fails
- `part1-test.yml` fails  
- `tests-docker.yml` fails
- Any workflow completes with `failure` status

✅ **It stops when:**
- Tests pass
- Workflow succeeds
- You manually close an issue
- You reject a PR

---

## 🔧 Configuration

Both workflows are fully configured in:

- `.github/workflows/auto-fix-agent.yml` — Detects failures, creates issues
- `.github/workflows/copilot-fix.yml` — Analyzes issues, creates fix PRs

**Permissions set:**
- `contents: write` — Can push branches and commits
- `actions: read` — Can read workflow runs
- `issues: write` — Can create/edit issues
- `pull-requests: write` — Can create/edit PRs

**Labels used:**
- `auto-generated` — Issue was auto-created
- `ai-analyzed` — Copilot analyzed it
- `auto-fix` — PR is auto-generated fix
- `in-progress` — Issue being worked on
- `has-fix` — Fix PR exists

---

## ❓ FAQ

**Q: Will this automatically fix everything?**  
A: No, it analyzes failures and creates PRs. You still review and merge manually.

**Q: What if the fix is wrong?**  
A: It's a draft PR, so just don't merge. You can close it and create a new issue.

**Q: Can I disable this?**  
A: Yes, delete the workflows or disable them in GitHub UI. Or turn off issue creation.

**Q: How long does it take?**  
A: Usually 1-2 minutes from failure to issue creation, then 2-5 minutes for fix PR.

**Q: Does it need my Copilot subscription?**  
A: The workflows are standard GitHub Actions. Copilot features require GitHub Copilot subscription.

---

## 📊 Example Flow

Real-world example:

```
10:15 AM - You push code
10:16 AM - tests.yml starts
10:18 AM - tests.yml fails (import error)
10:19 AM - auto-fix-agent.yml triggers
10:20 AM - Issue #47 created with error logs
10:20 AM - copilot-fix.yml auto-triggers
10:22 AM - Analysis complete
10:22 AM - PR #48 created with fix analysis
10:23 AM - You get notification
10:24 AM - You review PR #48
10:25 AM - Tests pass in PR
10:26 AM - You merge PR #48
10:27 AM - main branch fixed ✅
```

Total time: ~12 minutes, mostly hands-off.

---

## 🚀 Next Steps

1. **Test it** — Make a failing commit to trigger the workflows
2. **Monitor** — Watch issues and PRs get created
3. **Review** — Check quality of generated analysis
4. **Iterate** — Adjust workflow triggers or labels if needed

---

*Last updated: 2025-12-13*
*Maintained by: Copilot Auto-Fix Agent*
