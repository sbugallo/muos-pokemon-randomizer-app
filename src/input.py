"""Input handling system for game controller events.

This module provides a robust input handling system built on top of SDL2, specializing in game
controller support. It handles button press events, key repeat functionality, and maintains clean
state management for input devices.
"""

import os
import time
from enum import IntEnum
from threading import Lock
from typing import Any

import sdl2
from loguru import logger


class ControllerButton(IntEnum):
    """Enumeration of supported controller buttons mapped to SDL2 constants.

    This enum provides a clean interface for working with controller buttons by mapping
    human-readable names to SDL2's button constants. This abstraction allows the rest of the
    application to work with button inputs without directly dealing with SDL2's constants.

    The enum includes all standard game controller buttons including:
    - Face buttons (A, B, X, Y)
    - Shoulder buttons (L1, R1)
    - Stick buttons (L3, R3)
    - Menu buttons (SELECT, START, MENU)
    - D-pad directions (UP, DOWN, LEFT, RIGHT)
    """

    A = sdl2.SDL_CONTROLLER_BUTTON_A
    B = sdl2.SDL_CONTROLLER_BUTTON_B
    X = sdl2.SDL_CONTROLLER_BUTTON_X
    Y = sdl2.SDL_CONTROLLER_BUTTON_Y
    L1 = sdl2.SDL_CONTROLLER_BUTTON_LEFTSHOULDER
    R1 = sdl2.SDL_CONTROLLER_BUTTON_RIGHTSHOULDER
    L3 = sdl2.SDL_CONTROLLER_BUTTON_LEFTSTICK
    R3 = sdl2.SDL_CONTROLLER_BUTTON_RIGHTSTICK
    SELECT = sdl2.SDL_CONTROLLER_BUTTON_BACK
    START = sdl2.SDL_CONTROLLER_BUTTON_START
    MENUF = sdl2.SDL_CONTROLLER_BUTTON_GUIDE
    DPAD_UP = sdl2.SDL_CONTROLLER_BUTTON_DPAD_UP
    DPAD_DOWN = sdl2.SDL_CONTROLLER_BUTTON_DPAD_DOWN
    DPAD_LEFT = sdl2.SDL_CONTROLLER_BUTTON_DPAD_LEFT
    DPAD_RIGHT = sdl2.SDL_CONTROLLER_BUTTON_DPAD_RIGHT


