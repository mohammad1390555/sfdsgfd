#!/usr/bin/env python3
# ─── Made by Mohammad — github.com/mohammad1390555 ───
from __future__ import annotations

import argparse
import getpass
import os
import platform
import random
import socket
import sys
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Deque, Dict, List, Optional

from rich.align import Align
from rich.console import Console, Group
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress_bar import ProgressBar
from rich.table import Table
from rich.text import Text

from config import (
    ACCENT_COLOR,
    APP_COMMAND,
    APP_NAME,
    APP_VERSION,
    BORDER_COLOR,
    DEFAULT_LOG_TO_FILE,
    ERROR_COLOR,
    INFO_COLOR,
    LINUX_ONLY,
    LOG_DIR,
    LOG_FILE_NAME,
    LOG_LINES,
    MAX_OPS_PER_TICK,
    MIN_OPS_PER_TICK,
    REFRESH_INTERVAL_SECONDS,
    SCREEN_REFRESH_PER_SECOND,
    TICK_SECONDS,
    WARNING_COLOR,
)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)

BASE_DIR = Path(__file__).resolve().parent
LOG_PATH = BASE_DIR / LOG_DIR / LOG_FILE_NAME
CONSOLE = Console()

BANNER = r"""
██████╗ ██╗      █████╗  ██████╗██╗  ██╗    ██████╗ ███████╗ █████╗ ██████╗
██╔══██╗██║     ██╔══██╗██╔════╝██║ ██╔╝    ██╔══██╗██╔════╝██╔══██╗██╔══██╗
██████╔╝██║     ███████║██║     █████╔╝     ██████╔╝█████╗  ███████║██████╔╝
██╔══██╗██║     ██╔══██║██║     ██╔═██╗     ██╔══██╗██╔══╝  ██╔══██║██╔══██╗
██████╔╝███████╗██║  ██║╚██████╗██║  ██╗    ██████╔╝███████╗██║  ██║██║  ██║
╚═════╝ ╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝    ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝
"""

SCENARIOS: Dict[str, Dict[str, object]] = {
    "1": {
        "name": "Network Pulse Demo",
        "description": "Synthetic network telemetry and event flow.",
        "unit": "events",
        "latency_range": (22, 145),
        "phases": ["Signal Sweep", "Stability Pass", "Relay Sync", "Telemetry Seal"],
        "nodes": [
            ("edge-gw-01", "gateway"),
            ("edge-gw-02", "gateway"),
            ("api-node-03", "api"),
            ("relay-04", "relay"),
            ("sensor-07", "sensor"),
        ],
        "actions": [
            "synthetic packet window sampled",
            "mock heartbeat acknowledged",
            "demo route latency normalized",
            "sandbox event stream updated",
            "safe replay buffer rotated",
            "telemetry envelope sealed",
        ],
    },
    "2": {
        "name": "Token Audit Demo",
        "description": "Authorized token and payload verification simulator.",
        "unit": "checks",
        "latency_range": (35, 180),
        "phases": ["Policy Sync", "Token Sweep", "Signature Pass", "Audit Seal"],
        "nodes": [
            ("vault-a", "vault"),
            ("vault-b", "vault"),
            ("validator-1", "validator"),
            ("validator-2", "validator"),
            ("queue-scan-5", "scanner"),
        ],
        "actions": [
            "sample token format verified",
            "mock signature path checked",
            "synthetic payload matched policy",
            "rate window recalculated",
            "demo audit checkpoint recorded",
            "authorized cache scope rotated",
        ],
    },
    "3": {
        "name": "Queue Worker Demo",
        "description": "Synthetic queue jobs and worker activity dashboard.",
        "unit": "jobs",
        "latency_range": (18, 130),
        "phases": ["Queue Prime", "Worker Burst", "Ack Pass", "Buffer Seal"],
        "nodes": [
            ("queue-alpha", "queue"),
            ("queue-beta", "queue"),
            ("queue-gamma", "queue"),
            ("worker-11", "worker"),
            ("worker-12", "worker"),
        ],
        "actions": [
            "mock task dequeued",
            "safe payload transformed",
            "batch confirmation emitted",
            "demo retry bucket scanned",
            "result envelope published",
            "worker dispatch checkpoint confirmed",
        ],
    },
}

