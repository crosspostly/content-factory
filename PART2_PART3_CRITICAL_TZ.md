# 🧨 PART 2 + 3: КРИТИЧЕСКОЕ ТЕХНИЧЕСКОЕ ЗАДАНИЕ

**Основано на ОФИЦИАЛЬНОЙ документации Google (Dec 12, 2025)**

---

## 🔟 PART 2: TTS GENERATOR (Edge-TTS)

### Основная задача

Осеум: **core/generators/tts_generator.py** – синтез речи из текста на русском языке.

### Основные требования

```python
class TTSGenerator:
    """
    Мотор синтеза речи с Edge-TTS
    
    Входные данные:
    - config: настройка проекта (projects/youtube_horoscope/config.yaml)
    - script_data: данные скрипта из ScriptGenerator
    
    Выходные данные:
    - WAV файлы (22050 Hz, mono)
    - JSON метаданные (duration, blocks, etc)
    """
    
    async def synthesize(self, text: str, output_file: str) -> dict:
        """
        Генерирует один audio файл из текста
        
        Args:
            text (str): Русский текст (до 600 симв.)
            output_file (str): Путь для сохранения output_dir/shorts_main.wav
        
        Returns:
            {
                "audio_path": "/path/to/shorts_main.wav",
                "duration_sec": 45.3,
                "sample_rate": 22050,
                "channels": 1,
                "codec": "pcm_s16le"
            }
        
        Constraints:
            - Макс 60 сек для shorts
            - Русский алфавит ONLY
            - Голос: ru-RU-DariyaNeural (женский)
        """
        
        # 1. Edge-TTS: Получить MS Word WAV
        #    Пакет: edge-tts==6.1.0
        #    Voice: ru-RU-DariyaNeural (ru-RU-GalitsynNeural — доп.)
        #    Speed: 1.0 (from config.yaml audio.engines.edge-tts.speed)
        
        communicate = Communicate(text, voice="ru-RU-DariyaNeural", rate="+0%")
        await communicate.save(output_file)
        
        # 2. Получить длительность (ffprobe)
        duration = get_audio_duration(output_file)  # или librosa
        
        return {
            "audio_path": output_file,
            "duration_sec": duration,
            "sample_rate": 22050,
            "channels": 1
        }
    
    def synthesize_blocks(self, script_data: dict, output_dir: str) -> dict:
        """
        Генерирует все блоки скрипта
        
        Args:
            script_data (dict): От core/generators/script_generator.py
                {
                    "hook": "Текст hook",
                    "blocks": {
                        "main": "Основной текст",
                        "love": "О любви",
                        "money": "О деньгах",
                        "health": "О здоровье"
                    }
                }
            output_dir (str): /path/to/output/audio/youtube_horoscope/
        
        Returns:
            {
                "blocks": {
                    "main": {
                        "path": "/path/to/main.wav",
                        "duration_sec": 45.3
                    },
                    "love": {...},
                    ...
                },
                "total_duration_sec": 135.9,
                "sample_rate": 22050
            }
        """
        # 1. Обработать каждый блок async + await
        # 2. Кэшировать такие же тексты — не регенерировать
        # 3. Проверить shorts < 60 сек
        
        results = {"blocks": {}, "total_duration_sec": 0}
        
        for block_name, block_text in script_data.get("blocks", {}).items():
            output_file = f"{output_dir}/{block_name}.wav"
            result = asyncio.run(self.synthesize(block_text, output_file))
            results["blocks"][block_name] = result
            results["total_duration_sec"] += result["duration_sec"]
        
        return results
```

### Тех детали

| Параметр | Значение |
|-----------|----------|
| **Пакет** | `edge-tts==6.1.0` |
| **Голос** | `ru-RU-DariyaNeural` (бесплатный) |
| **Обыдело** | Поддерживает async/await |
| **Формат** | WAV (PCM 16-bit, 22050 Hz, mono) |
| **Макс длина** | 600 симв. пер запросу |

