# Testing Guide for Content Factory

This guide explains how to run tests for the Content Factory project.

## Prerequisites

### System Dependencies

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y ffmpeg imagemagick

# macOS
brew install ffmpeg imagemagick

# Verify installation
ffmpeg -version
convert -version  # or magick -version
```

### Python Dependencies

```bash
# Install all dependencies including test frameworks
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the project root:

```bash
# Required for script generation
GOOGLE_AI_API_KEY=your_gemini_api_key_here

# Optional for video backgrounds (will use gradients if not set)
PIXABAY_API_KEY=your_pixabay_api_key_here

# Optional for fallback models
OPENROUTER_API_KEY=your_openrouter_key_here

# Optional for notifications
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here
```

## Running Tests

### Check Environment

Before running tests, verify your environment:

```bash
python -m core.utils.environment_checker
```

Expected output:
```
✅ Python version: 3.11.x
✅ ffmpeg found: /usr/bin/ffmpeg
✅ ImageMagick found: /usr/bin/convert
✅ GOOGLE_AI_API_KEY: set
✅ Output directories created: output/scripts, output/audio, output/videos, output/logs
✅ ALL CRITICAL CHECKS PASSED
```

### Run All Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=core --cov-report=html --cov-report=term

# Run specific test file
pytest tests/test_tts_generator.py -v

# Run specific test class
pytest tests/test_tts_generator.py::TestTextSanitization -v

# Run specific test
pytest tests/test_tts_generator.py::TestTextSanitization::test_sanitize_html_tags -v
```

### Test Categories

Tests are organized into categories using pytest markers:

```bash
# Run only fast unit tests (default)
pytest tests/ -v -m "not slow"

# Run only slow integration tests
pytest tests/ -v -m "slow"

# Run all tests including slow ones
pytest tests/ -v
```

### Test Output

Test outputs are saved to:
- **Audio files**: `output/audio/test_horoscope/`
- **Video files**: `output/videos/test_horoscope/`
- **Logs**: `output/logs/`
- **Coverage reports**: `htmlcov/index.html`

To view coverage report:
```bash
pytest tests/ --cov=core --cov-report=html
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## Test Structure

```
tests/
├── __init__.py
├── conftest.py                      # Shared fixtures
├── test_tts_generator.py            # TTS tests
├── test_video_renderer.py           # Video rendering tests
├── test_pipeline_orchestrator.py    # Pipeline integration tests
└── test_environment_checker.py      # Environment verification tests
```

## Writing Tests

### Basic Test Structure

```python
import pytest
from core.generators import tts_generator

def test_something():
    """Test description."""
    result = tts_generator.some_function()
    assert result is not None
```

### Using Fixtures

```python
def test_with_config(mock_config):
    """Test using mock config fixture."""
    result = tts_generator.synthesize(mock_config, script, "shorts")
    assert "blocks" in result
```

### Async Tests

```python
@pytest.mark.asyncio
async def test_async_function():
    """Test async function."""
    result = await tts_generator._synthesize_edge_tts_async(...)
    assert result > 0
```

### Slow Tests

```python
@pytest.mark.slow
def test_full_pipeline():
    """This test takes a long time."""
    # Full integration test here
```

## Common Issues

### Issue: Tests fail with "ffmpeg not found"

**Solution**: Install ffmpeg:
```bash
sudo apt-get install ffmpeg
```

### Issue: Tests fail with API key errors

**Solution**: Set required environment variables:
```bash
export GOOGLE_AI_API_KEY=your_key_here
# Or create .env file
```

### Issue: Slow tests timeout

**Solution**: Run without slow tests:
```bash
pytest tests/ -v -m "not slow"
```

### Issue: Module import errors

**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

## CI/CD Testing

Tests run automatically on:
- Push to `main` or `feature-*` branches
- Pull requests to `main`
- Manual workflow dispatch

View test results at:
https://github.com/your-org/content-factory/actions

## Test Coverage Goals

Target coverage: **≥ 90%**

Current coverage by module:
- `core/generators/tts_generator.py`: Target 95%
- `core/generators/video_renderer.py`: Target 90%
- `core/orchestrators/pipeline_orchestrator.py`: Target 85%
- `core/utils/`: Target 80%

## Performance Benchmarks

Typical test execution times:
- Unit tests (fast): ~10-30 seconds
- Integration tests (slow): ~2-5 minutes
- Full test suite: ~5-8 minutes

## Debugging Tests

### Run with verbose output
```bash
pytest tests/ -vv -s
```

### Run with logs
```bash
pytest tests/ -v --log-cli-level=DEBUG
```

### Run with pdb on failure
```bash
pytest tests/ --pdb
```

### Run single test with maximum verbosity
```bash
pytest tests/test_tts_generator.py::TestTextSanitization::test_sanitize_html_tags -vv -s --log-cli-level=DEBUG
```

## Continuous Testing

For development, use pytest-watch:
```bash
pip install pytest-watch
ptw tests/
```

This will re-run tests automatically when files change.

## Contributing

When adding new features:
1. Write tests first (TDD)
2. Ensure all tests pass: `pytest tests/ -v`
3. Check coverage: `pytest tests/ --cov=core --cov-report=term`
4. Aim for ≥ 90% coverage on new code
5. Document any new fixtures in `conftest.py`

## Support

For issues with testing:
1. Check this guide
2. Review test logs in CI/CD
3. Open an issue on GitHub
4. Contact the team

---

**Last Updated**: December 12, 2025
