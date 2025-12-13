# 🔐 Copilot Verification Checklist

> **Purpose:** Verify that Copilot debugging workflows are set up correctly and understand what to expect

---

## ✅ Part 1: Workflow Files Setup

### auto-fix-agent.yml
- [x] File exists at `.github/workflows/auto-fix-agent.yml`
- [x] Listens to: `tests.yml`, `part1-test.yml`, `tests-docker.yml`
- [x] Triggers on: `workflow_run` with `types: [completed]`
- [x] Condition: `if: failure` (only on workflow failures)
- [x] Permissions: `contents: write`, `issues: write`, `pull-requests: write`
- [x] **What it does:**
  ```
  🔍 Detects when tests fail
  📄 Fetches workflow logs
  💳 Creates GitHub Issue with:
     - Error summary
     - Error context (last 100 lines)
     - Workflow run link
     - Labels: auto-generated, ai-analyzed
  ```

### copilot-fix.yml
- [x] File exists at `.github/workflows/copilot-fix.yml`
- [x] Triggers on: `issues` with `types: [opened, edited]`
- [x] Also supports: `workflow_dispatch` for manual runs
- [x] Condition: Issue must have `auto-generated` label
- [x] Permissions: `contents: write`, `issues: write`, `pull-requests: write`
- [x] **What it does:**
  ```
  🚀 Analyzes the issue
  🛠 Determines fix type (Docker/Workflow/Tests/Imports)
  📋 Generates analysis document
  🔧 Creates branch: copilot-fix/issue-XXX
  💌 Creates Draft PR with:
     - Fix type identification
     - Analysis documentation
     - Review checklist
     - Labels: auto-fix, copilot, ai-generated
  ```

---

## ✅ Part 2: Labels & Automation

### Issue Labels Used

| Label | Created By | Purpose |
|-------|-----------|----------|
| `auto-generated` | auto-fix-agent.yml | Marks auto-created issue |
| `ai-analyzed` | auto-fix-agent.yml | Marks AI analysis done |
| `in-progress` | copilot-fix.yml | Issue being worked on |
| `has-fix` | copilot-fix.yml | Fix PR exists |
| `bug` | auto-fix-agent.yml | Issue category |

### PR Labels Used

| Label | Purpose |
|-------|----------|
| `auto-fix` | Auto-generated fix PR |
| `copilot` | Created by Copilot |
| `ai-generated` | AI-created content |
| `draft` | PR is draft (review before merge) |

---

## 🤖 Part 3: What Copilot Understands

### It KNOWS:

- [x] When tests fail (workflow status = failure)
- [x] What errors occurred (reads workflow logs)
- [x] What type of error it is (Docker/Python/YAML/etc)
- [x] Where to find error context (last N lines of output)
- [x] How to describe the problem (error message + context)
- [x] How to create GitHub issues (using `gh issue create`)
- [x] How to create branches (git checkout -b)
- [x] How to create PRs (using `gh pr create`)
- [x] How to add labels and comments (gh issue/pr commands)
- [x] How to update issue status (add/remove labels)

### It DOES:

- [x] Automatically trigger when workflow fails
- [x] Extract and parse error logs
- [x] Create issue with clear problem statement
- [x] Determine what type of fix is needed
- [x] Create appropriate branch for fix
- [x] Generate analysis documentation
- [x] Create draft PR with review checklist
- [x] Add helpful comments to issues
- [x] Label issues and PRs automatically
- [x] Update issue status as work progresses

### It DOES NOT:

- [ ] Automatically fix complex bugs (requires human review)
- [ ] Merge PRs without manual approval
- [ ] Push to main without PR
- [ ] Delete files or make destructive changes
- [ ] Make changes outside suggested fix context
- [ ] Deploy to production
- [ ] Modify test files permanently
- [ ] Change configuration without context

---

## 📋 Part 4: Verification Steps

### Step 1: Verify Workflows Exist

```bash
# Check if workflows are present
ls -la .github/workflows/ | grep -E "auto-fix|copilot-fix"

# Expected output:
# -rw-r--r-- auto-fix-agent.yml
# -rw-r--r-- copilot-fix.yml
```

### Step 2: Verify Workflow Syntax

```bash
# Validate YAML syntax
gh workflow view auto-fix-agent.yml
gh workflow view copilot-fix.yml

# Both should show as enabled
```

### Step 3: Test Trigger (Optional)

To manually trigger a test:

```bash
# Option A: Create a test branch and intentionally fail a test
git checkout -b test/verify-copilot-workflow
echo "BREAK_TEST = True" >> tests/test_main.py
git add .
git commit -m "test: trigger failure for verification"
git push origin test/verify-copilot-workflow

# Watch the workflow:
gh run list --workflow tests.yml --limit 1
gh run watch <RUN_ID>

# Wait for failure, then check if issue is created
gh issue list --label auto-generated
```

### Step 4: Monitor Auto-Issue Creation

```bash
# After workflow fails, check for new issue
gh issue list --label auto-generated --limit 5

# View the issue
gh issue view <ISSUE_NUMBER> --json title,body,labels

# Expected:
# - Title: 🔴 [workflow-name #run-number] Workflow failed
# - Body: Contains error logs and context
# - Labels: ["auto-generated", "ai-analyzed", "bug"]
```

### Step 5: Monitor Auto-PR Creation