---

## 🎬 PART 3: VIDEO RENDERER (moviepy)

### Основная задача

Файл: **core/generators/video_renderer.py** – композиция видео (аудио + видео + текст).

### Основные требования

```python
class VideoRenderer:
    """
    Композиция: audio + background + text overlay
    
    Отпавты:
    - shorts: 1080x1920 (vertical, 9:16)
    - long_form: 1920x1080 (horizontal, 16:9)
    - ad: 1080x1920 (vertical, 9:16)
    """
    
    def render_shorts(self,
                     audio_path: str,
                     script_data: dict,
                     output_path: str,
                     background_video_path: str = None) -> dict:
        """
        Генерирует 1080x1920 вертикальное видео
        
        Args:
            audio_path (str): /path/to/shorts_main.wav
            script_data (dict): {
                "hook": "Текст хука (основной текст)"
            }
            output_path (str): /path/to/output/videos/shorts.mp4
            background_video_path (str, optional): Pixabay видео
        
        Returns:
            {
                "video_path": "/path/to/shorts.mp4",
                "duration_sec": 45.3,
                "resolution": "1080x1920",
                "file_size_mb": 12.5,
                "codec": "h264",
                "fps": 30
            }
        
        Process:
            1. Load audio from WAV
            2. If no background → create black screen
            3. Add text overlay (hook) centered
            4. Compose: background + text
            5. Add audio to video
            6. Export MP4 (H.264, AAC, 30fps)
        """
        
        # 1. Лоадунг авдио
        audio = AudioFileClip(audio_path)
        duration = audio.duration
        
        # 2. Выбор фона
        if not background_video_path:
            # Черный фон + текст
            video = self._create_text_overlay_video(
                duration=duration,
                text=script_data['hook'],
                resolution=(1080, 1920),
                bg_color=(0, 0, 0)
            )
        else:
            # Pixabay фон + текст
            video = self._composite_with_background(
                bg_video_path=background_video_path,
                duration=duration,
                text=script_data['hook']
            )
        
        # 3. Композиция: видео + аудио
        final = video.set_audio(audio)
        
        # 4. Экспорт MP4
        final.write_videofile(
            output_path,
            fps=30,
            codec='libx264',
            audio_codec='aac',
            verbose=False,
            logger=None
        )
        
        return {
            "video_path": output_path,
            "duration_sec": duration,
            "resolution": "1080x1920",
            "file_size_mb": get_file_size_mb(output_path),
            "codec": "h264",
            "fps": 30
        }
    
    def _create_text_overlay_video(self, duration: float, text: str,
                                   resolution: tuple, bg_color: tuple) -> VideoClip:
        """
        Создает статичное видео:
        - Solid color background
        - Text overlay (white, centered)
        - With shadow for readability
        """
        
        w, h = resolution
        
        # 1. Нарисовать снимок (PIL)
        img = Image.new('RGB', (w, h), color=bg_color)
        draw = ImageDraw.Draw(img)
        
        # 2. Выбрать размер шрифта (авто)
        font_size = calculate_font_size(text, max_width=w*0.9)
        font = ImageFont.truetype("Arial.ttf", font_size)  # Либо /System/Library/Fonts/Arial.ttf
        
        # 3. Центрировать текст
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (w - text_width) // 2
        y = (h - text_height) // 2
        
        # 4. Рисовать с тенью
        shadow_offset = 2
        draw.text((x+shadow_offset, y+shadow_offset), text, fill=(0, 0, 0), font=font)
        draw.text((x, y), text, fill=(255, 255, 255), font=font)
        
        # 5. Конвертировать в VideoClip
        return ImageClip(np.array(img)).set_duration(duration)
    
    def _composite_with_background(self, bg_video_path: str,
                                   duration: float, text: str) -> VideoClip:
        """
        Композит Pixabay видео + текст overlay
        
        1. Лоад: видео Pixabay
        2. Масштаб: 1080x1920 (crop/scale)
        3. Оверлей: текст + правоугольник (трансп. чёрный)
        4. Композ: background + rectangle + text
        """
        
        # Load + resize
        bg = VideoFileClip(bg_video_path).set_duration(duration)
        bg = bg.resize((1080, 1920))
        
        # Text + semi-transparent rectangle
        text_clip = self._create_text_clip(text, duration, position='bottom')
        bg_rect = ImageClip(np.zeros((1920, 1080, 3), dtype='uint8'))
        bg_rect = bg_rect.set_opacity(0.3).set_duration(duration).set_size((1080, 400))
        
        # Composite
        return CompositeVideoClip([
            bg,
            bg_rect.set_position(('center', 'bottom')),
            text_clip
        ])

    def render_long_form(self, audio_path: str, script_data: dict, 
                        output_path: str) -> dict:
        """1920x1080 горизонтальное видео"""
        # Similar to render_shorts but with 1920x1080 resolution
        pass
    
    def render_ad(self, audio_path: str, script_data: dict,
                  output_path: str) -> dict:
        """1080x1920 ад для соц. сетей"""
        # Same as render_shorts
        return self.render_shorts(audio_path, script_data, output_path)
```

