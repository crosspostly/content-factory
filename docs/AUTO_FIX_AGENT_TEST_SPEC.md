# 🤖 Auto-Fix Agent Testing Specification

> **Техническое задание для AI-агента по тестированию автоматического исправления ошибок в GitHub Actions workflows с использованием Qwen/Gemini**

---

## 📋 Цель Тестирования

Протестировать работу **Auto-Fix Agent** — AI-powered системы, которая:
1. ✅ Обнаруживает падения workflow'ов
2. ✅ Анализирует логи ошибок через Qwen (локально) или Gemini (fallback)
3. ✅ Генерирует решение в формате JSON
4. ✅ Создаёт GitHub Issue с описанием проблемы
5. ✅ (Опционально) Создаёт Pull Request с автоматическим исправлением

---

## 🎯 Scope Тестирования

### Что тестируем:

| Компонент | Цель |
|-----------|------|
| **Qwen Analysis** | Проверить что Qwen правильно анализирует ошибки |
| **Gemini Fallback** | Убедиться что Gemini подхватывает если Qwen упал |
| **Issue Creation** | Проверить качество создаваемых Issues |
| **PR Creation** | Проверить корректность auto-fix кода |
| **Model Router** | Протестировать переключение Qwen ↔ Gemini |

### Что НЕ тестируем:
- ❌ Реальный merge PR'ов (только creation)
- ❌ Деплой на production
- ❌ Performance под нагрузкой

---

## 🧪 Test Scenarios

### Scenario 1: Missing Dependency Error

**Trigger:** Удалить зависимость из `requirements.txt`

**Steps:**
```bash
# 1. Создать тестовую ветку
git checkout -b test/auto-fix-missing-dependency

# 2. Сломать requirements.txt (удалить google-generativeai)
sed -i '/google-generativeai/d' requirements.txt

# 3. Commit & Push
git add requirements.txt
git commit -m "test: remove google-generativeai to trigger auto-fix"
git push origin test/auto-fix-missing-dependency

# 4. Создать PR и trigger workflow
gh pr create --base main --head test/auto-fix-missing-dependency \
  --title "TEST: Missing dependency (trigger auto-fix)" \
  --body "This PR intentionally breaks the build to test Auto-Fix Agent"

# 5. Запустить workflow вручную
gh workflow run "Part 1 MVP Test" --ref test/auto-fix-missing-dependency
```

**Expected Behavior:**

1. ✅ Workflow падает с `ModuleNotFoundError: No module named 'google.generativeai'`
2. ✅ Auto-Fix Agent срабатывает автоматически
3. ✅ Qwen анализирует лог и генерирует:
   ```json
   {
     "problem": "ModuleNotFoundError: No module named 'google.generativeai'",
     "root_cause": "Missing dependency in requirements.txt",
     "severity": "high",
     "solution_steps": [
       "Add 'google-generativeai==0.6.0' to requirements.txt",
       "Reinstall dependencies with 'pip install -r requirements.txt'"
     ],
     "code_fix": "google-generativeai==0.6.0",
     "file_to_modify": "requirements.txt",
     "suggested_commit_message": "fix: add missing google-generativeai dependency",
     "auto_fix_possible": true
   }
   ```
4. ✅ Создаётся Issue: `🔴 [HIGH] ModuleNotFoundError: No module named 'google.generativeai'`
5. ✅ Создаётся PR: `🔧 Auto-Fix: Add missing google-generativeai dependency`
6. ✅ В Issue/PR указано что использовалась модель `qwen`

**Validation:**
```bash
# Проверить что Issue создан
gh issue list --label "auto-generated,ai-analyzed"

# Проверить что PR создан
gh pr list --label "auto-generated,auto-fix"

# Проверить содержимое PR
gh pr view <PR_NUMBER> --json files,body

# Проверить что используется Qwen (не Gemini)
gh run view <RUN_ID> --log | grep "model_used"
```

---

### Scenario 2: Syntax Error in Python Code

**Trigger:** Внести синтаксическую ошибку в Python файл

