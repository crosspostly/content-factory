# 🤖 GitHub Workflows Guide

Полный список всех настроенных GitHub Actions workflows в проекте Content Factory.

## 📋 Обзор всех workflows

```
├─ ai-code-review.yml          🤖 AI Code Review (Gemini 2.5 Flash)
├─ code-quality.yml            📚 Linting, Coverage, Spell Check
├─ tests.yml                  🤓 Unit Tests (pytest)
├─ tests-docker.yml           🐋 Docker Container Tests
├─ build-docker.yml           🐋 Build Docker Image
├─ generate-batch.yml         🎗 Batch Content Generation
├─ generate-horoscope-video.yml  🔮 Horoscope Video Generation
├─ test-pipeline-mocks.yml    🗪 Pipeline Testing
├─ todo-to-issue.yml          📄 TODO to Issue Conversion
├─ notifications.yml          💵 Telegram Notifications
├─ release-drafter.yml        📦 Auto-Changelog Generation
└─ cleanup-artifacts.yml      🗑 Weekly Artifact Cleanup
```

---

## 🤖 AI Code Review (`ai-code-review.yml`)

**Запускается:** На каждый PR к `main` или `develop`

**Что делает:**
- ✅ Анализирует изменения в коде с помощью **Gemini 2.5 Flash**
- 🚨 Проверяет на соответствие архитектуре ARCHITECTURE.md
- 🔒 Находит использование запрещённых версий Gemini (2.0, 1.5)
- 💬 Постит подробный отзыв в комментарий к PR
- ⚠️ Может заблокировать merge при критических ошибках

**Результат:** Комментарий в PR с ✅/⚠️/❌ рейтингом

**Требования:**
```
secrets.GOOGLE_AI_API_KEY (Gemini API key)
```

---

## 📚 Code Quality (`code-quality.yml`)

**Запускается:** На push и PR к `main`/`develop`

**Компоненты:**

### 🏃 MegaLinter
- Проверяет: Python, YAML, JSON, Markdown, Docker
- Использует: pylint, flake8, black, yamllint и 50+ других
- Отключены: JavaScript, TypeScript, Rust (не используется)

### 💫 Typos Check
- Ловит опечатки и правописание
- Работает на всех языках, включая русский
- Быстро выполняется (~10 сек)

