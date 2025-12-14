# План реализации субтитров (Part 4)

**Статус**: 🔮 PLANNING  
**Дата**: 14 Декабря 2025  
**Зависимость**: Part 3 (Video Rendering) - MVP готов

## Текущее состояние

### ✅ Что уже синхронизировано
- **Audio + Video синхронизированы**
  - Audio duration известна
  - Video duration = audio duration  
  - MoviePy правильно смешивает их
  - ModelRouter статистика записывается в metadata

### ❌ Что НЕ реализовано в Part 3
- **Субтитры полностью отсутствуют**
  - В video_renderer.py нет логики для SRT
  - Нет распознавания речи
  - Нет встраивания в MP4
  - README ложно упоминает "SubtitleX (WhisperX, ffsubsync)"

## План реализации (4 недели)

### 📅 Week 1: Распознавание речи (WhisperX)

#### Установка и настройка
```bash
pip install whisper-x
# или
pip install openai-whisper

# Проверка
python -c "import whisper; print(whisper.load_model('base').device)"
```

#### Интеграция в pipeline
```python
# core/generators/subtitle_generator.py (НОВЫЙ)
import whisper

class SubtitleGenerator:
    def __init__(self, model_name: str = "large-v3"):
        self.model = whisper.load_model(model_name)
        
    def transcribe_audio(self, audio_path: str, language: str = "ru") -> list[dict]:
        """Получить сегменты с timestamps"""
        result = self.model.transcribe(audio_path, language=language)
        
        segments = []
        for seg in result["segments"]:
            segments.append({
                "start": seg["start"],
                "end": seg["end"], 
                "text": seg["text"].strip()
            })
        return segments
```

#### Тестирование
```python
# tests/test_subtitle_generator.py
def test_whisper_transcription():
    generator = SubtitleGenerator("base")
    segments = generator.transcribe_audio("test_audio.wav")
    assert len(segments) > 0
    assert all("start" in seg and "end" in seg for seg in segments)
```

### 📅 Week 2: Генерация SRT/VTT

#### SRT генерация
```python
def whisper_to_srt(segments: list[dict]) -> str:
    """Конвертировать Whisper output в SRT"""
    srt_content = ""
    for i, seg in enumerate(segments, 1):
        start = format_timestamp(seg["start"], "srt")
        end = format_timestamp(seg["end"], "srt")
        srt_content += f"{i}\n{start} --> {end}\n{seg['text']}\n\n"
    return srt_content

def format_timestamp(seconds: float, format_type: str) -> str:
    """Форматировать время для SRT/VTT"""
    if format_type == "srt":
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:06.3f}".replace(".", ",")
    else:  # VTT
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"
```

#### Конфигурация субтитров
```yaml
# projects/youtube_horoscope/config.yaml
subtitles:
  enabled: true
  auto_generate: true
  language: "ru"
  model: "large-v3"  # whisper model
  format: "srt"  # srt|vtt
  embed_in_video: true
  
  # Стиль субтитров
  style:
    font_size: 24
    color: "white"
    background_color: "black"
    position: "bottom"  # top|bottom|center
    opacity: 0.8
    margin_v: 50  # отступ от края
```

### 📅 Week 3: Интеграция в видеорендерер

#### Обновление video_renderer.py
```python
# core/generators/video_renderer.py
from core.generators.subtitle_generator import SubtitleGenerator

class VideoRenderer:
    def __init__(self, config: ProjectConfig):
        self.config = config
        if config.subtitles.enabled:
            self.subtitle_gen = SubtitleGenerator(config.subtitles.model)
            
    def render_with_subtitles(self, script: dict, audio_path: str, output_path: Path):
        """Рендер с субтитрами"""
        
        # 1. Генерировать субтитры
        if self.config.subtitles.auto_generate:
            segments = self.subtitle_gen.transcribe_audio(
                str(audio_path), 
                self.config.subtitles.language
            )
            
            # 2. Создать SRT файл
            srt_path = output_path.with_suffix('.srt')
            srt_content = whisper_to_srt(segments)
            srt_path.write_text(srt_content, encoding='utf-8')
            
            # 3. Встроить в видео
            if self.config.subtitles.embed_in_video:
                self._embed_subtitles_in_video(
                    video_path, srt_path, output_path
                )
        else:
            # Использовать готовый SRT файл
            pass
```

#### FFmpeg команды для встраивания
```python
def _embed_subtitles_in_video(self, video_path: Path, srt_path: Path, output_path: Path):
    """Встроить субтитры через FFmpeg"""
    
    # Вариант 1: Встроенные субтитры (recommended)
    cmd = [
        "ffmpeg",
        "-i", str(video_path),
        "-i", str(srt_path),
        "-c", "copy",
        "-c:s", "mov_text",
        "-map", "0:v",
        "-map", "0:a", 
        "-map", "1:s",
        str(output_path)
    ]
    
    # Вариант 2: Hard subtitles (рендерить в видео)
    cmd = [
        "ffmpeg", 
        "-i", str(video_path),
        "-vf", f"subtitles={srt_path}:force_style='Fontsize=24,PrimaryColour=&Hffffff,OutlineColour=&H0,BackColour=&H80000000'",
        "-c:a", "copy",
        str(output_path)
    ]
```

### 📅 Week 4: Тестирование и конфигурация

