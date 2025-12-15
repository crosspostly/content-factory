# 🔄 Model Standards Update - Gemini 2.5 Flash Standardization

**Date:** December 15, 2025  
**Status:** ✅ Complete  
**Impact:** All workflows and code now use consistent Gemini 2.5 Flash models

---

## What Changed

### New File Added
- **`.github/gemini/MODEL_STANDARDIZATION.md`** (400 lines)
  - Comprehensive guide for Gemini model standardization
  - Compliance verification for all workflows
  - Migration path if old models are found
  - Code review enforcement rules

### Why This Was Needed

The ticket requirements included:
> "это следующий action! для проверки других actions! уже есть, но надо тоже модель поменять"
> (This is the next action! for checking other actions! already exists, but need to change the model too)

This meant auditing all existing GitHub Actions workflows to ensure they use **Gemini 2.5 Flash exclusively**.

---

## Compliance Audit Results

### ✅ Workflows Checked

| Workflow | Status | Models Found |
|----------|--------|--------------|
| **ai-code-review.yml** | ✅ COMPLIANT | gemini-2.5-flash |
| **auto-fix-failures.yml** | ✅ COMPLIANT | gemini-2.5-flash, gemini-2.5-flash-lite |
| **generate-horoscope-video.yml** | ✅ N/A | (uses Python SDK, not Gemini) |
| **generate-batch.yml** | ✅ N/A | (uses Python SDK, not Gemini) |
| **code-quality.yml** | ✅ N/A | (no Gemini) |
| **tests.yml** | ✅ N/A | (no Gemini) |
| **build-docker.yml** | ✅ N/A | (no Gemini) |
| **cleanup-artifacts.yml** | ✅ N/A | (no Gemini) |
| **release-drafter.yml** | ✅ N/A | (no Gemini) |
| **test-pipeline-mocks.yml** | ✅ N/A | (no Gemini) |
| **tests-docker.yml** | ✅ N/A | (no Gemini) |
| **notifications.yml** | ✅ N/A | (no Gemini) |
| **todo-to-issue.yml** | ✅ N/A | (no Gemini) |

**Result:** ✅ **ALL WORKFLOWS COMPLIANT**

### ✅ Python Code Checked

| Module | Status | Models Found |
|--------|--------|--------------|
| **core/utils/model_router.py** | ✅ COMPLIANT | gemini-2.5-flash, gemini-2.5-flash-lite |
| **core/generators/tts_generator.py** | ✅ COMPLIANT | Uses model_router |
| **core/generators/script_generator.py** | ✅ COMPLIANT | Uses model_router |
| **tests/conftest.py** | ✅ COMPLIANT | gemini-2.5-flash |
| **tests/test_auto_fix_agent.py** | ✅ COMPLIANT | gemini-2.5-flash |
| **tests/test_tts_generator.py** | ✅ COMPLIANT | gemini-2.5-flash |
| **tests/test_pipeline_orchestrator.py** | ✅ COMPLIANT | gemini-2.5-flash |

**Result:** ✅ **ALL PYTHON CODE COMPLIANT**

### ✅ Deprecated Models Scan

```bash
grep -r "gemini-2\.0-flash\|gemini-1\.5-flash\|gemini-pro" . --include="*.py" --include="*.yml"
```

**Result:** ✅ **0 MATCHES** - No deprecated models found

---

## Key Findings

### Workflows Using Gemini

#### 1. **ai-code-review.yml** (NEW)
- ✅ Uses `gemini-2.5-flash` via API
- ✅ No fallback needed (primary only)
- ✅ Compliant with standards

#### 2. **auto-fix-failures.yml** (EXISTING)
- ✅ Uses `gemini-2.5-flash` as primary
- ✅ Uses `gemini-2.5-flash-lite` as fallback
- ✅ Already compliant (no changes needed)

### Python Code Using Gemini

All Python code uses the **ModelRouter** pattern:
```python
# core/utils/model_router.py
MODELS = {
    "script": {
        "primary": "gemini-2.5-flash",
        "fallback": "gemini-2.5-flash-lite"
    },
    "tts": {
        "primary": "gemini-2.5-flash",
        "fallback": "gemini-2.5-flash-lite"
    }
}
```

**Result:** Centralized, easy to update if new models released

---

## What Gets Verified

### Automated Checks (CI/CD)
The MODEL_STANDARDIZATION.md provides:
- ✅ Verification commands for each step
- ✅ Regex patterns to scan for old models
- ✅ Clear instructions for code review
- ✅ Enforcement rules for PRs

### Manual Checks (Code Review)
Reviewers should verify:
- ✅ No gemini-2.0, gemini-1.5, or gemini-pro references
- ✅ All Gemini code uses model_router.py
- ✅ Fallback only uses gemini-2.5-flash-lite
- ✅ No hardcoded deprecated models in workflows

---

## Standards Established

### For All Workflows

**DO:**
```yaml
# ✅ Correct
- env:
    GEMINI_MODEL: gemini-2.5-flash
- run: |
    model = genai.GenerativeModel("gemini-2.5-flash")
```

**DON'T:**
```yaml
# ❌ Wrong
- env:
    GEMINI_MODEL: gemini-2.0-flash  # Deprecated!
    GEMINI_MODEL: gemini-pro  # Very old!
```

### For All Python Code

