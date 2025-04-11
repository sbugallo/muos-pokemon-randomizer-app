"""Application entry point and main app class for the Pokémon ROM randomizer.

This module contains the main App class that orchestrates the application's components including
input handling, GUI rendering, and event processing. It provides the core game loop and
initialization logic for the application.
"""

import threading

import sdl2
import sdl2.ext

from gui import GraphicalUserInterface
from input import Input
from models import AppStatus


class App(object):
    """Main application class that handles the game loop and input monitoring.

    This class serves as the central coordinator for the application, managing:
    - Input handling through SDL2
    - GUI rendering and updates
    - Application state management
    - Event processing and navigation

    The class follows a simple game loop pattern where input is processed, state is updated, and the
    GUI is rendered in a continuous cycle.
    """

    def __init__(self) -> None:
        """Initialize application components.

        Creates instances of:
        - Input handler for controller/keyboard events
        - AppStatus for application state management
        - GraphicalUserInterface for rendering
        """
        self.input = Input()
        self.status = AppStatus()
        self.gui = GraphicalUserInterface()
        self.running = False

    def _handle_navigation(self) -> None:
        """Handle navigation events and update application state.

        Processes navigation events through the GUI view and updates the application's running state
        based on exit menu status.
        """
        self.gui.view.handle_navigation(self.input, self.status)

        if self.status.exit_menu_status.exit:
            self.running = False

    def _monitor_input(self) -> None:
        """Monitor SDL2 events in a separate thread.

        Continuously polls for SDL2 events and processes them through the input handler. Also
        handles application quit events.
        """
        while self.running:
            events: list[sdl2.SDL_Event] = sdl2.ext.get_events()
            for event in events:
                self.input.check_event(event)
                if event.type == sdl2.SDL_QUIT:
                    self.running = False

    def start(self) -> None:
        """Start the application and input monitoring thread.

        Initializes the main application loop and starts a daemon thread to monitor input events.
        """
        self.running = True
        threading.Thread(target=self._monitor_input, daemon=True).start()

    def update(self) -> None:
        """Update the application state and render the GUI.

        Performs one iteration of the game loop:
        1. Renders the current GUI state
        2. Processes navigation events
        3. Clears the input state for the next frame
        """
        self.gui.render(self.status)
        self._handle_navigation()
        self.input.clear_pressed()

    def destroy(self) -> None:
        """Clean up resources before shutting down.

        Performs cleanup of:
        - Input handler resources
        - GUI resources
        - SDL2 subsystems
        """
        self.input.destroy()
        self.gui.destroy()
        sdl2.SDL_Quit()
