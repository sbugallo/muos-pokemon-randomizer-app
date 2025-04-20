"""Core data models for the Pokémon ROM randomizer application.

This module defines the data structures and state management classes that form the backbone of the
application. It includes:
- UI color definitions and glyph constants
- File system tree representation
- Application state management
- Step/screen workflow definition
- Button configuration models

The models use Pydantic for data validation and serialization.
"""

from enum import IntEnum, StrEnum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class Colors(StrEnum):
    """Colors used throughout the application UI.

    This enum defines the color palette used across the application, ensuring consistent styling and
    theming. Colors are defined in hexadecimal format.
    """

    BACKGROUND = "#000000"  # Black background
    PRIMARY = "#FFFFFF"  # White for primary text/elements
    ERROR = "#FF0000"  # Red for error states
    SUCCESS = "#19CB00"  # Green for success states
    ALERT = "#B03030"  # Red variant for alerts/warnings


class Glyphs(StrEnum):
    """Unicode glyphs used for icons in the UI.

    This enum maps semantic names to Unicode characters that serve as icons in the application. The
    glyphs are sourced from a custom font that provides consistent iconography across different
    platforms.

    The glyphs are organized into categories:
    - Status indicators (heart, exclamation, thunder)
    - Action indicators (check, close)
    - File system icons (file, folder, SD card)
    - Game controller buttons (d-pad, face buttons, menu)
    """

    HEART = "\ue000"
    EXCLAMATION = "\ue002"
    THUNDER = "\ue001"
    THUNDER_FILLED = "\ue003"

    CHECK = "\ue005"
    CLOSE = "\ue006"

    FILE = "\ue007"
    FOLDER = "\ue008"
    SD_CARD = "\ue009"

    GAME_PAD = "\ue004"
    GAME_PAD_A = "\ue00a"
    GAME_PAD_B = "\ue00b"
    GAME_PAD_MENU = "\ue00c"
    GAME_PAD_X = "\ue00d"
    GAME_PAD_Y = "\ue00e"
    GAME_PAD_DOWN = "\ue00f"
    GAME_PAD_LEFT = "\ue010"
    GAME_PAD_RIGHT = "\ue011"
    GAME_PAD_UP = "\ue012"


class ButtonConfig(BaseModel):
    """Configuration for a controller button in the UI.

    Maps a controller button to its visual representation in the UI, pairing a glyph icon with a
    text label.

    Attributes:
        glyph (Glyphs): The icon to display for this button
        label (str): The text label describing the button's action
    """

    glyph: Glyphs
    label: str


class TreeNode(BaseModel):
    """Represents a node in the file system tree structure.

    This model is used to build a hierarchical representation of the file system for ROM selection.
    Each node can represent either a file or directory.

    Attributes:
        name (str): Display name of the file or directory
        is_file (bool): True if this node represents a file, False for directories
        path (Path): Absolute path to the file or directory
        children (list[TreeNode]): List of child nodes for directories
    """

    name: str
    is_file: bool = False
    path: Path
    children: list["TreeNode"] = Field(default_factory=list)


class Step(IntEnum):
    """Steps/screens in the application workflow.

    Defines the possible screens in the application and their order. The integer values represent
    the sequence of steps in the workflow.
    """

    SELECT_ROM = 0
    RANDOMIZE_ROM = 1


class ExitMenuStatus(BaseModel):
    """Status of the exit menu dialog.

    Tracks the state of the exit confirmation dialog, including visibility and user selection.

    Attributes:
        exit (bool): Whether the user has confirmed exit
        show (bool): Whether the exit dialog is currently visible
        selected_item (int): Index of the currently selected menu item
    """

    exit: bool = False
    show: bool = False
    selected_item: int = 1


