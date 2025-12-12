# Auto-Fix Agent Test Suite Documentation

## Overview

The Auto-Fix Agent Test Suite provides comprehensive testing for the AI-powered system that automatically detects, analyzes, and fixes GitHub Actions workflow failures using Qwen (local) and Gemini (fallback) models.

**Test Files:**
- `tests/test_auto_fix_agent.py` - Core auto-fix agent functionality (34 unit tests)
- `tests/test_model_router_autofix.py` - Advanced model routing scenarios (14 unit tests)
- `tests/fixtures/error_logs/` - Real-world error log examples (6 fixtures)

**Status:** ✅ All 48 unit tests pass | 2 slow integration tests (optional)

## Quick Start

### Run All Auto-Fix Tests (Fast - No API Calls)
```bash
pytest tests/test_auto_fix_agent.py tests/test_model_router_autofix.py -v -m "not slow"
```

Expected output: `48 passed, 2 deselected` in ~4 seconds

### Run Specific Test Class
```bash
pytest tests/test_auto_fix_agent.py::TestQwenPrimaryModelFlow -v
pytest tests/test_model_router_autofix.py::TestModelFallbackSequence -v
```

### Run with Coverage
```bash
pytest tests/test_auto_fix_agent.py tests/test_model_router_autofix.py \
  --cov=core.utils.model_router \
  --cov-report=html
```

## Test Categories

### 1. Model Detection Tests (4 tests)

Tests that verify correct provider detection for various model identifiers.

```python
# In: TestModelDetection
test_detect_gemini_model()                    # ✅ Gemini models → gemini provider
test_detect_ollama_model_with_colon()         # ✅ Ollama models → ollama provider
test_detect_openrouter_qwen_model()           # ✅ Qwen models → openrouter provider
test_model_detection_case_insensitive()       # ✅ Case-insensitive detection
```

**Provider Mapping:**
```
Model Name                Provider
─────────────────────────────────────
gemini-2.5-flash         →  gemini
gemini-2.5-flash-lite    →  gemini
qwen-large               →  openrouter
qwen2.5-coder:1.5b       →  openrouter (detected as qwen first)
mistral:latest           →  ollama (has colon)
llama2:13b               →  ollama (has colon)
```

### 2. Error Log Analysis Tests (5 tests)

Tests that verify correct identification of different error types in GitHub Actions logs.

```python
# In: TestErrorLogAnalysis
test_missing_dependency_error_identification()         # ✅ ModuleNotFoundError
test_syntax_error_identification()                     # ✅ SyntaxError
test_file_not_found_error_identification()             # ✅ FileNotFoundError
test_api_rate_limit_error_identification()             # ✅ 429 Rate Limited
test_import_error_identification()                     # ✅ ImportError
```

**Error Log Fixtures:**
Located in `tests/fixtures/error_logs/`:
- `missing_dependency.log` - Missing Python package error
- `syntax_error.log` - Invalid Python syntax
- `file_not_found.log` - Missing required file
- `api_rate_limit.log` - API 429 error
- `import_error.log` - Module import failure
- `assertion_error.log` - Test assertion failure

### 3. Primary Model Flow Tests (2 tests)

Tests for Qwen (OpenRouter) as primary model with Gemini as fallback.

```python
# In: TestQwenPrimaryModelFlow
test_qwen_success()                           # ✅ Qwen analysis succeeds
test_qwen_fails_fallback_to_gemini()          # ✅ Qwen fails → Gemini succeeds
```

### 4. Fallback Flow Tests (4 tests)

Tests for Gemini as fallback when primary model unavailable.

```python
# In: TestGeminiFallback
test_gemini_analysis_missing_dependency()     # ✅ Analyzes missing dependency
test_gemini_analysis_syntax_error()           # ✅ Analyzes syntax error

# In: TestModelFallbackSequence
test_qwen_primary_gemini_fallback()           # ✅ Fallback chain works
test_qwen_success_no_gemini_call()            # ✅ No fallback if primary succeeds
```

### 5. Analysis JSON Structure Tests (2 tests)

Tests that verify response JSON structure and fields.

```python
# In: TestAutoFixAnalysisJson
test_analysis_json_structure()                # ✅ Valid JSON with all required fields
test_analysis_manual_fix_required()           # ✅ Handles non-auto-fixable errors
```

**Expected JSON Structure:**
```json
{
  "problem": "Brief description of the error",
  "root_cause": "Why it happened",
  "severity": "critical|high|medium|low",
  "solution_steps": ["Step 1", "Step 2"],
  "code_fix": "Code to apply (if auto-fixable)",
  "file_to_modify": "path/to/file or null",
  "suggested_commit_message": "git commit message",
  "technical_task": "Detailed technical description",
  "auto_fix_possible": true|false
}
```

### 6. Rate Limit Handling Tests (2 tests)

Tests for retry logic with exponential backoff.

