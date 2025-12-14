"""Builder for creating slides from text content."""

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class Slide:
    """Represents a single slide in the video."""
    
    def __init__(
        self,
        text: str,
        duration: float = 2.0,
        index: int = 0,
    ):
        """
        Initialize a slide.
        
        Args:
            text: Text content for the slide
            duration: Duration in seconds
            index: Slide index in the sequence
        """
        self.text = text
        self.duration = duration
        self.index = index
        self.audio_path: str | None = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "text": self.text,
            "duration": self.duration,
            "index": self.index,
            "audio_path": self.audio_path,
        }


class SlideBuilder:
    """
    Builds slides from text content.
    
    Splits long text into multiple slides with automatic duration calculation.
    """
    
    def __init__(
        self,
        max_chars_per_slide: int = 200,
        min_duration: float = 1.5,
        max_duration: float = 5.0,
    ):
        """
        Initialize slide builder.
        
        Args:
            max_chars_per_slide: Maximum characters per slide
            min_duration: Minimum slide duration in seconds
            max_duration: Maximum slide duration in seconds
        """
        self.max_chars_per_slide = max_chars_per_slide
        self.min_duration = min_duration
        self.max_duration = max_duration
    
    def build_slides(self, text: str) -> List[Slide]:
        """
        Build slides from text content.
        
        Intelligently splits text into slides with appropriate durations
        based on character count.
        
        Args:
            text: Full text content
            
        Returns:
            List of Slide objects
        """
        if not text or not text.strip():
            raise ValueError("Text content cannot be empty")
        
        # Split by sentences or line breaks
        sentences = self._split_text(text)
        
        # Filter empty sentences
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            raise ValueError("Could not create any slides from text")
        
        slides = []
        current_slide_text = ""
        current_chars = 0
        
        for sentence in sentences:
            # Check if adding this sentence would exceed limit
            test_text = (
                current_slide_text + " " + sentence
                if current_slide_text
                else sentence
            )
            
            if len(test_text) <= self.max_chars_per_slide:
                # Add to current slide
                current_slide_text = test_text
                current_chars = len(test_text)
            else:
                # Start new slide if we already have content
                if current_slide_text:
                    duration = self._calculate_duration(current_chars)
                    slides.append(
                        Slide(
                            text=current_slide_text,
                            duration=duration,
                            index=len(slides),
                        )
                    )
                    current_slide_text = sentence
                    current_chars = len(sentence)
                else:
                    # Even if sentence is too long, we need to put it somewhere
                    # Split long sentences or just add them as-is
                    current_slide_text = sentence
                    current_chars = len(sentence)
        
        # Add final slide
        if current_slide_text:
            duration = self._calculate_duration(current_chars)
            slides.append(
                Slide(
                    text=current_slide_text,
                    duration=duration,
                    index=len(slides),
                )
            )
        
        if not slides:
            raise ValueError("Could not create any slides from text")
        
        logger.info(f"✅ Built {len(slides)} slides from text")
        return slides
    
    def _split_text(self, text: str) -> List[str]:
        """
        Split text into sentences.
        
        Tries to split by periods/exclamation marks first,
        falls back to newlines, then to the whole text.
        """
        parts = []
        
        # Try splitting by periods first (most common)
        if "." in text:
            for part in text.split("."):
                part = part.strip()
                if part:
                    parts.append(part)
            if parts:
                return parts
        
        # Try splitting by exclamation marks
        if "!" in text:
            for part in text.split("!"):
                part = part.strip()
                if part:
                    parts.append(part)
            if parts:
                return parts
        
        # Try splitting by newlines
        if "\n" in text:
            for part in text.split("\n"):
                part = part.strip()
                if part:
                    parts.append(part)
            if parts:
                return parts
        
        # Default: return as single slide
        return [text.strip()]
    
    def _calculate_duration(self, char_count: int) -> float:
        """
        Calculate slide duration based on character count.
        
        Assumes ~150 characters per minute of speech (average reading speed).
        
        Args:
            char_count: Number of characters in slide
            
        Returns:
            Duration in seconds, clamped to min/max
        """
        # 150 chars/minute = 2.5 chars/second
        # So duration = chars / 2.5
        chars_per_second = 2.5
        duration = char_count / chars_per_second
        
        # Clamp to min/max
        return max(self.min_duration, min(duration, self.max_duration))