**Steps:**
```bash
# 1. Создать тестовую ветку
git checkout -b test/auto-fix-syntax-error

# 2. Сломать Python код
cat > core/utils/broken_test.py << 'EOF'
def test_function()
    # Намеренная ошибка - пропущено двоеточие
    return "This should fail"
EOF

# 3. Добавить импорт в main файл
echo "from core.utils.broken_test import test_function" >> core/orchestrators/pipeline_orchestrator.py

# 4. Commit & Push
git add core/utils/broken_test.py core/orchestrators/pipeline_orchestrator.py
git commit -m "test: introduce syntax error to trigger auto-fix"
git push origin test/auto-fix-syntax-error

# 5. Trigger workflow
gh workflow run "Run Tests" --ref test/auto-fix-syntax-error
```

**Expected Behavior:**

1. ✅ Workflow падает с `SyntaxError: invalid syntax`
2. ✅ Auto-Fix Agent анализирует и генерирует:
   ```json
   {
     "problem": "SyntaxError: invalid syntax in broken_test.py",
     "root_cause": "Missing colon after function definition",
     "severity": "high",
     "solution_steps": [
       "Add ':' after 'def test_function()'",
       "Fix line 1 in core/utils/broken_test.py"
     ],
     "code_fix": "def test_function():\n    # Fixed\n    return \"This should fail\"",
     "file_to_modify": "core/utils/broken_test.py",
     "auto_fix_possible": true
   }
   ```
3. ✅ Issue + PR созданы
4. ✅ PR содержит исправленный код

**Validation:**
```bash
# Проверить что fix применён корректно
gh pr diff <PR_NUMBER> | grep "def test_function():"
```

---

### Scenario 3: File Not Found Error

**Trigger:** Удалить файл но оставить ссылку на него

**Steps:**
```bash
# 1. Создать тестовую ветку
git checkout -b test/auto-fix-file-not-found

# 2. Удалить файл
rm projects/youtube_horoscope/prompts/shorts_scenario.txt

# 3. Commit & Push
git add -A
git commit -m "test: remove prompt file to trigger auto-fix"
git push origin test/auto-fix-file-not-found

# 4. Trigger workflow
gh workflow run "Part 1 MVP Test" --ref test/auto-fix-file-not-found
```

**Expected Behavior:**

1. ✅ Workflow падает с `FileNotFoundError: prompts/shorts_scenario.txt`
2. ✅ Auto-Fix Agent анализирует:
   ```json
   {
     "problem": "FileNotFoundError: prompts/shorts_scenario.txt not found",
     "root_cause": "File was deleted or moved",
     "severity": "critical",
     "solution_steps": [
       "Restore file from git history",
       "Or update path in config.yaml"
     ],
     "code_fix": "",
     "file_to_modify": null,
     "auto_fix_possible": false
   }
   ```
3. ✅ Issue создан (но без PR, так как `auto_fix_possible: false`)
4. ✅ Issue содержит инструкции для ручного исправления

**Validation:**
```bash
# Проверить что PR НЕ создан (только Issue)
gh pr list --label "auto-fix" | grep -c "Auto-Fix" # должно быть 0

# Проверить что Issue содержит инструкции
gh issue view <ISSUE_NUMBER> --json body
```

---

### Scenario 4: API Rate Limit Error

**Trigger:** Симулировать rate limit ошибку

**Steps:**
```bash
# 1. Создать тестовую ветку
git checkout -b test/auto-fix-rate-limit

# 2. Добавить mock для rate limit
cat > tests/test_rate_limit.py << 'EOF'
import pytest
from unittest.mock import patch
from core.utils.model_router import generate_text

def test_rate_limit():
    # Simulate 429 error from Gemini API
    with patch('core.utils.model_router._call_gemini') as mock:
        mock.side_effect = Exception("429 Resource Exhausted")
        
        # This should trigger rate limit handling
        with pytest.raises(Exception):
            generate_text(config, "test prompt", model_hint="gemini-2.0-flash")
EOF

# 3. Commit & Push
git add tests/test_rate_limit.py
git commit -m "test: add rate limit test to trigger auto-fix"
git push origin test/auto-fix-rate-limit

# 4. Trigger workflow
gh workflow run "Run Tests" --ref test/auto-fix-rate-limit
```

**Expected Behavior:**