class Input(object):
    """Input handler for controller events.

    This class manages all input-related functionality including:
    - Controller initialization and mapping
    - Button state tracking
    - Key repeat handling
    - Thread-safe state management

    The class uses SDL2's game controller API and provides thread-safe operations for managing input
    state across multiple threads.

    Attributes:
        controllers (list[Any]): List of initialized game controllers
    """

    def __init__(self) -> None:
        """Initialize the input system and load controller mappings.

        Sets up:
        - Input state tracking with thread safety
        - Controller mappings from environment or default
        - Key repeat settings
        - Game controller initialization

        Raises:
            RuntimeError: If no game controllers are found
        """
        self._initialized = True
        self._input_lock = Lock()

        # Track the state of all keys
        self._keys_pressed: set[ControllerButton] = set()
        self._keys_held: set[ControllerButton] = set()
        self._keys_held_start_time: dict[ControllerButton, float] = {}

        # Key repeat settings
        self._initial_delay = 0.35

        # Enable controller events
        self._load_controller_mappings()
        sdl2.SDL_GameControllerEventState(sdl2.SDL_ENABLE)
        sdl2.SDL_JoystickEventState(sdl2.SDL_ENABLE)

        # Open controllers
        self.controllers: list[Any] = []

        num_controllers = sdl2.SDL_NumJoysticks()
        logger.info(f"Found {num_controllers} controller(s)")

        for i in range(num_controllers):
            if sdl2.SDL_IsGameController(i):
                controller = sdl2.SDL_GameControllerOpen(i)
                if controller:
                    name = sdl2.SDL_GameControllerName(controller).decode("utf-8")
                    self.controllers.append(controller)
                    logger.info(f"Found game controller {i}: {name}")
            else:
                logger.info(f"Joystick {i} is not a recognized game controller")

        if not self.controllers:
            logger.error("No game controllers found.")
            raise RuntimeError("No game controllers found.")

    def _load_controller_mappings(self) -> None:
        """Load controller mappings from environment variable or fallback file.

        Attempts to load controller mappings in the following order:
        1. From SDL_GAMECONTROLLERCONFIG environment variable as a mapping string
        2. From SDL_GAMECONTROLLERCONFIG environment variable as a file path
        3. Falls back to SDL default mappings if neither is available

        The method handles both direct mapping strings and mapping files, providing detailed
        feedback about the mapping process.
        """
        config_path = sdl2.SDL_getenv(b"SDL_GAMECONTROLLERCONFIG")
        if config_path:
            config_str = config_path.decode("utf-8")

            if "," in config_str and not config_str.endswith((".txt", ".cfg")):
                # Treat as mapping string - encode to bytes
                mapping_bytes = config_str.encode("utf-8")
                result = sdl2.SDL_GameControllerAddMapping(mapping_bytes)
                if result == -1:
                    logger.warning(
                        "Warning: Failed to load mapping from environment: "
                        f"{sdl2.SDL_GetError().decode()}"
                    )
                else:
                    logger.info("Loaded controller mapping from environment")
            else:
                # Treat as file path - encode to bytes for SDL function
                if os.path.exists(config_str):
                    file_path_bytes = config_str.encode("utf-8")
                    result = sdl2.SDL_GameControllerAddMappingsFromFile(file_path_bytes)
                    if result == -1:
                        logger.warning(
                            f"Warning: Could not load file {config_str}: "
                            f"{sdl2.SDL_GetError().decode()}"
                        )
                    else:
                        logger.info(f"Loaded {result} controller mappings from file {config_str}")
                else:
                    logger.warning(f"Warning: Controller config file {config_str} not found")
        else:
            logger.info("No controller mappings loaded - using SDL defaults")

    def _add_key_pressed(self, key: ControllerButton) -> None:
        """Add a key to the pressed set.

        This method is thread-safe and handles the addition of a key to both the pressed and held
        sets, also recording the press time for key repeat functionality.

        Args:
            key (ControllerButton): The button that was pressed.
        """
        with self._input_lock:
            self._keys_pressed.add(key)
            self._keys_held.add(key)
            self._keys_held_start_time[key] = time.time()

    def _remove_key_held(self, key: ControllerButton) -> None:
        """Remove a key from the held set.

        This method is thread-safe and handles the removal of a key from the held set and cleans up
        the associated timing information.

        Args:
            key (ControllerButton): The button that was released.
        """
        with self._input_lock:
            self._keys_held.discard(key)
            self._keys_held_start_time.pop(key, None)

    def check_event(self, event: sdl2.SDL_Event | None = None) -> bool:
        """Check for input events and update key states.

        Process SDL2 controller events, updating internal key state tracking. This method is
        thread-safe and handles both button press and release events.

        Args:
            event (sdl2.SDL_Event | None): The SDL event to process. Defaults to None.

        Returns:
            bool: True if an event was processed, False otherwise.
        """
        if event:
            # Controller button press
            if event.type == sdl2.SDL_CONTROLLERBUTTONDOWN:
                button = event.cbutton.button
                # Map button to key name using the _key_mapping dictionary
                if button in ControllerButton.__members__.values():
                    key_name = ControllerButton(button)
                    self._add_key_pressed(key_name)
                    return True

            # Controller button release
            elif event.type == sdl2.SDL_CONTROLLERBUTTONUP:
                button = event.cbutton.button

                # Clear the key if it was pressed
                if button in ControllerButton.__members__.values():
                    key_name = ControllerButton(button)
                    self._remove_key_held(key_name)

        return False

    def key(self, key: ControllerButton) -> bool:
        """Check if a specific key is pressed or being held.

        This method is thread-safe and implements key repeat functionality. A key is considered
        "pressed" if:
        1. It was just pressed this frame
        2. It has been held beyond the initial delay threshold

        Args:
            key (ControllerButton): The button to check

        Returns:
            bool: True if the button is pressed or held beyond delay
        """
        with self._input_lock:
            is_pressed = key in self._keys_pressed
            self._keys_pressed.discard(key)

            if key in self._keys_held:
                held_time = time.time() - self._keys_held_start_time[key]
                if held_time >= self._initial_delay:
                    is_pressed = True

            return is_pressed

    def clear_pressed(self) -> None:
        """Clear the pressed keys set.

        This thread-safe method resets the state of pressed keys while maintaining held key state.
        This is typically called at the end of each frame to prepare for the next frame's input
        processing.
        """
        with self._input_lock:
            self._keys_pressed.clear()

    def destroy(self) -> None:
        """Clean up SDL resources.

        This method performs thorough cleanup of all input-related resources:
        - Closes all open game controllers
        - Clears internal state
        - Shuts down the SDL game controller subsystem

        This should be called before the application exits to ensure proper resource cleanup.
        """
        with self._input_lock:
            for controller in self.controllers:
                sdl2.SDL_GameControllerClose(controller)

            self.controllers = []  # Clear the list of controllers
            self._keys_pressed = set()
            self._keys_held = set()
            self._keys_held_start_time = {}

        sdl2.SDL_QuitSubSystem(sdl2.SDL_INIT_GAMECONTROLLER)
