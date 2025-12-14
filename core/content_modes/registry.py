"""Content mode registry for managing available modes."""

import logging
from typing import Dict, Type, Optional
from .base import BaseContentMode

logger = logging.getLogger(__name__)

_MODES: Dict[str, Type[BaseContentMode]] = {}


def register_mode(name: str):
    """Decorator to register a content mode."""
    def decorator(cls: Type[BaseContentMode]):
        _MODES[name] = cls
        logger.info(f"Registered content mode: {name}")
        return cls
    return decorator


class ContentModeRegistry:
    """Registry for all available content modes."""
    
    @classmethod
    def get(cls, name: str, variant: str = "default") -> BaseContentMode:
        """
        Get an instance of a content mode.
        
        Args:
            name: Name of the mode (e.g., 'slides')
            variant: Optional variant (e.g., 'carousel')
            
        Returns:
            Instance of the requested mode
            
        Raises:
            ValueError: If mode not found
        """
        if name not in _MODES:
            available = ", ".join(_MODES.keys())
            raise ValueError(
                f"Content mode '{name}' not found. "
                f"Available modes: {available}"
            )
        
        mode_class = _MODES[name]
        return mode_class(variant=variant)
    
    @classmethod
    def list_modes(cls) -> Dict[str, str]:
        """Get list of all available modes."""
        result = {}
        for name, mode_class in _MODES.items():
            try:
                instance = mode_class()
                result[name] = instance.description
            except Exception as e:
                logger.warning(f"Failed to instantiate {name}: {e}")
                result[name] = "Error loading description"
        return result