LEVEL_STYLES = {
    "TRACE": "bright_black",
    "LOG": "white",
    "INFO": INFO_COLOR,
    "WARN": WARNING_COLOR,
    "ERROR": ERROR_COLOR,
    "STATS": ACCENT_COLOR,
    "FINAL": f"bold {ACCENT_COLOR}",
}

STATUS_STYLES = {
    "ONLINE": "bold bright_green",
    "WARM": "bold bright_yellow",
    "DEGRADED": "bold bright_red",
}

STATUS_WEIGHTS = [
    ("ONLINE", 0.76),
    ("WARM", 0.18),
    ("DEGRADED", 0.06),
]


@dataclass
class LogEntry:
    timestamp: str
    level: str
    message: str


@dataclass
class NodeState:
    name: str
    role: str
    status: str = "ONLINE"
    latency_ms: int = 0
    load_percent: int = 0
    last_seen: str = "just now"


@dataclass
class AppSettings:
    file_logging_enabled: bool = DEFAULT_LOG_TO_FILE


@dataclass
class SimulationState:
    scenario_key: str
    scenario_name: str
    scenario_description: str
    unit: str
    phases: List[str]
    latency_range: tuple[int, int]
    settings: AppSettings
    nodes: List[NodeState]
    session_id: str = field(default_factory=lambda: f"BB-{random.randint(100000, 999999)}")
    phase: str = "Boot Sequence"
    start_time: float = field(default_factory=time.time)
    last_refresh: float = field(default_factory=time.time)
    total_ops: int = 0
    last_tick_ops: int = 0
    loop_count: int = 0
    queue_depth: int = 0
    active_workers: int = 0
    success_count: int = 0
    warning_count: int = 0
    error_count: int = 0
    policy_hits: int = 0
    latency_ms: int = 0
    cpu_percent: int = 0
    mem_percent: int = 0
    net_mbps: int = 0
    last_checkpoint: str = "awaiting first checkpoint"
    running: bool = True
    logs: Deque[LogEntry] = field(default_factory=lambda: deque(maxlen=LOG_LINES))


def ensure_linux() -> None:
    if LINUX_ONLY and not sys.platform.startswith("linux"):
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # print(f...",),{APP_NAME} is Linux-only.")
        sys.exit(1)


def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def clear_screen() -> None:
    if sys.stdout.isatty() and os.environ.get("TERM"):
        os.system("clear")


def ensure_log_dir() -> None:
    (BASE_DIR / LOG_DIR).mkdir(parents=True, exist_ok=True)


def write_log_file(line: str) -> None:
    ensure_log_dir()
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def add_log(state: SimulationState, level: str, message: str, echo: bool = False) -> None:
    entry = LogEntry(timestamp=now_str(), level=level, message=message)
    state.logs.append(entry)
    line = f"[{entry.timestamp}] [{entry.level}] {entry.message}"
    if state.settings.file_logging_enabled:
        write_log_file(line)
    if echo:
        # print(line)


def weighted_status() -> str:
    roll = random.random()
    current = 0.0
    for name, weight in STATUS_WEIGHTS:
        current += weight
        if roll <= current:
            return name
    return "ONLINE"


def build_header(state: Optional[SimulationState] = None) -> Panel:
    if state is None:
        status_line = Text(
            f"Idle • launcher: {APP_COMMAND} • mode: synthetic demo engine",
            style=ACCENT_COLOR,
        )
    else:
        status_line = Text(
            f"Session {state.session_id} • {state.scenario_name} • phase: {state.phase} • mode: synthetic demo engine",
            style=ACCENT_COLOR,
        )

    body = Group(
        Align.center(Text(BANNER.strip("\n"), style=f"bold {ACCENT_COLOR}")),
        Align.center(status_line),
    )
    return Panel(body, title=f"{APP_NAME} v{APP_VERSION}", border_style=BORDER_COLOR)


