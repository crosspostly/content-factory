# ⚙️ AI Context for content-factory

## 🔴 CRITICAL: Model Configuration

### ✅ ONLY These Models Exist:
- `gemini-2.5-flash` (PRIMARY)
- `gemini-2.5-flash-lite` (FALLBACK)

### ❌ DO NOT USE (They Don't Exist):
- ❌ `gemini-2.0-flash-exp`
- ❌ `gemini-1.5-flash`
- ❌ `gemini-1.5-pro`
- ❌ `gemini-1.5-flash-001`
- ❌ `qwen2.5-coder`

**These will FAIL 100% of the time.**

---

## 📋 Config Locations

**Primary config:** `config/shared.yaml`
```yaml
generation:
  primary_model: gemini-2.5-flash
  fallback_models:
    - gemini-2.5-flash-lite
```

**Project configs inherit from:** `projects/*/config.yaml`

---

## 🔍 Validation Rules

Before committing changes to model configuration:

1. ✅ Confirm `primary_model: gemini-2.5-flash`
2. ✅ Confirm `fallback_models: [gemini-2.5-flash-lite]`
3. ✅ Search entire repo: `gemini-1.5` → should return 0 results
4. ✅ Search entire repo: `gemini-2.0` → should return 0 results
5. ✅ Search entire repo: `qwen` in generation config → should return 0 results

---

## 📝 For AI Agents (Copilot, Claude, etc.)

When handling issues/PRs about:
- **Model errors**: Check `config/shared.yaml` - likely wrong model name
- **Generation failures**: Verify models exist - 99% chance it's a model name issue
- **Config updates**: ONLY use `gemini-2.5-flash` and `gemini-2.5-flash-lite`
- **Adding fallback**: ONLY `gemini-2.5-flash-lite`, nothing else

---

## 🚀 Quick Reference

```bash
# Check current config
grep -r "primary_model\|fallback_models" config/

# Find all model references
grep -r "gemini" config/ --include="*.yaml"

# Search for forbidden models (should be empty)
grep -r "gemini-1.5\|gemini-2.0\|qwen" config/ --include="*.yaml"
```

---

**Last Updated:** 2025-12-13  
**Status:** ✅ CORRECT (gemini-2.5-flash only)
