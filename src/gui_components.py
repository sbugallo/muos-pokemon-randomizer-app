"""GUI components for building the application's user interface.

This module implements a component-based UI system with specialized components for:
- Base component abstractions
- Header and footer bars
- ROM selection interface
- ROM randomization interface
- Exit confirmation dialog

Each component handles its own:
- Rendering logic
- Input processing
- Layout management
- State updates

The components follow a consistent interface defined by BaseComponent and BaseContent classes,
allowing for uniform integration into the view system.
"""

import os
import subprocess
import threading
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from shutil import copyfile
from tempfile import TemporaryDirectory

from loguru import logger
from PIL.ImageDraw import ImageDraw

import draw_utils
from __version__ import version
from input import ControllerButton, Input
from models import AppStatus, ButtonConfig, Colors, Glyphs


class BaseComponent(ABC):
    """Base class for GUI components.

    Defines the fundamental interface that all UI components must implement. This abstract base
    class ensures consistent behavior across components by enforcing a standard rendering interface.

    Components are responsible for:
    - Rendering themselves within given bounds
    - Maintaining their internal state
    - Processing relevant application status
    """

    @abstractmethod
    def render(
        self,
        status: AppStatus,
        canvas: ImageDraw,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
    ) -> None:
        """Render the content of the component.

        Args:
            status (AppStatus): Current application status for state-dependent rendering
            canvas (ImageDraw): The PIL drawing canvas
            start_x (int): Left boundary of component's drawing area
            start_y (int): Top boundary of component's drawing area
            end_x (int): Right boundary of component's drawing area
            end_y (int): Bottom boundary of component's drawing area
        """
        pass


class BaseContent(BaseComponent):
    """Base class for main content components.

    Extends BaseComponent with input handling and button configuration capabilities required for
    interactive content areas. Content components represent full screens or major UI sections that
    can receive user input.

    In addition to rendering, content components must:
    - Define their button mappings
    - Handle navigation events
    - Maintain their state
    """

    @staticmethod
    @abstractmethod
    def get_buttons_config() -> dict[ControllerButton, ButtonConfig]:
        """Get button configuration for this content.

        Defines the mapping of controller buttons to their functions for this content component.
        This configuration is used to render the button guide in the footer.

        Returns:
            dict[ControllerButton, ButtonConfig]: Mapping of buttons to their configurations
        """
        pass

    @abstractmethod
    def handle_navigation(self, input: Input, status: AppStatus) -> None:
        """Handle navigation input events.

        Process controller input to update component and application state. This method is called
        when the component is active and receiving input.

        Args:
            input (Input): Input handler for checking button states
            status (AppStatus): Current application status to update
        """
        pass


class Header(BaseComponent):
    """Header component showing application title and version."""

    def __init__(
        self,
        padding: int = 20,
        font_size: int = 25,
        separator_height: int = 2,
    ) -> None:
        """Initialize header component.

        Args:
            padding (int): Padding around text. Defaults to 20.
            font_size (int): Font size for header text. Defaults to 25.
            separator_height (int): Height of separator line. Defaults to 2.
        """
        self.padding = padding
        self.font_size = font_size
        self.separator_height = separator_height

    def render(
        self,
        status: AppStatus,
        canvas: ImageDraw,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
    ) -> None:
        """Render the header component.

        Args:
            status (AppStatus): Current application status.
            canvas (ImageDraw): The canvas to draw on.
            start_x (int): Left coordinate.
            start_y (int): Top coordinate.
            end_x (int): Right coordinate.
            end_y (int): Bottom coordinate.
        """
        height = end_y - start_y

        separator_start_x = start_x
        separator_start_y = end_y - self.separator_height
        separator_end_x = end_x
        separator_end_y = end_y

        text_start_x = start_x + self.padding
        text_start_y = start_y + int(height / 2 - self.font_size / 2)

        draw_utils.draw_text(
            canvas=canvas,
            start_x=text_start_x,
            start_y=text_start_y,
            text=f"{Glyphs.THUNDER_FILLED} Pokémon Randomizer v{version}",
            font_size=self.font_size,
            color=Colors.PRIMARY,
        )

        draw_utils.draw_rectangle(
            canvas=canvas,
            start_x=separator_start_x,
            start_y=separator_start_y,
            end_x=separator_end_x,
            end_y=separator_end_y,
            fill_color=Colors.PRIMARY,
        )


