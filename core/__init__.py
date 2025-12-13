"""Core package for Content Factory pipeline.

This package intentionally keeps imports lightweight to avoid importing optional
heavy dependencies (LLM/TTS/Video) at import time.
"""

import sys
from types import ModuleType


def __getattr__(name):
    """Lazy load modules for proper mocking in tests."""
    if name in ('generators', 'orchestrators', 'uploaders', 'utils'):
        # Use importlib to avoid recursion issues
        import importlib
        module = importlib.import_module(f'.{name}', __name__)
        # Cache the module in sys.modules to avoid re-importing
        sys.modules[f'{__name__}.{name}'] = module
        return module
    raise AttributeError(f'module {__name__!r} has no attribute {name!r}')


__all__ = ['generators', 'orchestrators', 'uploaders', 'utils']
