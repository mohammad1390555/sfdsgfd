#!/usr/bin/env bash
set -euo pipefail

APP_NAME="Black Bear"
APP_COMMAND="blackbear"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${PROJECT_DIR}/.venv"
BIN_DIR="${HOME}/.local/bin"
LAUNCHER_PATH="${BIN_DIR}/${APP_COMMAND}"
UNINSTALLER_PATH="${BIN_DIR}/${APP_COMMAND}-uninstall"

print_step() {
  printf '\n[+] %s\n' "$1"
}

print_warn() {
  printf '[!] %s\n' "$1"
}

command_exists() {
  command -v "$1" >/dev/null 2>&1
}

run_root() {
  if [[ "${EUID}" -eq 0 ]]; then
    "$@"
  elif command_exists sudo; then
    sudo "$@"
  else
    print_warn "Root privileges are required for system package installation, but sudo is not available."
    print_warn "Please install Python 3, venv, and pip manually, then run this script again."
    exit 1
  fi
}

install_system_packages() {
  if command_exists apt-get; then
    run_root apt-get update
    run_root apt-get install -y python3 python3-venv python3-pip
  elif command_exists dnf; then
    run_root dnf install -y python3 python3-pip
  elif command_exists pacman; then
    run_root pacman -Sy --noconfirm python python-pip
  elif command_exists zypper; then
    run_root zypper --non-interactive install python3 python3-pip python3-virtualenv
  elif command_exists apk; then
    run_root apk add --no-cache python3 py3-pip
  else
    print_warn "No supported package manager was detected."
    print_warn "Install Python 3, pip, and venv manually, then rerun install.sh."
    exit 1
  fi
}

ensure_linux() {
  if [[ "$(uname -s)" != "Linux" ]]; then
    print_warn "${APP_NAME} is Linux-only."
    exit 1
  fi
}

ensure_python() {
  if ! command_exists python3; then
    print_step "Python 3 was not found. Installing system packages..."
    install_system_packages
  fi

  if ! python3 -m venv --help >/dev/null 2>&1; then
    print_step "Python venv support was not found. Installing system packages..."
    install_system_packages
  fi
}

create_virtualenv() {
  print_step "Creating virtual environment"
  python3 -m venv "${VENV_DIR}"

  print_step "Installing Python dependencies"
  "${VENV_DIR}/bin/pip" install --upgrade pip
  "${VENV_DIR}/bin/pip" install -r "${PROJECT_DIR}/requirements.txt"
}

install_launcher() {
  print_step "Installing launcher into ${LAUNCHER_PATH}"
  mkdir -p "${BIN_DIR}"

  cat > "${LAUNCHER_PATH}" <<EOF
#!/usr/bin/env bash
exec "${VENV_DIR}/bin/python" "${PROJECT_DIR}/main.py" "\$@"
EOF

  chmod +x "${LAUNCHER_PATH}"

  cat > "${UNINSTALLER_PATH}" <<EOF
#!/usr/bin/env bash
exec "${PROJECT_DIR}/uninstall.sh" "\$@"
EOF

  chmod +x "${UNINSTALLER_PATH}"
}

print_finish() {
  print_step "Installation complete"
  printf 'Project directory: %s\n' "${PROJECT_DIR}"
  printf 'Run command      : %s\n' "${APP_COMMAND}"
  printf 'Direct run       : %s\n' "${VENV_DIR}/bin/python ${PROJECT_DIR}/main.py"

  if [[ ":${PATH}:" != *":${BIN_DIR}:"* ]]; then
    print_warn "${BIN_DIR} is not in your PATH."
    printf 'Add this line to your shell profile: export PATH="%s:$PATH"\n' "${BIN_DIR}"
  fi
}

main() {
  ensure_linux
  ensure_python
  create_virtualenv
  install_launcher
  mkdir -p "${PROJECT_DIR}/logs"
  print_finish
}

main "$@"