class Footer(BaseComponent):
    """Footer component showing available button controls."""

    def __init__(
        self,
        padding: int = 10,
        font_size: int = 25,
        separator_height: int = 2,
        radius: int = 10,
        label_margin: int = 5,
        buttons_config: dict[ControllerButton, ButtonConfig] | None = None,
    ) -> None:
        """Initialize footer component.

        Args:
            padding (int): Padding around buttons. Defaults to 10.
            font_size (int): Font size for button labels. Defaults to 25.
            separator_height (int): Height of separator line. Defaults to 2.
            radius (int): Border radius of buttons. Defaults to 10.
            label_margin (int): Margin between button and label. Defaults to 5.
            buttons_config (dict[ControllerButton, ButtonConfig] | None): Button configuration.
                Defaults to None.
        """
        self.padding = padding
        self.font_size = font_size
        self.separator_height = separator_height
        self.radius = radius
        self.label_margin = label_margin
        self.buttons_config = buttons_config or {}

        self.buttons_config[ControllerButton.MENUF] = ButtonConfig(
            glyph=Glyphs.GAME_PAD_MENU,
            label="Exit",
        )

    def render(
        self,
        status: AppStatus,
        canvas: ImageDraw,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
    ) -> None:
        """Render the footer component.

        Args:
            status (AppStatus): Current application status.
            canvas (ImageDraw): The canvas to draw on.
            start_x (int): Left coordinate.
            start_y (int): Top coordinate.
            end_x (int): Right coordinate.
            end_y (int): Bottom coordinate.
        """
        button_start_y = start_y + self.padding + self.separator_height
        button_start_x = start_x + self.padding

        draw_utils.draw_rectangle(
            canvas=canvas,
            start_x=start_x,
            start_y=start_y,
            end_x=end_x,
            end_y=start_y + self.separator_height,
            fill_color=Colors.PRIMARY,
        )

        for config in self.buttons_config.values():
            full_text = f"{config.glyph} {config.label}"

            draw_utils.draw_text(
                canvas=canvas,
                start_x=button_start_x,
                start_y=button_start_y,
                text=full_text,
                color=Colors.PRIMARY,
                font_size=self.font_size,
            )

            button_start_x += draw_utils.get_text_width(full_text, self.font_size) + 20


