# Auto-Fix Agent Test Scenarios

This document describes the comprehensive test coverage for the Auto-Fix Agent system that uses Qwen (local/Ollama) and Gemini (fallback) to automatically analyze and fix GitHub Actions workflow failures.

## Overview

The Auto-Fix Agent test suite consists of:
- **Unit Tests**: `tests/test_auto_fix_agent.py` - Core auto-fix functionality
- **Model Router Tests**: `tests/test_model_router_autofix.py` - Advanced model routing scenarios
- **Error Log Fixtures**: `tests/fixtures/error_logs/` - Real-world error logs
- **Shared Fixtures**: `tests/conftest.py` - Common test utilities

## Test Scenarios

### Scenario 1: Missing Dependency Error

**Test Class:** `TestErrorLogAnalysis.test_missing_dependency_error_identification`

**What it tests:**
- Detection of `ModuleNotFoundError` in workflow logs
- Identification of missing Python package
- Extraction of package name from error message

**Error Log:**
```
ModuleNotFoundError: No module named 'google.generativeai'
```

**Expected Behavior:**
- ✅ Error is correctly identified as missing dependency
- ✅ Analysis returns JSON with:
  - `problem`: "ModuleNotFoundError: No module named 'google.generativeai'"
  - `root_cause`: "Missing dependency in requirements.txt"
  - `severity`: "high"
  - `auto_fix_possible`: true
  - `file_to_modify`: "requirements.txt"
  - `code_fix`: "google-generativeai==0.7.2"

### Scenario 2: Syntax Error in Python Code

**Test Class:** `TestErrorLogAnalysis.test_syntax_error_identification`

**What it tests:**
- Detection of `SyntaxError` in workflow logs
- Identification of exact syntax issue
- Location of problematic code line

**Error Log:**
```
SyntaxError: invalid syntax in broken_test.py
def test_function()
                  ^
```

**Expected Behavior:**
- ✅ Error is correctly identified as syntax error
- ✅ Analysis returns JSON with:
  - `problem`: "SyntaxError: invalid syntax"
  - `root_cause`: "Missing colon after function definition"
  - `severity`: "high"
  - `auto_fix_possible`: true
  - `file_to_modify`: "core/utils/broken_test.py"
  - `code_fix`: Contains corrected function definition

### Scenario 3: File Not Found Error

**Test Class:** `TestErrorLogAnalysis.test_file_not_found_error_identification`

**What it tests:**
- Detection of `FileNotFoundError` in workflow logs
- Identification of missing file path
- Recognition that auto-fix is not possible

**Error Log:**
```
FileNotFoundError: [Errno 2] No such file or directory: 
'projects/youtube_horoscope/prompts/shorts_scenario.txt'
```

**Expected Behavior:**
- ✅ Error is correctly identified as file not found
- ✅ Analysis returns JSON with:
  - `problem`: "FileNotFoundError: shorts_scenario.txt not found"
  - `root_cause`: "File was deleted or moved"
  - `severity`: "critical"
  - `auto_fix_possible`: false
  - `code_fix`: "" (empty - manual fix needed)
  - `file_to_modify`: null

### Scenario 4: API Rate Limit Error

**Test Class:** `TestErrorLogAnalysis.test_api_rate_limit_error_identification`

**What it tests:**
- Detection of 429 rate limit errors
- Identification of resource exhaustion
- Recognition of retry-able error

**Error Log:**
```
google.generativeai.types.generation_types.APIError: 429 Resource Exhausted: 
API request limit exceeded. Please retry with exponential backoff.
```

**Expected Behavior:**
- ✅ Error is correctly identified as rate limit error
- ✅ Analysis returns JSON with:
  - `problem`: "API Rate Limit Exceeded (429)"
  - `root_cause`: "Too many requests to Gemini API"
  - `severity`: "medium"
  - `solution_steps`: Include retry logic with exponential backoff
  - `auto_fix_possible`: true
  - `file_to_modify`: "core/utils/model_router.py"

