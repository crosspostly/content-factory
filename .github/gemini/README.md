# 🤖 Gemini AI Code Review System

Welcome to the **AI Code Review** system for the `crosspostly/content-factory` repository!

This directory contains all configuration, prompts, and documentation for the automated code review workflow powered by **Gemini 2.5 Flash**.

---

## 📁 Directory Contents

### Configuration & Prompts

#### `code-review-prompt.md`
**System prompt for Gemini API**

- Defines the AI agent's role
- Specifies code review criteria
- Lists critical validation rules
- Provides output format specification
- Project-aware (understands content-factory)

**Used by:** Workflow when calling Gemini API

---

### Documentation

#### `AI-CODE-REVIEW-GUIDE.md` ⭐ **START HERE**
**Complete user guide for developers**

- How to use the workflow
- Setup instructions
- PR linking best practices
- Review criteria checklist
- Example outputs
- Troubleshooting guide
- Advanced usage examples

**Read this if:** You're a developer creating PRs

---

#### `IMPLEMENTATION_SUMMARY.md`
**Technical implementation details**

- What was built
- Workflow structure (9 steps)
- Configuration requirements
- Review criteria explained
- How to use (setup + usage)
- Example PR comments
- Before/after comparison

**Read this if:** You're implementing or maintaining the system

---

#### `DEPLOYMENT_CHECKLIST.md`
**Deployment and validation checklist**

- Pre-deployment verification
- Deployment steps
- Testing procedures
- Security verification
- Success metrics
- Troubleshooting by issue

**Read this if:** You're deploying or operating the system

---

## 🚀 Quick Start

### 1. Add API Key
Go to: **Settings → Secrets and variables → Actions**

Create a new repository secret:
```
Name: GOOGLE_AI_API_KEY
Value: <your-gemini-api-key>
```

### 2. Create a PR
- Create a new branch
- Make some code changes
- Push to GitHub

### 3. Link an Issue
In your PR description, add:
```markdown
Fixes #43
```

### 4. Watch the Magic! ✨
- Workflow runs automatically
- Gemini analyzes your code
- AI posts review comment
- Auto-commits improvements
- You review and merge

---

## 📋 How It Works

### Automatic Flow

```
1. PR Created
   ↓
2. Workflow Triggered
   ↓
3. Code Analyzed by Gemini
   ↓
4. Review Posted as Comment
   ↓
5. Changes Auto-Committed (if any)
   ↓
6. You Review & Approve
   ↓
7. Merge to Main
```

### What Gets Reviewed

✅ **Architecture Compliance**
- Does code follow project patterns?
- Is error handling proper?
- Are tests included?

✅ **Code Quality**
- Style and formatting
- Documentation
- Type hints

✅ **Critical Checks**
- ✅ ONLY Gemini 2.5-flash/lite allowed
- ❌ NEVER hardcoded API keys
- ❌ NEVER use old Gemini models

✅ **Best Practices**
- Logging instead of print()
- Configuration via config_loader
- Proper async/await handling

---

## 🎯 Key Features

### Automatic PR Review
- Runs on every PR (auto-trigger)
- Reviews code against issue requirements
- Checks quality and standards
- Provides actionable feedback

### Manual Trigger Support
- Review any PR via workflow_dispatch
- Compare any two branches
- On-demand code analysis

### Auto-Fix Capability
- Detects issues automatically
- Suggests improvements
- Auto-commits fixes (if any)
- All changes reviewable in PR

### Comprehensive Reporting
- Issues with severity levels
- Checklist status from issue
- Files modified by AI
- Recommendations for author

### Smart Issue Integration
- Extracts issue from PR description
- Validates against requirements
- Tracks checklist completion
- Provides progress summary

---

## 🔐 Security & Safety

### What It NEVER Does
- ❌ Merges PRs automatically
- ❌ Modifies main branch
- ❌ Exposes API keys in logs
- ❌ Breaks existing tests

### What It Always Does
- ✅ Only commits to PR branch
- ✅ Requires human approval to merge
- ✅ Shows all changes for review
- ✅ Respects branch protection rules

### AI Safety
- Suggestions are guidance only
- Human review still required
- No auto-merge (by design)
- All changes are git-tracked

---

## 📖 Documentation Map

```
.github/gemini/
├── README.md (you are here)
│
├── code-review-prompt.md
│   └── System prompt used by Gemini
│
├── AI-CODE-REVIEW-GUIDE.md ⭐ START HERE
│   └── Complete user guide
│
├── IMPLEMENTATION_SUMMARY.md
│   └── Technical details
│
└── DEPLOYMENT_CHECKLIST.md
    └── Deployment & testing guide
```