class ExitMenu(BaseContent):
    """Exit confirmation dialog component."""

    def __init__(
        self,
        height: int = 160,
        padding: int = 10,
        gap: int = 3,
        title_font_size: int = 25,
        button_font_size: int = 20,
    ) -> None:
        """Initialize exit menu.

        Args:
            height (int): Height of the dialog. Defaults to 160.
            padding (int): Padding around elements. Defaults to 10.
            gap (int): Gap between buttons. Defaults to 3.
            title_font_size (int): Font size for title. Defaults to 25.
            button_font_size (int): Font size for buttons. Defaults to 20.
        """
        self.height = height
        self.padding = padding
        self.gap = gap
        self.title_font_size = title_font_size
        self.button_font_size = button_font_size

    def _draw_modal(
        self,
        status: AppStatus,
        canvas: ImageDraw,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        title_text: str,
    ) -> None:
        """Draw the modal dialog box.

        Args:
            status (AppStatus): Current application status.
            canvas (ImageDraw): Canvas to draw on.
            start_x (int): Left position.
            start_y (int): Top position.
            end_x (int): Right position.
            end_y (int): Bottom position.
            title_text (str): Title text to display.
        """
        draw_utils.draw_rectangle(
            canvas=canvas,
            start_x=start_x,
            start_y=start_y,
            end_x=end_x,
            end_y=end_y,
            fill_color=Colors.BACKGROUND,
            outline_color=Colors.ALERT,
            line_width=2,
        )

        title_start_x = start_x + self.padding
        title_start_y = start_y + 2 + self.padding

        draw_utils.draw_text(
            canvas=canvas,
            start_x=title_start_x,
            start_y=title_start_y,
            text=title_text,
            font_size=self.title_font_size,
            color=Colors.PRIMARY,
        )

        buttons_container_start_x = start_x + self.padding * 3
        buttons_container_start_y = title_start_y + self.title_font_size + self.padding
        buttons_container_end_x = end_x - self.padding * 3
        buttons_container_end_y = end_y - 2 - self.padding

        buttons_container_center_y = (
            buttons_container_start_y + (buttons_container_end_y - buttons_container_start_y) // 2
        )

        button_height = self.button_font_size + self.padding * 2

        buttons_height = button_height * 2 + self.gap

        buttons_start_x = buttons_container_start_x
        buttons_start_y = buttons_container_center_y - buttons_height // 2
        buttons_end_x = buttons_container_end_x

        option_1_start_x = buttons_start_x
        option_1_start_y = buttons_start_y
        option_1_end_x = buttons_end_x
        option_1_end_y = option_1_start_y + button_height
        option_1_center_x = buttons_start_x + (buttons_end_x - buttons_start_x) // 2
        option_1_center_y = option_1_start_y + button_height // 2

        draw_utils.draw_rectangle(
            canvas=canvas,
            start_x=option_1_start_x,
            start_y=option_1_start_y,
            end_x=option_1_end_x,
            end_y=option_1_end_y,
            fill_color=Colors.ALERT if status.exit_menu_status.selected_item == 0 else None,
            outline_color=Colors.ALERT,
            line_width=1,
        )

        option_1_text = f"{Glyphs.CHECK} YES"
        option_1_text_width = draw_utils.get_text_width(option_1_text, self.button_font_size)
        option_1_text_start_x = option_1_center_x - option_1_text_width // 2
        option_1_text_start_y = option_1_center_y - self.button_font_size // 2

        draw_utils.draw_text(
            canvas=canvas,
            start_x=option_1_text_start_x,
            start_y=option_1_text_start_y,
            text=option_1_text,
            font_size=self.button_font_size,
            color=Colors.PRIMARY if status.exit_menu_status.selected_item == 0 else Colors.ALERT,
        )

        option_2_start_x = buttons_start_x
        option_2_start_y = option_1_end_y + self.gap
        option_2_end_x = buttons_end_x
        option_2_end_y = option_2_start_y + button_height
        option_2_center_x = buttons_start_x + (buttons_end_x - buttons_start_x) // 2
        option_2_center_y = option_2_start_y + button_height // 2

        draw_utils.draw_rectangle(
            canvas=canvas,
            start_x=option_2_start_x,
            start_y=option_2_start_y,
            end_x=option_2_end_x,
            end_y=option_2_end_y,
            fill_color=Colors.ALERT if status.exit_menu_status.selected_item == 1 else None,
            outline_color=Colors.ALERT,
            line_width=1,
        )

        option_2_text = f"{Glyphs.CLOSE} NO"
        option_2_text_width = draw_utils.get_text_width(option_2_text, self.button_font_size)
        option_2_text_start_x = option_2_center_x - option_2_text_width // 2
        option_2_text_start_y = option_2_center_y - self.button_font_size // 2

        draw_utils.draw_text(
            canvas=canvas,
            start_x=option_2_text_start_x,
            start_y=option_2_text_start_y,
            text=option_2_text,
            font_size=self.button_font_size,
            color=Colors.PRIMARY if status.exit_menu_status.selected_item == 1 else Colors.ALERT,
        )

    @staticmethod
    def get_buttons_config() -> dict[ControllerButton, ButtonConfig]:
        """Get button configuration for exit menu.

        Returns:
            dict[ControllerButton, ButtonConfig]: Button configuration mapping.
        """
        return {
            ControllerButton.DPAD_UP: ButtonConfig(
                glyph=Glyphs.GAME_PAD_UP,
                label="Up",
            ),
            ControllerButton.DPAD_DOWN: ButtonConfig(
                glyph=Glyphs.GAME_PAD_DOWN,
                label="Down",
            ),
            ControllerButton.A: ButtonConfig(
                glyph=Glyphs.GAME_PAD_A,
                label="Select",
            ),
        }

    def handle_navigation(self, input: Input, status: AppStatus) -> None:
        """Handle navigation events.

        Process directional pad and button inputs to navigate the exit confirmation dialog.

        Args:
            input (Input): Input handler instance to check button presses
            status (AppStatus): Current application status for exit menu state
        """
        if input.key(ControllerButton.DPAD_UP):
            status.exit_menu_status.selected_item -= 1
            status.exit_menu_status.selected_item %= 2

        elif input.key(ControllerButton.DPAD_DOWN):
            status.exit_menu_status.selected_item += 1
            status.exit_menu_status.selected_item %= 2

        elif input.key(ControllerButton.A):
            if status.exit_menu_status.selected_item == 0:
                status.exit_menu_status.exit = True
            else:
                status.exit_menu_status.show = False

            status.exit_menu_status.selected_item = 1

    def render(
        self,
        status: AppStatus,
        canvas: ImageDraw,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
    ) -> None:
        """Render the exit confirmation dialog.

        Draws the modal dialog box with title and buttons for user confirmation.

        Args:
            status (AppStatus): Current application status.
            canvas (ImageDraw): The canvas to draw on.
            start_x (int): Left coordinate.
            start_y (int): Top coordinate.
            end_x (int): Right coordinate.
            end_y (int): Bottom coordinate.
        """
        container_width = end_x - start_x
        container_height = end_y - start_y

        title_text = "DO YOU WANT TO EXIT?"
        title_width = draw_utils.get_text_width(title_text, self.title_font_size)

        modal_width = title_width + self.padding * 2

        modal_start_x = int(start_x + container_width / 2 - modal_width / 2)
        modal_start_y = int(start_y + container_height / 2 - self.height / 2)
        modal_end_x = int(modal_start_x + modal_width)
        modal_end_y = int(modal_start_y + self.height)

        self._draw_modal(
            status=status,
            canvas=canvas,
            start_x=modal_start_x,
            start_y=modal_start_y,
            end_x=modal_end_x,
            end_y=modal_end_y,
            title_text=title_text,
        )


