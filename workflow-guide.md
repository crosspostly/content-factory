# 🚀 ПРАВИЛЬНЫЙ WORKFLOW - БЕЗ РИСКА

## 📋 ПРАВИЛО НОМЕР 1: НИКОГДА НЕ В MAIN!

```
❌ НЕПРАВИЛЬНО:
git push origin main
→ Тесты упали → main сломан!

✅ ПРАВИЛЬНО:
git push origin feature-branch
→ Тесты упадут в безопасной ветке
→ Auto-Fix анализирует в PR
→ Ты получаешь ДЕТАЛЬНОЕ техзадание
→ Исправляешь
→ Потом мёржишь в main ✅
```

---

## 🔄 ПОШАГОВЫЙ ПРОЦЕСС

### Шаг 1: Создай feature branch
```bash
git checkout -b feature/my-awesome-feature
# Разработка...
git add .
git commit -m "feat: awesome feature"
git push origin feature/my-awesome-feature
```

### Шаг 2: GitHub Actions запустится АВТОМАТИЧЕСКИ
```
✅ Запускает tests.yml на твоей branch
✅ Если тесты упали → Auto-Fix Agent запускается
✅ Анализирует ошибку с помощью Qwen/Gemini
✅ Создаёт КАЧЕСТВЕННОЕ техзадание Issue
✅ Комментирует в PR ссылку на Issue
```

### Шаг 3: Ты видишь PR с комментом

На GitHub PR появится комментарий:
```
🔍 Auto-Fix Agent analyzed the failure:

📋 View detailed analysis → [Issue #123](...)
```

### Шаг 4: Читаешь ДЕТАЛЬНОЕ техзадание в Issue

GitHub Issue содержит:
```
## 🚨 Workflow Failure - Technical Task

Severity: CRITICAL
Project: content-factory

---

## 📋 Problem Statement
ImportError: google.generativeai module not found

---

## 🔍 Root Cause Analysis
The google-generativeai package is imported in core/utils/model_router.py
but is missing from requirements.txt. This causes the import to fail
when the module is first executed during pytest initialization.

---

## 📌 Technical Details
When the workflow runs, Python tries to import google-generativeai
at line 5 of core/utils/model_router.py. Since pip didn't install it
(not in requirements.txt), ImportError is raised immediately.

### Files Involved
- requirements.txt
- core/utils/model_router.py
- core/auto_fix_agent.py

---

## ✅ Solution: Task Description

Auto-Fix Available: Yes ✅
An automated PR has been created with the suggested fix.
Review the PR and merge if the fix looks correct.

### Steps to Fix
1. Open requirements.txt
2. Add: google-generativeai==0.7.2
3. Run: pip install -r requirements.txt
4. Test: pytest tests/ -v

### Testing Instructions

```bash
pip install -r requirements.txt
pytest tests/ -v --tb=short -m "not slow"
```

---

## 📝 Notes for Developer
- Make sure to run the testing instructions before creating a PR
- Follow the solution steps in order
- Reference this issue in your PR: `Fixes #123`
- Auto-Fix Agent will verify the fix works ✅
```

Это не просто ошибка - это **ПОЛНОЕ ТЕХЗАДАНИЕ** с:
- ✅ Описанием проблемы
- ✅ Анализом корневой причины
- ✅ Техническими деталями
- ✅ Списком затронутых файлов
- ✅ Пошаговыми инструкциями
- ✅ Командами для тестирования
- ✅ Авто-PR с готовым фиксом (если возможно)

### Шаг 5: Делаешь выбор

**Вариант A: Есть авто-PR** (синтаксис, dependencies)
- ✅ Мёржишь PR с auto-fix
- ✅ Тесты перезапускаются
- ✅ Всё зелёное ✅
- ✅ Мёржишь в main

**Вариант B: Нет авто-PR** (логика, баг)
- ✅ Читаешь ДЕТАЛЬНОЕ техзадание
- ✅ Видишь точно что нужно исправить
- ✅ Исправляешь код в своей ветке
- ✅ Коммитишь исправление
- ✅ Тесты снова запускаются
- ✅ Когда всё зелёно → мёржишь в main

### Шаг 6: Merge в main ТОЛЬКО КОГДА ВСЕ ТЕСТЫ ЗЕЛЁНЫЕ

```bash
# На GitHub нажимаешь "Merge pull request"
↓
✅ Все checks прошли
✅ main остаётся чистым
```

---

## 🛡️ ЗАЩИТЫ КОТОРЫЕ ЕСТЬ

1. **Auto-Fix только на feature branches**
   - main никогда не сломается автоматически
   - Анализ + Issues только на `feature-*` и других ветках

2. **Требование прохождения тестов**
   - Нельзя merge PR пока тесты не зелёные
   - GitHub блокирует merge кнопку если есть failures

3. **Качественные Issues как техзадания**
   - Видишь сразу: ЧТО сломалось, ПОЧЕМУ, КАК исправить
   - Детальный анализ от AI
   - Пошаговые инструкции
   - Команды для тестирования

---

## 📊 ПРИМЕРЫ ISSUES

### Пример 1: Missing Dependency → Issue с техзаданием

**Issue содержит:**
```
## Problem
ImportError: google.generativeai not found