### Scenario 5: Qwen Fallback to Gemini

**Test Class:** `TestQwenPrimaryModelFlow.test_qwen_fails_fallback_to_gemini`

**What it tests:**
- Primary model (Qwen/Ollama) failure detection
- Automatic fallback to secondary model (Gemini)
- Proper tracking of which model was used

**Test Flow:**
1. Qwen is configured as primary model
2. Qwen call fails with `ProviderCallError`
3. System automatically tries Gemini
4. Gemini succeeds with analysis

**Expected Behavior:**
- ✅ Qwen failure is caught
- ✅ Gemini is attempted as fallback
- ✅ Analysis is completed successfully
- ✅ Fallback model used is tracked in Issue/PR

## Model Router Tests

### Test Class: `TestModelDetection`

Tests that verify correct provider detection for various model identifiers.

```python
# Gemini models -> "gemini" provider
"gemini-2.5-flash" -> gemini
"gemini-2.5-flash-lite" -> gemini

# Qwen with Ollama (local) -> "ollama" provider
"qwen2.5-coder:1.5b" -> ollama

# Qwen with OpenRouter (fallback) -> "openrouter" provider
"qwen-large" -> openrouter
```

### Test Class: `TestQwenPrimaryModelFlow`

Tests for Qwen as primary model with fallback support.

**Key Tests:**
- `test_qwen_success`: Qwen analysis succeeds
- `test_qwen_fails_fallback_to_gemini`: Qwen fails, Gemini succeeds

### Test Class: `TestGeminiFallback`

Tests for Gemini as fallback when Qwen unavailable.

**Key Tests:**
- `test_gemini_analysis_missing_dependency`: Analyzes missing dependency
- `test_gemini_analysis_syntax_error`: Analyzes syntax error

## Retry Logic Tests

### Test Class: `TestRetryLogicWithAutoFix`

Tests retry behavior with exponential backoff.

**Scenarios:**
1. **Rate Limit (429)**: Retries with exponential backoff
2. **Auth Error (401)**: Fails immediately, no retry
3. **Transient Error**: Retries up to max_retries

**Example Test:**
```python
def test_retry_on_rate_limit(mock_sleep, mock_gemini, mock_config):
    """Test retry on rate limit with exponential backoff."""
    mock_gemini.side_effect = [
        ProviderCallError("429 Rate Limited", status_code=429),
        "Success after retry"
    ]
    
    response = generate_text(mock_config, "Analyze error")
    
    assert response == "Success after retry"
    assert mock_gemini.call_count == 2  # Called twice
    assert mock_sleep.called  # Sleep called for backoff
```

## Severity Classification Tests

### Test Class: `TestErrorSeverityClassification`

Tests that errors are classified with correct severity levels.

| Severity | Examples |
|----------|----------|
| **CRITICAL** | Database connection lost, Core functionality broken |
| **HIGH** | Missing required dependency, Syntax error |
| **MEDIUM** | API rate limit, Deprecation warnings |
| **LOW** | Minor warnings, Non-critical deprecations |

## Issue/PR Creation Tests

### Test Class: `TestIssueCreationData`

Tests for GitHub Issue content and formatting.

**Issue Title Format:**
```
🔴 [HIGH] ModuleNotFoundError: No module named 'google.generativeai'
```

**Issue Body Sections:**
- 🚨 Failure Analysis
- Problem description
- Root cause analysis
- Severity level
- Solution steps (bulleted list)
- Technical task
- Auto-fix status
- Links to workflow and commit

### Test Class: `TestPRCreationData`

Tests for GitHub Pull Request content and formatting.

**PR Title Format:**
```
🔧 Auto-Fix: Add missing google-generativeai dependency
```

**PR Body Sections:**
- Issue being fixed
- Root cause
- Severity level
- Solution steps
- Changed files
- Workflow run link
- Created by Auto-Fix Agent

