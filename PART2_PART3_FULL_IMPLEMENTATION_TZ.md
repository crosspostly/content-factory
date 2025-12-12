# 🎯 ПОЛНОЕ ТЕХНИЧЕСКОЕ ЗАДАНИЕ: Part 2 (TTS) + Part 3 (Video Rendering) + Tests

**Дата:** 12 декабря 2025  
**Версия:** 2.0 (COMPLETE)  
**Статус:** ✅ READY FOR IMPLEMENTATION

---

## 📋 СОДЕРЖАНИЕ

1. [Обзор](#обзор)
2. [Требования](#требования)
3. [Part 2: TTS Generator](#part-2-tts-generator)
4. [Part 3: Video Renderer](#part-3-video-renderer)
5. [Part 4: Integration with Orchestrator](#part-4-integration-with-orchestrator)
6. [Part 5: Testing](#part-5-testing)
7. [Part 6: Logging](#part-6-logging)
8. [Part 7: Проверка окружения](#part-7-проверка-окружения)
9. [Критерии приёмки](#критерии-приёмки)
10. [Примеры использования](#примеры-использования)

---

## ОБЗОР

### Цель

Реализовать **законченные, рабочие** модули для:
- **Part 2:** Синтез речи (TTS) с использованием Edge-TTS
- **Part 3:** Рендеринг видео с использованием MoviePy + FFmpeg
- **Tests:** Полное покрытие тестами всех функций
- **Logging:** Детальное логирование каждого шага

### Контекст

**ЧТО УЖЕ ЕСТЬ:**
- ✅ Part 1: Script Generation (работает)
- ✅ Config loader (YAML)
- ✅ Model router (Gemini API)
- ✅ Pipeline orchestrator (CLI)
- ✅ requirements.txt с зависимостями

**ЧТО НУЖНО СДЕЛАТЬ:**
- ❌ Part 2: TTS Generator (только скелет)
- ❌ Part 3: Video Renderer (только скелет)
- ❌ Tests (нет вообще)
- ❌ Integration (оркестратор не вызывает Part 2/3)

---

## ТРЕБОВАНИЯ

### Системные требования

```bash
# OS
Ubuntu 24.04 (GitHub Actions runner)

# Python
Python 3.11+

# System dependencies
sudo apt-get install -y ffmpeg imagemagick

# Python dependencies (requirements.txt)
google-generativeai==0.7.2
python-dotenv==1.0.1
pyyaml==6.0.2
requests==2.31.0
edge-tts==6.1.0
pydub==0.25.1
moviepy==1.0.3
imageio-ffmpeg==0.4.10
Pillow==10.2.0
numpy==1.24.3
pytest==7.4.3
pytest-asyncio==0.21.1
```

### Переменные окружения

```bash
# Обязательные для Part 1
GOOGLE_AI_API_KEY=<gemini-api-key>

# Обязательные для Part 3
PIXABAY_API_KEY=<pixabay-api-key>

# Опциональные
OPENROUTER_API_KEY=<openrouter-fallback>
TELEGRAM_BOT_TOKEN=<telegram-notifications>
TELEGRAM_CHAT_ID=<telegram-chat>
```

---

## PART 2: TTS GENERATOR

### Файл: `core/generators/tts_generator.py`

#### Требования

1. **Класс `TTSGenerator`**
   - Инициализация с конфигом проекта
   - Поддержка Edge-TTS (Microsoft Azure TTS)
   - Асинхронная генерация аудио
   - Точное измерение длительности через pydub

2. **Методы**

```python
class TTSGenerator:
    def __init__(self, config: ProjectConfig):
        """
        Инициализация TTS генератора
        
        Args:
            config: ProjectConfig из config_loader
        
        Raises:
            ValueError: если конфиг невалидный
        """
        pass
    
    async def synthesize(
        self,
        text: str,
        output_file: str,
        voice: Optional[str] = None,
        rate: float = 1.0
    ) -> dict:
        """
        Синтезировать речь из текста
        
        Args:
            text: Текст для озвучки
            output_file: Путь для сохранения WAV файла
            voice: Голос (default: ru-RU-DariyaNeural)
            rate: Скорость речи (0.5-2.0, default: 1.0)
        
        Returns:
            {
                "audio_path": str,        # Полный путь к WAV файлу
                "duration_sec": float,    # Длительность в секундах
                "sample_rate": int,       # 22050 Hz
                "format": str,            # "wav"
                "voice": str,             # Использованный голос
                "text_length": int        # Длина текста в символах
            }
        
        Raises:
            TTSError: если синтез не удался
            IOError: если не удалось сохранить файл
        """
        pass
    
    def synthesize_blocks(
        self,
        blocks: List[dict],
        output_dir: str = "output/audio"
    ) -> dict:
        """
        Синтезировать блоки скрипта
        
        Args:
            blocks: Список блоков из script JSON
                    [{'type': 'hook', 'text': '...', 'duration_sec': 3}, ...]
            output_dir: Базовая директория для сохранения
        
        Returns:
            {
                "blocks": [
                    {
                        "type": str,
                        "audio_path": str,
                        "duration_sec": float,
                        "text": str
                    },
                    ...
                ],
                "total_duration_sec": float,
                "output_dir": str
            }
        
        Raises:
            TTSError: если синтез хотя бы одного блока не удался
        """
        pass
    
    def merge_audio_files(
        self,
        audio_files: List[str],
        output_file: str
    ) -> dict:
        """
        Объединить несколько аудиофайлов в один
        
        Args:
            audio_files: Список путей к WAV файлам
            output_file: Путь для сохранения объединённого файла
        
        Returns:
            {
                "audio_path": str,
                "duration_sec": float,
                "file_count": int
            }
        
        Raises:
            IOError: если не удалось прочитать/записать файлы
        """
        pass
    
    def _get_audio_duration(self, audio_path: str) -> float:
        """
        Получить точную длительность аудиофайла через pydub
        
        Args:
            audio_path: Путь к WAV файлу
        
        Returns:
            float: Длительность в секундах
        
        Raises:
            IOError: если файл не найден или повреждён
        """
        pass
    
    def _validate_config(self) -> bool:
        """
        Проверить что конфиг содержит все нужные поля
        
        Returns:
            bool: True если конфиг валидный
        
        Raises:
            ValueError: если конфиг невалидный
        """
        pass
```

#### Логирование

**Каждый метод должен логировать:**

```python
import logging

logger = logging.getLogger(__name__)

# При инициализации
logger.info(f"✅ TTSGenerator initialized (voice: {self.voice})")

# При синтезе
logger.info(f"🎤 Synthesizing text ({len(text)} chars) -> {output_file}")
logger.debug(f"Text preview: {text[:50]}...")

# При успехе
logger.info(f"✅ TTS synthesized: {output_file} ({duration:.2f}s)")

# При ошибке
logger.error(f"❌ TTS synthesis failed: {str(e)}")
logger.exception(e)  # С traceback
```

#### Пример использования

```python
from core.generators.tts_generator import TTSGenerator
from core.utils.config_loader import load_project_config
import asyncio

config = load_project_config("youtube_horoscope")
tts = TTSGenerator(config)

# Синтез одного блока
result = asyncio.run(
    tts.synthesize(
        text="Привет, это тест синтеза речи!",
        output_file="output/audio/test.wav"
    )
)
print(result)
# => {
#     "audio_path": "output/audio/test.wav",
#     "duration_sec": 3.2,
#     "sample_rate": 22050,
#     "format": "wav",
#     "voice": "ru-RU-DariyaNeural",
#     "text_length": 33
# }

# Синтез блоков скрипта
blocks_result = tts.synthesize_blocks(
    blocks=[
        {"type": "hook", "text": "Ваш гороскоп на сегодня!"},
        {"type": "content", "text": "Овен: отличный день для новых начинаний..."}
    ],
    output_dir="output/audio/youtube_horoscope"
)
print(blocks_result["total_duration_sec"])
# => 45.3
```

#### Тесты

**Файл:** `tests/test_tts_generator.py`

```python
import pytest
import asyncio
from pathlib import Path
from core.generators.tts_generator import TTSGenerator
from core.utils.config_loader import load_project_config

@pytest.fixture
def tts_generator():
    """Фикстура с инициализированным TTSGenerator"""
    config = load_project_config("youtube_horoscope")
    return TTSGenerator(config)

@pytest.mark.asyncio
async def test_synthesize_simple_text(tts_generator, tmp_path):
    """Тест: синтез простого текста"""
    output_file = tmp_path / "test.wav"
    
    result = await tts_generator.synthesize(
        text="Привет, мир!",
        output_file=str(output_file)
    )
    
    assert result["audio_path"] == str(output_file)
    assert result["duration_sec"] > 0
    assert result["sample_rate"] == 22050
    assert result["format"] == "wav"
    assert output_file.exists()
    assert output_file.stat().st_size > 0

@pytest.mark.asyncio
async def test_synthesize_empty_text(tts_generator, tmp_path):
    """Тест: синтез пустого текста должен выдать ошибку"""
    output_file = tmp_path / "empty.wav"
    
    with pytest.raises(ValueError, match="Text cannot be empty"):
        await tts_generator.synthesize(
            text="",
            output_file=str(output_file)
        )

@pytest.mark.asyncio
async def test_synthesize_long_text(tts_generator, tmp_path):
    """Тест: синтез длинного текста (>500 символов)"""
    long_text = "Тест " * 100  # 500 символов
    output_file = tmp_path / "long.wav"
    
    result = await tts_generator.synthesize(
        text=long_text,
        output_file=str(output_file)
    )
    
    assert result["duration_sec"] > 10  # Должно быть >10 секунд
    assert output_file.exists()

def test_synthesize_blocks(tts_generator, tmp_path):
    """Тест: синтез блоков скрипта"""
    blocks = [
        {"type": "hook", "text": "Первый блок"},
        {"type": "content", "text": "Второй блок с большим текстом"}
    ]
    
    result = tts_generator.synthesize_blocks(
        blocks=blocks,
        output_dir=str(tmp_path)
    )
    
    assert len(result["blocks"]) == 2
    assert result["total_duration_sec"] > 0
    assert all(Path(b["audio_path"]).exists() for b in result["blocks"])

def test_merge_audio_files(tts_generator, tmp_path):
    """Тест: объединение аудиофайлов"""
    # Создать 2 тестовых аудиофайла
    audio_files = []
    for i in range(2):
        file_path = tmp_path / f"audio_{i}.wav"
        asyncio.run(
            tts_generator.synthesize(
                text=f"Текст {i}",
                output_file=str(file_path)
            )
        )
        audio_files.append(str(file_path))
    
    # Объединить
    merged_file = tmp_path / "merged.wav"
    result = tts_generator.merge_audio_files(
        audio_files=audio_files,
        output_file=str(merged_file)
    )
    
    assert result["file_count"] == 2
    assert result["duration_sec"] > 0
    assert merged_file.exists()

def test_validate_config_missing_keys(tts_generator):
    """Тест: проверка конфига с отсутствующими ключами"""
    # Симулировать битый конфиг
    tts_generator.config.audio = None
    
    with pytest.raises(ValueError, match="Missing audio config"):
        tts_generator._validate_config()
```

---

## PART 3: VIDEO RENDERER

### Файл: `core/generators/video_renderer.py`

#### Требования

1. **Класс `VideoRenderer`**
   - Инициализация с конфигом проекта
   - Поддержка MoviePy для монтажа
   - Поддержка Pixabay API для фоновых видео
   - Генерация Shorts (1080x1920), Long Form (1920x1080), Ads (1080x1920)

2. **Методы**

```python
class VideoRenderer:
    def __init__(self, config: ProjectConfig):
        """
        Инициализация Video Renderer
        
        Args:
            config: ProjectConfig из config_loader
        
        Raises:
            ValueError: если конфиг невалидный
            EnvironmentError: если ffmpeg не найден
        """
        pass
    
    def render_shorts(
        self,
        audio_path: str,
        script_data: dict,
        output_path: str
    ) -> dict:
        """
        Отрендерить Shorts видео (1080x1920 вертикальное)
        
        Args:
            audio_path: Путь к WAV файлу (из TTS)
            script_data: Script JSON с блоками текста
            output_path: Путь для сохранения MP4
        
        Returns:
            {
                "video_path": str,
                "resolution": str,      # "1080x1920"
                "duration_sec": float,
                "file_size_mb": float,
                "fps": int,             # 30
                "codec": str,           # "libx264"
                "audio_codec": str      # "aac"
            }
        
        Raises:
            RenderError: если рендеринг не удался
        """
        pass
    
    def render_long_form(
        self,
        audio_paths: List[str],
        script_data: dict,
        output_path: str
    ) -> dict:
        """
        Отрендерить Long Form видео (1920x1080 горизонтальное)
        
        Args:
            audio_paths: Список путей к аудиофайлам (по блокам)
            script_data: Script JSON с таймлайном
            output_path: Путь для сохранения MP4
        
        Returns:
            dict: Аналогично render_shorts
        
        Raises:
            RenderError: если рендеринг не удался
        """
        pass
    
    def render_ad(
        self,
        audio_path: str,
        script_data: dict,
        output_path: str
    ) -> dict:
        """
        Отрендерить Ad видео (1080x1920 вертикальное)
        
        Args:
            audio_path: Путь к WAV файлу
            script_data: Script JSON для рекламы
            output_path: Путь для сохранения MP4
        
        Returns:
            dict: Аналогично render_shorts
        
        Raises:
            RenderError: если рендеринг не удался
        """
        pass
    
    def _get_background_video(
        self,
        duration: float,
        resolution: str,
        query: str = "abstract background"
    ) -> VideoFileClip:
        """
        Получить фоновое видео из Pixabay или создать чёрный фон
        
        Args:
            duration: Требуемая длительность в секундах
            resolution: "1080x1920" или "1920x1080"
            query: Поисковый запрос для Pixabay
        
        Returns:
            VideoFileClip: MoviePy clip с фоном
        
        Raises:
            APIError: если Pixabay API недоступен (fallback на ColorClip)
        """
        pass
    
    def _create_text_overlay(
        self,
        text: str,
        duration: float,
        resolution: str,
        position: str = "center"
    ) -> TextClip:
        """
        Создать текстовый оверлей с тенью
        
        Args:
            text: Текст для отображения
            duration: Длительность в секундах
            resolution: "1080x1920" или "1920x1080"
            position: "top", "center", "bottom"
        
        Returns:
            TextClip: MoviePy clip с текстом
        
        Raises:
            FontError: если шрифт не найден
        """
        pass
    
    def _check_ffmpeg(self) -> bool:
        """
        Проверить что ffmpeg установлен
        
        Returns:
            bool: True если ffmpeg доступен
        
        Raises:
            EnvironmentError: если ffmpeg не найден
        """
        pass
    
    def _validate_config(self) -> bool:
        """
        Проверить что конфиг содержит video настройки
        
        Returns:
            bool: True если конфиг валидный
        
        Raises:
            ValueError: если конфиг невалидный
        """
        pass
```

#### Логирование

```python
import logging

logger = logging.getLogger(__name__)

# При инициализации
logger.info(f"✅ VideoRenderer initialized (ffmpeg: {self.ffmpeg_path})")

# При рендере
logger.info(f"🎬 Rendering {mode} video: {output_path}")
logger.info(f"  Audio: {audio_path}")
logger.info(f"  Resolution: {resolution}")
logger.info(f"  Duration: {duration:.2f}s")

# Прогресс
logger.info(f"  [1/5] Loading audio...")
logger.info(f"  [2/5] Getting background video...")
logger.info(f"  [3/5] Creating text overlays...")
logger.info(f"  [4/5] Compositing clips...")
logger.info(f"  [5/5] Encoding to MP4...")

# При успехе
logger.info(f"✅ Video rendered: {output_path} ({file_size_mb:.1f} MB)")

# При ошибке
logger.error(f"❌ Video rendering failed: {str(e)}")
logger.exception(e)
```

#### Пример использования

```python
from core.generators.video_renderer import VideoRenderer
from core.utils.config_loader import load_project_config

config = load_project_config("youtube_horoscope")
renderer = VideoRenderer(config)

# Рендер Shorts
result = renderer.render_shorts(
    audio_path="output/audio/shorts_main.wav",
    script_data={
        "hook": "Ваш гороскоп на сегодня!",
        "blocks": [
            {"type": "hook", "text": "Ваш гороскоп на сегодня!"},
            {"type": "content", "text": "Овен: отличный день..."}
        ]
    },
    output_path="output/videos/shorts.mp4"
)
print(result)
# => {
#     "video_path": "output/videos/shorts.mp4",
#     "resolution": "1080x1920",
#     "duration_sec": 60.0,
#     "file_size_mb": 45.3,
#     "fps": 30,
#     "codec": "libx264",
#     "audio_codec": "aac"
# }
```

#### Тесты

**Файл:** `tests/test_video_renderer.py`

```python
import pytest
from pathlib import Path
from core.generators.video_renderer import VideoRenderer
from core.utils.config_loader import load_project_config

@pytest.fixture
def video_renderer():
    """Фикстура с инициализированным VideoRenderer"""
    config = load_project_config("youtube_horoscope")
    return VideoRenderer(config)

def test_check_ffmpeg(video_renderer):
    """Тест: проверка наличия ffmpeg"""
    assert video_renderer._check_ffmpeg() is True

def test_render_shorts_black_background(video_renderer, tmp_path):
    """Тест: рендер Shorts с чёрным фоном (без Pixabay)"""
    # Создать тестовый аудио файл
    audio_file = tmp_path / "test_audio.wav"
    # ... генерация тестового аудио через TTS или mock
    
    output_file = tmp_path / "shorts.mp4"
    
    result = video_renderer.render_shorts(
        audio_path=str(audio_file),
        script_data={"hook": "Test"},
        output_path=str(output_file)
    )
    
    assert result["resolution"] == "1080x1920"
    assert result["fps"] == 30
    assert result["codec"] == "libx264"
    assert output_file.exists()
    assert output_file.stat().st_size > 0

def test_render_shorts_with_pixabay(video_renderer, tmp_path, monkeypatch):
    """Тест: рендер Shorts с Pixabay видео"""
    # Mock Pixabay API response
    def mock_pixabay_request(*args, **kwargs):
        return {"hits": [{"videos": {"large": {"url": "https://example.com/video.mp4"}}}]}
    
    monkeypatch.setattr("requests.get", lambda *a, **k: type('obj', (object,), {'json': mock_pixabay_request})())
    
    # ... аналогично test_render_shorts_black_background

def test_render_shorts_missing_audio(video_renderer, tmp_path):
    """Тест: рендер без аудиофайла должен выдать ошибку"""
    output_file = tmp_path / "shorts.mp4"
    
    with pytest.raises(FileNotFoundError):
        video_renderer.render_shorts(
            audio_path="nonexistent.wav",
            script_data={},
            output_path=str(output_file)
        )

def test_create_text_overlay(video_renderer):
    """Тест: создание текстового оверлея"""
    text_clip = video_renderer._create_text_overlay(
        text="Test",
        duration=5.0,
        resolution="1080x1920",
        position="center"
    )
    
    assert text_clip.duration == 5.0
    assert text_clip.size == (1080, 1920) or text_clip.w <= 1080

def test_validate_config_missing_video_section(video_renderer):
    """Тест: проверка конфига без video секции"""
    video_renderer.config.video = None
    
    with pytest.raises(ValueError, match="Missing video config"):
        video_renderer._validate_config()
```

---

## PART 4: INTEGRATION WITH ORCHESTRATOR

### Файл: `core/orchestrators/pipeline_orchestrator.py`

#### Изменения

Добавить вызов Part 2 и Part 3 после Part 1:

```python
import asyncio
from core.generators.script_generator import ScriptGenerator
from core.generators.tts_generator import TTSGenerator
from core.generators.video_renderer import VideoRenderer

def run_full_pipeline(project: str, mode: str, dry_run: bool = False):
    """
    Запустить полный pipeline: Part 1 → Part 2 → Part 3
    
    Args:
        project: Имя проекта (youtube_horoscope)
        mode: Режим (shorts, long_form, ad)
        dry_run: Если True, только логи без реальной генерации
    """
    logger.info(f"🚀 Starting full pipeline: {project} / {mode}")
    logger.info(f"  Dry run: {dry_run}")
    
    # Загрузить конфиг
    config = load_project_config(project)
    logger.info(f"✅ Config loaded: {project}")
    
    # ===== PART 1: SCRIPT GENERATION =====
    logger.info("\n📝 PART 1: Script Generation")
    script_gen = ScriptGenerator(config)
    
    if dry_run:
        logger.info("  [DRY RUN] Skipping script generation")
        script_data = {"id": "test", "blocks": []}
    else:
        script_data = script_gen.generate(mode=mode)
        logger.info(f"✅ Script generated: {script_data['id']}")
    
    # ===== PART 2: TTS GENERATION =====
    logger.info("\n🎤 PART 2: TTS Generation")
    tts_gen = TTSGenerator(config)
    
    if dry_run:
        logger.info("  [DRY RUN] Skipping TTS generation")
        audio_result = {"blocks": [], "total_duration_sec": 0}
    else:
        audio_result = tts_gen.synthesize_blocks(
            blocks=script_data["blocks"],
            output_dir=f"output/audio/{project}"
        )
        logger.info(f"✅ Audio generated: {audio_result['total_duration_sec']:.2f}s")
    
    # ===== PART 3: VIDEO RENDERING =====
    logger.info("\n🎬 PART 3: Video Rendering")
    video_renderer = VideoRenderer(config)
    
    if dry_run:
        logger.info("  [DRY RUN] Skipping video rendering")
        video_result = {"video_path": "test.mp4"}
    else:
        # Выбрать метод рендера по режиму
        if mode == "shorts":
            video_result = video_renderer.render_shorts(
                audio_path=audio_result["blocks"][0]["audio_path"],
                script_data=script_data,
                output_path=f"output/videos/{project}/shorts.mp4"
            )
        elif mode == "long_form":
            video_result = video_renderer.render_long_form(
                audio_paths=[b["audio_path"] for b in audio_result["blocks"]],
                script_data=script_data,
                output_path=f"output/videos/{project}/long_form.mp4"
            )
        elif mode == "ad":
            video_result = video_renderer.render_ad(
                audio_path=audio_result["blocks"][0]["audio_path"],
                script_data=script_data,
                output_path=f"output/videos/{project}/ad.mp4"
            )
        
        logger.info(f"✅ Video rendered: {video_result['video_path']}")
    
    # ===== SUMMARY =====
    logger.info("\n✅ PIPELINE COMPLETE")
    logger.info(f"  Script: {script_data['id']}")
    logger.info(f"  Audio: {audio_result['total_duration_sec']:.2f}s")
    logger.info(f"  Video: {video_result['video_path']}")
    
    return {
        "script": script_data,
        "audio": audio_result,
        "video": video_result
    }
```

#### Тесты

**Файл:** `tests/test_pipeline_orchestrator.py`

```python
import pytest
from core.orchestrators.pipeline_orchestrator import run_full_pipeline

def test_full_pipeline_dry_run():
    """Тест: полный pipeline в dry-run режиме"""
    result = run_full_pipeline(
        project="youtube_horoscope",
        mode="shorts",
        dry_run=True
    )
    
    assert "script" in result
    assert "audio" in result
    assert "video" in result

def test_full_pipeline_shorts_real(tmp_path, monkeypatch):
    """Тест: полный pipeline для shorts (реальный)"""
    # Mock output directories
    monkeypatch.setenv("OUTPUT_DIR", str(tmp_path))
    
    result = run_full_pipeline(
        project="youtube_horoscope",
        mode="shorts",
        dry_run=False
    )
    
    assert result["script"]["id"] is not None
    assert result["audio"]["total_duration_sec"] > 0
    assert Path(result["video"]["video_path"]).exists()
```

---

## PART 5: TESTING

### Структура тестов

```
tests/
├── __init__.py
├── conftest.py                      # Фикстуры
├── test_tts_generator.py            # Part 2 tests
├── test_video_renderer.py           # Part 3 tests
├── test_pipeline_orchestrator.py    # Integration tests
└── test_utils.py                    # Утилиты
```

### Файл: `tests/conftest.py`

```python
import pytest
from pathlib import Path
import os
import tempfile

@pytest.fixture(scope="session")
def test_output_dir():
    """Временная директория для тестов"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

@pytest.fixture(scope="session")
def mock_env_vars():
    """Mock переменных окружения для тестов"""
    os.environ["GOOGLE_AI_API_KEY"] = "test-key"
    os.environ["PIXABAY_API_KEY"] = "test-key"
    yield
    # Cleanup
    del os.environ["GOOGLE_AI_API_KEY"]
    del os.environ["PIXABAY_API_KEY"]

@pytest.fixture
def sample_script_data():
    """Пример script JSON для тестов"""
    return {
        "id": "test_script_123",
        "type": "shorts",
        "hook": "Тестовый hook",
        "blocks": [
            {"type": "hook", "text": "Тестовый hook"},
            {"type": "content", "text": "Тестовый контент"}
        ],
        "total_duration_sec": 60
    }
```

### Запуск тестов

```bash
# Запустить все тесты
pytest tests/ -v

# Запустить с покрытием
pytest tests/ --cov=core --cov-report=html

# Запустить только Part 2 тесты
pytest tests/test_tts_generator.py -v

# Запустить только Part 3 тесты
pytest tests/test_video_renderer.py -v

# Запустить с логами
pytest tests/ -v -s --log-cli-level=DEBUG
```

---

## PART 6: LOGGING

### Конфигурация логирования

**Файл:** `core/utils/logger.py`

```python
import logging
import sys
from pathlib import Path
from datetime import datetime

def setup_logger(
    name: str,
    level: int = logging.INFO,
    log_file: str = None
) -> logging.Logger:
    """
    Настроить логгер с консолью и файлом
    
    Args:
        name: Имя логгера (обычно __name__)
        level: Уровень логирования (DEBUG, INFO, WARNING, ERROR)
        log_file: Путь к файлу логов (опционально)
    
    Returns:
        logging.Logger: Настроенный логгер
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Формат логов
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (если указан путь)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)  # Всё в файл
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger
```

### Использование в модулях

```python
from core.utils.logger import setup_logger

logger = setup_logger(
    name=__name__,
    level=logging.INFO,
    log_file=f"output/logs/tts_generator/{datetime.now().strftime('%Y%m%d')}.log"
)

logger.info("Module initialized")
logger.debug("Detailed debug info")
logger.warning("Warning message")
logger.error("Error occurred", exc_info=True)
```

---

## PART 7: ПРОВЕРКА ОКРУЖЕНИЯ

### Файл: `core/utils/environment_checker.py`

```python
import os
import sys
import shutil
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def check_environment() -> dict:
    """
    Проверить что все зависимости установлены
    
    Returns:
        dict: {
            "python_version": str,
            "ffmpeg": bool,
            "imagemagick": bool,
            "env_vars": {
                "GOOGLE_AI_API_KEY": bool,
                "PIXABAY_API_KEY": bool,
                ...
            },
            "output_dirs": bool,
            "all_checks_passed": bool
        }
    """
    results = {}
    
    # 1. Python version
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    results["python_version"] = python_version
    logger.info(f"✅ Python version: {python_version}")
    
    if sys.version_info < (3, 11):
        logger.warning(f"⚠️  Python 3.11+ required, you have {python_version}")
    
    # 2. FFmpeg
    ffmpeg_path = shutil.which("ffmpeg")
    results["ffmpeg"] = ffmpeg_path is not None
    if ffmpeg_path:
        logger.info(f"✅ ffmpeg found: {ffmpeg_path}")
    else:
        logger.error("❌ ffmpeg NOT FOUND (install: sudo apt-get install ffmpeg)")
    
    # 3. ImageMagick
    imagemagick_path = shutil.which("convert") or shutil.which("magick")
    results["imagemagick"] = imagemagick_path is not None
    if imagemagick_path:
        logger.info(f"✅ ImageMagick found: {imagemagick_path}")
    else:
        logger.error("❌ ImageMagick NOT FOUND (install: sudo apt-get install imagemagick)")
    
    # 4. Environment variables
    env_vars = {
        "GOOGLE_AI_API_KEY": os.getenv("GOOGLE_AI_API_KEY"),
        "PIXABAY_API_KEY": os.getenv("PIXABAY_API_KEY"),
        "OPENROUTER_API_KEY": os.getenv("OPENROUTER_API_KEY"),
        "TELEGRAM_BOT_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN"),
        "TELEGRAM_CHAT_ID": os.getenv("TELEGRAM_CHAT_ID")
    }
    
    results["env_vars"] = {}
    for key, value in env_vars.items():
        is_set = value is not None and value != ""
        results["env_vars"][key] = is_set
        
        if is_set:
            logger.info(f"✅ {key}: set ({value[:10]}...)")
        else:
            if key in ["GOOGLE_AI_API_KEY", "PIXABAY_API_KEY"]:
                logger.error(f"❌ {key}: NOT SET (required!)")
            else:
                logger.warning(f"⚠️  {key}: not set (optional)")
    
    # 5. Output directories
    output_dirs = ["output/scripts", "output/audio", "output/videos", "output/logs"]
    for dir_path in output_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    results["output_dirs"] = True
    logger.info(f"✅ Output directories created: {', '.join(output_dirs)}")
    
    # 6. Summary
    required_checks = [
        results["ffmpeg"],
        results["imagemagick"],
        results["env_vars"]["GOOGLE_AI_API_KEY"],
        results["env_vars"]["PIXABAY_API_KEY"]
    ]
    results["all_checks_passed"] = all(required_checks)
    
    if results["all_checks_passed"]:
        logger.info("\n✅ ALL ENVIRONMENT CHECKS PASSED")
    else:
        logger.error("\n❌ SOME ENVIRONMENT CHECKS FAILED")
        logger.error("Fix the issues above before running the pipeline")
    
    return results

if __name__ == "__main__":
    from core.utils.logger import setup_logger
    logger = setup_logger(__name__, level=logging.INFO)
    check_environment()
```

### Запуск проверки

```bash
# Локально
python -m core.utils.environment_checker

# В GitHub Actions (добавить в workflow)
- name: 🔍 Check Environment
  run: python -m core.utils.environment_checker
```

---

## КРИТЕРИИ ПРИЁМКИ

### Part 2: TTS Generator

- ✅ Класс `TTSGenerator` реализован
- ✅ Метод `synthesize()` работает с Edge-TTS
- ✅ Метод `synthesize_blocks()` обрабатывает блоки скрипта
- ✅ Метод `merge_audio_files()` объединяет аудио
- ✅ Точная длительность через pydub
- ✅ Логирование каждого шага
- ✅ Тесты покрывают 90%+ кода
- ✅ Генерируются WAV файлы (22050 Hz, mono)

### Part 3: Video Renderer

- ✅ Класс `VideoRenderer` реализован
- ✅ Метод `render_shorts()` работает
- ✅ Метод `render_long_form()` работает
- ✅ Метод `render_ad()` работает
- ✅ Поддержка Pixabay API (с fallback на чёрный фон)
- ✅ Текстовые оверлеи с тенью
- ✅ Экспорт в H.264 (MP4, 30fps)
- ✅ Логирование каждого шага
- ✅ Тесты покрывают 90%+ кода
- ✅ Генерируются MP4 файлы правильного разрешения

### Part 4: Integration

- ✅ Оркестратор вызывает Part 1 → 2 → 3
- ✅ Dry-run режим работает
- ✅ Все режимы (shorts, long_form, ad) работают
- ✅ Логи показывают прогресс каждого этапа

### Part 5: Testing

- ✅ Все модули покрыты юнит-тестами
- ✅ Интеграционные тесты для pipeline
- ✅ Тесты проходят локально и в CI
- ✅ Coverage ≥ 90%

### Part 6: Environment

- ✅ `environment_checker.py` проверяет все зависимости
- ✅ GitHub Actions workflow запускает проверку
- ✅ Понятные сообщения об ошибках

---

## ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ

### Локальный запуск (полный pipeline)

```bash
# 1. Проверить окружение
python -m core.utils.environment_checker

# 2. Запустить полный pipeline
python -m core.orchestrators.pipeline_orchestrator \
  --project youtube_horoscope \
  --mode shorts

# 3. Проверить результаты
ls -lah output/scripts/youtube_horoscope/
ls -lah output/audio/youtube_horoscope/
ls -lah output/videos/youtube_horoscope/

# 4. Посмотреть логи
cat output/logs/youtube_horoscope/$(date +%Y%m%d).log
```

### GitHub Actions workflow

```yaml
name: Generate Content (Full Pipeline)

on:
  workflow_dispatch:
    inputs:
      project:
        description: 'Project name'
        required: true
        default: 'youtube_horoscope'
      mode:
        description: 'Generation mode'
        required: true
        type: choice
        options:
          - shorts
          - long_form
          - ad

jobs:
  generate-content:
    runs-on: ubuntu-24.04
    timeout-minutes: 30
    
    steps:
      - name: 📥 Checkout
        uses: actions/checkout@v4
      
      - name: 🐍 Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: 🔧 Install system dependencies
        run: |
          sudo apt-get update -qq
          sudo apt-get install -y ffmpeg imagemagick
      
      - name: 📦 Install Python dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: 🔍 Check Environment
        env:
          GOOGLE_AI_API_KEY: ${{ secrets.GOOGLE_AI_API_KEY }}
          PIXABAY_API_KEY: ${{ secrets.PIXABAY_API_KEY }}
        run: python -m core.utils.environment_checker
      
      - name: 🎬 Generate Content
        env:
          GOOGLE_AI_API_KEY: ${{ secrets.GOOGLE_AI_API_KEY }}
          PIXABAY_API_KEY: ${{ secrets.PIXABAY_API_KEY }}
          OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}
        run: |
          python -m core.orchestrators.pipeline_orchestrator \
            --project ${{ github.event.inputs.project }} \
            --mode ${{ github.event.inputs.mode }}
      
      - name: 📊 Upload Artifacts
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: content-factory-output
          path: |
            output/scripts/
            output/audio/
            output/videos/
            output/logs/
          retention-days: 7
      
      - name: 🧪 Run Tests
        run: pytest tests/ -v --cov=core --cov-report=term
```

---

## ФИНАЛЬНЫЙ ЧЕКЛИСТ

### До начала работы

- [ ] Прочитать ТЗ полностью
- [ ] Убедиться что все зависимости установлены
- [ ] Проверить что API ключи установлены
- [ ] Запустить `environment_checker.py`

### Реализация Part 2

- [ ] Создать `core/generators/tts_generator.py`
- [ ] Реализовать `TTSGenerator.__init__()`
- [ ] Реализовать `synthesize()`
- [ ] Реализовать `synthesize_blocks()`
- [ ] Реализовать `merge_audio_files()`
- [ ] Добавить логирование
- [ ] Написать тесты
- [ ] Проверить что тесты проходят

### Реализация Part 3

- [ ] Создать `core/generators/video_renderer.py`
- [ ] Реализовать `VideoRenderer.__init__()`
- [ ] Реализовать `render_shorts()`
- [ ] Реализовать `render_long_form()`
- [ ] Реализовать `render_ad()`
- [ ] Реализовать `_get_background_video()`
- [ ] Реализовать `_create_text_overlay()`
- [ ] Добавить логирование
- [ ] Написать тесты
- [ ] Проверить что тесты проходят

### Интеграция

- [ ] Обновить `pipeline_orchestrator.py`
- [ ] Добавить вызов Part 2
- [ ] Добавить вызов Part 3
- [ ] Проверить dry-run режим
- [ ] Проверить все режимы (shorts, long_form, ad)
- [ ] Написать интеграционные тесты

### Тестирование

- [ ] Локальный запуск всех тестов
- [ ] Coverage ≥ 90%
- [ ] GitHub Actions запуск
- [ ] Проверить artifacts

### Финал

- [ ] Все тесты проходят
- [ ] Логи понятные и детальные
- [ ] Документация обновлена
- [ ] README.md обновлён
- [ ] Коммит и push

---

**🎉 ГОТОВО К РЕАЛИЗАЦИИ!**

**Ожидаемый результат:**
```bash
output/
├── scripts/youtube_horoscope/20251212/short_a1b2c3.json
├── audio/youtube_horoscope/shorts_main.wav              # ✅ РЕАЛЬНЫЙ АУДИО
├── videos/youtube_horoscope/shorts.mp4                  # ✅ РЕАЛЬНОЕ ВИДЕО
└── logs/youtube_horoscope/20251212.log                  # ✅ ДЕТАЛЬНЫЕ ЛОГИ
```

**Контакт для вопросов:** GitHub Issues или PR comments  
**Deadline:** По готовности, качество важнее скорости  
**Status:** 🟢 READY TO START
