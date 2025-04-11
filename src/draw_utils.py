"""Drawing utilities for rendering the application UI.

This module provides a collection of high-level drawing functions that abstract common UI rendering
tasks. It handles text rendering, shapes, and layout calculations while maintaining consistent
styling and appearance across the application.

The module uses PIL's ImageDraw for rendering and supports:
- Text rendering with custom fonts
- Rectangle drawing with optional rounded corners
- Color management and fills
- Basic layout calculations
"""

import math
from pathlib import Path

from PIL import ImageFont
from PIL.ImageDraw import ImageDraw

from models import Colors


def draw_rectangle(
    canvas: ImageDraw,
    start_x: int,
    start_y: int,
    end_x: int,
    end_y: int,
    fill_color: str | None = None,
    outline_color: str | None = None,
    line_width: int = 1,
    radius: float | None = None,
) -> None:
    """Draw a rectangle on the canvas.

    Provides a unified interface for drawing rectangles, supporting both standard and rounded
    rectangles with customizable appearance.

    Args:
        canvas (ImageDraw): The PIL drawing canvas
        start_x (int): Left coordinate of the rectangle
        start_y (int): Top coordinate of the rectangle
        end_x (int): Right coordinate of the rectangle
        end_y (int): Bottom coordinate of the rectangle
        fill_color (str | None): Color to fill the rectangle with. Defaults to None
        outline_color (str | None): Color of the rectangle's outline. Defaults to None
        line_width (int): Width of the outline in pixels. Defaults to 1
        radius (float | None): Radius for rounded corners. Defaults to None for sharp corners
    """
    position = (start_x, start_y, end_x, end_y)

    if radius is None:
        canvas.rectangle(position, fill=fill_color, outline=outline_color, width=line_width)
    else:
        canvas.rounded_rectangle(
            position, radius=radius, fill=fill_color, outline=outline_color, width=line_width
        )


def draw_text(
    canvas: ImageDraw,
    start_x: int,
    start_y: int,
    text: str,
    font_size: int = 15,
    color: str = "#FFFFFF",
    anchor: str | None = None,
) -> None:
    """Draw text on the canvas using the application's custom font.

    Renders text with consistent styling using the application's custom font. The text can be
    positioned precisely with optional anchor points.

    Args:
        canvas (ImageDraw): The PIL drawing canvas
        start_x (int): X-coordinate for text placement
        start_y (int): Y-coordinate for text placement
        text (str): The text to render
        font_size (int): Size of the font in points. Defaults to 15
        color (str): Color of the text in hex format. Defaults to white
        anchor (str | None): PIL text anchor point (e.g., "lt", "mm"). Defaults to None
    """
    position = (start_x, start_y)
    font_path = Path(__file__).resolve().parent / "fonts" / "pokemon-randomizer.ttf"
    font = ImageFont.truetype(str(font_path.absolute()), font_size)

    canvas.text(position, text, font=font, fill=color, anchor=anchor)


def draw_clear(canvas: ImageDraw) -> None:
    """Clear the canvas by filling it with the background color.

    Resets the entire canvas to the application's background color, effectively clearing all
    content.

    Args:
        canvas (ImageDraw): The PIL drawing canvas to clear
    """
    height = canvas.im.size[1]
    width = canvas.im.size[0]

    draw_rectangle(
        canvas=canvas, start_x=0, start_y=0, end_x=width, end_y=height, fill_color=Colors.BACKGROUND
    )


def get_text_width(text: str, font_size: int) -> int:
    """Calculate the approximate width of text in pixels.

    Provides a fast approximation of text width without loading the font. This is useful for layout
    calculations where exact precision isn't required.

    Args:
        text (str): The text to measure
        font_size (int): The font size to use for measurement

    Returns:
        int: Approximate width of the text in pixels, based on average character width
    """
    return math.ceil(len(text) * (font_size * 0.67))
