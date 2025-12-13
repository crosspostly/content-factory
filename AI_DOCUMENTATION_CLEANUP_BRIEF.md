# 🤖 AI Agent Brief: Documentation Cleanup Task

## 📋 Задача для ИИ-агента

**Название:** Documentation Cleanup - Remove Duplicate Files  
**Приоритет:** Medium  
**Сложность:** Simple  
**Время:** 5 минут  
**Статус:** 🔘 Ready to Assign  

---

## 🎯 Что нужно сделать

В репозитории скопилось 5+ дублирующихся файлов документации. Нужно удалить все лишние, оставив только одну истину.

### ❌ Удалить эти файлы (ВСЕ ДУБЛИ)

1. **`CONTENT_MODES_IMPLEMENTATION.md`** (root)
   - 📏 Размер: 8KB
   - 🔗 Ссылается на: то же, что COMPLETE_GUIDE.md
   - ❓ Почему: Дублирует информацию из `docs/CONTENT_MODES_COMPLETE_GUIDE.md`

2. **`CONTENT_MODES_DETAILED_GUIDE.md`** (root)
   - 📏 Размер: 15KB
   - 🔗 Ссылается на: то же, что COMPLETE_GUIDE.md
   - ❓ Почему: Большой дубль основного гайда

3. **`IMPLEMENTATION_COMPLETE.md`** (root)
   - 📏 Размер: 6KB
   - 🔗 Ссылается на: статус реализации
   - ❓ Почему: Информация устарела, есть Issue #24

4. **`docs/CONTENT_MODES_GUIDE.md`** (если существует в docs/)
   - 📏 Размер: 5KB
   - 🔗 Ссылается на: систему Content Modes
   - ❓ Почему: Старая версия, заменена на COMPLETE_GUIDE.md

### ✅ Оставить эти файлы (ИСТОЧНИК ИСТИНЫ)

1. **`docs/CONTENT_MODES_COMPLETE_GUIDE.md`** ← ГЛАВНЫЙ ГАЙД
   - 📏 Размер: 10KB
   - 📍 Путь: `/docs/CONTENT_MODES_COMPLETE_GUIDE.md`
   - ✨ Содержит: Полную документацию, примеры, FAQ, архитектуру
   - 🔗 GitHub: https://github.com/crosspostly/content-factory/blob/main/docs/CONTENT_MODES_COMPLETE_GUIDE.md

2. **`docs/README.md`** ← НАВИГАЦИЯ
   - 📏 Размер: 3KB
   - 📍 Путь: `/docs/README.md`
   - ✨ Содержит: Таблицу выбора, быстрые ссылки
   - 🔗 GitHub: https://github.com/crosspostly/content-factory/blob/main/docs/README.md

3. **`README.md`** ← ГЛАВНЫЙ README
   - 📏 Размер: Существующий (обновлён)
   - 📍 Путь: `/README.md`
   - ✨ Содержит: Общую информацию о проекте
   - 🔗 GitHub: https://github.com/crosspostly/content-factory/blob/main/README.md

### 📊 GitHub Issues (для контекста)

- **Issue #24:** https://github.com/crosspostly/content-factory/issues/24
  - Содержит: Полный техспек Content Modes System
  - Статус: ✅ Открыта
  - Зачем: Это техническое ТЗ, дополняет гайд

- **Issue #25:** https://github.com/crosspostly/content-factory/issues/25
  - Название: "Cleanup: Remove duplicate documentation files"
  - Содержит: Checklist что удалить
  - Статус: ✅ Открыта
  - Зачем: Отслеживает процесс cleanup

---

## 🛠️ Как удалить файлы

### Способ 1: Через GitHub Web UI (ПРОСТЕЙШИЙ)

1. Открыть файл
2. Нажать кнопку Delete (🗑️)
3. Commit напрямую в main

### Способ 2: Git Command Line (ПРАВИЛЬНЫЙ)

```bash
# 1. Клонировать репо
git clone https://github.com/crosspostly/content-factory.git
cd content-factory

# 2. Удалить файлы
git rm CONTENT_MODES_IMPLEMENTATION.md
git rm CONTENT_MODES_DETAILED_GUIDE.md
git rm IMPLEMENTATION_COMPLETE.md
if [ -f docs/CONTENT_MODES_GUIDE.md ]; then git rm docs/CONTENT_MODES_GUIDE.md; fi

# 3. Коммит с информативным сообщением
git commit -m "chore: Remove duplicate documentation files

- Remove CONTENT_MODES_IMPLEMENTATION.md (duplicate of COMPLETE_GUIDE)
- Remove CONTENT_MODES_DETAILED_GUIDE.md (large duplicate)
- Remove IMPLEMENTATION_COMPLETE.md (outdated status)
- Remove docs/CONTENT_MODES_GUIDE.md (old version)

All content preserved in docs/CONTENT_MODES_COMPLETE_GUIDE.md
References: Issue #25"

# 4. Запушить
git push origin main
```