```python
# In: TestRateLimitHandling
test_rate_limit_retry()                      # ✅ Retries on 429 with backoff
test_auth_error_skips_retry()                # ✅ No retry on 401 auth error
```

**Retry Strategy:**
- Max retries: 2 (configurable)
- 429 Rate Limit: Retries with exponential backoff (2s, 4s)
- 401 Auth Error: Breaks immediately, tries next model
- Other errors: Retries with exponential backoff

### 7. GitHub Issue Creation Tests (3 tests)

Tests for Issue title and body formatting.

```python
# In: TestIssueCreationData
test_issue_title_format_critical()            # ✅ Title format for CRITICAL
test_issue_title_format_high()                # ✅ Title format for HIGH
test_issue_body_format()                      # ✅ Issue body structure
```

**Issue Title Format:**
```
🔴 [CRITICAL] Database connection failed
🔴 [HIGH] ModuleNotFoundError: No module named 'google.generativeai'
🔴 [MEDIUM] API rate limit exceeded
```

**Issue Body Sections:**
- 🚨 Failure Analysis
- Problem description
- Root cause analysis
- Severity level
- Solution steps
- Technical task
- Auto-fix status

### 8. Pull Request Creation Tests (2 tests)

Tests for PR title and body formatting.

```python
# In: TestPRCreationData
test_pr_title_format()                       # ✅ PR title format
test_pr_body_format()                        # ✅ PR body structure
```

**PR Title Format:**
```
🔧 Auto-Fix: Add missing google-generativeai dependency
🔧 Auto-Fix: Fix syntax error in broken_test.py
```

### 9. Error Severity Classification Tests (4 tests)

Tests for proper error severity classification.

```python
# In: TestErrorSeverityClassification
test_severity_critical()                     # ✅ CRITICAL level
test_severity_high()                         # ✅ HIGH level
test_severity_medium()                       # ✅ MEDIUM level
test_severity_low()                          # ✅ LOW level
```

**Severity Levels:**
| Level | Examples |
|-------|----------|
| CRITICAL | Database connection lost, Core functionality broken |
| HIGH | Missing dependency, Syntax error |
| MEDIUM | API rate limit, Deprecation warnings |
| LOW | Minor warnings, Non-critical issues |

### 10. Multiple Error Type Tests (3 tests)

Tests for handling various Python error types.

```python
# In: TestMultipleErrorTypes
test_type_error_analysis()                   # ✅ TypeError handling
test_attribute_error_analysis()              # ✅ AttributeError handling
test_value_error_analysis()                  # ✅ ValueError handling
```

### 11. Ollama Provider Tests (1 test)

Tests for Ollama provider model detection.

```python
# In: TestOllamaProvider
test_ollama_model_detection()                # ✅ Colon-based model detection
```

### 12. Gemini Provider Tests (1 test)

Tests for Gemini provider model detection.

```python
# In: TestGeminiProvider
test_gemini_model_detection()                # ✅ Gemini model variants
```

### 13. OpenRouter Provider Tests (1 test)

Tests for OpenRouter provider (Qwen fallback).

```python
# In: TestOpenRouterProvider
test_openrouter_qwen_detection()             # ✅ Qwen model detection
```

### 14. Retry Logic Tests (3 tests)

Tests for retry behavior and exponential backoff.

```python
# In: TestRetryLogicWithAutoFix
test_retry_on_rate_limit()                   # ✅ Retries with sleep
test_no_retry_on_auth_error()                # ✅ Auth error breaks chain
test_max_retries_respected()                 # ✅ Respects config max_retries
```

### 15. Analysis Prompt Tests (2 tests)

Tests for LLM prompt construction.

```python
# In: TestAutoFixAnalysisPrompts
test_analysis_prompt_structure()             # ✅ Prompt includes all sections
test_analysis_prompt_includes_workflow_context()  # ✅ Workflow context included
```

### 16. Error Analysis Accuracy Tests (3 tests)

Tests for accuracy of error analysis.

```python
# In: TestErrorAnalysisAccuracy
test_identifies_missing_dependency_correctly()    # ✅ Dependency detection
test_identifies_syntax_error_correctly()          # ✅ Syntax error detection
test_identifies_file_not_found_correctly()        # ✅ File not found detection
```

### 17. Model Configuration Tests (6 tests)

Tests for default model configuration.

```python
# In: TestModelConfigurationDefaults
test_config_primary_model()                  # ✅ Primary model from config
test_config_fallback_models()                # ✅ Fallback models list
test_config_temperature()                    # ✅ Temperature parameter
test_config_max_retries()                    # ✅ Max retries count
test_qwen_config_primary_model()             # ✅ Qwen as primary
test_qwen_config_fallback_models()           # ✅ Qwen config fallbacks
```

### 18. Integration Tests (2 tests - Slow)

Tests that make real API calls (optional, slow).

```python
# In: TestAutoFixAgentIntegration (marked with @pytest.mark.slow)
test_qwen_integration_missing_dependency()   # ⏸️ Requires Ollama
test_gemini_integration_syntax_error()       # ⏸️ Requires Gemini API key
```