### Тех детали

| Параметр | Shorts | Long-form | Ad |
|-----------|--------|-----------|----|
| **Пакет** | moviepy==1.0.3 | moviepy==1.0.3 | moviepy==1.0.3 |
| **Резолюция** | 1080x1920 | 1920x1080 | 1080x1920 |
| **FPS** | 30 | 30 | 30 |
| **Кодек** | libx264 (H.264) | libx264 | libx264 |
| **Аудио** | AAC | AAC | AAC |
| **Макс длительность** | 60 сек | 600 сек | 60 сек |

---

## 🔑 GOOGLE GEMINI API - РЕАЛЬНЫЕ МОДЕЛИ (Dec 2025)

**ОСНОВНОП** НЕ ОШНОс !

Источник: [ai.google.dev/gemini-api/docs/models](https://ai.google.dev/gemini-api/docs/models)

### 🔴 НОВЕ НОКОДЕЦЕННО (Deprecated Feb 2025+)

| Модель | Код | Статус | Причина |
|--------|------|---------|----------|
| Gemini 2.0 Flash | `gemini-2.0-flash` | ☖️ Deprecated | Заменяют на 2.5 Flash (Feb 2026) |
| Gemini 1.5 Flash | `gemini-1.5-flash` | ☖️ Deprecated | Retired April 2025 |
| Gemini 1.5 Pro | `gemini-1.5-pro` | ☖️ Deprecated | Retired April 2025 |
| Gemini exp-1206 | `gemini-exp-1206` | ❌ **НЕ ЕХИСТУЕТ** | Never existed |
| Gemini 2.0 flash-exp | `gemini-2.0-flash-exp` | ❌ **НЕ ЭКсПЕРИМЕНТАЛЬНАЯ** | Removed from public API |

### 👋 АКТУАЛЬНЫЕ МОДЕЛИ (Dec 2025)

| Модель | Код | Основные черты | Оптимальная |
|--------|------|------|-------|
| **Gemini 2.5 Pro** | `gemini-2.5-pro` | Мощнейшая, рассуждение | документы, код |
| **Gemini 2.5 Flash** | `gemini-2.5-flash` | Быстрая, баланс | **РЕКОМЕНДУЕМ** ✅ |
| **Gemini 2.5 Flash-Lite** | `gemini-2.5-flash-lite` | Экономная, самая дешевая | счетчики, чаты |
| **Gemini 3 Pro Preview** | `gemini-3-pro-preview` | Новейшая (Nov 2025) | Прениём акцесс |

**ДЛЯ content-factory (youtube_horoscope):**

```yaml
# projects/youtube_horoscope/config.yaml

generation:
  primary_model: "gemini-2.5-flash"        # Основная для скриптов
  fallback_models:
    - "gemini-2.5-flash-lite"               # Fallback (faster)
    - "gemini-2.5-pro"                      # Fallback (smarter)
  temperature: 0.8
  max_retries: 3
```

---

## 📦 REQUIREMENTS.TXT

Добавить:

```txt
# Part 2 TTS
edge-tts==6.1.0                    # Синтез речи (MS Azure)

# Part 3 Video
moviepy==1.0.3                     # Композиция видео
imageio-ffmpeg==0.4.10             # FFmpeg враппер в moviepy
Pillow==10.2.0                     # Image processing (PIL)
numpy==1.24.3                      # For image arrays

# Existing
google-generativeai==0.7.2
python-dotenv==1.0.1
pyyaml==6.0.2
requests==2.31.0
```

---

## 🎧 GITHUB ACTIONS: Кеширование депенденций

Обновить `.github/workflows/part1-test.yml`:

```yaml
jobs:
  generate-content:
    runs-on: ubuntu-24.04
    
    steps:
      # 1. Checkout
      - uses: actions/checkout@v4
      
      # 2. Setup Python МНАЧА КЕШИНЮ
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'  # ✅ Кэш pip депенденций
      
      # 3. Install system deps
      - name: Install FFmpeg & ImageMagick
        run: |
          sudo apt-get update -qq
          sudo apt-get install -y ffmpeg imagemagick >/dev/null 2>&1
      
      # 4. Install Python deps (кэшеэ)
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      # 5. Run pipeline
      - name: Generate content (Part 1 + 2 + 3)
        env:
          GOOGLE_AI_API_KEY: ${{ secrets.GOOGLE_AI_API_KEY }}
          OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}
          PIXABAY_API_KEY: ${{ secrets.PIXABAY_API_KEY }}
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
        run: |
          python -m core.orchestrators.pipeline_orchestrator \
            --project youtube_horoscope \
            --mode shorts
      
      # 6. Upload artifacts
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: content-factory-output
          path: |
            output/
            logs/
```

---

## ✅ ЧЕКЛИСТ ДЛЯ AI АГЕНТА

- [ ] **УНОЯНИИ** requirements.txt
  - [ ] Добавить edge-tts, moviepy, imageio-ffmpeg, Pillow
  - [ ] Проверить версии пакетов

- [ ] **НОВИЙ файл** `core/generators/tts_generator.py`
  - [ ] Edge-TTS интеграция
  - [ ] Асинхронные операции
  - [ ] Validation (< 60 sec for shorts)
  - [ ] Caching identical texts

- [ ] **ОБНОВЛЕННЫЙ** `core/generators/video_renderer.py`
  - [ ] moviepy структура
  - [ ] render_shorts() - 1080x1920
  - [ ] render_long_form() - 1920x1080
  - [ ] render_ad() - 1080x1920
  - [ ] Pixabay API integration
  - [ ] H.264 codec, 30fps
  - [ ] Text overlay with shadow

- [ ] **ОБНОВЛЕННАЯ** `projects/youtube_horoscope/config.yaml`
  - [ ] ОНО НОВА НОКОДец (gemini-2.5-*)
  - [ ] NO deprecated models
  - [ ] audio.engines.edge-tts configured
  - [ ] video.codec = libx264

- [ ] **ОБНОВЛЕННЫЙ** `.github/workflows/part1-test.yml`
  - [ ] cache: 'pip' в setup-python
  - [ ] 5-minute timeout for install
  - [ ] All secrets pass as env vars

- [ ] **ЛОКАЛЬНЫЕ тесты**
  - [ ] TTS: Проверить WAV генерацию
  - [ ] Video: Проверить MP4 генерацию
  - [ ] Pipeline: Полный сценарий

---

**ПОДПОЛнАютЕ:** НЕ МОДИФИЦИРУЙТЕ Part 1 (scripts, config loader, routing)!