1. ✅ Workflow падает с `429 Resource Exhausted`
2. ✅ Auto-Fix Agent анализирует:
   ```json
   {
     "problem": "API Rate Limit Exceeded (429)",
     "root_cause": "Too many requests to Gemini API",
     "severity": "medium",
     "solution_steps": [
       "Add retry logic with exponential backoff",
       "Implement request throttling",
       "Use fallback to local Qwen model"
     ],
     "code_fix": "time.sleep(retry_delay * (2 ** attempt))",
     "file_to_modify": "core/utils/model_router.py",
     "auto_fix_possible": true
   }
   ```
3. ✅ Issue + PR созданы
4. ✅ PR содержит retry logic

---

### Scenario 5: Qwen Fallback to Gemini

**Trigger:** Симулировать недоступность Qwen

**Steps:**
```bash
# 1. Создать тестовую ветку
git checkout -b test/qwen-fallback-gemini

# 2. Модифицировать workflow чтобы Qwen не работал
# Изменить auto-fix-agent.yml чтобы Qwen не запускался
cat > .github/workflows/auto-fix-agent-test.yml << 'EOF'
name: Auto-Fix Agent Test (Qwen Fallback)

on:
  workflow_dispatch:

jobs:
  test-fallback:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      # Намеренно НЕ устанавливаем Ollama/Qwen
      # - name: Setup Ollama & Qwen
      #   run: ...
      
      - name: Trigger fake error
        run: |
          echo "Simulating error..."
          exit 1
      
      - name: Auto-Fix with Gemini only
        if: failure()
        env:
          GOOGLE_AI_API_KEY: ${{ secrets.GOOGLE_AI_API_KEY }}
        run: |
          python3 << 'PYTHON'
          from core.utils.model_router import generate_text
          
          # Qwen недоступен, должен fallback на Gemini
          result = generate_text(
              config,
              prompt="Analyze this error...",
              model_hint="qwen2.5-coder:1.5b"  # Попробуем Qwen
          )
          
          # Проверяем что использовался Gemini
          assert "gemini" in result.lower(), "Expected fallback to Gemini"
          PYTHON
EOF

# 3. Commit & Push
git add .github/workflows/auto-fix-agent-test.yml
git commit -m "test: simulate Qwen unavailability for fallback test"
git push origin test/qwen-fallback-gemini

# 4. Trigger workflow
gh workflow run "Auto-Fix Agent Test (Qwen Fallback)" --ref test/qwen-fallback-gemini
```

**Expected Behavior:**

1. ✅ Qwen недоступен (не установлен Ollama)
2. ✅ model_router автоматически переключается на Gemini
3. ✅ В логах видно:
   ```
   ⚠️ Failed with ollama/qwen2.5-coder:1.5b: Connection refused
   ℹ️ Trying fallback model: gemini-2.0-flash
   ✅ Success with gemini/gemini-2.0-flash
   ```
4. ✅ Issue создан с пометкой `AI Model Used: gemini`

**Validation:**
```bash
# Проверить логи fallback'а
gh run view <RUN_ID> --log | grep -A 5 "fallback"

# Проверить что в Issue указан gemini
gh issue view <ISSUE_NUMBER> --json body | jq '.body' | grep "gemini"
```

---

## 🔍 Manual Verification Steps

После каждого сценария проверить:

### 1. Issue Quality Check

```bash
# Получить последний Issue
ISSUE_NUM=$(gh issue list --label "auto-generated" --limit 1 --json number --jq '.[0].number')

# Проверить содержимое
gh issue view $ISSUE_NUM --json title,body,labels

# Убедиться что содержит:
# ✅ Problem description
# ✅ Root cause analysis
# ✅ Severity level (CRITICAL/HIGH/MEDIUM/LOW)
# ✅ Solution steps (список)
# ✅ AI Model used (qwen или gemini)
# ✅ Link to failed workflow run
```

### 2. PR Quality Check

```bash
# Получить последний auto-fix PR
PR_NUM=$(gh pr list --label "auto-fix" --limit 1 --json number --jq '.[0].number')

# Проверить содержимое
gh pr view $PR_NUM --json title,body,files,labels

# Убедиться что:
# ✅ Title описательный ("Auto-Fix: ...")
# ✅ Body содержит problem/solution
# ✅ Files изменены корректно
# ✅ Code fix применён правильно
# ✅ Commit message осмысленный
```

### 3. Model Router Logic Check

