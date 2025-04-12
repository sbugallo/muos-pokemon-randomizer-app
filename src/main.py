"""Main entry point for the Pokémon ROM Randomizer application.

This module initializes SDL2 with the required subsystems and manages the main application loop.
It's responsible for:
- SDL2 initialization and cleanup
- Application lifecycle management
- Error handling and graceful shutdown

The module serves as the starting point for the application, creating the main App instance and
running the event loop until exit.
"""

import sys
from pathlib import Path

libs_path = Path(__file__).resolve().parent / "deps"
sys.path.insert(0, str(libs_path.absolute()))

import sdl2  # noqa: E402
from loguru import logger  # noqa: E402

from app import App  # noqa: E402


def destroy(app: App, exit_code: int) -> None:
    """Destroy the application and clean up resources.

    Cleans up application resources and exits with the specified code.

    Args:
        app (App): The application instance to destroy.
        exit_code (int): The exit code to return to the operating system.
    """
    logger.info("Destroying application...")
    app.destroy()

    sys.stdout.close()
    sys.exit(exit_code)


@logger.catch(reraise=True)
def main() -> None:
    """Main function to initialize the application and handle events.

    Initializes SDL2 with video and joystick support, creates the main app instance, and runs the
    main event loop until exit.
    """
    logs_folder = Path(__file__).resolve().parent / "logs"
    logs_folder.mkdir(parents=True, exist_ok=True)

    log_file_path = logs_folder / "{time}.log"
    logger.add(log_file_path)

    logger.info("Starting Pokémon ROM Randomizer app...")
    if sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO | sdl2.SDL_INIT_GAMECONTROLLER) < 0:
        logger.error(f"SDL2 initialization failed: {sdl2.SDL_GetError()}")
        sys.exit(1)

    app = App()
    app.start()

    try:
        while app.running:
            app.update()
            sdl2.SDL_Delay(16)

    except RuntimeError:
        destroy(app, 1)

    destroy(app, 0)


if __name__ == "__main__":
    main()
