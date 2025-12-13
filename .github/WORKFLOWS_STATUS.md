# Workflow Status & Troubleshooting

**Last Updated:** 2025-12-13 16:55 MSK  
**Status:** ✅ All systems operational

---

## 📋 Installed Workflows

### ✅ Production Workflows

| Workflow | Purpose | Trigger | Status |
|----------|---------|---------|--------|
| **Run Tests** | Python tests with pytest | push/PR to main, feature-* | ✅ Active |
| **Auto-Fix Test Failures** | Gemini 2.5 Flash auto-fixing (10 attempts max) | Test failure | ✅ Active |
| **Notifications & Alerts** | Telegram alerts | Workflow completion | ✅ Active |
| **AI Code Review with Gemini 2.5** | PR code review | PR opened/sync | ✅ Active |
| **Code Quality & Linting** | pylint + format checks | push to main | ✅ Active |
| **Build Docker** | Docker image build | push to main | ✅ Active |
| **TODO to Issue** | Convert TODO comments | push to main/develop | ✅ Active (v6) |

### 🔧 Infrastructure Workflows

| Workflow | Purpose | Schedule |
|----------|---------|----------|
| **Artifact Cleanup** | Remove old artifacts | Weekly + manual |
| **Release Drafter** | Auto-generate changelog | PR merge |
| **Test Pipeline Mocks** | Validate pipeline workflow | Manual dispatch |

---

## 🔐 Required Secrets

### GitHub Settings → Secrets & Variables → Actions

```yaml
# CRITICAL - Tests won't run without these
GOOGLE_AI_API_KEY: "<your-gemini-api-key>"  # From console.cloud.google.com
GEMINI_API_KEY: "<your-gemini-api-key>"     # For auto-fix workflow
PIXABAY_API_KEY: "<your-pixabay-api-key>"   # For video generation

# NOTIFICATIONS (Optional but recommended)
TELEGRAM_BOT_TOKEN: "<your-bot-token>"      # From @BotFather
TELEGRAM_CHAT_ID: "<your-chat-id>"         # Your chat ID
```

**How to get API Keys:**
- **Gemini API**: https://aistudio.google.com/app/apikey
- **Pixabay API**: https://pixabay.com/api/docs/
- **Telegram Bot**: https://t.me/BotFather → /newbot

---

## 🤖 Auto-Fix Workflow Logic

### When Tests Fail:

```
❌ Test Failure
    ↓
📱 Telegram: "Auto-fix started..."
    ↓
🤖 Gemini 2.5 Flash × 10 Attempts:
    ├─ Analyze errors
    ├─ Generate fixes
    ├─ Apply to code
    └─ Re-run tests
    ↓
✅ Success? → Create PR
❌ Failure? → Create 🧊 FROZEN issue
```

### Labels Used:

- **🧊 frozen** - Manual intervention needed, don't auto-touch
- **🔴 manual-fix** - Requires human developer
- **✅ auto-fix** - Successfully auto-fixed
- **🤖 ai-generated** - Created by AI workflow
- **todo** - Auto-converted from TODO comments

---

## ✅ Known Issues & Fixes

### Issue: Tests fail with "missing import"

**Root Cause:** Mocking issues in conftest.py

**Fixed:** ✅ Added proper imports and Path checking

### Issue: Gemini API errors

**Root Cause:** Using deprecated model names (gemini-2.0-flash, gemini-2.0-flash-exp)

**Fixed:** ✅ Changed to **gemini-2.5-flash** only

**Allowed Models:**
- ✅ `gemini-2.5-flash` - Primary (recommended)
- ✅ `gemini-2.5-flash-lite` - Lightweight alternative

**Forbidden:**
- ❌ gemini-2.0-flash
- ❌ gemini-2.0-flash-exp
- ❌ gemini-1.5-flash (deprecated)

### Issue: Telegram notifications not working

**Fix:** Make sure secrets are set correctly in Settings → Secrets

### Issue: Auto-fix creates too many issues

**Solution:** Issues with 🧊 frozen label are skipped by CI - they won't auto-trigger fixes again

---

## 🚀 Testing Workflows Manually

### Run Tests Locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_tts_generator.py -v

# Run with coverage
pytest tests/ --cov=core --cov-report=html
```

### Trigger Workflow Manually:

1. Go to Actions tab
2. Select workflow
3. Click "Run workflow" → "Run workflow"

### Check Workflow Logs:

1. Actions tab → Select workflow run
2. Click job name → See logs
3. Download artifacts for analysis

---

## 📊 Workflow Statistics

### Typical Run Times:

- **Run Tests**: 5-8 minutes
- **Auto-Fix Loop**: 10-15 minutes (per attempt)
- **Code Review**: 2-3 minutes
- **Docker Build**: 5-10 minutes

### Artifact Retention:

- Test outputs: 3 days
- Coverage reports: 7 days
- Auto-fix analysis: 14 days
- Docker images: 30 days

---

## 🔍 Debugging Tips

### If tests keep failing:

1. Check `pytest-last.log` in artifacts
2. Look at last attempt's analysis in auto-fix artifacts
3. Check if 🧊 frozen issue was created
4. Run tests locally first before pushing

### If auto-fix never runs:

1. Verify `GEMINI_API_KEY` secret is set
2. Check workflow is enabled in Actions
3. Verify test failure triggered the workflow
4. Check workflow run logs for errors

### Common Test Failures:

```
❌ ImportError: No module named 'google.genai'
→ Fix: Verify mocking in conftest.py

❌ NameError: name 'model_router' is not defined  
→ Fix: Check sys.modules mock setup

❌ AssertionError: Lists are not equal
→ Fix: Check fixture data matches expectations
```

---

## 📝 Maintenance Checklist

- [ ] Check Telegram notifications are working
- [ ] Verify Gemini API key is active
- [ ] Review auto-fix artifacts weekly
- [ ] Clean up 🧊 frozen issues (resolve manually)
- [ ] Update deprecated models in workflows
- [ ] Monitor artifact storage (14 days retention)

---

## 🆘 Getting Help

If workflows are failing:

1. **Check the error message** in workflow logs
2. **Look for 🧊 frozen issues** - they contain analysis
3. **Review recent commits** - test changes?
4. **Run tests locally** - reproduce issue locally first
5. **Check secrets** - API keys still valid?

---

**Last Check:** All 11 workflows operational ✅  
**Next Review:** 2025-12-20
