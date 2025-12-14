"""Base class for content modes."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional
from pathlib import Path


@dataclass
class GenerationResult:
    """Result of content generation."""
    
    video_path: str
    """Path to generated video file"""
    
    duration: float
    """Video duration in seconds"""
    
    width: int
    """Video width in pixels"""
    
    height: int
    """Video height in pixels"""
    
    metadata: Dict[str, Any]
    """Additional metadata about the generation"""


class BaseContentMode(ABC):
    """
    Abstract base class for content modes.
    
    A content mode is a complete pipeline for generating videos from content.
    It handles splitting content into components and rendering them into a video.
    """
    
    def __init__(self, variant: str = "default"):
        """
        Initialize content mode.
        
        Args:
            variant: Optional variant name for the mode (e.g., 'carousel', 'animated')
        """
        self.variant = variant
    
    @abstractmethod
    async def generate(
        self,
        scenario: str,
        audio_map: Dict[str, str],
        config: Dict[str, Any],
        output_dir: Optional[Path] = None,
    ) -> GenerationResult:
        """
        Generate video from content.
        
        Args:
            scenario: Text content to convert to video
            audio_map: Mapping of text segments to audio file paths
            config: Configuration dict with design/layout settings
            output_dir: Output directory for generated files
            
        Returns:
            GenerationResult with video path and metadata
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Get the name of this content mode."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Get the description of this content mode."""
        pass