## Analysis JSON Structure

All auto-fix analysis responses follow this JSON schema:

```json
{
  "problem": "Brief description of what failed",
  "root_cause": "Why it happened",
  "severity": "critical|high|medium|low",
  "solution_steps": [
    "Step 1 to fix the issue",
    "Step 2 to fix the issue"
  ],
  "code_fix": "Python/YAML code to fix (if applicable) or empty string",
  "file_to_modify": "path/to/file or null if not applicable",
  "suggested_commit_message": "git commit message for the fix",
  "technical_task": "Detailed technical task description",
  "auto_fix_possible": true/false
}
```

## Running the Tests

### Run all auto-fix tests:
```bash
pytest tests/test_auto_fix_agent.py -v
pytest tests/test_model_router_autofix.py -v
```

### Run only fast tests (no API calls):
```bash
pytest tests/test_auto_fix_agent.py tests/test_model_router_autofix.py -v -m "not slow"
```

### Run only slow integration tests:
```bash
pytest tests/test_auto_fix_agent.py tests/test_model_router_autofix.py -v -m "slow"
```

### Run with coverage:
```bash
pytest tests/test_auto_fix_agent.py tests/test_model_router_autofix.py \
  --cov=core.utils.model_router \
  --cov-report=html
```

## Test Fixtures

### `mock_config`
Standard Gemini-based config for testing.

```python
@pytest.fixture
def mock_config():
    # Returns ProjectConfig with:
    # - primary_model: gemini-2.5-flash
    # - fallback_models: [gemini-2.5-flash-lite]
    # - temperature: 0.7
    # - max_retries: 2
```

### `mock_config_with_qwen`
Qwen-based config with Gemini fallback.

```python
@pytest.fixture
def mock_config_with_qwen():
    # Returns ProjectConfig with:
    # - primary_model: qwen2.5-coder:1.5b
    # - fallback_models: [gemini-2.5-flash]
    # - temperature: 0.7
    # - max_retries: 2
```

### `error_log_fixtures`
Loads all error logs from `tests/fixtures/error_logs/`.

```python
@pytest.fixture
def error_log_fixtures():
    # Returns dict with keys:
    # - missing_dependency
    # - syntax_error
    # - file_not_found
    # - api_rate_limit
    # - import_error
    # - assertion_error
```

## Error Log Fixtures

Located in `tests/fixtures/error_logs/`:

1. **missing_dependency.log** - ModuleNotFoundError example
2. **syntax_error.log** - SyntaxError example
3. **file_not_found.log** - FileNotFoundError example
4. **api_rate_limit.log** - 429 rate limit error
5. **import_error.log** - ImportError example
6. **assertion_error.log** - AssertionError example

## Test Coverage

Target: ≥ 90% coverage for:
- `core/utils/model_router.py` - Model selection and calling
- Auto-fix analysis logic
- Error detection and classification

## Key Testing Principles

1. **No External API Calls by Default**: All tests use mocks for API calls
2. **Marked Integration Tests**: Tests requiring real API calls use `@pytest.mark.slow`
3. **Clear Error Messages**: Failed assertions include context about what was tested
4. **Isolated Tests**: Each test is independent and can run in any order
5. **Realistic Scenarios**: Error logs are based on real GitHub Actions failures

## CI/CD Integration

These tests run automatically in:
- `.github/workflows/tests.yml` - On every push
- `.github/workflows/auto-fix-agent.yml` - When workflows fail

The Auto-Fix Agent itself uses Qwen/Gemini to analyze real workflow failures and create Issues and PRs.

## Future Test Enhancements

- [ ] Add tests for complex multi-file fixes
- [ ] Add tests for configuration error detection
- [ ] Add tests for performance regression
- [ ] Add tests for concurrent analysis requests
- [ ] Add tests for very large error logs (>100MB)
- [ ] Add tests for non-English error messages
- [ ] Add tests for Windows-style paths in errors