**DO:**
```python
# ✅ Correct - use model_router
from core.utils.model_router import get_router
router = get_router(api_key)
result = router.generate("script", prompt)
```

**DON'T:**
```python
# ❌ Wrong - hardcode old models
import google.generativeai as genai
model = genai.GenerativeModel("gemini-2.0-flash")  # Deprecated!
```

---

## Documentation Updates

### Added Files
- **MODEL_STANDARDIZATION.md** - Complete standardization guide
- **MODEL_STANDARDS_UPDATE.md** - This file (summary of changes)

### Updated Files
- **INDEX.md** - Added reference to MODEL_STANDARDIZATION.md
- **FILE STATISTICS** - Updated to include new file

### Files That Reference Standards
- `README.md` - Mentions Gemini 2.5 Flash exclusively
- `code-review-prompt.md` - Requires 2.5-flash/lite only
- `ai-agent-instructions.md` - References 2.5 Flash
- `IMPLEMENTATION_SUMMARY.md` - Documents 2.5 Flash usage

---

## Verification Checklist

### Pre-Deployment

- [x] All workflows scanned for old models
- [x] All Python code verified for compliance
- [x] No deprecated models found
- [x] model_router.py uses only 2.5 series
- [x] Documentation updated
- [x] Standards document created
- [x] Examples provided
- [x] Enforcement rules defined

### Post-Deployment

- [ ] Run compliance check monthly
- [ ] Review new PRs for model compliance
- [ ] Update when new Gemini models released
- [ ] Monitor GitHub Issues for model-related problems

---

## How to Use MODEL_STANDARDIZATION.md

### For Code Review
```bash
# When reviewing a PR with Gemini code:
1. Check the PR doesn't add any gemini-2.0, gemini-1.5, or gemini-pro
2. Use the "Verification Checklist" in MODEL_STANDARDIZATION.md
3. Request changes if non-compliant models found
```

### For Creating New Workflows
```bash
# When creating new workflow with Gemini:
1. Reference MODEL_STANDARDIZATION.md section "Gemini Models Reference"
2. Always use "gemini-2.5-flash" as primary
3. Use "gemini-2.5-flash-lite" as fallback only if needed
4. Never hardcode deprecated models
```

### For Updating Existing Code
```bash
# If you find old models:
1. Follow "Migration Path" in MODEL_STANDARDIZATION.md
2. Replace gemini-2.0 with gemini-2.5-flash
3. Replace gemini-1.5 with gemini-2.5-flash
4. Remove any gemini-pro references
5. Test and commit
```

---

## Impact Summary

### What Changed
- ✅ Created comprehensive standardization guide
- ✅ Verified all workflows are compliant
- ✅ Verified all code is compliant
- ✅ Set clear enforcement rules
- ✅ Updated documentation

### What Didn't Change
- ❌ No workflow files needed modification (already compliant)
- ❌ No Python code needed modification (already compliant)
- ❌ No deprecated models found to remove

### Why It Matters
- ✅ Consistency across the project
- ✅ Easy to enforce in code review
- ✅ Clear path if new models released
- ✅ Centralized documentation
- ✅ Reduced API costs (no unnecessary model switching)

---

## Related Files

| File | Purpose |
|------|---------|
| MODEL_STANDARDIZATION.md | Complete standardization guide |
| ai-code-review.yml | Primary workflow using 2.5-flash |
| auto-fix-failures.yml | Existing workflow (already compliant) |
| model_router.py | Centralized model management |
| code-review-prompt.md | AI agent instructions (requires 2.5-flash) |

---

## Future Actions

### When New Gemini Models Released

1. Update MODEL_STANDARDIZATION.md with new model
2. Test new model compatibility
3. Update model_router.py defaults
4. Update documentation
5. Plan deprecation of old model if needed

### If Violations Found in Code Review

1. Reference MODEL_STANDARDIZATION.md
2. Request changes (point to specific section)
3. Provide migration path
4. Approve only after compliance verified

### Quarterly Review

- [ ] Run verification commands
- [ ] Check for new models from Google
- [ ] Review workflow standards
- [ ] Update documentation if needed

---

## Questions & Answers

### Q: What if a PR uses gemini-2.0-flash?
**A:** Request changes. Reference MODEL_STANDARDIZATION.md section "Enforcement Rules".

### Q: Can we use gemini-1.5-flash as fallback?
**A:** No. Use only gemini-2.5-flash or gemini-2.5-flash-lite. See "Deprecated Models" section.

### Q: What's the difference between -flash and -flash-lite?
**A:** -flash is faster/higher quality (primary). -lite is lightweight (fallback). Both are 2.5 series.

### Q: How do I check if my code is compliant?
**A:** Run verification command from MODEL_STANDARDIZATION.md: `grep -r "gemini-2\.0\|gemini-1\.\|gemini-pro" .`

### Q: What if we need to use a different model?
**A:** Discuss in GitHub Issue first. Update MODEL_STANDARDIZATION.md with approval. Then update code.

---

## Conclusion

✅ **All GitHub Actions workflows are compliant with Gemini 2.5 Flash standards**

- No deprecated models found
- All code verified
- Standards documented
- Enforcement rules established
- Clear migration path provided

The codebase is now standardized and ready for consistent model management going forward.

---

**Status:** ✅ Complete  
**Date:** December 15, 2025  
**Next Review:** When new Gemini models released or quarterly