## Root Cause
Package not installed - missing in requirements.txt

## Solution Steps
1. Add google-generativeai==0.7.2 to requirements.txt
2. Run: pip install -r requirements.txt
3. Verify: pytest tests/test_api.py -v

## Auto-Fix Status
✅ Auto-Fix Available
(PR #125 has been created with the fix)
```

### Пример 2: YAML Syntax Error → Issue с техзаданием

**Issue содержит:**
```
## Problem
SyntaxError in YAML file: invalid syntax on line 12

## Root Cause
Malformed YAML: missing colon after key
File: projects/youtube_horoscope/prompts/main.yaml

## Technical Details
YAML parser failed at:
  templates:
    short
      text: "value"  ← missing colon after 'short'

## Solution Steps
1. Open projects/youtube_horoscope/prompts/main.yaml
2. Find line 12
3. Change "short" to "short:" (add colon)
4. Test: pytest tests/ -v

## Auto-Fix Status
✅ Auto-Fix Available
(PR #126 with corrected YAML)
```

### Пример 3: Logic Bug → Issue с анализом + инструкциями

**Issue содержит:**
```
## Problem
Test failure in test_horoscope_generation: output mismatch

## Root Cause
The horoscope text generation algorithm returns empty string
instead of proper horoscope text. This happens when
the API response parsing fails on line 45 of generators/horoscope.py

## Technical Details
When generate_horoscope() is called:
1. API returns 200 OK
2. Response parsing at line 45 fails silently
3. Returns empty string
4. Test expects min 50 characters

## Files Involved
- generators/horoscope.py (line 45)
- tests/test_horoscope.py (line 12)

## Solution Steps
1. Debug response parsing logic
2. Check if API structure changed
3. Update parsing code
4. Test: pytest tests/test_horoscope.py -v

## Auto-Fix Status
❌ Manual Fix Required
(This requires logic debugging, not just code replacement)
```

---

## ✅ ГЛАВНЫЕ ПРАВИЛА

| Правило | Статус |
|---------|--------|
| Никогда не push в main без tests ✅ | ✅ Защищено |
| Feature branches для разработки | ✅ Обязательно |
| Issues содержат ПОЛНОЕ техзадание | ✅ Качественно |
| Merge в main только при зелёных тестах | ✅ Обязательно |

---

## 🚨 ЕСЛИ ЧТО-ТО ПОШЛО НЕ ТАК

```
ЕСЛИ ВДРУГ В MAIN СЛУЧИТСЯ БЕДА:

1. git revert <commit_hash>
   → Откатить плохой commit

2. Auto-Fix Agent запустится на revert commit
   → Создаст Issue с анализом

3. Всё откатится назад ✅
```

---

## 🎯 РЕЗЮМЕ

**ТЫ ПИШЕШЬ КОД:**
```bash
git push origin feature/something
```

**GITHUB ДЕЛАЕТ:**
- ✅ Запускает тесты
- ✅ Если упали → Auto-Fix анализирует с Qwen/Gemini
- ✅ Создаёт ДЕТАЛЬНОЕ техзадание Issue
- ✅ (Опционально) Создаёт PR с готовым фиксом

**ТЫ ПОЛУЧАЕШЬ:**
- ✅ Полное объяснение что сломалось
- ✅ Анализ корневой причины
- ✅ Пошаговые инструкции
- ✅ Команды для тестирования
- ✅ (Опционально) готовое решение в PR

**ТЫ ПРОВЕРЯЕШЬ И ИСПРАВЛЯЕШЬ:**
- ✅ Читаешь техзадание
- ✅ Мёржишь PR если fix хороший
- ✅ Или правишь вручную если нужно
- ✅ Когда тесты зелёные → мёржишь в main

**MAIN ОСТАЁТСЯ ЧИСТЫМ:** ✅✅✅

---

## 📚 ДОПОЛНИТЕЛЬНО

**Labels на Issues:**
- `bug` - это баг
- `auto-generated` - создано Auto-Fix Agent
- `ai-analyzed` - проанализировано ИИ
- `project:content-factory` - проект

**Labels на PRs:**
- `auto-generated` - создано автоматически
- `ai-generated` - решение от ИИ

Это помогает отслеживать какие проблемы решал Auto-Fix Agent!
