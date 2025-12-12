# Dual-Model Analysis: Gemini 2.5 + Qwen 3 Strategy

## 🧠 Why Two Models?

Два разных взгляда на проблему = лучше анализ!

| Аспект | Gemini 2.5 Flash | Qwen 3 Max |
|--------|------------------|----------|
| **Скорость** | ⚡ Очень быстро (мс) | ⚡ Быстро (сек) |
| **Глубина анализа** | 💡 Хорошо | 🧠 Отличная |
| **Код анализ** | ✅ Хороший | ✅✅ Лучше |
| **Документация** | ✅ Нормально | ✅ Отличная |
| **Бесплатный лимит** | Включен в quota | ✅ 2000 req/day бесплатно! |
| **Лучше для** | Быстрых fix | Сложных проблем |

---

## 💡 Идея: Сравнительный Анализ

**При каждом failure:**

1. Gemini 2.5 Flash анализирует (быстро)
2. Qwen 3 анализирует (глубоко)
3. Сравнивают результаты
4. Если разные мнения → выбирают лучшее
5. Создают PR с объединённым анализом

---

## 📊 Сравнение на Примере

### Сценарий: Test падает с ValueError

**Error:**
```
FAILED tests/test_tts_generator.py
ValueError: Missing required parameter 'api_key'
```

### Gemini 2.5 Flash (50ms)
```json
{
  "problem": "Missing api_key parameter in function call",
  "root_cause": "Function signature changed, call sites not updated",
  "severity": "high",
  "solution": "Add api_key parameter to all synthesize() calls",
  "confidence": "high"
}
```

### Qwen 3 Max (2 sec)
```json
{
  "problem": "TTS synthesize() function requires api_key but it's not provided",
  "root_cause": "API refactoring in tts_generator.py - synthesize() signature changed from synthesize(config, script, mode) to synthesize(config, script, mode, api_key)",
  "severity": "high",
  "solution_steps": [
    "1. Search all calls to tts_generator.synthesize()",
    "2. Add api_key=api_key parameter to each call",
    "3. Check tests/test_tts_generator.py line XX",
    "4. Also check core/orchestrators/pipeline_orchestrator.py",
    "5. Run full test suite to verify"
  ],
  "confidence": "very_high",
  "detailed_explanation": "..."
}
```

**Result:** Qwen даёт более детальный анализ + точные line numbers!

---

## 🚀 Как Использовать Qwen

### Option 1: Free (Recommended) ✅

**Qwen 3 дает 2000 free requests/day!**

```bash
# 1. Создай account на https://qwen.ai
# 2. Get API key из dashboard
# 3. Добавь в GitHub Secrets:
#    - QWEN_API_KEY
#    - QWEN_BASE_URL: https://dashscope.aliyuncs.com/compatible-mode/v1
```

**Python code:**
```python
import requests

QWEN_API_KEY = os.getenv('QWEN_API_KEY')
QWEN_BASE_URL = os.getenv('QWEN_BASE_URL')

headers = {
    "Authorization": f"Bearer {QWEN_API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "model": "qwen-max",  # or qwen-plus, qwen-turbo
    "messages": [
        {"role": "user", "content": prompt}
    ]
}

response = requests.post(
    f"{QWEN_BASE_URL}/chat/completions",
    headers=headers,
    json=payload
)
```

### Option 2: OpenRouter (Alternative)

```bash
# OpenRouter поддерживает Qwen
# API_BASE: https://openrouter.ai/api/v1
# Model: qwen/qwen-max
```

---

## 📋 Workflow с Двумя Моделями

```yaml
name: Dual-Model Auto-Fix

jobs:
  analyze:
    steps:
      # 1. Gemini быстрый анализ
      - name: Analyze with Gemini 2.5
        run: python analyze_gemini.py
        
      # 2. Qwen глубокий анализ
      - name: Analyze with Qwen 3
        run: python analyze_qwen.py
        env:
          QWEN_API_KEY: ${{ secrets.QWEN_API_KEY }}
      
      # 3. Сравни результаты
      - name: Compare analyses
        run: python compare_results.py
      
      # 4. Создай PR с лучшим решением
      - name: Create PR
        run: python create_pr.py
```

---

## 🎯 Плюсы Dual-Model

