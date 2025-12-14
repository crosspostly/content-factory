"""Renders individual slides to images."""

import logging
from pathlib import Path
from typing import Tuple, Dict, Any
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)


class SlideRenderer:
    """Renders slides as images for video composition."""
    
    def __init__(
        self,
        width: int = 1080,
        height: int = 1920,
        background_color: str = "#2B1B3D",
        text_color: str = "white",
        font_size: int = 70,
        font_family: str = "Arial",
    ):
        """
        Initialize slide renderer.
        
        Args:
            width: Image width in pixels
            height: Image height in pixels
            background_color: Hex color or color name
            text_color: Text color (hex or name)
            font_size: Font size in pixels
            font_family: Font family name
        """
        self.width = width
        self.height = height
        self.background_color = self._parse_color(background_color)
        self.text_color = self._parse_color(text_color)
        self.font_size = font_size
        self.font_family = font_family
    
    def render_slide(self, text: str, output_path: Path) -> Path:
        """
        Render a slide to an image file.
        
        Args:
            text: Text to render
            output_path: Path to save the image
            
        Returns:
            Path to the generated image
        """
        # Create image with background
        image = Image.new(
            "RGB",
            (self.width, self.height),
            self.background_color
        )
        
        # Draw text
        self._draw_text(image, text)
        
        # Save
        output_path.parent.mkdir(parents=True, exist_ok=True)
        image.save(str(output_path), quality=95)
        
        logger.debug(f"✅ Rendered slide: {output_path}")
        return output_path
    
    def _draw_text(self, image: Image.Image, text: str) -> None:
        """Draw text on image."""
        draw = ImageDraw.Draw(image)
        
        # Load font
        font = self._load_font()
        
        # Wrap text
        wrapped_lines = self._wrap_text(text, draw, font)
        
        # Calculate vertical position
        total_height = len(wrapped_lines) * self.font_size
        y_start = (self.height - total_height) // 2
        
        # Draw each line
        for i, line in enumerate(wrapped_lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]
            x = (self.width - line_width) // 2
            y = y_start + i * self.font_size
            
            # Draw with shadow for better readability
            shadow_color = (0, 0, 0)
            draw.text((x + 3, y + 3), line, fill=shadow_color, font=font)
            draw.text((x, y), line, fill=self.text_color, font=font)
    
    def _load_font(self) -> ImageFont.FreeTypeFont:
        """Load the best available font."""
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/System/Library/Fonts/Arial.ttf",  # macOS
            "C:\\Windows\\Fonts\\arial.ttf",  # Windows
        ]
        
        for font_path in font_paths:
            try:
                return ImageFont.truetype(font_path, self.font_size)
            except Exception:
                continue
        
        # Fallback to default font
        logger.warning("Could not load TrueType font, using default")
        return ImageFont.load_default()
    
    def _wrap_text(
        self,
        text: str,
        draw: ImageDraw.ImageDraw,
        font: ImageFont.FreeTypeFont,
    ) -> list[str]:
        """Wrap text to fit within image width."""
        # Estimate characters per line based on font size
        avg_char_width = self.font_size * 0.6  # Rough estimate
        max_width = self.width - 80  # 40px padding on each side
        max_chars_per_line = int(max_width / avg_char_width)
        
        lines = []
        words = text.split()
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            
            if len(test_line) <= max_chars_per_line:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines if lines else [text]
    
    def _parse_color(
        self, color: str | tuple[int, int, int]
    ) -> tuple[int, int, int]:
        """Parse color string to RGB tuple."""
        if isinstance(color, tuple):
            return color
        
        # Handle hex colors
        if color.startswith("#"):
            hex_color = color.lstrip("#")
            if len(hex_color) == 6:
                return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        # Handle named colors (basic set)
        color_names = {
            "white": (255, 255, 255),
            "black": (0, 0, 0),
            "red": (255, 0, 0),
            "green": (0, 255, 0),
            "blue": (0, 0, 255),
            "yellow": (255, 255, 0),
            "purple": (128, 0, 128),
            "orange": (255, 165, 0),
        }
        
        if color.lower() in color_names:
            return color_names[color.lower()]
        
        # Default to white
        logger.warning(f"Unknown color '{color}', using white")
        return (255, 255, 255)
