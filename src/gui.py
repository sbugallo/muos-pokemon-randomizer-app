"""GUI management system for the Pokémon ROM Randomizer.

This module provides the core graphical interface functionality, handling:
- Window creation and management via SDL2
- Hardware-accelerated rendering
- Aspect ratio preservation during scaling
- PIL to SDL2 texture conversion
- Screen resolution and scaling management

The module acts as a bridge between the application's PIL-based drawing and SDL2's
hardware-accelerated display system.
"""

import ctypes

import sdl2
from loguru import logger
from PIL import Image, ImageDraw

from models import AppStatus
from view import View


class GraphicalUserInterface(object):
    """Main GUI handler for SDL2-based window management and rendering.

    This class manages the application's main window and rendering pipeline, bridging PIL-based
    drawing with SDL2's hardware acceleration. It handles:
    - Window creation and management
    - Hardware-accelerated rendering
    - Resolution and scaling
    - Double-buffered display
    - PIL to SDL2 texture conversion

    The class maintains a virtual resolution that is scaled to fit the actual window while
    preserving aspect ratio.

    Attributes:
        screen_height (int): Virtual screen height for internal rendering
        screen_width (int): Virtual screen width for internal rendering
        view (View): The main view handler for rendering content
    """

    def __init__(self) -> None:
        """Initialize the GUI instance.

        Creates and configures:
        - Fullscreen SDL2 window
        - Hardware-accelerated renderer
        - PIL image and drawing canvas
        - View handler

        Raises:
            RuntimeError: If window or renderer creation fails
        """
        self.screen_height = 480
        self.screen_width = 640

        # 1. Create window
        self._window = sdl2.SDL_CreateWindow(
            "Pokémon Randomizer".encode("utf-8"),
            sdl2.SDL_WINDOWPOS_UNDEFINED,
            sdl2.SDL_WINDOWPOS_UNDEFINED,
            0,
            0,  # Size ignored in fullscreen mode
            sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP | sdl2.SDL_WINDOW_SHOWN,
        )

        if not self._window:
            logger.error(f"Failed to create window: {sdl2.SDL_GetError()}")
            raise RuntimeError("Failed to create window")

        # 2. Create renderer
        self._renderer = sdl2.SDL_CreateRenderer(self._window, -1, sdl2.SDL_RENDERER_ACCELERATED)

        if not self._renderer:
            logger.error(f"Failed to create renderer: {sdl2.SDL_GetError()}")
            raise RuntimeError("Failed to create renderer")

        # 3. Create Image and Draw
        self._reset()

        # 4. Set the view
        self.view = View()

    def _reset(self) -> None:
        """Reset the drawing canvas to its initial state.

        Creates a new PIL Image and ImageDraw instance for the next frame, clearing the canvas to
        black.
        """
        sdl2.SDL_SetRenderDrawColor(self._renderer, 0, 0, 0, 255)
        sdl2.SDL_RenderClear(self._renderer)
        self._image = Image.new("RGBA", (self.screen_width, self.screen_height), color="black")
        self._draw = ImageDraw.Draw(self._image)

    def _to_screen(self) -> None:
        """Render the PIL image to the SDL2 window while preserving aspect ratio.

        This method:
        1. Converts the PIL image to an SDL2 texture
        2. Calculates scaling to maintain aspect ratio
        3. Centers the scaled image in the window
        4. Renders the final result to screen

        The process maintains the original 4:3 aspect ratio regardless of window size while using
        hardware acceleration for scaling.
        """
        # Convert PIL image to SDL2 texture at base resolution
        rgba_data = self._image.tobytes()
        surface = sdl2.SDL_CreateRGBSurfaceWithFormatFrom(
            rgba_data,
            self.screen_width,
            self.screen_height,
            32,
            self.screen_width * 4,
            sdl2.SDL_PIXELFORMAT_RGBA32,
        )
        texture = sdl2.SDL_CreateTextureFromSurface(self._renderer, surface)
        sdl2.SDL_FreeSurface(surface)

        # Get current window size for scaling
        raw_window_width = ctypes.c_int()
        raw_window_height = ctypes.c_int()
        sdl2.SDL_GetWindowSize(
            self._window, ctypes.byref(raw_window_width), ctypes.byref(raw_window_height)
        )
        window_width = int(raw_window_width.value)
        window_height = int(raw_window_height.value)

        # Calculate scaling to fit fullscreen while preserving 4:3 aspect ratio
        scale = min(window_width / self.screen_width, window_height / self.screen_height)
        dst_width = int(self.screen_width * scale)
        dst_height = int(self.screen_height * scale)
        dst_x = (window_width - dst_width) // 2
        dst_y = (window_height - dst_height) // 2
        dst_rect = sdl2.SDL_Rect(dst_x, dst_y, dst_width, dst_height)

        # Render the texture to the window
        sdl2.SDL_RenderCopy(self._renderer, texture, None, dst_rect)
        sdl2.SDL_RenderPresent(self._renderer)
        sdl2.SDL_DestroyTexture(texture)

    def render(self, status: AppStatus) -> None:
        """Render the GUI to the screen.

        Updates the PIL image with the current view state and renders it to the SDL2 window while
        preserving aspect ratio.

        Args:
            status (AppStatus): The current application status.
        """
        self._reset()
        self.view.render(self._draw, status)
        self._to_screen()

    def destroy(self) -> None:
        """Clean up SDL2 resources before shutting down.

        Performs cleanup of:
        - SDL2 renderer
        - SDL2 window
        - SDL2 video subsystem
        """
        sdl2.SDL_DestroyRenderer(self._renderer)
        sdl2.SDL_DestroyWindow(self._window)
        sdl2.SDL_Quit()