✅ **Два разных взгляда** = лучше accuracy  
✅ **Gemini быстрый** = quick preliminary fix  
✅ **Qwen детальный** = sophisticated understanding  
✅ **Redundancy** = если один model неправ, другой поправит  
✅ **Qwen бесплатный** = 2000 requests/day!  
✅ **OpenAI compatible** = просто swap model name  

---

## ⚙️ Как Внедрить

### Шаг 1: Add Qwen Secret
```bash
# GitHub Repo Settings → Secrets
# Add:
QWEN_API_KEY = "sk-your-key-here"
QWEN_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
```

### Шаг 2: Update auto-fix-agent.yml

Добавить step для Qwen анализа после Gemini анализа:

```yaml
- name: Analyze with Qwen 3 (Deep Analysis)
  id: qwen
  run: |
    python3 << 'PYTHON_SCRIPT'
    import requests
    import json
    import os
    
    api_key = os.getenv('QWEN_API_KEY')
    base_url = os.getenv('QWEN_BASE_URL')
    
    if not api_key or not base_url:
        print("⚠️ Qwen API key not configured, skipping Qwen analysis")
        exit(0)
    
    with open("/tmp/workflow_logs.txt", "r") as f:
        logs = f.read()[-2000:]  # Last 2000 chars
    
    prompt = f"""Analyze this GitHub Actions error with deep technical understanding...
    
{logs}

Provide JSON analysis: {"problem": "...", "root_cause": "...", ...}"""
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        f"{base_url}/chat/completions",
        headers=headers,
        json={
            "model": "qwen-max",
            "messages": [{"role": "user", "content": prompt}]
        }
    )
    
    analysis = response.json()["choices"][0]["message"]["content"]
    print(analysis)
    
    # Save for comparison
    with open("/tmp/qwen_analysis.json", "w") as f:
        json.dump(json.loads(analysis), f)
    
    PYTHON_SCRIPT
```

### Шаг 3: Compare & Merge

```python
# compare_results.py
import json

with open("/tmp/analysis.json") as f:
    gemini = json.load(f)
with open("/tmp/qwen_analysis.json") as f:
    qwen = json.load(f)

# Если оба согласны → уверенность высокая
if gemini['root_cause'] == qwen['root_cause']:
    confidence = "very_high"
    solution = gemini  # Gemini быстрее
else:
    confidence = "medium"
    solution = qwen  # Qwen более детальный
```

---

## 💰 Costs

### Gemini 2.5 Flash
- $0.075 per 1M input tokens
- $0.30 per 1M output tokens
- Typical analysis: ~1000 input tokens = $0.000075

### Qwen 3 Max (FREE TIER)
- **2,000 requests per day** - completely free!
- $0.04 per 1M input tokens (paid tier)
- $0.12 per 1M output tokens (paid tier)

**Cost per failure analysis:**
- Gemini: $0.00008
- Qwen: FREE! (first 2000/day)
- **Total: basically free!**

---

## 🎨 UI для User

PR будет показывать результаты обоих моделей:

```markdown
## 🤖 Dual-Model Analysis

### Gemini 2.5 Flash Analysis (⚡ 50ms)
**Problem:** Missing api_key parameter
**Root Cause:** Function signature changed
**Confidence:** HIGH

### Qwen 3 Max Analysis (🧠 2s)
**Problem:** TTS synthesize() missing api_key
**Root Cause:** API refactoring in tts_generator.py
**Details:** 
- Check line XX in test_tts_generator.py
- Also check pipeline_orchestrator.py
**Confidence:** VERY_HIGH

### 🎯 Recommended Solution (Qwen)
Based on both analyses, Qwen provides more detailed understanding.
```

---

## ⚠️ Важно!

**Qwen требует регистрации:**
1. https://qwen.ai (или https://dashscope.aliyun.com)
2. Get API key
3. Add to GitHub Secrets

**Но это бесплатно и даёт 2000 запросов/день!**

---

## 🚀 Next Steps

1. ✅ Create test workflow to verify auto-fix
2. ⬜ Add Qwen API key to GitHub Secrets
3. ⬜ Update auto-fix-agent.yml with Qwen step
4. ⬜ Test with intentional failure
5. ⬜ Compare Gemini vs Qwen results
6. ⬜ Implement comparison logic

---

**Status:** Ready for dual-model implementation! 🎉