Run with: `pytest -v -m slow`

## Test Fixtures

### `mock_config`
Standard Gemini-based configuration for testing.

```python
{
    "generation": {
        "primary_model": "gemini-2.5-flash",
        "fallback_models": ["gemini-2.5-flash-lite"],
        "temperature": 0.7,
        "max_retries": 2
    }
}
```

### `mock_config_with_qwen`
Qwen-based configuration with Gemini fallback.

```python
{
    "generation": {
        "primary_model": "qwen2.5-coder:1.5b",
        "fallback_models": ["gemini-2.5-flash"],
        "temperature": 0.7,
        "max_retries": 2,
        "retry_delay_sec": 1.0
    }
}
```

### `error_log_fixtures`
Dictionary containing all error log fixtures.

```python
{
    "missing_dependency": "...",
    "syntax_error": "...",
    "file_not_found": "...",
    "api_rate_limit": "...",
    "import_error": "...",
    "assertion_error": "..."
}
```

## Test Execution Examples

### Run All Auto-Fix Tests
```bash
$ pytest tests/test_auto_fix_agent.py tests/test_model_router_autofix.py -v

========== test session starts ===========
collected 50 items

tests/test_auto_fix_agent.py::TestModelDetection::test_detect_gemini_model PASSED [ 2%]
...
===================== 48 passed, 2 deselected in 4.23s =======================
```

### Run Specific Test Category
```bash
$ pytest tests/test_auto_fix_agent.py::TestErrorLogAnalysis -v

========== test session starts ===========
collected 5 items

tests/test_auto_fix_agent.py::TestErrorLogAnalysis::test_missing_dependency_error_identification PASSED [ 20%]
tests/test_auto_fix_agent.py::TestErrorLogAnalysis::test_syntax_error_identification PASSED [ 40%]
tests/test_auto_fix_agent.py::TestErrorLogAnalysis::test_file_not_found_error_identification PASSED [ 60%]
tests/test_auto_fix_agent.py::TestErrorLogAnalysis::test_api_rate_limit_error_identification PASSED [ 80%]
tests/test_auto_fix_agent.py::TestErrorLogAnalysis::test_import_error_identification PASSED [100%]

===================== 5 passed in 0.15s =======================
```

### Run with Verbose Output
```bash
$ pytest tests/test_auto_fix_agent.py::TestGeminiFallback::test_gemini_analysis_missing_dependency -vv

tests/test_auto_fix_agent.py::TestGeminiFallback::test_gemini_analysis_missing_dependency
Module: core.utils.model_router
Config: gemini-2.5-flash (primary)
Response: JSON with {"problem": "ModuleNotFoundError...", ...}
Result: ✅ PASSED
```

## Coverage Report

To generate a coverage report:

```bash
pytest tests/test_auto_fix_agent.py tests/test_model_router_autofix.py \
  --cov=core.utils.model_router \
  --cov-report=html

# Open htmlcov/index.html in browser
```

**Target Coverage:** ≥ 90% for:
- `core/utils/model_router.py`
- Auto-fix analysis logic
- Error detection and classification

## Test Isolation

All tests are:
- **Independent**: Can run in any order
- **Isolated**: Use mocks for external dependencies
- **Deterministic**: No random failures
- **Fast**: Complete in < 5 seconds

## CI/CD Integration

These tests run automatically in:
- `.github/workflows/tests.yml` - On every push
- `.github/workflows/auto-fix-agent.yml` - When workflows fail

## Debugging Failed Tests

### Enable Debug Logging
```bash
pytest tests/test_auto_fix_agent.py -vv --log-cli-level=DEBUG
```

### Run Single Test with Output
```bash
pytest tests/test_auto_fix_agent.py::TestQwenPrimaryModelFlow::test_qwen_success -vv -s
```

### Show Full Traceback
```bash
pytest tests/test_auto_fix_agent.py --tb=long
```

## Future Test Enhancements

- [ ] Add tests for complex multi-file fixes
- [ ] Add tests for configuration error detection
- [ ] Add performance regression tests
- [ ] Add tests for concurrent analysis requests
- [ ] Add tests for very large error logs (>100MB)
- [ ] Add tests for non-English error messages
- [ ] Add tests for Windows-style paths in errors

## References

- **Test Scenarios**: See `AUTO_FIX_AGENT_TEST_SCENARIOS.md`
- **Model Router**: See `core/utils/model_router.py`
- **Workflow**: See `.github/workflows/auto-fix-agent.yml`
- **Config**: See `projects/*/config.yaml`

## Support

For issues with tests, check:
1. Are API keys set in environment? (for slow tests)
2. Is pytest installed? `pip install pytest pytest-cov`
3. Are fixtures loading correctly?
4. Do mocks have proper side_effect setup?

---

**Last Updated:** December 12, 2025  
**Test Suite Version:** 1.0  
**Status:** ✅ Production Ready
