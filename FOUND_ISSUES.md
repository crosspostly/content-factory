# Found Issues & Improvements

## 🚨 Critical Bugs

### 1. Video Renderer Incomplete Logic
**Файл**: `core/generators/video_renderer.py`
**Строка**: 88-99
**Проблема**: Незавершённая логика для Pixabay video API
```python
# BROKEN CODE:
for fmt in ["large", "medium", "small", "tiny"]: # Comment indicates wrong format
     # But the ticket code had ["360", "720", "1080"]. Pixabay API usually has "large", "medium", "small", "tiny".
     # Actually Pixabay API response structure:
     # "videos": { "large": { "url": ... }, "medium": { ... }, ... }
     # Or sometimes specific resolutions.
     # Let's check what the ticket code assumed.
     pass
```
**Impact**: Средний - fallback на gradient backgrounds работает
**Fix**: Завершить логику для Pixabay video formats или удалить неиспользуемый код

### 2. Missing Error Handling in Batch Generator
**Файл**: `core/generators/batch_generator.py`
**Строка**: 105
**Проблема**: Не обрабатываются ошибки ModelRouter.get_stats() если router не инициализирован
```python
# Potential crash if no successful scripts generated
router = get_router(api_key)
stats = router.get_stats()  # May be empty if nothing succeeded
```
**Impact**: Низкий - обычно всегда есть успешные скрипты
**Fix**: Добавить проверку `if stats.get('total_attempts', 0) > 0`

---

## ⚠️ Potential Issues

### 3. Config Validation Edge Cases
**Файл**: `core/utils/config_loader.py`
**Проблема**: Возможны проблемы с merge shared.yaml файлов
```python
# Lines 188-196: Deep merge logic
shared_raw = yaml.safe_load(shared_path.read_text(encoding="utf-8")) or {}
if isinstance(shared_raw, dict):
    raw = _deep_merge(shared_raw, raw)
```
**Potential Issue**: Если shared.yaml содержит `project.name`, он может быть перезаписан
**Impact**: Средний - может привести к неожиданному поведению
**Fix**: Добавить проверку на конфликтующие ключи

### 4. Model Router Singleton Memory Leak
**Файл**: `core/utils/model_router.py`
**Проблема**: ModelRouter instance живет на протяжении всего процесса
```python
_router_instance: Optional[ModelRouter] = None

def get_router(api_key: str) -> ModelRouter:
    global _router_instance
    if _router_instance is None:
        _router_instance = ModelRouter(api_key)
    return _router_instance
```
**Potential Issue**: В длительных процессах может накапливаться память в статистике
**Impact**: Низкий - статистика небольшая
**Fix**: Добавить метод `reset_stats()` или ограничить размер статистики

### 5. Edge-TTS Rate Limiting Without Backoff
**Файл**: `core/generators/tts_generator.py`
**Проблема**: Нет retry логики при 403 ошибках от Microsoft
```python
# No retry logic implemented
communicate = edge_tts.Communicate(text, voice, rate=f"{int(speed * 100)}%")
await communicate.save(str(output_path))
```
**Potential Issue**: При rate limiting весь batch может падать
**Impact**: Высокий для batch генерации
**Fix**: Добавить retry с exponential backoff для Edge-TTS

---

## 🏗️ Code Smells

### 6. Duplicate String Constants
**Файлы**: `core/generators/script_generator.py`
**Проблема**: Магические строки повторяются в коде
```python
# Multiple occurrences of these strings:
"Гороскоп на сегодня."
"Специальное предложение для вас."
"Подпишись на канал!"
```
**Impact**: Низкий - только maintainability
**Fix**: Вынести в константы класса

### 7. Large Function in Pipeline Orchestrator
**Файл**: `core/orchestrators/pipeline_orchestrator.py`
**Функция**: `main()`
**Проблема**: Функция делает слишком много (200+ строк)
**Impact**: Средний - сложно тестировать и поддерживать
**Fix**: Разбить на smaller helper functions

### 8. Hardcoded File Paths
**Файлы**: Multiple
**Проблема**: Пути к файлам захардкожены как строки
```python
# Example from tts_generator.py
output_path = Path("output") / "audio" / project_slug / "shorts_main.wav"
```
**Impact**: Низкий - но может затруднить конфигурацию
**Fix**: Добавить config section для output paths