```bash
# Check if PR was created
gh pr list --label auto-fix --limit 5

# View the PR
gh pr view <PR_NUMBER> --json title,body,labels

# Expected:
# - Title: [Copilot] Auto-fix for issue #XXX
# - Body: Contains fix type, checklist, analysis link
# - Labels: ["auto-fix", "copilot", "ai-generated"]
# - Status: DRAFT (should be draft, not ready to merge)
```

### Step 6: Verify GitHub CLI Access

```bash
# Make sure GH_TOKEN is set (in Actions context)
# In Actions, it uses: ${{ github.token }}

# Locally, verify:
gh auth status

# Should show: Logged in to github.com
```

---

## 📄 Part 5: Expected Behavior Timeline

### When Test Fails

```
T+0m00s: 🚨 Test starts failing
T+0m30s: 🔍 Failure detected by workflow
T+1m00s: 📄 Error logs extracted
T+1m30s: 💳 Issue #47 created with context
T+1m35s: 🚀 copilot-fix.yml triggered (auto)
T+2m00s: 🛠 Fix type analyzed
T+2m30s: 📋 Analysis document generated
T+3m00s: 💌 PR #48 created (DRAFT)
T+3m05s: 🤖 You get notified
T+3m10s: 👀 You review the changes
T+5m00s: ✅ (Option) You merge if fix is good
```

---

## 🔧 Part 6: Configuration Reference

### auto-fix-agent.yml Configuration

```yaml
on:
  workflow_run:
    workflows: ["tests.yml", "part1-test.yml", "tests-docker.yml"]
    types: [completed]  # Only on completion (success or failure)

jobs:
  analyze-and-fix:
    if: ${{ github.event.workflow_run.conclusion == 'failure' }}  # Only on failure
    runs-on: ubuntu-latest
    permissions:
      contents: write        # Can push
      actions: read          # Can read workflow runs
      issues: write          # Can create issues
      pull-requests: write   # Can create PRs
```

### copilot-fix.yml Configuration

```yaml
on:
  issues:
    types: [opened, edited]  # Trigger when issue created/edited
  workflow_dispatch:         # Allow manual trigger
    inputs:
      issue_number:
        description: 'Issue number to fix'
        required: true

jobs:
  copilot_fix:
    if: ${{ contains(github.event.issue.labels.*.name, 'auto-generated') }}
    # Only runs if issue has 'auto-generated' label
```

---

## 💌 Part 7: What Gets Created

### Issue Template (Auto-Generated)

```markdown
## Automated Failure Report

**Workflow:** [workflow-name](link-to-run)
**Run:** #123
**Branch:** `main`
**Commit:** `abc123...`
**Time:** 2025-12-13T10:15:00Z

### Error Summary
```
ModuleNotFoundError: No module named 'something'
```

### Error Context (Last 50 lines)
```
[50 lines of error output...]
```

### Next Steps
1. ✅ **Copilot is analyzing** this failure
2. An auto-fix PR will be created if possible
3. Manual review recommended before merge
```

### PR Template (Auto-Generated)

```markdown
## Copilot Auto-Fix PR

Automatically created fix for: #47

**Fix Type:** Test suite

### Changes Made
- Analyzed workflow/test failure
- Generated code fixes
- Added analysis documentation

### Review Checklist
- [ ] Review proposed changes
- [ ] Run tests locally
- [ ] Verify fix resolves issue
- [ ] Merge when ready

---
*Generated by Copilot Auto-Fix Agent 🤖*
```

---

## ✅ Part 8: Success Indicators

You'll know it's working when:

- [x] Test fails
- [x] Issue appears in Issues tab within 2 minutes
- [x] Issue has `auto-generated` label
- [x] Issue contains workflow run link
- [x] Issue shows error logs/context
- [x] PR appears in PRs tab within 3 minutes
- [x] PR has `auto-fix` label
- [x] PR is marked as DRAFT
- [x] PR links back to the issue
- [x] PR has review checklist

---

## 🛐️ Troubleshooting

### Issue Not Created

**Check:**
```bash
gh run list --workflow auto-fix-agent.yml
gh run view <RUN_ID> --log
```

**Common causes:**
- Workflow file has syntax error
- `tests.yml` didn't actually fail
- `gh` CLI auth issue
- Missing permissions

**Fix:**
```bash
# Validate workflow
gh workflow view auto-fix-agent.yml --json state

# Check permissions in repo settings
gh repo view --json name,permissions
```

### PR Not Created

**Check:**
```bash
gh run list --workflow copilot-fix.yml
gh run view <RUN_ID> --log
```

**Common causes:**
- Issue doesn't have `auto-generated` label
- Branch creation failed
- PR already exists for that branch

**Fix:**
```bash
# Check issue has label
gh issue view <ISSUE_NUMBER> --json labels

# Manually trigger workflow
gh workflow run copilot-fix.yml -f issue_number=<NUMBER>
```

---

## 🎯 Summary

🤖 **Copilot will help you with debugging by:**

1. 🔍 **Detecting failures** — Watches workflow runs
2. 📄 **Creating issues** — Documents the error
3. 🛠 **Analyzing problems** — Determines error type
4. 💌 **Creating PRs** — Proposes fixes
5. 👀 **Awaiting review** — You make the final call

✅ **Result:** Less manual debugging, faster fixes, better documentation

---

*Last Updated: 2025-12-13*  
*Maintainer: Copilot Auto-Fix System*
