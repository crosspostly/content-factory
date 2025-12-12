# 📊 GitHub Actions Workflows

## 🎯 Part 1 MVP Test Workflow

**Файл:** `.github/workflows/part1-test.yml`

### 🥒 Как Запустить?

#### **Способ 1: Ручной Запуск (Manual Trigger) - Рекомендуется!**

1. Открй репо на GitHub
2. Перейди на вкладку **"Actions"** (вверху)
3. Слева найди **"🎯 Part 1 MVP Test"**
4. Нажми **"Run workflow"**

```
https://github.com/crosspostly/content-factory/actions
↓
Выбери "Part 1 MVP Test" (слева)
↓
Нажми кнопку "Run workflow" (обычная зелёная кнопка)
↓
Выбери параметры:
   - Mode: shorts (или long_form, ad)
   - Project: youtube_horoscope
   - Dry Run: true (или false для upload)
↓
Нажми "Run workflow"
```

#### **Способ 2: Автоматически (на каждый push в main)**

Просто сделай `git push` в main — workflow запустится автоматически.

---

### 📋 Параметры Workflow

| Параметр | Вариант | Что Делает |
|----------|---------|----------|
| **Mode** | `shorts` | Генерирует короткое видео (30-60 сек) |
| | `long_form` | Генерирует длинное видео (20-45 мин) |
| | `ad` | Генерирует рекламное видео |
| **Project** | `youtube_horoscope` | Используется проект гороскопов |
| | Другое | Любое имя проекта из `projects/` |
| **Dry Run** | `true` ⭐ | Генерирует, но НЕ загружает на YouTube |
| | `false` | Генерирует И загружает (Part 5) |

---

### 💳 Пример: Генерировать Shorts (No Upload)

```
Режим выполнения:
  • Workflow: Part 1 MVP Test
  • Mode: shorts
  • Project: youtube_horoscope
  • Dry Run: true ← ✅ НЕ ЗАГРУЖАЕМ

Результат:
  ✅ output/scripts/youtube_horoscope/2025-12-12/short_uuid.json
  ✅ output/audio/youtube_horoscope/shorts.wav
  ✅ output/videos/youtube_horoscope/shorts.mp4
  
  Артефакты можно скачать!
```

---

### 🔒 Secrets (GitHub Actions Secrets)

Если ты хочешь использовать `--upload` (Dry Run = false), нужны secrets:

**Перейди в Settings → Secrets and variables → Actions:**

```
GOOGLE_AI_API_KEY          # Для Gemini (Part 3)
OPENROUTER_API_KEY         # Fallback LLM (Part 3)
YOUTUBE_API_KEY            # YouTube upload (Part 5)
TELEGRAM_BOT_TOKEN         # Уведомления (optional)
TELEGRAM_CHAT_ID           # Где писать (optional)
```

**НА ТЕКУЩЕЙ ЭТАПЕ (Part 1):**
- Для `--dry-run` → secrets не нужны ✅
- Для `--upload` → нужны YouTube_API_KEY (Part 5)

---

### 📊 Что Происходит в Workflow?

```yaml
1. Checkout code                    # Скачиваю репо
2. Setup Python 3.11               # Ставлю Python
3. Install dependencies            # pip install
4. Generate Content ⭐️             # python -m core.orchestrators...
5. Check Output Artifacts          # Показываю созданные файлы
6. Upload Artifacts                # Архивирую output/ для скачивания
7. Success/Failure Notification    # Алерт в Telegram (если есть)
```

---

### 📁 Где Скачать Результаты?

После завершения workflow:

1. Перейди на **Actions** вкладку
2. Найди последний запуск (зелёная галочка)
3. Нажми на него
4. В секции **"Artifacts"** есть архив:
   - `content-factory-output.zip` (7 дней)

**Внутри архива:**
```
content-factory-output/
├── scripts/youtube_horoscope/2025-12-12/
│   └── short_a1b2c3d4.json
├── audio/youtube_horoscope/
│   └── shorts.wav
├── videos/youtube_horoscope/
│   └── shorts.mp4
└── logs/youtube_horoscope/
    └── 2025-12-12.log
```

---

### 🏷️ GitHub Actions URL

```
https://github.com/crosspostly/content-factory/actions/workflows/part1-test.yml
```

Это прямая ссылка на workflow. Открой, и сразу видишь все запуски.

---

### 🔎 Как Проверить Логи?

1. Перейди на **Actions** → последний запуск
2. Нажми на job **"Generate Content (Part 1 MVP)"`
3. Разверни шаги ("Steps"):
   - Checkout code
   - Setup Python
   - **← Здесь логи основного генератора**
   - Check Output Artifacts ← Файлы которые создались

**Если ошибка:**

```
Step: Generate Content (Mode: shorts)
↓
Это покажет:
  - Ошибки Python
  - Config loading issues
  - Missing files
  - Etc
```

---

## 📄 Пример: Реальный Запуск

### **Сценарий 1: Генерировать Shorts (Сухой Запуск)**

```
1. Открыл: https://github.com/crosspostly/content-factory/actions
2. Нажал "Part 1 MVP Test"
3. Нажал "Run workflow"
4. Выбрал:
   - Mode: shorts
   - Project: youtube_horoscope
   - Dry Run: true
5. Нажал "Run workflow" (зелёная кнопка)

⏳ Ждал 2-3 минуты

✅ Результат:
   - Скрипт: output/scripts/youtube_horoscope/2025-12-12/short_uuid.json
   - Аудио: output/audio/youtube_horoscope/shorts.wav (молчание, Part 2)
   - Видео: output/videos/youtube_horoscope/shorts.mp4 (пусто, Part 4)
   - Логи: output/logs/youtube_horoscope/2025-12-12.log

📥 Скачал архив "content-factory-output.zip"
📊 Посмотрел JSON скрипт
✅ Part 1 MVP работает!
```

---

### **Сценарий 2: Генерировать Long-Form**

```
1. Workflow: Part 1 MVP Test
2. Mode: long_form
3. Project: youtube_horoscope
4. Dry Run: true
5. Run!

✅ Результат: Скрипт для длинного видео
   "video_title": "Полный гороскоп на 2025-12-12",
   "blocks": {
     "love": "Любовные перспективы...",
     "money": "Финансовые прогнозы...",
     "health": "Здоровье и благополучие..."
   }
```

---

## 📕 ВАЖНО!

### Part 1 (MVP):
- ✅ Workflow запускается
- ✅ Скрипты генерируются
- ✅ Файлы сохраняются
- ❌ Аудио молчит (Part 2)
- ❌ Видео пусто (Part 4)
- ❌ Upload не работает (Part 5)

### Part 2+:
- Когда добавим Real TTS → аудио будет голос
- Когда добавим Real Video → видео будет с фонами
- Когда добавим Upload → `--upload` будет работать

---

## 🚀 Next Steps

**Что сейчас:**
1. Открыть Actions на GitHub
2. Нажать "Run workflow"
3. Выбрать параметры
4. Скачать артефакты
5. Проверить структуру

**Что дальше (Part 2):**
- Real Edge-TTS / Gemini TTS
- Audio blocks synthesis
- Workflow обновится автоматически

---

**Тестировать можно прямо в GitHub, никакой локальной машины не нужно!** 🚀