### 9. Inconsistent Error Message Format
**Проблема**: Разные стили ошибок в логах
```python
logger.error(f"❌ Gemini TTS error: {e}")  # Emoji style
logging_utils.log_error(f"Config not found: {e}")  # Plain style
logger.warning(f"Voice config error: {e}")  # Warning style
```
**Impact**: Низкий - только UX в логах
**Fix**: Стандартизировать формат логирования

---

## 📊 Performance Issues

### 10. Inefficient String Building in Loops
**Файл**: `core/generators/script_generator.py`
**Функция**: `_build_horoscope_prompt()`
**Проблема**: Конкатенация строк в цикле (не обнаружено, но типично)
**Impact**: Низкий для текущих объемов
**Fix**: Использовать f-strings или list.join()

### 11. No Connection Pooling for HTTP Requests
**Файл**: `core/generators/video_renderer.py`
**Проблема**: Каждый Pixabay API запрос создает новое соединение
```python
response = requests.get(PIXABAY_VIDEOS_API, params=params, timeout=10)
```
**Impact**: Средний при массовых запросах
**Fix**: Использовать `requests.Session()`

### 12. Unnecessary File I/O Operations
**Проблема**: Некоторые файлы читаются несколько раз
**Пример**: Config файлы могут перечитываться
**Impact**: Низкий для локальных файлов
**Fix**: Добавить кэширование

---

## 🔧 Technical Debt

### 13. Deprecated Model References
**Файл**: `core/utils/model_router.py` (исправлено)
**Было**: `gemini-2.5-flash`, `gemini-2.5-flash-lite` (не существуют)
**Статус**: ✅ Исправлено на `gemini-2.0-flash-exp`, `gemini-1.5-flash`

### 14. Unused Import in Auto-Fix Agent
**Файл**: `core/auto_fix_agent.py`
**Проблема**: Импорты Qwen/OpenRouter когда они не используются
```python
# Likely unused imports from Qwen/OpenRouter integration
import openai  # Not used in current logic
import ollama   # Not used in current logic
```
**Impact**: Низкий - не влияет на функциональность
**Fix**: Удалить неиспользуемые импорты

### 15. Legacy Error Handling Patterns
**Проблема**: Mixed approaches to error handling
```python
# Old pattern:
except Exception as e:
    logger.error(f"Error: {e}")
    raise

# New pattern (preferred):
except SpecificError as e:
    logger.error(f"Detailed error: {e}")
    return fallback_value
```
**Impact**: Средний - непоследовательность
**Fix**: Стандартизировать паттерны error handling

### 16. Inconsistent Type Hints
**Проблема**: Mixed typing approaches
```python
# Some functions use full typing
def function(param: str) -> dict[str, Any]:

# Others use minimal typing  
def function(param):
    return {}
```
**Impact**: Низкий - но ухудшает IDE support
**Fix**: Добавить type hints везде

---

## 📦 Deprecated Patterns

### 17. Old Qwen/OpenRouter Integration (Inactive)
**Файлы**: Multiple test files
**Статус**: Код остался, но не используется в production
**Impact**: Низкий - может сбивать с толку новых разработчиков
**Fix**: Удалить или закомментировать неиспользуемый код

### 18. Legacy Config Loading Logic
**Файл**: `core/utils/config_loader.py`
**Проблема**: Поддержка старых форматов когда актуальны только YAML
```python
# Old support for JSON configs (likely unused)
elif path.suffix.lower() == ".json":
    raw = json.loads(path.read_text(encoding="utf-8"))
```
**Impact**: Низкий - код не мешает
**Fix**: Удалить поддержку JSON если не нужна

### 19. Manual String Manipulation
**Проблема**: Использование regex вместо структурированного парсинга
```python
# From tts_generator.py
text = re.sub(r'<[^>]+>', '', text)  # HTML removal
text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Markdown bold removal
```
**Impact**: Низкий - работает, но хрупко
**Fix**: Использовать proper HTML/Markdown parsers

---

## 🔍 Hardcoded Values