def build_logs_panel(state: SimulationState) -> Panel:
    if not state.logs:
        return Panel(Text("Waiting for synthetic activity...", style=INFO_COLOR), title="Live Logs", border_style=ACCENT_COLOR)

    text = Text()
    for entry in state.logs:
        text.append(f"[{entry.timestamp}] ")
        text.append(f"[{entry.level}] ", style=LEVEL_STYLES.get(entry.level, "white"))
        text.append(entry.message)
        text.append("\n")
    text.rstrip()
    return Panel(text, title=f"Live Logs • {state.scenario_name}", border_style=ACCENT_COLOR)


def build_stats_panel(state: SimulationState) -> Panel:
    elapsed = max(1, int(time.time() - state.start_time))
    avg_rate = state.total_ops / elapsed
    refresh_in = max(0, REFRESH_INTERVAL_SECONDS - int(time.time() - state.last_refresh))

    table = Table.grid(padding=(0, 1))
    table.add_column(style="bold")
    table.add_column()
    table.add_row("Scenario", state.scenario_name)
    table.add_row("Session ID", state.session_id)
    table.add_row("Phase", state.phase)
    table.add_row("Elapsed", f"{elapsed}s")
    table.add_row("Synthetic ops", f"{state.total_ops} {state.unit}")
    table.add_row("Last tick", f"{state.last_tick_ops} {state.unit}")
    table.add_row("Average rate", f"{avg_rate:.2f} {state.unit}/s")
    table.add_row("Workers active", str(state.active_workers))
    table.add_row("Queue depth", str(state.queue_depth))
    table.add_row("Latency", f"{state.latency_ms} ms")
    table.add_row("Policy hits", str(state.policy_hits))
    table.add_row("Success / Warn / Error", f"{state.success_count} / {state.warning_count} / {state.error_count}")
    table.add_row("Next 60s refresh", f"{refresh_in}s")
    table.add_row("File logging", "ON" if state.settings.file_logging_enabled else "OFF")
    table.add_row("Last checkpoint", state.last_checkpoint)
    return Panel(table, title="Session Stats", border_style=BORDER_COLOR)


def build_nodes_panel(state: SimulationState) -> Panel:
    table = Table(expand=True, show_header=True)
    table.add_column("Node", style="bold")
    table.add_column("Role")
    table.add_column("State")
    table.add_column("Load")
    table.add_column("RTT")

    for node in state.nodes:
        table.add_row(
            node.name,
            node.role,
            f"[{STATUS_STYLES.get(node.status, 'white')}]{node.status}[/]",
            f"{node.load_percent}%",
            f"{node.latency_ms} ms",
        )

    return Panel(table, title="Node Health", border_style=WARNING_COLOR)


def gauge_table(state: SimulationState) -> Table:
    table = Table.grid(expand=True, padding=(0, 1))
    table.add_column(width=12, style="bold")
    table.add_column(ratio=1)
    table.add_column(width=8, justify="right")

    table.add_row(
        "CPU",
        ProgressBar(total=100, completed=state.cpu_percent, width=22, complete_style="bright_green", finished_style="bright_green"),
        f"{state.cpu_percent}%",
    )
    table.add_row(
        "Memory",
        ProgressBar(total=100, completed=state.mem_percent, width=22, complete_style="bright_cyan", finished_style="bright_cyan"),
        f"{state.mem_percent}%",
    )
    table.add_row(
        "Network",
        ProgressBar(total=1000, completed=min(state.net_mbps, 1000), width=22, complete_style="bright_magenta", finished_style="bright_magenta"),
        f"{state.net_mbps} Mb/s",
    )
    return table


def build_activity_panel(state: SimulationState) -> Panel:
    group = Group(
        gauge_table(state),
        Text(
            f"Synthetic mode: ON\n"
            f"Refresh cadence: {REFRESH_INTERVAL_SECONDS}s\n"
            f"Log path: {LOG_PATH}\n"
            f"Checkpoint: {state.last_checkpoint}",
            style=INFO_COLOR,
        ),
    )
    return Panel(group, title="Activity Bus", border_style=INFO_COLOR)


