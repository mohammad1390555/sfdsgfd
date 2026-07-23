# Black Bear

**Black Bear** is a Linux-only Python terminal dashboard with a numeric start menu, live logs, synthetic activity counters, 60-second status refreshes, file logging, and a one-command launcher.

> This project is a **safe synthetic demo**. It does **not** perform real cracking, credential attacks, payment testing, card testing, or unauthorized access of any kind.

---

## Features

- Linux-only runtime check
- English-only interface
- Numeric startup menu
- Full-screen Rich terminal dashboard
- Plain-text fallback mode
- Live synthetic logs with realistic session IDs and checkpoints
- Node health, latency, worker, queue, and activity panels
- Rolling statistics with a refresh every 60 seconds
- Optional file logging
- `Ctrl+C` to stop the live session safely
- `install.sh` installer for Linux
- `blackbear` command launcher
- `blackbear-uninstall` helper
- Ready to extend later with your own authorized API integrations

---

## Repository

GitHub URL used for this project documentation:

```bash
https://github.com/mohammad1390555/sfdsgfd
```

Clone it on Linux with:

```bash
git clone https://github.com/mohammad1390555/sfdsgfd.git
cd sfdsgfd
```

---

## Quick Install

From the repository directory:

```bash
chmod +x install.sh
./install.sh
```

If `~/.local/bin` is already in your `PATH`, start the app with:

```bash
blackbear
```

If it is not in your `PATH`, add it to your shell profile:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Then reload your shell and run:

```bash
blackbear
```

---

## Manual Run

If you do not want to install the launcher, you can run the app directly:

```bash
python3 main.py
```

Or with the virtual environment created by the installer:

```bash
.venv/bin/python main.py
```

---

## Menu Options

When Black Bear starts, it shows a numeric menu:

1. **Network Pulse Demo**
2. **Token Audit Demo**
3. **Queue Worker Demo**
4. **System Snapshot**
5. **Toggle File Logging**
6. **Exit**

Choose a number and press `Enter`.

---

## What Happens During a Live Session

After selecting a demo mode, Black Bear will:

- open a full-screen terminal dashboard
- generate realistic-looking but fully synthetic operational activity
- show live logs, node state changes, queue depth, latency, workers, and checkpoints
- update counters continuously
- refresh session statistics every 60 seconds
- keep running until you press `Ctrl+C`
- print a final summary before returning

---

## Commands

### Start the app

```bash
blackbear
```

### Start in plain mode

```bash
blackbear --plain
```

### Launch directly into a scenario

```bash
blackbear --scenario 1
blackbear --scenario 2
blackbear --scenario 3
```

### Auto-stop after a number of seconds

```bash
blackbear --scenario 1 --duration 20
```

### Enable log file output immediately

```bash
blackbear --log-to-file
```

### Show version

```bash
blackbear --version
```

### Uninstall the launcher

```bash
blackbear-uninstall
```

### Publish this repository to GitHub securely

```bash
chmod +x publish.sh
./publish.sh
```

The script:

- asks for your GitHub username and token interactively
- does not save the token in the repository
- commits pending changes if needed
- pushes to the configured GitHub repository

---

## Configuration

Edit `config.py` to customize behavior:

```python
APP_NAME = "Black Bear"
APP_COMMAND = "blackbear"
APP_VERSION = "1.0.0"
REFRESH_INTERVAL_SECONDS = 60
TICK_SECONDS = 1
SCREEN_REFRESH_PER_SECOND = 4
LOG_LINES = 20
MIN_OPS_PER_TICK = 4
MAX_OPS_PER_TICK = 18
DEFAULT_LOG_TO_FILE = False
LOG_DIR = "logs"
LOG_FILE_NAME = "blackbear.log"
```

### Important settings

- `REFRESH_INTERVAL_SECONDS`: stats refresh interval
- `TICK_SECONDS`: loop delay between updates
- `LOG_LINES`: visible in-memory live log lines
- `MIN_OPS_PER_TICK` and `MAX_OPS_PER_TICK`: synthetic activity range
- `DEFAULT_LOG_TO_FILE`: default file logging state

---

## Log Files

When file logging is enabled, logs are written to:

```bash
logs/blackbear.log
```

You can enable file logging in two ways:

- by selecting **Toggle File Logging** in the menu
- by launching with `--log-to-file`

---

## Project Structure

```text
sfdsgfd/
├── main.py
├── config.py
├── requirements.txt
├── install.sh
├── uninstall.sh
├── README.md
├── LICENSE
└── .gitignore
```

---

## Tested Usage Example

```bash
git clone https://github.com/mohammad1390555/sfdsgfd.git
cd sfdsgfd
chmod +x install.sh
./install.sh
blackbear
```

---

## Extending It Later With Your Own API

If you want to connect a real and authorized API later, the main entry points are:

- `simulate_tick(...)` in `main.py`
- `maybe_emit_refresh_stats(...)` in `main.py`
- `config.py` for intervals, behavior, and naming

You can replace the synthetic event generator with your own approved API calls, job polling, or monitoring logic.

---

## Linux Notes

Black Bear is intentionally Linux-only.

The installer tries to support common package managers:

- `apt-get`
- `dnf`
- `pacman`
- `zypper`
- `apk`

If your system is different, install Python 3 manually and run the app directly.

---

## Safe Use Notice

Black Bear is designed as a terminal simulation/dashboard project.
It is not a tool for bypassing access controls, testing stolen data, brute-forcing passwords, or performing cyber abuse.

---

## License

MIT