### 20. Magic Numbers in Video Configuration
**Файл**: `core/generators/video_renderer.py`
```python
VIDEO_CONFIG = {
    "shorts": {
        "width": 1080,      # Hardcoded
        "height": 1920,     # Hardcoded
        "bitrate": "5000k", # Hardcoded
    }
}
```
**Impact**: Средний - затрудняет конфигурацию
**Fix**: Вынести в config файл

### 21. TTS Duration Estimation
**Файл**: `core/generators/tts_generator.py`
```python
duration = max(len(text) / 10.0 * (2.0 - speed), 1.0)
```
**Проблема**: Magic number `10.0` и `2.0` без объяснения
**Impact**: Низкий - estimation работает достаточно хорошо
**Fix**: Добавить константы с комментариями

### 22. Audio Sample Rate Constants
**Файл**: `core/generators/tts_generator.py`
```python
OUTPUT_SAMPLE_RATE = 22050  # Why 22050 specifically?
OUTPUT_CHANNELS = 1         # Why mono?
```
**Impact**: Низкий - стандартные значения
**Fix**: Добавить комментарии объясняющие выбор

---

## 🧪 Testing Gaps

### 23. Missing Integration Tests
**Проблема**: Мало тестов end-to-end pipeline
**Coverage**: Большинство тестов unit-level
**Impact**: Средний - может не ловить integration issues
**Fix**: Добавить tests/test_pipeline_endtoend.py

### 24. No Load Testing
**Проблема**: Нет тестов для batch generation под нагрузкой
**Impact**: Низкий для текущего использования
**Fix**: Добавить load tests для batch_generator

### 25. Insufficient Edge Case Testing
**Проблема**: Мало тестов для error conditions
**Examples**: Empty configs, API failures, missing files
**Impact**: Средний - может привести к runtime failures
**Fix**: Добавить negative tests

---

## 🔄 Workflow Issues

### 26. Too Many GitHub Workflow Files
**Папка**: `.github/workflows/`
**Проблема**: Множество workflow файлов может запутать
**Current**: 6+ workflow файлов
**Impact**: Низкий - но усложняет maintenance
**Fix**: Консолидация или better organization

### 27. Inconsistent Job Naming
**Проблема**: Разные naming conventions в workflows
```yaml
jobs:
  test:                    # Simple name
  generate-content:        # Hyphenated
  batch_generation:        # Underscored
  auto_fix_agent:          # Underscored
```
**Impact**: Низкий - косметическая проблема
**Fix**: Стандартизировать naming convention

---

## 📝 Documentation Issues

### 28. Removed Documentation Debt ✅
**Статус**: Исправлено в рамках этого аудита
**Удалено**: 26 мусорных .md файлов
**Создано**: 
- README.md (для пользователей, <500 строк)
- ARCHITECTURE.md (для разработчиков, >1000 строк)
- FOUND_ISSUES.md (этот файл)

### 29. Code Comments Quality
**Проблема**: Mixed quality comments
- Некоторые функции перекомментированы
- Некоторые critical sections не имеют комментариев
**Impact**: Низкий
**Fix**: Улучшить docstrings и критические комментарии

---

## 🎯 Prioritized Fix List

### High Priority (Fix Soon)
1. **Video Renderer Pixabay Logic** - завершить или удалить
2. **Edge-TTS Rate Limiting** - добавить retry с backoff
3. **Batch Generator Error Handling** - исправить potential crash

### Medium Priority (Fix Next Release)
4. **Config Validation Edge Cases** - улучшить merge logic
5. **Large Pipeline Function** - рефакторинг на smaller functions
6. **Integration Tests** - добавить end-to-end coverage

### Low Priority (Nice to Have)
7. **String Constants** - вынести magic strings
8. **Type Hints** - добавить везде
9. **Documentation** - улучшить комментарии

---

## 📈 Improvement Opportunities

### Performance Optimizations
- Connection pooling для HTTP requests
- Config file caching
- Async processing improvements

### User Experience
- Better error messages
- Progress indicators для batch operations
- More detailed logging levels

### Developer Experience
- Better IDE support с type hints
- Consistent code style
- Automated code formatting

### Scalability
- Support для multiple projects parallel
- Resource usage optimization
- Better caching strategies

---

Этот документ должен обновляться при каждом significant code change или обнаружении новых проблем.