**Other related files:**
- `.github/workflows/ai-code-review.yml` - Main workflow file
- `README.md` (in root) - Project overview with workflow section

---

## 🤔 Common Questions

### Q: Does the AI Agent merge my PR?
**A:** No! It only reviews and auto-commits suggestions. You still must review and approve before merging.

### Q: What if I don't link an issue?
**A:** The workflow still runs, but won't validate against requirements. Best practice is to always link an issue.

### Q: How long does a review take?
**A:** Typically 2-5 minutes from PR creation to comment.

### Q: Can I run it manually?
**A:** Yes! Go to Actions → AI Code Review → Run workflow, enter PR number.

### Q: What if the API is down?
**A:** Workflow will fail with clear error. Check API status and try again.

### Q: Can I customize review criteria?
**A:** Yes! Edit `code-review-prompt.md` to change what gets reviewed.

---

## 🐛 Troubleshooting

### Workflow Won't Run
- Check if PR is on main/develop branch
- Verify GOOGLE_AI_API_KEY is set
- Check workflow logs in Actions tab

### No Comment Posted
- Check if PR has issue link (Fixes #NUMBER)
- Check workflow logs for errors
- Verify API key is valid

### Changes Not Auto-Committed
- Workflow may have found no issues
- Check if changes are actually needed
- Review workflow logs for details

### Large PR / Slow Review
- Large diffs are truncated (8000 chars)
- Break PR into smaller changes
- Wait for API response

**Full troubleshooting guide:** See [AI-CODE-REVIEW-GUIDE.md](./AI-CODE-REVIEW-GUIDE.md#troubleshooting)

---

## 📊 What Gets Checked

| Aspect | Checked | Example |
|--------|---------|---------|
| **Models** | ✅ | ONLY 2.5-flash/lite |
| **Architecture** | ✅ | Follows ARCHITECTURE.md |
| **Tests** | ✅ | Unit tests present |
| **Docs** | ✅ | Code documented |
| **Errors** | ✅ | Try/except proper |
| **Logging** | ✅ | Uses logging module |
| **Security** | ✅ | No hardcoded keys |
| **Style** | ✅ | PEP 8 compliance |

---

## 🚀 Getting Started Checklist

- [ ] Read [AI-CODE-REVIEW-GUIDE.md](./AI-CODE-REVIEW-GUIDE.md)
- [ ] Add GOOGLE_AI_API_KEY secret
- [ ] Create a test PR
- [ ] Link an issue in PR
- [ ] Watch workflow run
- [ ] Review AI comment
- [ ] Check auto-commits
- [ ] Approve and merge

---

## 📚 Related Documentation

- **[ARCHITECTURE.md](../../ARCHITECTURE.md)** - Project architecture
- **[README.md](../../README.md)** - Project overview
- **[GitHub Actions Docs](https://docs.github.com/en/actions)** - Actions reference
- **[Gemini API Docs](https://ai.google.dev/docs)** - Gemini API guide

---

## 🤝 Contributing

### Found a Bug?
Create a GitHub issue with:
- What happened
- What you expected
- Steps to reproduce
- Screenshot if applicable

### Have a Suggestion?
Create a GitHub discussion or issue with:
- Your idea
- Why it would help
- How to implement it

### Want to Improve?
1. Fork the repository
2. Create a feature branch
3. Make improvements
4. Create a PR with details

---

## 📞 Support

### For Developers
- Check [AI-CODE-REVIEW-GUIDE.md](./AI-CODE-REVIEW-GUIDE.md)
- Review troubleshooting section
- Check workflow logs in Actions

### For Maintainers
- See [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md)
- Check [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md)
- Review workflow file (.github/workflows/ai-code-review.yml)

### For Issues
- Workflow errors → Check Actions logs
- Code review feedback → Create GitHub issue
- Feature requests → Create GitHub discussion

---

## 📈 Version Information

- **Version:** 1.0
- **Last Updated:** December 2025
- **Status:** ✅ Production Ready
- **License:** MIT (same as project)

---

## 🎉 Summary

The **AI Code Review system** provides:

✅ Automatic code review on every PR  
✅ Smart issue requirement validation  
✅ Auto-commit of improvements  
✅ Comprehensive review comments  
✅ Manual trigger support  
✅ Full documentation  

**Start using it now!** → Read [AI-CODE-REVIEW-GUIDE.md](./AI-CODE-REVIEW-GUIDE.md)

---

**Questions?** Check the [troubleshooting guide](./AI-CODE-REVIEW-GUIDE.md#troubleshooting) or create an issue on GitHub.

**Ready to review your first PR?** 🚀 Just add your API key and open a PR!