### 📄 Coverage Report
- Запускает тесты с `--cov=core`
- Генерирует HTML отчёт
- Загружает на [Codecov](https://codecov.io) для трекинга истории
- Артефакт доступен в Actions 7 дней

**Требования:**
```
secrets.GOOGLE_AI_API_KEY (для запуска тестов)
secrets.PIXABAY_API_KEY (для запуска тестов)
codecov.io (бесплатно для open-source)
```

---

## 📄 TODO to Issue (`todo-to-issue.yml`)

**Запускается:** На каждый push к `main`/`develop`/`feature-*`

**Что делает:**
- 📄 Ищет комментарии `# TODO:` в коде
- 📧 Автоматически создаёт GitHub Issue
- 🔗 Вставляет URL Issue обратно в комментарий
- ✅ Закрывает Issue, если TODO удалили
- 🎯 Помечает все TODO issues меткой `todo`

**Пример использования:**
```python
# TODO: Добавить поддержку Claude 3.5 Sonnet
# После push появится Issue с этим текстом
```

**Результат:** Новый Issue с автоматическим URL

---

## 💵 Notifications (`notifications.yml`)

**Запускается:** Автоматически после завершения других workflows

**Интеграция:** Telegram Bot

**Отправляет:**
- ✅ Успешное завершение workflow
- ❌ Ошибки и failure
- 📊 Информацию о commit и author
- 🔗 Прямую ссылку на Action logs

**Специальные алерты:**
- 🔴 При падении тестов — дополнительное сообщение с инструкциями

**Требования:**
```
secrets.TELEGRAM_BOT_TOKEN
secrets.TELEGRAM_CHAT_ID
```

**Пример сообщения:**
```
🎉 Workflow: Run Tests
Status: ✅ SUCCESS

Repository: crosspostly/content-factory
Branch: main
Commit: Fix Gemini model version
Author: shekhovpavel

🔗 Details: https://github.com/...
```

---

## 📦 Release Drafter (`release-drafter.yml`)

**Запускается:** На push к `main` и при открытии PR

**Что делает:**
- 📦 Автоматически собирает Changelog
- 📊 Группирует изменения по типам:
  - 🚀 Features (label: `feature`, `enhancement`)
  - 🐛 Bug Fixes (label: `bug`, `bugfix`)
  - 🔧 Improvements (label: `improvement`, `refactor`)
  - 📚 Documentation (label: `documentation`)
  - 🤖 AI & Automation (label: `ai`, `gemini`)
  - 🔐 Security (label: `security`)
  - ⚡ Performance (label: `performance`)
- 📋 Автоматически инкрементирует версию (major/minor/patch)
- 📤 Создаёт draft release, готовый к публикации

**Конфигурация:** `.github/release-drafter-config.yml`

**Как использовать:**
1. Добавляй правильные labels при создании PR
2. После merge в main автоматически обновляется draft release
3. В GitHub Releases вкладке видишь готовый Changelog
4. Нажимаешь "Publish" — release готов!

**Пример генерируемого Changelog:**
```markdown
## What's Changed

### 🚀 Features
- Add Gemini 2.5 Flash support (#42)
- Implement AI Code Review workflow (#40)

### 🐛 Bug Fixes  
- Fix Docker build error (#39)
- Remove deprecated Gemini 1.5 (#38)

### 🔧 Improvements
- Refactor ModelRouter for better error handling (#41)
- Improve test coverage to 85% (#37)
```

---

## 🗑 Cleanup Artifacts (`cleanup-artifacts.yml`)

**Запускается:** Каждый понедельник в 00:00 UTC (или вручную)

**Что делает:**
- 🗑 Удаляет артефакты старше **7 дней**
- 💾 Оставляет 10 **самых свежих** артефактов
- 📊 Экономит место в GitHub Storage
- ✅ Пропускает tagged releases

**Ручной запуск:**
```
GitHub Actions tab → cleanup-artifacts.yml → Run workflow
```

---

## 🧪 Existing Workflows (уже настроены)

### `tests.yml` - Unit Tests
- Запускает pytest с `--cov`
- На push и PR
- Кэширует зависимости для скорости

### `build-docker.yml` - Docker Build
- Собирает Docker image
- На push к main
- Оптимизация с кэшем слоёв

### `generate-batch.yml` - Batch Generation
- Генерирует контент (видео, гороскопы)
- По расписанию
- Загружает артефакты

---

## ⚙️ Настройка Secrets

**В GitHub Settings → Secrets and variables → Actions:**

```
GOOGLE_AI_API_KEY          # Gemini API key
PIXABAY_API_KEY            # Pixabay stock images
TELEGRAM_BOT_TOKEN         # Telegram bot token
TELEGRAM_CHAT_ID           # Твой Telegram ID
CODECOV_TOKEN              # (опционально) для codecov.io
SONAR_TOKEN                # (опционально) для SonarQube
```

---

## 📊 Workflow Статусы

**Посмотреть статусы всех workflows:**
1. Открой репо на GitHub
2. Actions tab
3. Видишь список всех запусков
4. Кликни на интересующий workflow

**Статус badges для README:**
```markdown
[![AI Code Review](https://github.com/crosspostly/content-factory/actions/workflows/ai-code-review.yml/badge.svg)](https://github.com/crosspostly/content-factory/actions/workflows/ai-code-review.yml)
[![Code Quality](https://github.com/crosspostly/content-factory/actions/workflows/code-quality.yml/badge.svg)](https://github.com/crosspostly/content-factory/actions/workflows/code-quality.yml)
[![Tests](https://github.com/crosspostly/content-factory/actions/workflows/tests.yml/badge.svg)](https://github.com/crosspostly/content-factory/actions/workflows/tests.yml)
```

---

## 🔄 Workflow Dependencies

```
Push to main/develop
    ↓
┌─────────────────────────────────────┐
│ Parallel Execution:                 │
├─────────────────────────────────────┤
│ 1. tests.yml (2-3 min)             │
│ 2. code-quality.yml (2-3 min)      │
│ 3. ai-code-review.yml (1-2 min)    │ (только PR)
│ 4. todo-to-issue.yml (1 min)       │
└─────────────────────────────────────┘
    ↓ (когда все завершены)
    ↓
notifications.yml → 📱 Telegram alert
```

---

## 🐛 Troubleshooting

### Workflow не запускается
- ✅ Проверь ветку (должна быть `main` или `develop`)
- ✅ Проверь `on:` условие в YAML
- ✅ Проверь, что файл сохранён в `.github/workflows/`

### Workflow падает с ошибкой
- ✅ Кликни на workflow → видишь лог с ошибкой
- ✅ Проверь Secrets настройки
- ✅ Проверь права доступа (GITHUB_TOKEN)

### Codecov не получает данные
- ✅ Проверь, что pytest запускается с `--cov=core --cov-report=xml`
- ✅ Проверь, что `coverage.xml` генерируется

### Telegram не отправляет уведомления
- ✅ Проверь `TELEGRAM_BOT_TOKEN` и `TELEGRAM_CHAT_ID` в Secrets
- ✅ Проверь, что бот может писать в указанный чат

---

## 📚 Полезные ссылки

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [MegaLinter](https://megalinter.io/)
- [Codecov](https://codecov.io/)
- [Release Drafter](https://github.com/release-drafter/release-drafter)
- [Telegram Bot API](https://core.telegram.org/bots/api)

---

**Последнее обновление:** December 13, 2025
**Версия:** 2.0 (с поддержкой Gemini 2.5 Flash и полным CI/CD)
