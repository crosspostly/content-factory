# Qwen Code на GitHub 🚀

## ✅ Готово!

### Что было:
1. ✅ QWEN_ACCESS_TOKEN в GitHub Secrets
2. ✅ Workflow для установки Qwen Code (с кешированием)
3. ✅ Готово использовать!

---

## 📄 Как использовать

### Вариант 1: Fast Install (первый раз)
```yaml
- uses: actions/setup-node@v4
  with:
    node-version: '20'
    cache: 'npm'

- run: npm install -g @qwen-code/qwen-code@latest
```

### Вариант 2: С кешированием (рекомендуется)
```yaml
- uses: actions/setup-node@v4
  with:
    node-version: '20'
    cache: 'npm'

- uses: actions/cache@v3
  with:
    path: ~/.npm
    key: qwen-code-${{ runner.os }}-${{ hashFiles('**/package-lock.json') }}
    restore-keys: qwen-code-${{ runner.os }}-

- run: npm install -g @qwen-code/qwen-code@latest
```

### Использование:
```yaml
- name: Run Qwen
  env:
    OPENAI_API_KEY: ${{ secrets.QWEN_ACCESS_TOKEN }}
    OPENAI_BASE_URL: https://dashscope.aliyuncs.com/compatible-mode/v1
    OPENAI_MODEL: qwen-max
  run: |
    echo "Analyze this code" | qwen
```

---

## 🔗 Схема (финальная)

```
GitHub Secrets
    ↓
    QWEN_ACCESS_TOKEN
    ↓
GitHub Actions
    ↓
    npm install qwen-code
    ↓
    Используем в workflow'ах
```

**Всё. Больше ничего.** ✅
