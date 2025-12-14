"""Content modes package for modular video generation.

Provides a plugin-like system for different video rendering modes.
Each mode represents a complete pipeline from content to video output.

Available modes:
    - slides: Generate videos from text slides (carousel style)
"""

# Import modes to register them
from . import slides_mode  # noqa: F401
from .registry import ContentModeRegistry

__all__ = ["ContentModeRegistry"]
