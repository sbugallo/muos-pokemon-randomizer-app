#!/bin/bash
# HELP: MuOS app to randomize Pokémon games
# ICON: pokemon-randomizer

. /opt/muos/script/var/func.sh

echo app >/tmp/act_go

ROOT_DIR="$(GET_VAR "device" "storage/rom/mount")"
APP_DIR="${ROOT_DIR}/MUOS/application/Pokémon Randomizer"
ICON_DIR=/opt/muos/default/MUOS/theme/active/glyph/muxapp/
FONTS_DIR="/usr/share/fonts/pokemon-randomizer"
RANDOMIZER_JAR="${APP_DIR}/3rd-party/PokeRandoZX.jar"

# Copy app icon
cp "${APP_DIR}/resources/pokemon-randomizer.png" "${ICON_DIR}/pokemon-randomizer.png"

# Copy app fonts
mkdir -p "${FONTS_DIR}"
cp "${APP_DIR}/fonts/pokemon-randomizer.ttf" "${FONTS_DIR}/pokemon-randomizer.ttf"
cd "${APP_DIR}" || exit

source "${ROOT_DIR}/MUOS/PortMaster/muos/control.txt"
get_controls

export PYSDL2_DLL_PATH="/usr/lib"
export LD_LIBRARY_PATH="${APP_DIR}/libs:${LD_LIBRARY_PATH}"

python3 -u main.py

SCREEN_TYPE="internal"
DEVICE_MODE="$(GET_VAR "global" "boot/device_mode")"
if [[ ${DEVICE_MODE} -eq 1 ]]; then
	SCREEN_TYPE="external"
fi

DEVICE_WIDTH="$(GET_VAR "device" "screen/${SCREEN_TYPE}/width")"
DEVICE_HEIGHT="$(GET_VAR "device" "screen/${SCREEN_TYPE}/height")"
FB_SWITCH "${DEVICE_WIDTH}" "${DEVICE_HEIGHT}" 32
