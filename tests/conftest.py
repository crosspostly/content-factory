"""Pytest configuration and fixtures for Content Factory tests."""
from __future__ import annotations

# Mock google.genai BEFORE any imports to prevent import errors
import sys
from unittest.mock import MagicMock
mock_google = MagicMock()
mock_google.genai = MagicMock()
sys.modules['google'] = mock_google
sys.modules['google.genai'] = mock_google.genai
import tempfile
sys.modules['core.utils.model_router'] = MagicMock()
# Also mock core.utils as a package with model_router attribute
cls_utils = MagicMock()
cls_utils.model_router = sys.modules['core.utils.model_router']
sys.modules['core.utils'] = cls_utils
from pathlib import Path
from typing import Any

import pytest


@pytest.fixture(scope="session")
def test_output_dir():
    """Temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture(scope="session")
def mock_env_vars():
    """Mock environment variables for tests."""
    original_env = {}
    test_vars = {
        "GOOGLE_AI_API_KEY": "test-google-key-12345",
        "PIXABAY_API_KEY": "test-pixabay-key-67890",
    }
    
    for key, value in test_vars.items():
        original_env[key] = os.environ.get(key)
        os.environ[key] = value
    
    yield test_vars
    
    # Cleanup
    for key, original_value in original_env.items():
        if original_value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = original_value


@pytest.fixture
def sample_script_shorts() -> dict[str, Any]:
    """Sample shorts script for testing."""
    return {
        "id": "test_script_shorts_123",
        "type": "shorts",
        "hook": "Тестовый гороскоп на сегодня!",
        "script": "Тестовый гороскоп на сегодня! Овен: день успеха. Телец: будьте внимательны.",
        "narration_text": "Тестовый гороскоп на сегодня! Овен: день успеха. Телец: будьте внимательны.",
        "duration_sec": 15,
    }


@pytest.fixture
def sample_script_long_form() -> dict[str, Any]:
    """Sample long-form script for testing."""
    return {
        "id": "test_script_long_123",
        "type": "long_form",
        "video_title": "Подробный гороскоп",
        "blocks": {
            "love": "Любовь: Романтические перспективы благоприятны.",
            "money": "Деньги: Финансовая стабильность ожидается.",
            "health": "Здоровье: Обратите внимание на самочувствие.",
        },
        "duration_sec": 180,
    }


@pytest.fixture
def sample_script_ad() -> dict[str, Any]:
    """Sample ad script for testing."""
    return {
        "id": "test_script_ad_123",
        "type": "ad",
        "product_id": "Тестовый продукт",
        "narration_text": "Специальное предложение! Только сегодня скидка 50%!",
        "script": "Специальное предложение! Только сегодня скидка 50%!",
        "duration_sec": 20,
    }


@pytest.fixture
def mock_config():
    """Mock ProjectConfig for testing."""
    from core.utils.config_loader import ProjectConfig
    
    config_dict = {
        "project": {
            "name": "test_horoscope",
            "language": "russian",
        },
        "content_strategy": {},
        "generation": {
            "primary_model": "gemini-2.5-flash",
            "fallback_models": ["gemini-2.5-flash-lite"],
            "temperature": 0.7,
            "max_retries": 2,
        },
        "audio": {
            "engines": {
                "edge-tts": {
                    "voice": "ru-RU-SvetlanaNeural",
                    "speed": 1.0,
                }
            }
        },
        "video": {
            "resolution": {
                "shorts": "1080x1920",
                "long_form": "1920x1080",
            }
        },
        "subtitles": {},
        "upload": {
            "platforms": []
        },
        "caching": {},
        "monitoring": {
            "telegram_notifications": False
        }
    }
    
    return ProjectConfig(config_dict)


@pytest.fixture
def mock_config_with_qwen():
    """Mock ProjectConfig configured for Qwen (Ollama) with Gemini fallback."""
    from core.utils.config_loader import ProjectConfig
    
    config_dict = {
        "project": {
            "name": "test_project",
            "language": "english",
        },
        "content_strategy": {},
        "generation": {
            "primary_model": "qwen2.5-coder:1.5b",
            "fallback_models": ["gemini-2.5-flash"],
            "temperature": 0.7,
            "max_retries": 2,
            "retry_delay_sec": 1.0,
        },
        "audio": {
            "engines": {
                "edge-tts": {
                    "voice": "en-US-AriaNeural",
                    "speed": 1.0,
                }
            }
        },
        "video": {
            "resolution": {
                "shorts": "1080x1920",
                "long_form": "1920x1080",
            }
        },
        "subtitles": {},
        "upload": {
            "platforms": []
        },
        "caching": {},
        "monitoring": {
            "telegram_notifications": False
        }
    }
    
    return ProjectConfig(config_dict)


@pytest.fixture
def error_log_fixtures() -> dict[str, str]:
    """Load error log fixtures for testing."""
    from pathlib import Path
    
    fixtures_dir = Path(__file__).parent / "fixtures" / "error_logs"
    logs = {}
    
    for log_file in fixtures_dir.glob("*.log"):
        logs[log_file.stem] = log_file.read_text()
    
    return logs