def build_system_panel() -> Panel:
    table = Table.grid(padding=(0, 1))
    table.add_column(style="bold")
    table.add_column()
    table.add_row("Host", socket.gethostname())
    table.add_row("User", getpass.getuser())
    table.add_row("Platform", platform.platform())
    table.add_row("Python", platform.python_version())
    table.add_row("Working dir", str(BASE_DIR))
    table.add_row("Clock", now_str())
    return Panel(table, title="System Snapshot", border_style=WARNING_COLOR)


def build_footer_panel(state: Optional[SimulationState] = None) -> Panel:
    if state is None:
        content = Text(
            f"Select a number to continue • Linux-only • launch anytime with {APP_COMMAND} • synthetic demo only",
            justify="center",
            style=INFO_COLOR,
        )
    else:
        content = Text(
            f"Ctrl+C to stop • session {state.session_id} • synthetic demo only • last checkpoint: {state.last_checkpoint}",
            justify="center",
            style=INFO_COLOR,
        )
    return Panel(content, border_style=INFO_COLOR)


def render_layout(state: SimulationState) -> Layout:
    layout = Layout()
    layout.split_column(
        Layout(build_header(state), size=11),
        Layout(name="body", ratio=1),
        Layout(build_footer_panel(state), size=3),
    )
    layout["body"].split_row(
        Layout(build_logs_panel(state), ratio=2),
        Layout(name="sidebar", ratio=1),
    )
    layout["body"]["sidebar"].split_column(
        Layout(build_stats_panel(state), ratio=2),
        Layout(build_nodes_panel(state), ratio=2),
        Layout(build_activity_panel(state), ratio=2),
        Layout(build_system_panel(), ratio=1),
    )
    return layout


def choose_level() -> str:
    roll = random.random()
    if roll < 0.08:
        return "WARN"
    if roll < 0.10:
        return "ERROR"
    if roll < 0.26:
        return "INFO"
    if roll < 0.42:
        return "TRACE"
    return "LOG"


def update_nodes(state: SimulationState) -> None:
    low, high = state.latency_range
    for node in state.nodes:
        node.status = weighted_status()
        node.latency_ms = random.randint(low, high)
        node.load_percent = random.randint(18, 96)
        node.last_seen = f"{random.randint(0, 4)}s ago"


def rotate_phase(state: SimulationState) -> None:
    if state.loop_count == 1 or state.loop_count % 12 == 0:
        state.phase = random.choice(state.phases)
        state.last_checkpoint = f"{state.phase.lower().replace(' ', '-')}-{random.randint(100, 999)}"
        add_log(state, "INFO", f"checkpoint advanced to {state.last_checkpoint}")


def simulate_tick(state: SimulationState, echo: bool = False) -> None:
    scenario = SCENARIOS[state.scenario_key]
    state.loop_count += 1
    rotate_phase(state)

    ops = random.randint(MIN_OPS_PER_TICK, MAX_OPS_PER_TICK)
    state.last_tick_ops = ops
    state.total_ops += ops
    state.queue_depth = max(0, state.queue_depth + random.randint(-4, 9))
    state.active_workers = random.randint(max(2, len(state.nodes) - 2), len(state.nodes) + 3)
    state.latency_ms = random.randint(*state.latency_range)
    state.cpu_percent = random.randint(23, 94)
    state.mem_percent = random.randint(19, 89)
    state.net_mbps = random.randint(80, 960)
    state.policy_hits += random.randint(0, 3)
    update_nodes(state)

    for _ in range(random.randint(2, 4)):
        node = random.choice(state.nodes)
        action = random.choice(scenario["actions"])
        level = choose_level()
        seq = random.randint(10000, 99999)
        message = (
            f"{action} on {node.name} | role={node.role} | seq={seq} | "
            f"phase={state.phase.lower().replace(' ', '-') }"
        )
        add_log(state, level, message, echo=echo)

        if level in {"LOG", "INFO", "TRACE"}:
            state.success_count += 1
        elif level == "WARN":
            state.warning_count += 1
        elif level == "ERROR":
            state.error_count += 1

    if random.random() < 0.22:
        drift = state.latency_ms + random.randint(8, 55)
        add_log(
            state,
            "WARN",
            f"latency drift observed; retry window widened to {drift} ms | queue_depth={state.queue_depth}",
            echo=echo,
        )
        state.warning_count += 1

    if random.random() < 0.12:
        add_log(
            state,
            "INFO",
            f"checkpoint sealed | workers={state.active_workers} | policy_hits={state.policy_hits} | buffer_state=stable",
            echo=echo,
        )
        state.success_count += 1


