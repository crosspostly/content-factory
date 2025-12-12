# Qwen Code Setup for GitHub Actions 🎯

## ✅ У тебя уже есть всё!

Твой Qwen Code CLI хранит ключи здесь:
```
C:\Users\varsm\.qwen\oauth_creds.json
```

### Содержимое файла:
```json
{
  "access_token": "MAuuK24ct034RejWX7W_FuET6r1nsQ1iq9uzV5AXIMPC8iuPoEuoZNah74vdfkxmRINIJdhmjN47lzaheCDLvQ",
  "refresh_token": "1dxcdJ3uDRIPl5F0EEaB0un0lS1-dkEby3Hqb1z1qdSn4HWeUoa23jZKOkvJ_Bg4a7ijeR6TBOznPdJd1c1Wmg",
  "token_type": "Bearer",
  "resource_url": "portal.qwen.ai",
  "expiry_date": 1765543004617
}
```

---

## 🔑 Добавить в GitHub Secrets

### Шаг 1: Открыть GitHub Settings
```
https://github.com/crosspostly/content-factory/settings/secrets/actions
```

### Шаг 2: Добавить новый Secret

Кликни "New repository secret" и добавь:

```
Name:  QWEN_ACCESS_TOKEN
Value: MAuuK24ct034RejWX7W_FuET6r1nsQ1iq9uzV5AXIMPC8iuPoEuoZNah74vdfkxmRINIJdhmjN47lzaheCDLvQ
```

### Шаг 3 (опционально): Refresh Token для долгосрочного использования

Если захочешь автоматический refresh:

```
Name:  QWEN_REFRESH_TOKEN
Value: 1dxcdJ3uDRIPl5F0EEaB0un0lS1-dkEby3Hqb1z1qdSn4HWeUoa23jZKOkvJ_Bg4a7ijeR6TBOznPdJd1c1Wmg
```

---

## 🔧 Как использовать в Actions

### Вариант 1: OpenAI-совместимый API (Рекомендуется)

```yaml
- name: Analyze with Qwen
  env:
    OPENAI_API_KEY: ${{ secrets.QWEN_ACCESS_TOKEN }}
    OPENAI_BASE_URL: "https://dashscope.aliyuncs.com/compatible-mode/v1"
    OPENAI_MODEL: "qwen-max"
  run: |
    python3 << 'PY'
    import os
    import requests
    import json
    
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    model = os.getenv("OPENAI_MODEL")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    with open("/tmp/workflow_logs.txt", "r") as f:
        logs = f.read()[-2000:]
    
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": f"Analyze this error:\n{logs}"}
        ],
        "temperature": 0.2,
        "max_tokens": 2048
    }
    
    response = requests.post(
        f"{base_url}/chat/completions",
        headers=headers,
        json=payload
    )
    
    print(json.dumps(response.json(), indent=2))
    PY
```

### Вариант 2: Прямой DashScope API

```yaml
- name: Analyze with Qwen (DashScope Direct)
  env:
    QWEN_API_KEY: ${{ secrets.QWEN_ACCESS_TOKEN }}
  run: |
    python3 << 'PY'
    import os
    import requests
    
    api_key = os.getenv("QWEN_API_KEY")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "qwen-max",
        "messages": [{"role": "user", "content": "Test"}]
    }
    
    response = requests.post(
        "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
        headers=headers,
        json=payload
    )
    
    print(response.status_code, response.json())
    PY
```

---

## ⚙️ Обновить Master Config

В `.github/auto-fix-master-config.yml` теперь можешь менять:

```yaml
ai_models:
  primary: 'qwen'  # или 'gemini' или 'dual'
  
  qwen:
    enabled: true
    model: 'qwen-max'
    timeout: 60
```

---

## 🚨 Важно: Refresh Token

Твой `access_token` истекает **2025-02-09** (видно из `expiry_date`).

Чтобы автоматически обновлять:

```python
import requests
import json
import os
from datetime import datetime

refresh_token = os.getenv("QWEN_REFRESH_TOKEN")
expiry_date = 1765543004617  # milliseconds

# Проверить не истек ли
if datetime.now().timestamp() * 1000 > expiry_date - 86400000:  # за день до истечения
    # Обновить токен
    response = requests.post(
        "https://portal.qwen.ai/oauth/token",
        json={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
    )
    new_token = response.json()["access_token"]
    # Обновить GitHub Secret
    # ...
```

Но пока токен живой - может не делать!

---

## ✅ Готово!

### Что дальше:

1. ✅ Открыть GitHub Settings → Secrets
2. ✅ Добавить `QWEN_ACCESS_TOKEN` с твоим значением
3. ✅ Обновить workflow для использования Qwen
4. ✅ Менять `ai_models.primary` в master-config

### Тестирование:

```bash
# На GitHub запустить тестовый workflow
# Settings → Actions → Test Auto-Fix Trigger → Run workflow

# Он выберет модель из master-config
# Если primary: 'qwen' → использует Qwen
# Если primary: 'gemini' → использует Gemini
# Если primary: 'dual' → оба
```

---

**Ключи у тебя уже есть! 🎉**
