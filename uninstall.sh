#!/usr/bin/env bash
set -euo pipefail

APP_COMMAND="blackbear"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="${HOME}/.local/bin"
LAUNCHER_PATH="${BIN_DIR}/${APP_COMMAND}"
UNINSTALLER_PATH="${BIN_DIR}/${APP_COMMAND}-uninstall"

printf '[+] Removing launcher files...\n'
rm -f "${LAUNCHER_PATH}" "${UNINSTALLER_PATH}"

if [[ -d "${PROJECT_DIR}/.venv" ]]; then
  printf '[+] Removing virtual environment...\n'
  rm -rf "${PROJECT_DIR}/.venv"
fi

printf '[+] Black Bear was removed from this user account.\n'
printf '[i] Project files are still here: %s\n' "${PROJECT_DIR}"
printf '[i] Delete the project folder manually if you want a full cleanup.\n'