class SelectROM(BaseContent):
    """ROM selection screen component."""

    def __init__(self, padding: int = 10, font_size: int = 20, gap: int = 10) -> None:
        """Initialize ROM selection screen.

        Args:
            padding (int): Padding around elements. Defaults to 10.
            font_size (int): Font size for file names. Defaults to 20.
            gap (int): Gap between file entries. Defaults to 10.
        """
        self.padding = padding
        self.font_size = font_size
        self.gap = gap

    @staticmethod
    def get_buttons_config() -> dict[ControllerButton, ButtonConfig]:
        """Get button configuration for ROM selection screen.

        Returns:
            dict[ControllerButton, ButtonConfig]: Button configuration mapping.
        """
        return {
            ControllerButton.DPAD_UP: ButtonConfig(
                glyph=Glyphs.GAME_PAD_UP,
                label="Up",
            ),
            ControllerButton.DPAD_DOWN: ButtonConfig(
                glyph=Glyphs.GAME_PAD_DOWN,
                label="Down",
            ),
            ControllerButton.A: ButtonConfig(
                glyph=Glyphs.GAME_PAD_A,
                label="Select",
            ),
            ControllerButton.B: ButtonConfig(
                glyph=Glyphs.GAME_PAD_B,
                label="Back",
            ),
        }

    def handle_navigation(self, input: Input, status: AppStatus) -> None:
        """Handle navigation events for ROM selection screen.

        Process directional pad and button inputs to navigate the ROM selection interface, including
        moving up/down the file list, selecting files/folders, and going back.

        Args:
            input (Input): Input handler instance to check button presses
            status (AppStatus): Current application status for ROM selection state
        """
        if input.key(ControllerButton.DPAD_UP):
            status.select_rom_status.current_selection -= 1
            if status.select_rom_status.current_selection < 0:
                status.select_rom_status.current_selection = (
                    len(status.select_rom_status.current_dir.children) - 1
                )

        elif input.key(ControllerButton.DPAD_DOWN):
            status.select_rom_status.current_selection += 1
            if status.select_rom_status.current_selection >= len(
                status.select_rom_status.current_dir.children
            ):
                status.select_rom_status.current_selection = 0

        elif input.key(ControllerButton.A):
            selected_child = status.select_rom_status.current_dir.children[
                status.select_rom_status.current_selection
            ]
            status.select_rom_status.selections.append(selected_child)

            if selected_child.is_file:
                status.select_rom_status.selected_rom = selected_child.path
                status.next_step()

            else:
                status.select_rom_status.current_dir = (
                    status.select_rom_status.current_dir.children[
                        status.select_rom_status.current_selection
                    ]
                )
                status.select_rom_status.current_selection = 0

        elif input.key(ControllerButton.B):
            if status.select_rom_status.current_dir.path != Path("/"):
                status.select_rom_status.selections.pop()
                status.select_rom_status.current_dir = status.select_rom_status.tree
                for entry in status.select_rom_status.selections:
                    for children in status.select_rom_status.current_dir.children:
                        if entry.path == children.path:
                            status.select_rom_status.current_dir = children
                            break

                status.select_rom_status.current_selection = 0

    def render(
        self,
        status: AppStatus,
        canvas: ImageDraw,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
    ) -> None:
        """Render the ROM selection screen.

        Draws the list of files and directories in the current directory, highlighting the selected
        entry.

        Args:
            status (AppStatus): Current application status.
            canvas (ImageDraw): The canvas to draw on.
            start_x (int): Left coordinate.
            start_y (int): Top coordinate.
            end_x (int): Right coordinate.
            end_y (int): Bottom coordinate.
        """
        window_size = 10
        window_start_index = status.select_rom_status.current_selection // window_size * window_size
        window_end_index = window_start_index + window_size

        window = status.select_rom_status.current_dir.children[window_start_index:window_end_index]

        selected_index = status.select_rom_status.current_selection % window_size

        container_start_x = start_x + self.padding
        container_start_y = start_y + self.padding

        entry_start_y = container_start_y

        for i, children in enumerate(window):
            draw_utils.draw_text(
                canvas=canvas,
                start_x=container_start_x,
                start_y=entry_start_y,
                text=children.name,
                font_size=self.font_size,
                color=Colors.SUCCESS if i == selected_index else Colors.PRIMARY,
            )

            entry_start_y += self.font_size + self.gap


