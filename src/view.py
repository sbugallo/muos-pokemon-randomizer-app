"""View management and rendering system for the application UI.

This module implements the core view management system, handling:
- Main view rendering and composition
- Navigation between different screens
- Layout management for headers, footers, and content
- Input handling and event routing

The module uses a component-based architecture where different parts of the UI (header, footer,
content) are handled by specialized components.
"""

from PIL.ImageDraw import ImageDraw

import draw_utils
from gui_components import BaseContent, ExitMenu, Footer, Header, RandomizeROM, SelectROM
from input import ControllerButton, Input
from models import AppStatus, ButtonConfig, Step


class View(object):
    """Main view handler for the application UI.

    This class orchestrates the rendering and interaction of all UI components, including:
    - Screen layout management
    - Component composition
    - Navigation handling
    - Input routing

    The view maintains a collection of content components for different application steps and
    handles transitions between them.

    Attributes:
        _header_height (int): Height of the header section in pixels
        _footer_height (int): Height of the footer section in pixels
    """

    def __init__(self) -> None:
        """Initialize the view instance.

        Creates instances of all UI components and sets up the content registry mapping steps to
        their corresponding content components.
        """
        self._exit_menu = ExitMenu()
        self._steps: dict[Step, BaseContent] = {
            Step.SELECT_ROM: SelectROM(),
            Step.RANDOMIZE_ROM: RandomizeROM(),
        }

    @property
    def _header_height(self) -> int:
        """Height of the header section in pixels.

        Returns:
            int: The fixed height allocated for the header
        """
        return 50

    @property
    def _footer_height(self) -> int:
        """Height of the footer section in pixels.

        Returns:
            int: The fixed height allocated for the footer
        """
        return 50

    def _render_header(self, canvas: ImageDraw, status: AppStatus) -> None:
        """Render the header component.

        Renders the application header with title and version information in the allocated space.

        Args:
            canvas (ImageDraw): Canvas to draw on
            status (AppStatus): Current application status
        """
        header = Header()
        header.render(
            status=status,
            canvas=canvas,
            start_x=0,
            start_y=0,
            end_x=canvas.im.size[0],
            end_y=self._header_height,
        )

    def _render_footer(
        self,
        canvas: ImageDraw,
        status: AppStatus,
        buttons_config: dict[ControllerButton, ButtonConfig] | None = None,
    ) -> None:
        """Render the footer component with button controls.

        Renders the footer showing available button controls based on the current context and
        state.

        Args:
            canvas (ImageDraw): Canvas to draw on
            status (AppStatus): Current application status
            buttons_config (dict[ControllerButton, ButtonConfig] | None): Button configuration.
                Defaults to None.
        """
        screen_height = canvas.im.size[1]
        screen_width = canvas.im.size[0]

        footer = Footer(buttons_config=buttons_config)
        footer.render(
            status=status,
            canvas=canvas,
            start_x=0,
            start_y=screen_height - self._footer_height,
            end_x=screen_width,
            end_y=screen_height,
        )

    def _render_content(self, canvas: ImageDraw, status: AppStatus) -> None:
        """Render the main content area.

        Renders the content component corresponding to the current application step in the space
        between header and footer.

        Args:
            canvas (ImageDraw): Canvas to draw on
            status (AppStatus): Current application status
        """
        content = self._steps[status.current_step]
        content_start_x = 0
        content_start_y = self._header_height + 1
        content_end_x = canvas.im.size[0]
        content_end_y = canvas.im.size[1] - self._footer_height - 1

        content.render(
            status=status,
            canvas=canvas,
            start_x=content_start_x,
            start_y=content_start_y,
            end_x=content_end_x,
            end_y=content_end_y,
        )

    def _render_exit_menu(self, canvas: ImageDraw, status: AppStatus) -> None:
        """Render the exit confirmation dialog.

        Renders the exit menu as a modal dialog overlaying the main content when active.

        Args:
            canvas (ImageDraw): Canvas to draw on
            status (AppStatus): Current application status
        """
        screen_height = canvas.im.size[1]
        screen_width = canvas.im.size[0]

        self._exit_menu.render(
            status=status,
            canvas=canvas,
            start_x=0,
            start_y=0,
            end_x=screen_width,
            end_y=screen_height,
        )

    def handle_navigation(self, input: Input, status: AppStatus) -> None:
        """Handle navigation input.

        Routes navigation events to either the exit menu or current content view based on
        application state.

        Args:
            input (Input): The input handler to check for navigation
            status (AppStatus): The current application status
        """
        if input.key(ControllerButton.MENUF):
            status.exit_menu_status.selected_item = 1
            status.exit_menu_status.show = not status.exit_menu_status.show

        elif status.exit_menu_status.show:
            self._exit_menu.handle_navigation(input=input, status=status)

        else:
            self._steps[status.current_step].handle_navigation(input=input, status=status)

    def render(self, canvas: ImageDraw, status: AppStatus) -> None:
        """Render the complete view.

        Composes and renders all UI components in their proper layout positions. This includes:
        1. Header at the top
        2. Footer at the bottom
        3. Content in the middle
        4. Exit menu overlay when active

        Args:
            canvas (ImageDraw): The canvas to draw on
            status (AppStatus): The current status of the application
        """
        draw_utils.draw_clear(canvas=canvas)

        buttons_config = self._steps[status.current_step].get_buttons_config()
        if status.exit_menu_status.show:
            buttons_config = self._exit_menu.get_buttons_config()

        self._render_header(canvas=canvas, status=status)
        self._render_footer(canvas=canvas, status=status, buttons_config=buttons_config)
        self._render_content(canvas=canvas, status=status)

        if status.exit_menu_status.show:
            self._render_exit_menu(canvas=canvas, status=status)
