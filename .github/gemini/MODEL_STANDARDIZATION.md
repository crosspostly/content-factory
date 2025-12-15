# 🎯 Gemini Model Standardization Guide

**Version:** 1.0  
**Date:** December 2025  
**Status:** ✅ All Workflows Compliant

---

## Executive Summary

All GitHub Actions workflows and core code have been standardized to use **Gemini 2.5 Flash** exclusively.

**No deprecated models (2.0, 1.5, 1.0, gemini-pro) are present in the codebase.**

---

## ✅ Compliance Status

### Workflows

| Workflow | Primary Model | Fallback Model | Status |
|----------|---------------|----------------|--------|
| **ai-code-review.yml** | gemini-2.5-flash | N/A | ✅ Compliant |
| **auto-fix-failures.yml** | gemini-2.5-flash | gemini-2.5-flash-lite | ✅ Compliant |
| **generate-horoscope-video.yml** | (doesn't use Gemini) | N/A | ✅ N/A |
| **generate-batch.yml** | (doesn't use Gemini) | N/A | ✅ N/A |
| **code-quality.yml** | (doesn't use Gemini) | N/A | ✅ N/A |
| **tests.yml** | (doesn't use Gemini) | N/A | ✅ N/A |

### Python Core Code

| Module | Primary Model | Fallback Model | Status |
|--------|---------------|----------------|--------|
| **core/utils/model_router.py** | gemini-2.5-flash | gemini-2.5-flash-lite | ✅ Compliant |
| **core/generators/tts_generator.py** | gemini-2.5-flash | gemini-2.5-flash-lite | ✅ Compliant |
| **core/generators/script_generator.py** | gemini-2.5-flash | gemini-2.5-flash-lite | ✅ Compliant |

### Tests

| Test File | Model Reference | Status |
|-----------|-----------------|--------|
| **tests/conftest.py** | gemini-2.5-flash | ✅ Compliant |
| **tests/test_auto_fix_agent.py** | gemini-2.5-flash | ✅ Compliant |
| **tests/test_tts_generator.py** | gemini-2.5-flash | ✅ Compliant |
| **tests/test_pipeline_orchestrator.py** | gemini-2.5-flash | ✅ Compliant |

---

## 📋 Gemini Models Reference

### Currently Supported (Use These)

#### ✅ gemini-2.5-flash
- **Status:** Latest (December 2025)
- **Purpose:** Primary model for all tasks
- **Performance:** Fast, high quality
- **Use Cases:** Script generation, TTS, error analysis, code review
- **API:** Google GenerativeAI SDK

**Example:**
```python
import google.generativeai as genai

genai.configure(api_key="YOUR_KEY")
model = genai.GenerativeModel("gemini-2.5-flash")
response = model.generate_content("Your prompt here")
```

#### ✅ gemini-2.5-flash-lite
- **Status:** Latest (December 2025)
- **Purpose:** Fallback/lightweight alternative
- **Performance:** Faster, sufficient quality
- **Use Cases:** Fallback when 2.5-flash unavailable or rate-limited
- **API:** Google GenerativeAI SDK

**Example:**
```python
model = genai.GenerativeModel("gemini-2.5-flash-lite")
response = model.generate_content("Your prompt here")
```

### Deprecated (Never Use These)

#### ❌ gemini-2.0-flash
- **Status:** DEPRECATED - Do not use
- **Replacement:** Use gemini-2.5-flash
- **Why:** Older version, 2.5 is faster and better

#### ❌ gemini-1.5-flash
- **Status:** DEPRECATED - Do not use
- **Replacement:** Use gemini-2.5-flash
- **Why:** Old version, 2.5 is much better

#### ❌ gemini-pro
- **Status:** DEPRECATED - Do not use
- **Replacement:** Use gemini-2.5-flash
- **Why:** Very old API, completely outdated

#### ❌ gemini-1.0-pro
- **Status:** DEPRECATED - Do not use
- **Replacement:** Use gemini-2.5-flash
- **Why:** Very old, no longer supported

---

## 🔍 Verification Checklist

### For Workflow Files (.github/workflows/*.yml)

Use this checklist before merging any workflow changes:

```yaml
# ✅ Correct
- uses: google-github-actions/gemini-cli@v1  # or npm install @google/genai
- run: genai --model=gemini-2.5-flash ...
- env:
    GEMINI_MODEL: gemini-2.5-flash

# ❌ Wrong
- uses: google-github-actions/gemini-cli@v1
  with:
    model: gemini-2.0-flash  # ❌ OLD!
- env:
    GEMINI_MODEL: gemini-1.5-flash  # ❌ OLD!
- gemini-pro  # ❌ VERY OLD!
```

### For Python Code

Use this checklist before approving Python changes:

```python
# ✅ Correct
import google.generativeai as genai
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.5-flash")
response = model.generate_content(prompt)

# ❌ Wrong
genai.GenerativeModel("gemini-2.0-flash")  # ❌ OLD!
genai.GenerativeModel("gemini-1.5-flash")  # ❌ OLD!
genai.GenerativeModel("gemini-pro")  # ❌ VERY OLD!
```

---

## 📊 Model Standardization in Workflows

### ai-code-review.yml (New)

```yaml
name: AI Code Review with Gemini CLI

env:
  GEMINI_API_KEY: ${{ secrets.GOOGLE_AI_API_KEY }}
  GEMINI_MODEL: gemini-2.5-flash  # ✅ Latest

steps:
  - name: Run Gemini CLI review
    run: |
      # Uses gemini-2.5-flash via API
      curl -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
```

**Status:** ✅ **COMPLIANT**

---

### auto-fix-failures.yml (Existing)

```yaml
name: Auto-Fix Test Failures

env:
  GEMINI_API_KEY: ${{ secrets.GOOGLE_AI_API_KEY }}

steps:
  - name: Auto-Fix Loop
    run: |
      python3 << 'EOF'
      import google.generativeai as genai
      
      ALLOWED_MODELS = ['gemini-2.5-flash', 'gemini-2.5-flash-lite']
      CURRENT_MODEL = 'gemini-2.5-flash'  # ✅ Latest
      
      model = genai.GenerativeModel(CURRENT_MODEL)
      response = model.generate_content(prompt)
      EOF
```

**Status:** ✅ **COMPLIANT**

---

## 🛡️ Enforcement Rules

### When Creating New Workflows

**RULE 1: Always use gemini-2.5-flash as primary**
```yaml
env:
  GEMINI_MODEL: gemini-2.5-flash  # ✅ Required
```

**RULE 2: Use gemini-2.5-flash-lite as fallback only**
```yaml
FALLBACK_MODEL: gemini-2.5-flash-lite  # ✅ If needed
```

**RULE 3: Never hardcode old models**
```yaml
# ❌ FORBIDDEN
- run: genai --model=gemini-2.0-flash
- run: genai --model=gemini-1.5-flash
- run: genai --model=gemini-pro
```

### When Reviewing Code

**CHECK 1: Scan for deprecated models**
```bash
grep -r "gemini-2\.0\|gemini-1\.\|gemini-pro" .github/workflows/
```
✅ Should return **0 results**

**CHECK 2: Verify model_router.py**
```bash
grep "MODELS = " core/utils/model_router.py
```
✅ Should show only `gemini-2.5-flash` and `gemini-2.5-flash-lite`

**CHECK 3: Check new code uses SDK correctly**
```python
# ✅ Correct usage
model = genai.GenerativeModel("gemini-2.5-flash")

# ❌ Wrong - hardcoded model
model = genai.GenerativeModel("gemini-2.0-flash")
```

---

## 🚀 Migration Path (If Needed)

If you find old models in the codebase:

### Step 1: Identify
```bash
grep -r "gemini-2\.0-flash\|gemini-1\.5\|gemini-pro" . --include="*.yml" --include="*.py"
```

### Step 2: Replace

**In workflow files:**
```yaml
# Before
GEMINI_MODEL: gemini-2.0-flash

# After
GEMINI_MODEL: gemini-2.5-flash
```

**In Python code:**
```python
# Before
model = genai.GenerativeModel("gemini-1.5-flash")

# After
model = genai.GenerativeModel("gemini-2.5-flash")
```

### Step 3: Test

```bash
# Verify no old models remain
grep -r "gemini-2\.0\|gemini-1\.\|gemini-pro" . --include="*.yml" --include="*.py"
# Should return: (empty)

# Run tests
pytest tests/
```

### Step 4: Commit

```bash
git add -A
git commit -m "chore: standardize to Gemini 2.5 Flash models

- Update all workflows to use gemini-2.5-flash
- Update model_router.py to use 2.5 series only
- Remove deprecated gemini-2.0 and gemini-1.5 references
- Verified: no old models remain in codebase"
```

---

## 📚 Documentation Updates

All documentation files reference **Gemini 2.5 Flash**:

| File | Status |
|------|--------|
| README.md | ✅ References only 2.5-flash |
| .github/gemini/code-review-prompt.md | ✅ Requires 2.5-flash/lite only |
| .github/gemini/ai-agent-instructions.md | ✅ Mentions 2.5 Flash |
| .github/gemini/IMPLEMENTATION_SUMMARY.md | ✅ Documents 2.5 Flash |
| ARCHITECTURE.md | ✅ References Gemini 2.5 |
| core/utils/model_router.py | ✅ Only 2.5 series |

---

## 🔗 Related Standards

### API Key Management
- Store in `GOOGLE_AI_API_KEY` secret
- Support legacy `GEMINI_API_KEY` for backward compatibility
- **Never** hardcode keys
- **Never** commit keys to git

### Rate Limiting
- Free tier: 15 requests per minute (RPM)
- Upgrade if needed via Google Cloud Console
- Implement exponential backoff for retries
- Use gemini-2.5-flash-lite if rate-limited on 2.5-flash

### Error Handling
- Catch API errors gracefully
- Log errors with context
- Retry with exponential backoff
- Fall back to -lite variant if available

---

## ✨ Benefits of Standardization

### For Developers
✅ Consistent across all workflows  
✅ Single source of truth (model_router.py)  
✅ Easier to maintain and update  
✅ Clear deprecation path  

### For Operations
✅ Predictable API costs  
✅ Easier to troubleshoot issues  
✅ Simplified documentation  
✅ Clear audit trail  

### For Security
✅ No exposure of old/deprecated APIs  
✅ Aligned with Google's recommendations  
✅ Better error handling  
✅ Clearer authorization scope  

---

## 📞 Questions & Support

### Q: Can I use gemini-2.0-flash?
**A:** No. It's deprecated. Use gemini-2.5-flash instead.

### Q: What if gemini-2.5-flash is rate-limited?
**A:** Use gemini-2.5-flash-lite as fallback. Both are 2.5 series.

### Q: What about gemini-pro?
**A:** Never use. It's very old. Always use gemini-2.5-flash.

### Q: How do I check my code?
**A:** Run:
```bash
grep -r "gemini-2\.0\|gemini-1\.\|gemini-pro" . --include="*.py" --include="*.yml"
```

### Q: Can I add new workflow with old model?
**A:** No. PR will be rejected in code review. Use 2.5-flash only.

---

## 🎯 Enforcement

### In Code Review
- ❌ Reject PRs with gemini-2.0 or older
- ❌ Reject PRs with gemini-pro
- ✅ Approve PRs using gemini-2.5-flash
- ✅ Approve PRs using gemini-2.5-flash-lite as fallback

### In CI/CD
- Workflow validates model names
- Python tests check model strings
- Linting catches obvious mistakes

### In Documentation
- README mentions 2.5 Flash only
- Code comments note the standardization
- Examples use correct models

---

## 📋 Verification Commands

```bash
# Check for old models (should return empty)
grep -r "gemini-2\.0-flash\|gemini-1\.5-flash\|gemini-pro" . --include="*.py" --include="*.yml"

# Check for 2.5 models (should return many matches)
grep -r "gemini-2\.5-flash" . --include="*.py" --include="*.yml"

# Count models by version
grep -r "gemini-" . --include="*.py" --include="*.yml" | grep -o "gemini-[^\"' ]*" | sort | uniq -c
```

---

**Last Updated:** December 2025  
**Status:** ✅ All Compliant  
**Next Review:** When new Gemini models released (2.6+)