def maybe_emit_refresh_stats(state: SimulationState, echo: bool = False) -> None:
    now = time.time()
    if now - state.last_refresh >= REFRESH_INTERVAL_SECONDS:
        elapsed = max(1, int(now - state.start_time))
        avg_rate = state.total_ops / elapsed
        add_log(
            state,
            "STATS",
            (
                f"elapsed={elapsed}s | synthetic_{state.unit}={state.total_ops} | avg_rate={avg_rate:.2f} {state.unit}/s | "
                f"workers={state.active_workers} | queue_depth={state.queue_depth} | latency={state.latency_ms} ms"
            ),
            echo=echo,
        )
        state.last_refresh = now


def final_summary(state: SimulationState) -> str:
    elapsed = max(1, int(time.time() - state.start_time))
    avg_rate = state.total_ops / elapsed
    return (
        f"session={state.session_id} | scenario={state.scenario_name} | elapsed={elapsed}s | "
        f"synthetic_{state.unit}={state.total_ops} | avg_rate={avg_rate:.2f} {state.unit}/s | "
        f"success={state.success_count} | warn={state.warning_count} | error={state.error_count}"
    )


def run_plain_mode(state: SimulationState, duration: Optional[int] = None) -> None:
    add_log(state, "INFO", f"Starting {state.scenario_name}", echo=True)
    add_log(state, "INFO", f"Session ID: {state.session_id}", echo=True)
    add_log(state, "INFO", "Synthetic demo mode enabled. Press Ctrl+C to stop.", echo=True)

    try:
        while state.running:
            simulate_tick(state, echo=True)
            maybe_emit_refresh_stats(state, echo=True)
            time.sleep(TICK_SECONDS)
            if duration is not None and int(time.time() - state.start_time) >= duration:
                state.running = False
    except KeyboardInterrupt:
        state.running = False
        # print("\n[!] Stop requested. Closing session...")

    add_log(state, "FINAL", final_summary(state), echo=True)


def run_rich_mode(state: SimulationState, duration: Optional[int] = None) -> None:
    add_log(state, "INFO", f"Starting {state.scenario_name}")
    add_log(state, "INFO", f"Session ID: {state.session_id}")
    add_log(state, "INFO", "Synthetic demo mode enabled. Press Ctrl+C to stop.")

    try:
        with Live(render_layout(state), console=CONSOLE, refresh_per_second=SCREEN_REFRESH_PER_SECOND, screen=True) as live:
            while state.running:
                simulate_tick(state)
                maybe_emit_refresh_stats(state)
                live.update(render_layout(state))
                time.sleep(TICK_SECONDS)
                if duration is not None and int(time.time() - state.start_time) >= duration:
                    state.running = False
    except KeyboardInterrupt:
        state.running = False
        CONSOLE.# print("\n[bold yellow]Stop requested. Closing session...[/bold yellow]")

    add_log(state, "FINAL", final_summary(state))
    CONSOLE.# print(render_layout(state))


def print_menu(settings: AppSettings) -> None:
    clear_screen()
    CONSOLE.# print(build_header())

    menu = Table(title="Main Menu", border_style=BORDER_COLOR, show_lines=True)
    menu.add_column("ID", style="bold")
    menu.add_column("Option")
    menu.add_column("Description")
    menu.add_row("1", str(SCENARIOS["1"]["name"]), str(SCENARIOS["1"]["description"]))
    menu.add_row("2", str(SCENARIOS["2"]["name"]), str(SCENARIOS["2"]["description"]))
    menu.add_row("3", str(SCENARIOS["3"]["name"]), str(SCENARIOS["3"]["description"]))
    menu.add_row("4", "System Snapshot", "Show current host, Python, runtime, and launcher details.")
    menu.add_row("5", "Toggle File Logging", f"Current state: {'ON' if settings.file_logging_enabled else 'OFF'}")
    menu.add_row("6", "Exit", "Close Black Bear.")
    CONSOLE.# print(menu)
    CONSOLE.# print(build_footer_panel())