class SelectROMStatus(BaseModel):
    """Status of the ROM selection screen.

    Manages the state of the ROM selection interface, including the file system tree, current
    selection, and navigation history.

    Attributes:
        tree (TreeNode): Root of the file system tree
        selected_rom (Path | None): Currently selected ROM file
        selections (list[TreeNode]): History of selected nodes
        current_selection (int): Index of current selection in current directory
        current_dir (TreeNode): Currently displayed directory node
    """

    tree: TreeNode
    selected_rom: Path | None = None
    selections: list[TreeNode] = Field(default_factory=list)
    current_selection: int = 0
    current_dir: TreeNode

    def __init__(self, **data: Any) -> None:
        """Initialize the ROM selection status.

        Creates the initial file system tree and sets up the selection state.

        Args:
            **data: Additional initialization data
        """
        tree = TreeNode(
            name="root",
            path=Path("/"),
            children=self._generate_tree(),
        )

        data["tree"] = tree
        data["current_dir"] = tree

        super().__init__(**data)

    def _is_empty_child(self, child: TreeNode) -> bool:
        """Check if a tree node is a folder and has no children.

        Args:
            child (TreeNode): The node to check

        Returns:
            bool: True if the node is an empty folder, False otherwise
        """
        if not child.is_file and child.children is not None and len(child.children) == 0:
            return True

        return False

    def _generate_tree(self, folder: Path | None = None) -> list[TreeNode]:
        """Generate a tree structure from the filesystem.

        Recursively builds a tree of TreeNode objects representing the file system hierarchy,
        filtering for ROM files.

        Args:
            folder (Path | None): Starting folder. If None, starts from SD directories. Defaults to
                None.

        Returns:
            list[TreeNode]: List of tree nodes for the current level
        """
        results: list[TreeNode] = []

        if folder is None:
            sd1_roms_path = Path("/mnt") / "mmc" / "ROMS"
            sd2_roms_path = Path("/mnt") / "sdcard" / "ROMS"

            if sd1_roms_path.exists():
                child = TreeNode(
                    name=f"{Glyphs.SD_CARD} SD1/",
                    path=sd1_roms_path,
                    children=self._generate_tree(sd1_roms_path),
                )

                if not self._is_empty_child(child):
                    results.append(child)

            if sd2_roms_path.exists():
                child = TreeNode(
                    name=f"{Glyphs.SD_CARD} SD2/",
                    path=sd2_roms_path,
                    children=self._generate_tree(sd2_roms_path),
                )

                if not self._is_empty_child(child):
                    results.append(child)

        else:
            for entry in folder.iterdir():
                if entry.is_dir():
                    child = TreeNode(
                        name=f"{Glyphs.FOLDER} {entry.name}/",
                        path=entry,
                        children=self._generate_tree(entry),
                    )

                    if not self._is_empty_child(child):
                        results.append(child)

                elif entry.is_file() and entry.suffix.lower() in [".gba", ".gbc", ".gb"]:
                    results.append(
                        TreeNode(
                            name=f"{Glyphs.FILE} {entry.name}",
                            is_file=True,
                            path=entry,
                        )
                    )

        return results

    def reload_tree(self) -> TreeNode:
        """Reload the entire file system tree structure.

        Rebuilds the file system tree from scratch, useful when the underlying file system may have
        changed.

        Returns:
            TreeNode: The root node of the reloaded tree
        """
        self.tree = TreeNode(
            name="root",
            path=Path("/"),
            children=self._generate_tree(),
        )
        return self.tree


class RandomizeROMStatus(BaseModel):
    """Status of the ROM randomization process.

    Tracks the state and progress of the ROM randomization operation.

    Attributes:
        is_running (bool): Whether randomization is currently in progress
        is_finished (bool): Whether randomization has completed
        logs (str): Log output from the randomization process
    """

    is_running: bool = False
    is_finished: bool = False
    logs: str = ""


class AppStatus(BaseModel):
    """Overall application status containing all sub-component states.

    This is the root state container for the entire application, consolidating all the various
    status objects that track different aspects of the application state.

    Attributes:
        current_step (Step): Current screen/step in the workflow
        exit_menu_status (ExitMenuStatus): Exit dialog state
        select_rom_status (SelectROMStatus): ROM selection screen state
        randomize_rom_status (RandomizeROMStatus): Randomization process state
    """

    current_step: Step = Step.SELECT_ROM
    exit_menu_status: ExitMenuStatus = ExitMenuStatus()
    select_rom_status: SelectROMStatus = SelectROMStatus()
    randomize_rom_status: RandomizeROMStatus = RandomizeROMStatus()

    def next_step(self) -> None:
        """Move to the next step in the application workflow.

        Updates the current_step to the next logical step in the application flow. Currently handles
        progression from ROM selection to randomization.
        """
        if self.current_step == Step.SELECT_ROM:
            self.current_step = Step.RANDOMIZE_ROM

        elif self.current_step == Step.RANDOMIZE_ROM:
            self.current_step = Step.RANDOMIZE_ROM

    def previous_step(self) -> None:
        """Move to the previous step in the application workflow and reset state.

        Handles navigation to the previous step, including cleaning up any state from the current
        step. Currently handles moving back from randomization to ROM selection.
        """
        if self.current_step == Step.RANDOMIZE_ROM:
            self.select_rom_status.reload_tree()
            self.select_rom_status.current_dir = self.select_rom_status.tree
            self.select_rom_status.selections = []
            self.select_rom_status.selected_rom = None
            self.select_rom_status.current_selection = 0

            self.randomize_rom_status.is_running = False
            self.randomize_rom_status.is_finished = False
            self.randomize_rom_status.logs = ""

            self.current_step = Step.SELECT_ROM
