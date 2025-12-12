"""Pytest configuration and fixtures for Content Factory tests."""
from __future__ import annotations

import os
import tempfile
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
        "generation": {},
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