#### Обновление pipeline orchestrator
```python
# core/orchestrators/pipeline_orchestrator.py
def main():
    # Существующая логика...
    
    # Добавить генерацию субтитров
    if config.subtitles.enabled:
        logger.info("🎬 Generating subtitles...")
        # Генерировать субтитры после рендеринга видео
        subtitle_path = subtitle_generator.generate_from_audio(
            audio_path, config.subtitles
        )
        
        # Встроить в видео
        if config.subtitles.embed_in_video:
            final_video = subtitle_generator.embed_in_video(
                video_path, subtitle_path
            )
```

#### Тестирование полного цикла
```python
def test_full_subtitle_pipeline():
    """Тест полной цепочки с субтитрами"""
    config = load_project_config("youtube_horoscope")
    config.subtitles.enabled = True
    
    # Генерировать видео с субтитрами
    result = pipeline_orchestrator.main(
        project="youtube_horoscope",
        mode="shorts", 
        date="2025-12-14"
    )
    
    # Проверить что видео содержит субтитры
    assert result.video_path.exists()
    
    # Проверить SRT файл
    srt_path = Path(result.video_path).with_suffix('.srt')
    assert srt_path.exists()
    
    # Проверить содержание SRT
    srt_content = srt_path.read_text(encoding='utf-8')
    assert "1\n" in srt_content
    assert "-->" in srt_content
```

## Конфигурация в проектах

### Обновление config.yaml
```yaml
# projects/youtube_horoscope/config.yaml
subtitles:
  enabled: true
  auto_generate: true
  language: "ru"
  model: "large-v3"  # base|small|medium|large|large-v3
  
  # Формат вывода
  format: "srt"  # srt или vtt
  embed_in_video: true
  
  # Стиль субтитров (когда рендерятся в видео)
  style:
    font_size: 24
    color: "white"
    background_color: "black" 
    position: "bottom"
    opacity: 0.8
    margin_v: 50
```

### Опции конфигурации
```yaml
subtitles:
  # Включение/отключение
  enabled: true|false
  
  # Источник субтитров
  auto_generate: true|false  # генерировать автоматически
  source_file: "path/to/subtitles.srt"  # или использовать готовый файл
  
  # Параметры Whisper
  language: "ru"  # язык распознавания
  model: "large-v3"  # размер модели (скорость vs качество)
  
  # Формат и встраивание
  format: "srt|vtt"  # формат файла
  embed_in_video: true|false  # встроить в MP4 или оставить отдельным файлом
  
  # Стилизация (для hard subtitles)
  style:
    font_name: "Arial"  # шрифт
    font_size: 24       # размер
    color: "white"      # цвет текста  
    outline_color: "black"  # цвет обводки
    background_color: "black"  # фон субтитров
    position: "bottom|top|center"  # позиция
    margin_v: 50        # отступ от края (пиксели)
    opacity: 0.8        # прозрачность фона
```

## Модели Whisper (скорость vs качество)

| Модель | Размер | Скорость | Качество | Память | Рекомендация |
|--------|--------|----------|----------|--------|--------------|
| **tiny** | 39 MB | Очень быстро | Низкое | 1 GB | Быстрое тестирование |
| **base** | 74 MB | Быстро | Среднее | 1 GB | Хороший баланс |
| **small** | 244 MB | Медленно | Хорошее | 2 GB | Production рекомендуемая |
| **medium** | 769 MB | Медленно | Очень хорошее | 5 GB | Высокое качество |
| **large** | 1550 MB | Очень медленно | Лучшее | 10 GB | Максимальное качество |
| **large-v3** | 1550 MB | Очень медленно | Лучшее+ | 10 GB | Последняя версия |

## Возможные проблемы и решения

### Performance Issues
```python
# Проблема: Whisper медленный для длинных аудио
# Решение: Параллельная обработка
import asyncio

async def transcribe_segments(audio_path: str):
    # Разбить аудио на сегменты
    segments = split_audio_into_segments(audio_path, max_duration=30)
    
    # Параллельно обработать
    tasks = [transcribe_segment(seg) for seg in segments]
    results = await asyncio.gather(*tasks)
    
    return merge_results(results)
```

### Accuracy Issues  
```python
# Проблема: Низкая точность для русского языка
# Решение: Постобработка текста

def post_process_russian_text(text: str) -> str:
    """Улучшить качество русского текста"""
    # Исправить капитализацию
    text = re.sub(r'\.\s+([а-я])', lambda m: '. ' + m.group(1).upper(), text)
    
    # Исправить знаки препинания
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text
```

### Memory Issues
```python
# Проблема: Большие модели требуют много памяти
# Решение: Динамическая загрузка

class LazyWhisperModel:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.model = None
        
    def get_model(self):
        if self.model is None:
            self.model = whisper.load_model(self.model_name)
        return self.model
```

## Ожидаемые результаты

### После реализации Part 4:
- ✅ **Автоматические субтитры** для всех видео
- ✅ **Высокая точность** распознавания русской речи  
- ✅ **Встроенные субтитры** в MP4 файлы
- ✅ **Кастомизация стилей** через config
- ✅ **SRT/VTT файлы** для ручного редактирования

### Production готовность:
- **Время обработки**: +2-5 минут к рендерингу видео
- **Точность**: 90-95% для четкой русской речи
- **Форматы**: SRT (совместимость), VTT (веб)
- **Стили**: Полная кастомизация через config

---

**Критично**: Part 4 требует значительных ресурсов (память CPU/GPU) для Whisper модели. Рекомендуется start с "base" модели и upgrade при необходимости.