### Способ 3: Через PR (ЛУЧШИЙ ВАРИАНТ)

```bash
# 1-2. (как выше)

# 3. Создать ветку для PR
git checkout -b cleanup/remove-duplicate-docs
git commit -m "chore: Remove duplicate documentation"
git push origin cleanup/remove-duplicate-docs

# 4. Открыть PR на GitHub
# Title: "chore: Remove duplicate documentation files"
# Body: (см. ниже)
```

**PR Description (скопировать):**
```markdown
## Description

Removes all duplicate documentation files that have been consolidated into `docs/CONTENT_MODES_COMPLETE_GUIDE.md`.

## Files Deleted

- ❌ `CONTENT_MODES_IMPLEMENTATION.md` (8KB)
- ❌ `CONTENT_MODES_DETAILED_GUIDE.md` (15KB)
- ❌ `IMPLEMENTATION_COMPLETE.md` (6KB)
- ❌ `docs/CONTENT_MODES_GUIDE.md` (5KB)

## Files Retained (Source of Truth)

- ✅ `docs/CONTENT_MODES_COMPLETE_GUIDE.md` (main guide)
- ✅ `docs/README.md` (navigation)
- ✅ `README.md` (project overview)

## Why

Documentation cleanup:
- 📉 Reduces repository size by ~34KB
- 🎯 Single source of truth for Content Modes System
- 🧭 Clear navigation through `docs/README.md`
- 📚 All information preserved in consolidated guides

## Related Issues

Closes #25
References #24

## Testing

- [x] Verified all content is in `docs/CONTENT_MODES_COMPLETE_GUIDE.md`
- [x] Verified `docs/README.md` has proper navigation
- [x] Verified `README.md` links are correct
```

---

## 📋 Checklist (для AI агента)

### Перед удалением
- [ ] **Проверить наличие всех файлов**
  ```bash
  ls -la CONTENT_MODES_*.md IMPLEMENTATION_*.md docs/CONTENT_MODES_*.md 2>/dev/null || echo "Files not found or already deleted"
  ```

- [ ] **Убедиться что COMPLETE_GUIDE содержит всю инфу**
  - ✅ Есть примеры конфигов?
  - ✅ Есть FAQ?
  - ✅ Есть инструкции как добавить режим?
  - ✅ Есть архитектура?

### Удаление
- [ ] Удалить `CONTENT_MODES_IMPLEMENTATION.md`
- [ ] Удалить `CONTENT_MODES_DETAILED_GUIDE.md`
- [ ] Удалить `IMPLEMENTATION_COMPLETE.md`
- [ ] Удалить `docs/CONTENT_MODES_GUIDE.md` (если есть)

### После удаления
- [ ] Проверить что удалено:
  ```bash
  git log --oneline -1
  git show --stat  # должно показать удаленные файлы
  ```

- [ ] Проверить навигацию (кликнуть ссылки)
  - [ ] `docs/README.md` открывается
  - [ ] Ссылка на `CONTENT_MODES_COMPLETE_GUIDE.md` работает
  - [ ] Ссылка на Issue #24 работает

- [ ] Обновить Issue #25
  - Написать комментарий: "✅ Cleanup complete! All duplicate files removed."
  - Закрыть issue как completed

---

## 🎯 Критерии успеха

✅ **Успешно если:**
1. Все 4 дублирующихся файла удалены
2. `docs/CONTENT_MODES_COMPLETE_GUIDE.md` остался на месте
3. `docs/README.md` остался на месте
4. PR/коммит имеет информативное описание
5. Issue #25 обновлен

❌ **Не удалось если:**
- Удалены файлы, которые не дубли (например, main README.md)
- Случайно удалено COMPLETE_GUIDE.md вместо дублей
- Коммит без описания того что было сделано

---

## 📊 Результаты

**До:**
```
34KB документации в 5+ дублирующихся файлах
❌ Сложно найти нужную информацию
❌ Ненужные файлы в корне
```

**После:**
```
10KB документации в 3 хорошо организованных файлах
✅ Единая точка входа (docs/README.md)
✅ Чистая структура репо
✅ 70% экономия места
```

---

## 🔗 Ссылки для справки

- **Issue #24:** https://github.com/crosspostly/content-factory/issues/24 (техспек)
- **Issue #25:** https://github.com/crosspostly/content-factory/issues/25 (cleanup)
- **COMPLETE_GUIDE:** https://github.com/crosspostly/content-factory/blob/main/docs/CONTENT_MODES_COMPLETE_GUIDE.md
- **Navigation:** https://github.com/crosspostly/content-factory/blob/main/docs/README.md

---

## 💡 Советы AI-агенту

1. **Не спешить** — проверить каждый файл перед удалением
2. **Быть информативным** — написать хорошее описание PR/коммита
3. **Документировать** — добавить комментарий в Issue #25
4. **Проверить результат** — убедиться что навигация работает
5. **Использовать PR** — не коммитить напрямую в main

---

**Готово к назначению AI-агенту!** 🤖✨