class RandomizeROM(BaseContent):
    """Screen component for ROM randomization process."""

    def __init__(self, padding: int = 10, font_size: int = 20, gap: int = 10) -> None:
        """Initialize the ROM randomization screen.

        Args:
            padding (int): Padding around elements. Defaults to 10.
            font_size (int): Font size for text. Defaults to 20.
            gap (int): Gap between log entries. Defaults to 10.
        """
        self.padding = padding
        self.font_size = font_size
        self.gap = gap

        self._is_finished_lock = threading.Lock()
        self._is_running_lock = threading.Lock()
        self._logs_lock = threading.Lock()

    @staticmethod
    def get_buttons_config() -> dict[ControllerButton, ButtonConfig]:
        """Get button configuration for ROM randomization screen.

        Returns:
            dict[ControllerButton, ButtonConfig]: Button configuration mapping.
        """
        return {
            ControllerButton.A: ButtonConfig(
                glyph=Glyphs.GAME_PAD_A,
                label="Select",
            ),
            ControllerButton.B: ButtonConfig(
                glyph=Glyphs.GAME_PAD_B,
                label="Back",
            ),
        }

    def _patch_rom(self, status: AppStatus) -> None:
        """Execute the ROM randomization process.

        This method runs in a separate thread and handles the entire ROM randomization process,
        including file operations and running the randomizer JAR.

        Args:
            status (AppStatus): Current application status.
        """
        with TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)

            orig_rom_path = status.select_rom_status.selected_rom

            if orig_rom_path is None:
                with self._logs_lock:
                    message = "No ROM selected."
                    logger.info(message)
                    status.randomize_rom_status.logs = message

                with self._is_running_lock:
                    status.randomize_rom_status.is_running = False
                return

            if not orig_rom_path.exists():
                with self._logs_lock:
                    message = f"ROM not found: {orig_rom_path}"
                    logger.info(message)
                    status.randomize_rom_status.logs = message

                with self._is_running_lock:
                    status.randomize_rom_status.is_running = False
                return

            src_rom_path = temp_dir_path / f"src{orig_rom_path.suffix}"
            copyfile(orig_rom_path, src_rom_path)

            rom_extension = src_rom_path.suffix.lower().strip(".")
            config_path = Path(__file__).parent / "configs" / f"{rom_extension}.rnqs"

            if not config_path.exists():
                with self._logs_lock:
                    message = f"No configuration found for {rom_extension} files:\n {config_path}"
                    logger.info(message)
                    status.randomize_rom_status.logs = message

                with self._is_running_lock:
                    status.randomize_rom_status.is_running = False
                return

            bin_path = Path(__file__).parent / "3rd-party" / "PokeRandoZX.jar"
            if not bin_path.exists():
                with self._logs_lock:
                    message = f"Randomizer binary not found: {bin_path}"
                    logger.info(message)
                    status.randomize_rom_status.logs = message

                with self._is_running_lock:
                    status.randomize_rom_status.is_running = False
                return

            now = datetime.now().strftime("%Y%m%d%H%M%S")
            dst_rom_path = src_rom_path.with_suffix(f".randomized.{now}.{rom_extension}")
            out_rom_path = orig_rom_path.with_suffix(f".randomized.{now}.{rom_extension}")

            command = (
                f"/opt/java/bin/java -Xmx4608M -jar '{bin_path}' cli "
                f"-i '{src_rom_path}' "
                f"-o '{dst_rom_path}' "
                f"-s '{config_path}'"
            )

            with self._logs_lock:
                message = f"{Glyphs.EXCLAMATION} Starting randomization"
                logger.info(message)
                status.randomize_rom_status.logs += f"{message}\n"

            try:
                subprocess.run(
                    command,
                    check=True,
                    env=os.environ.copy(),
                    shell=True,
                )

                # There is a strange behaviour with the randomizer. E.g., when randomizer a .gb
                # file, it creates a .gbc file. So we need to be careful with the extension.
                files_in_output_dir = [
                    entry
                    for entry in temp_dir_path.iterdir()
                    if entry.is_file() and entry.name != src_rom_path.name
                ]

                if len(files_in_output_dir) != 1:
                    message = (
                        f"Expected one file in output directory, but found "
                        f"{len(files_in_output_dir)}: {files_in_output_dir}"
                    )
                    logger.error(message)
                    raise Exception(message)

                dst_rom_path = files_in_output_dir[0]
                copyfile(dst_rom_path, out_rom_path)

                with self._logs_lock:
                    message = (
                        f"[SUCCESS] Randomization completed {Glyphs.HEART}.\n"
                        f"Randomized ROM saved to: {out_rom_path}"
                    )
                    logger.info(message)
                    status.randomize_rom_status.logs += f"{message}\n"

            except Exception as e:
                with self._logs_lock:
                    message = f"[ERROR] Randomization failed: {e}"
                    logger.error(message)
                    status.randomize_rom_status.logs += f"{message}\n"

            with self._is_running_lock, self._is_finished_lock:
                status.randomize_rom_status.is_running = False
                status.randomize_rom_status.is_finished = True

    def handle_navigation(self, input: Input, status: AppStatus) -> None:
        """Handle navigation events for ROM randomization screen.

        Handle button inputs from the controller to start/stop randomization process or navigate
        back to the previous screen.

        Args:
            input (Input): Input handler instance to check button presses
            status (AppStatus): Current application status to track randomization state
        """
        if input.key(ControllerButton.A):
            with self._is_running_lock, self._is_finished_lock:
                if status.randomize_rom_status.is_finished:
                    return

                if not status.randomize_rom_status.is_running:
                    threading.Thread(
                        target=self._patch_rom,
                        args=(status,),
                        daemon=True,
                    ).start()
                    status.randomize_rom_status.is_running = True

        elif input.key(ControllerButton.B):
            with self._is_running_lock:
                if not status.randomize_rom_status.is_running:
                    status.previous_step()

    def render(
        self,
        status: AppStatus,
        canvas: ImageDraw,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
    ) -> None:
        """Render the ROM randomization screen.

        Draws the randomization screen interface including instructions text and log entries.

        Args:
            status (AppStatus): Current application status containing randomization state
            canvas (ImageDraw): The PIL ImageDraw canvas to draw on
            start_x (int): Left coordinate of the drawing area
            start_y (int): Top coordinate of the drawing area
            end_x (int): Right coordinate of the drawing area
            end_y (int): Bottom coordinate of the drawing area
        """
        container_start_x = start_x + self.padding
        container_start_y = start_y + self.padding

        draw_utils.draw_text(
            canvas=canvas,
            start_x=container_start_x,
            start_y=container_start_y,
            text=f"Press {Glyphs.GAME_PAD_A} to start randomizing the ROM.",
            font_size=self.font_size,
            color=Colors.PRIMARY,
        )

        with self._logs_lock:
            logs = status.randomize_rom_status.logs.split("\n")
            logs = [log for log in logs if log.strip() != ""]
            logs = logs[-20:]

        entry_start_y = container_start_y + self.font_size + self.gap
        for log in logs:
            if log.startswith("[ERROR]"):
                color = Colors.ERROR
            elif log.startswith("[SUCCESS]"):
                color = Colors.SUCCESS
            else:
                color = Colors.PRIMARY

            draw_utils.draw_text(
                canvas=canvas,
                start_x=container_start_x,
                start_y=entry_start_y,
                text=log,
                font_size=self.font_size,
                color=color,
            )

            entry_start_y += self.font_size + self.gap
