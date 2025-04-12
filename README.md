# muOS Pokémon Randomizer

<div align="center">
    <img src="https://raw.githubusercontent.com/sbugallo/muos-pokemon-randomizer-app/refs/heads/main/docs/assets/logo.png" 
        height="180px" 
        width="auto" 
        alt="logo"
    >
</div>

A powerful Pokémon ROM randomizer for muOS devices that lets you create unique adventures by 
randomizing GB, GBA and GBC Pokémon games directly on your device.

<iframe 
    width="180" 
    height="101" 
    src="https://www.youtube.com/embed/Bd8pb15EkcE?si=TyM7J4A87iLWap03" 
    title="YouTube video player" 
    frameborder="0" 
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" 
    referrerpolicy="strict-origin-when-cross-origin" 
    allowfullscreen
></iframe>

## 🌟 Features

- 🎮 Full game controller support with an intuitive interface
- 📂 Easy ROM selection from SD cards
- 💫 Real-time randomization progress display
- 🖥️ Hardware-accelerated GUI with proper aspect ratio preservation
- 🔒 Original ROM files are preserved - randomized versions are saved as new files

## 🚀 Installation

1. Download the latest release:

    - Visit the [Releases](https://github.com/yourusername/muos_pokemon_randomizer/releases/latest) 
     page
    - Download the `Pokemon-Randomizer-Installer-*.muxapp` file

2. Install on your muOS device:

    - Connect your device to your computer or use a card reader
    - Copy the `.muxapp` file to `/mnt/mmc/ARCHIVE/` on your device
    - Safely eject your device

3. Install the application:

    - On your muOS device, open the Archive Manager
    - Select the `.muxapp` file you copied
    - Wait for the installation to complete

<div align="center">
    <img src="https://raw.githubusercontent.com/sbugallo/muos-pokemon-randomizer-app/refs/heads/main/docs/assets/screenshots/01.png" 
        height="180px" 
        width="auto" 
        alt="screenshot 1"
    >
    <img src="https://raw.githubusercontent.com/sbugallo/muos-pokemon-randomizer-app/refs/heads/main/docs/assets/screenshots/02.png" 
        height="180px" 
        width="auto" 
        alt="screenshot 2"
    >
    <img src="https://raw.githubusercontent.com/sbugallo/muos-pokemon-randomizer-app/refs/heads/main/docs/assets/screenshots/03.png" 
        height="180px" 
        width="auto" 
        alt="screenshot 3"
    >
</div>

4. Launch the application:

    - Go to the Applications menu
    - Select "Pokémon Randomizer"
    - The app should start up and display the main menu.

<div align="center">
    <img src="https://raw.githubusercontent.com/sbugallo/muos-pokemon-randomizer-app/refs/heads/main/docs/assets/screenshots/04.png" 
        height="180px" 
        width="auto" 
        alt="screenshot 4"
    >
    <img src="https://raw.githubusercontent.com/sbugallo/muos-pokemon-randomizer-app/refs/heads/main/docs/assets/screenshots/05.png" 
        height="180px" 
        width="auto" 
        alt="screenshot 5"
    >
</div>

## 🎮 Usage

1. Place your Pokémon ROMs in the ROMS directory of either SD card:
    - `/mnt/mmc/ROMS/` for SD1
    - `/mnt/sdcard/ROMS/` for SD2

2. Launch the application through muOS interface

3. Use the gamepad to navigate:
    - ➕ D-Pad: Navigate menus
    - 🔵 A: Select/Confirm
    - 🔴 B: Back
    - ⚙️ Menu: Exit

4. Select your ROM and press A to start randomization

<div align="center">
    <img src="https://raw.githubusercontent.com/sbugallo/muos-pokemon-randomizer-app/refs/heads/main/docs/assets/screenshots/05.png" 
        height="180px" 
        width="auto" 
        alt="screenshot 5"
    >
    <img src="https://raw.githubusercontent.com/sbugallo/muos-pokemon-randomizer-app/refs/heads/main/docs/assets/screenshots/06.png" 
        height="180px" 
        width="auto" 
        alt="screenshot 6"
    >
    <img src="https://raw.githubusercontent.com/sbugallo/muos-pokemon-randomizer-app/refs/heads/main/docs/assets/screenshots/07.png" 
        height="180px" 
        width="auto" 
        alt="screenshot 7"
    >
    <img src="https://raw.githubusercontent.com/sbugallo/muos-pokemon-randomizer-app/refs/heads/main/docs/assets/screenshots/08.png" 
        height="180px" 
        width="auto" 
        alt="screenshot 8"
    >
    <img src="https://raw.githubusercontent.com/sbugallo/muos-pokemon-randomizer-app/refs/heads/main/docs/assets/screenshots/09.png" 
        height="180px" 
        width="auto" 
        alt="screenshot 9"
    >
</div>

5. The randomized ROM will be saved in the same directory as the original with a suffix `.randomized.<timestamp>.<original extension>`
    - Example: `mygame.gb.randomized.20250410112345.gb`

<div align="center">
    <img src="https://raw.githubusercontent.com/sbugallo/muos-pokemon-randomizer-app/refs/heads/main/docs/assets/screenshots/10.png" 
        height="180px" 
        width="auto" 
        alt="screenshot 10"
    >
</div>

6. You can now play the randomized ROM on your muOS device or any compatible emulator

## ⚙️ Customizing Randomization Settings

The randomizer uses setting files (`.rnqs`) to control how games are randomized. These settings are 
stored in the application's config directory:

```
/mnt/mmc/MUOS/applications/Pokémon Randomizer/configs/
├── gb.rnqs  - Settings for Game Boy games (.gb)
├── gbc.rnqs - Settings for Game Boy Color games (.gbc)
└── gba.rnqs - Settings for Game Boy Advance games (.gba)
```

The appropriate settings file is automatically selected based on the ROM file extension:
- `.gb` ROMs → `gb.rnqs`
- `.gbc` ROMs → `gbc.rnqs`
- `.gba` ROMs → `gba.rnqs`

To customize the randomization:

1. Create your own settings using the [Universal Pokemon Randomizer ZX](https://github.com/Ajarmar/universal-pokemon-randomizer-zx/releases)
2. Export your settings as a `.rnqs` file
3. Copy your custom settings file to the configs directory, replacing the existing file for the 
  desired platform
4. Launch the randomizer - your settings will be automatically applied to games of that type

This allows you to have different randomization preferences for different generations of Pokémon 
games.

## 📋 Development Prerequisites

- [`conda`](https://www.anaconda.com/docs/getting-started/miniconda/install)

## 💻 Development Setup

1. Clone the repository:
```bash
$ git clone https://github.com/yourusername/muos_pokemon_randomizer.git
$ cd muos_pokemon_randomizer
```

2. Create and activate the conda environment:
```bash
$ conda env create -f conda.yml
$ conda activate muos-pokemon-randomizer
$ pre-commit install
```

This will install all dependecies and development tools like:
- `just` for task management
- `pre-commit` hooks for code quality
- `black` for code formatting
- `flake8` for linting
- `mypy` for type checking
- `isort` for import sorting

## 🛠️ Building

To build the application package:

```bash
$ just clean    # Clean the build directory
$ just build    # Build the application
$ just zip      # Create the .muxapp package
```

Or simply:

```bash
$ just muxapp   # Build and package in one command
```

The resulting `.muxapp` file will be located in the `.dist/` directory.

## 🔧 Technical Details

The application is built with:
- SDL2 for hardware-accelerated graphics and input handling
- PIL for image manipulation
- Pydantic for data validation and settings management
- Threading for responsive UI during randomization
- Custom component-based UI system

## 📜 License

This project is licensed under the GNU Affero General Public License v3.0 - see the 
[LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- This project was inspired by [The RomM Project muOS app](https://github.com/rommapp/muos-app)
- Font based on [ProFont Nerd Font](https://github.com/ryanoasis/nerd-fonts)
- The randomizer user is [Universal Pokemon Randomizer ZX v4.6.1](https://github.com/Ajarmar/universal-pokemon-randomizer-zx)

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Install pre-commit hooks (`pre-commit install`)
4. Commit your changes (`git commit -m 'Add some amazing feature'`). Bonus points for using 
  [conventional commits](https://www.conventionalcommits.org/)!
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

[license-badge]: https://img.shields.io/badge/license-AGPL--3.0-blue.svg
[license-badge-img]: https://img.shields.io/badge/license-AGPL--3.0-blue.svg
[release-badge]: https://img.shields.io/github/v/release/yourusername/muos_pokemon_randomizer
[release-badge-img]: https://img.shields.io/github/v/release/yourusername/muos_pokemon_randomizer
