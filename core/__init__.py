"""Core package for Content Factory pipeline.

This package intentionally keeps imports lightweight to avoid importing optional
heavy dependencies (LLM/TTS/Video) at import time.
"""


def __getattr__(name):
    """Lazy load modules for proper mocking in tests."""
    if name == 'generators':
        from . import generators
        return generators
    elif name == 'orchestrators':
        from . import orchestrators
        return orchestrators
    elif name == 'uploaders':
        from . import uploaders
        return uploaders
    elif name == 'utils':
        from . import utils
        return utils
    raise AttributeError(f'module {__name__!r} has no attribute {name!r}')


__all__ = ['generators', 'orchestrators', 'uploaders', 'utils']