```python
# Проверить логику выбора модели
python3 << 'PYTHON'
from core.utils.model_router import _get_provider_for_model

class MockConfig:
    pass

config = MockConfig()

# Test 1: Gemini detection
assert _get_provider_for_model("gemini-2.0-flash", config) == "gemini"

# Test 2: Qwen detection (Ollama)
assert _get_provider_for_model("qwen2.5-coder:1.5b", config) == "ollama"

# Test 3: Qwen detection (OpenRouter fallback)
assert _get_provider_for_model("qwen-large", config) == "openrouter"

print("✅ All model routing tests passed!")
PYTHON
```

---

## 📊 Success Criteria

### Минимальные требования (Must Have):

| Критерий | Ожидание |
|----------|----------|
| **Qwen Analysis** | ✅ Успешно анализирует 80%+ ошибок |
| **Gemini Fallback** | ✅ Подхватывает если Qwen упал |
| **Issue Creation** | ✅ 100% Issues созданы с корректной информацией |
| **Auto-Fix Accuracy** | ✅ 70%+ PR'ов с правильным кодом |
| **Model Tracking** | ✅ 100% Issues содержат model_used |

### Желательные (Nice to Have):

| Критерий | Ожидание |
|----------|----------|
| **PR Merge Rate** | ✅ 50%+ PR'ов готовы к merge без правок |
| **Response Time** | ✅ < 2 минуты от ошибки до Issue/PR |
| **Cost Efficiency** | ✅ 90%+ используют Qwen (не Gemini API) |

---

## 🧪 AI Agent Testing Prompt

**Для AI-агента:**

```markdown
# TASK: Test Auto-Fix Agent with Qwen/Gemini

## Objective
Test the Auto-Fix Agent workflow in content-factory repository to ensure it:
1. Detects workflow failures
2. Analyzes error logs using Qwen (local) or Gemini (fallback)
3. Creates GitHub Issues with solutions
4. (Optional) Creates Pull Requests with code fixes

## Steps

### Phase 1: Setup
1. Clone repository: `https://github.com/crosspostly/content-factory`
2. Ensure GitHub CLI is installed: `gh --version`
3. Authenticate: `gh auth login`
4. Verify Auto-Fix Agent workflow exists: `gh workflow list | grep "Auto-Fix Agent"`

### Phase 2: Execute Test Scenarios
For each scenario in AUTO_FIX_AGENT_TEST_SPEC.md:

1. Create test branch
2. Introduce the specified error
3. Trigger workflow
4. Wait for Auto-Fix Agent to run (~2-3 minutes)
5. Validate results:
   - Check Issue was created
   - Check PR was created (if applicable)
   - Verify AI model used (qwen vs gemini)
   - Validate fix quality

### Phase 3: Report Results
Generate a report containing:

```json
{
  "test_run_id": "auto-fix-test-2025-12-12",
  "scenarios_tested": 5,
  "scenarios_passed": 4,
  "scenarios_failed": 1,
  "results": [
    {
      "scenario": "Missing Dependency Error",
      "status": "PASS",
      "ai_model_used": "qwen",
      "issue_created": true,
      "pr_created": true,
      "fix_quality": "correct",
      "comments": "Qwen correctly identified missing dependency and added it to requirements.txt"
    },
    {
      "scenario": "Syntax Error",
      "status": "PASS",
      "ai_model_used": "qwen",
      "issue_created": true,
      "pr_created": true,
      "fix_quality": "correct",
      "comments": "Fixed missing colon in function definition"
    },
    {
      "scenario": "File Not Found",
      "status": "PASS",
      "ai_model_used": "qwen",
      "issue_created": true,
      "pr_created": false,
      "fix_quality": "N/A",
      "comments": "Correctly identified manual intervention needed"
    },
    {
      "scenario": "API Rate Limit",
      "status": "PASS",
      "ai_model_used": "qwen",
      "issue_created": true,
      "pr_created": true,
      "fix_quality": "needs_review",
      "comments": "Added retry logic but may need adjustment"
    },
    {
      "scenario": "Qwen Fallback to Gemini",
      "status": "PASS",
      "ai_model_used": "gemini",
      "issue_created": true,
      "pr_created": true,
      "fix_quality": "correct",
      "comments": "Successfully fell back to Gemini when Qwen unavailable"
    }
  ],
  "performance_metrics": {
    "avg_time_to_issue": "1.2 minutes",
    "avg_time_to_pr": "1.8 minutes",
    "qwen_usage_rate": "80%",
    "gemini_fallback_rate": "20%"
  },
  "recommendations": [
    "Qwen performs well for common errors",
    "Gemini fallback works reliably",
    "Consider improving retry logic detection"
  ]
}
```