def show_snapshot(settings: AppSettings) -> None:
    clear_screen()
    CONSOLE.# print(build_header())

    table = Table(title="Snapshot", border_style=BORDER_COLOR, show_lines=True)
    table.add_column("Key", style="bold")
    table.add_column("Value")
    table.add_row("Application", APP_NAME)
    table.add_row("Version", APP_VERSION)
    table.add_row("Launcher", APP_COMMAND)
    table.add_row("Host", socket.gethostname())
    table.add_row("User", getpass.getuser())
    table.add_row("Platform", platform.platform())
    table.add_row("Python", platform.python_version())
    table.add_row("Project path", str(BASE_DIR))
    table.add_row("Log path", str(LOG_PATH))
    table.add_row("File logging", "ON" if settings.file_logging_enabled else "OFF")
    table.add_row("Mode", "Synthetic demo only")
    CONSOLE.# print(table)
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # input("\nPress Enter to return to the menu...")


def create_state(choice: str, settings: AppSettings) -> SimulationState:
    scenario = SCENARIOS[choice]
    nodes = [NodeState(name=name, role=role) for name, role in scenario["nodes"]]
    return SimulationState(
        scenario_key=choice,
        scenario_name=str(scenario["name"]),
        scenario_description=str(scenario["description"]),
        unit=str(scenario["unit"]),
        phases=list(scenario["phases"]),
        latency_range=tuple(scenario["latency_range"]),
        settings=settings,
        nodes=nodes,
    )


def interactive_loop(args: argparse.Namespace) -> int:
    settings = AppSettings(file_logging_enabled=args.log_to_file or DEFAULT_LOG_TO_FILE)

    while True:
        print_menu(settings)
        choice = # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # input("Select option: ").strip()

        if choice in SCENARIOS:
            state = create_state(choice, settings)
            if args.plain or not CONSOLE.is_terminal:
                run_plain_mode(state, duration=args.duration)
            else:
                run_rich_mode(state, duration=args.duration)
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # input("\nPress Enter to return to the menu...")
        elif choice == "4":
            show_snapshot(settings)
        elif choice == "5":
            settings.file_logging_enabled = not settings.file_logging_enabled
            status = "enabled" if settings.file_logging_enabled else "disabled"
            # # print(f...",),\nFile logging {status}. Log path: {LOG_PATH}")
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # input("Press Enter to return to the menu...")
        elif choice == "6":
            # print("Goodbye.")
            return 0
        else:
            # print("Invalid option. Try again.")
            time.sleep(1)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=f"{APP_NAME} Linux-only synthetic operations dashboard")
    parser.add_argument("--plain", action="store_true", help="Use plain text mode instead of the Rich dashboard.")
    parser.add_argument("--scenario", choices=sorted(SCENARIOS.keys()), help="Launch directly into a scenario.")
    parser.add_argument("--duration", type=int, default=None, help="Auto-stop after N seconds.")
    parser.add_argument("--log-to-file", action="store_true", help=f"Enable file logging to {LOG_PATH}.")
    parser.add_argument("--version", action="store_true", help="Print version and exit.")
    return parser


def main() -> int:
    ensure_linux()
    parser = build_arg_parser()
    args = parser.parse_args()

    if args.version:
        # # print(f...",),{APP_NAME} {APP_VERSION}")
        return 0

    if args.scenario:
        settings = AppSettings(file_logging_enabled=args.log_to_file or DEFAULT_LOG_TO_FILE)
        state = create_state(args.scenario, settings)
        if args.plain or not CONSOLE.is_terminal:
            run_plain_mode(state, duration=args.duration)
        else:
            run_rich_mode(state, duration=args.duration)
        return 0

    return interactive_loop(args)


if __name__ == "__main__":
    raise SystemExit(main())
