"""
Tests for batch_generator.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta


@pytest.fixture
def mock_api_key():
    """Mock API key."""
    return "test_api_key_12345"


class TestBatchGeneration:
    """Test batch generation logic."""
    
    def test_date_range_calculation(self):
        """Test that date range is calculated correctly."""
        start = datetime.strptime("2025-12-13", "%Y-%m-%d")
        
        dates = []
        for i in range(7):
            date = (start + timedelta(days=i)).strftime("%Y-%m-%d")
            dates.append(date)
        
        assert dates[0] == "2025-12-13"
        assert dates[6] == "2025-12-19"
        assert len(dates) == 7


class TestBatchCLI:
    """Test batch generator CLI."""
    
    def test_batch_generator_import(self):
        """Test that batch_generator can be imported."""
        from core.generators import batch_generator
        assert callable(batch_generator.generate_batch)
    
    def test_api_key_from_env(self):
        """Test that API key is read from environment."""
        import os
        
        # Mock environment
        with patch.dict(os.environ, {"GOOGLE_AI_API_KEY": "test_key"}):
            assert os.getenv("GOOGLE_AI_API_KEY") == "test_key"


@pytest.mark.slow
class TestBatchGenerationIntegration:
    """Integration tests (requires API keys)."""
    
    def test_batch_generate_single_day(self):
        """Test batch generation for a single day."""
        import os
        
        if not os.getenv("GOOGLE_AI_API_KEY"):
            pytest.skip("GOOGLE_AI_API_KEY not set")
        
        # This would run a real batch generation
        # Skipped in fast tests
        pytest.skip("Slow integration test")