### Phase 4: Cleanup
1. Close all test Issues: `gh issue list --label "auto-generated" --json number | jq -r '.[].number' | xargs -I {} gh issue close {}`
2. Close all test PRs: `gh pr list --label "auto-fix" --json number | jq -r '.[].number' | xargs -I {} gh pr close {}`
3. Delete test branches: `git branch -D test/*`

## Constraints
- Do NOT merge any PRs to main branch
- Do NOT delete production workflows
- Do NOT modify core files outside of test branches
- Use GitHub Secrets for API keys (do not hardcode)

## Expected Output
A markdown report with:
- Summary of test results
- Screenshots of created Issues/PRs
- Performance metrics
- Recommendations for improvements
```

---

## 📁 Test Data Files

### Sample Error Logs

```bash
# Create test error logs directory
mkdir -p tests/fixtures/error_logs

# Missing dependency error log
cat > tests/fixtures/error_logs/missing_dependency.log << 'EOF'
2025-12-12T15:30:00.000Z ERROR:
Traceback (most recent call last):
  File "core/orchestrators/pipeline_orchestrator.py", line 10, in <module>
    import google.generativeai as genai
ModuleNotFoundError: No module named 'google.generativeai'

The command exited with code 1
EOF

# Syntax error log
cat > tests/fixtures/error_logs/syntax_error.log << 'EOF'
2025-12-12T15:35:00.000Z ERROR:
  File "core/utils/broken_test.py", line 1
    def test_function()
                      ^
SyntaxError: invalid syntax
EOF

# File not found error log
cat > tests/fixtures/error_logs/file_not_found.log << 'EOF'
2025-12-12T15:40:00.000Z ERROR:
Traceback (most recent call last):
  File "core/generators/script_generator.py", line 45, in load_prompt
    with open("projects/youtube_horoscope/prompts/shorts_scenario.txt") as f:
FileNotFoundError: [Errno 2] No such file or directory: 'projects/youtube_horoscope/prompts/shorts_scenario.txt'
EOF
```

---

## 🎯 Next Steps After Testing

После успешного тестирования:

1. ✅ **Merge все успешные auto-fix PR'ы**
2. ✅ **Закрыть test Issues**
3. ✅ **Создать summary report** с метриками
4. ✅ **Улучшить prompts** для Qwen если нужно
5. ✅ **Добавить больше test scenarios** если найдены пробелы
6. ✅ **Документировать edge cases** для будущих улучшений

---

## 📝 Report Template

```markdown
# Auto-Fix Agent Test Report

**Date:** 2025-12-12  
**Tester:** AI Agent  
**Repository:** crosspostly/content-factory  
**Workflow:** Auto-Fix Agent v2.2  

## Executive Summary
- **Total Scenarios:** 5
- **Passed:** 4/5 (80%)
- **Failed:** 1/5 (20%)
- **Qwen Success Rate:** 80%
- **Gemini Fallback Rate:** 20%

## Detailed Results

### ✅ PASS: Missing Dependency Error
- **AI Model:** qwen
- **Issue:** #123
- **PR:** #124
- **Fix Quality:** ✅ Correct
- **Time to Fix:** 1.2 minutes
- **Comments:** Qwen correctly identified missing dependency and added to requirements.txt

### ✅ PASS: Syntax Error
...

### ❌ FAIL: File Not Found
- **AI Model:** qwen
- **Issue:** #125
- **PR:** N/A
- **Fix Quality:** N/A
- **Comments:** Qwen correctly identified issue but marked auto_fix_possible=false

## Recommendations
1. Improve Qwen prompt for edge cases
2. Add more retry logic examples
3. Consider caching analysis results

## Conclusion
Auto-Fix Agent works reliably with Qwen as primary model and Gemini as fallback. Ready for production use.
```

---

**Версия:** 1.0  
**Последнее обновление:** Декабрь 12, 2025  
**Статус:** 🟢 Ready for Testing

---

<div align="center">

**Made with ❤️ by Content Factory Team**

[⭐ Start Testing](https://github.com/crosspostly/content-factory/actions)

</div>
