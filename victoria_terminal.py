#!/usr/bin/env python3
"""Entry point for launching the Victoria terminal experience with Crush."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Mapping, MutableMapping, Sequence

from colorama import init as colorama_init
from dotenv import dotenv_values, load_dotenv, set_key
from rich.console import Console, Group
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.live import Live
import colorama
from colorama import Fore, Style

# Initialize colorama and rich console
colorama.init(autoreset=True)
console = Console()

__version__ = "2025.9.9"
VICTORIA_FILE = "VICTORIA.md"
CONFIGS_DIR = "configs"
CRUSH_TEMPLATE = Path(CONFIGS_DIR) / "crush" / "crush.template.json"
CRUSH_CONFIG_NAME = "crush.json"
ENV_FILENAME = ".env"
CRUSH_COMMAND = "crush"
SUPPORT_FILES: tuple[Path, ...] = (
    Path(CONFIGS_DIR) / "crush" / "CRUSH.md",
    Path(VICTORIA_FILE),
)
DEFAULT_APP_HOME = Path.home() / "Victoria"
APP_HOME = Path(os.environ.get("VICTORIA_HOME", DEFAULT_APP_HOME))
APP_HOME.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("VICTORIA_HOME", str(APP_HOME))

# Icons
if os.name == "nt":
    ICONS = {
        "info": "[*]",
        "good": "[v]",
        "warn": "[!]",
        "bad": "[x]",
        "rocket": "->",
        "wave": "~",
        "anchor": "#",
        "folder": "[]",
    }
else:
    ICONS = {
        "info": "ℹ️",
        "good": "✅",
        "warn": "⚠️",
        "bad": "❌",
        "rocket": "🚀",
        "wave": "🌊",
        "anchor": "⚓",
        "folder": "📁",
    }

def info(message: str) -> None:  # pragma: no cover - simple wrapper
    console.print(f"[cyan]{ICONS['info']} {message}")

def good(message: str) -> None:  # pragma: no cover - simple wrapper
    console.print(f"[green]{ICONS['good']} {message}")

def warn(message: str) -> None:  # pragma: no cover - simple wrapper
    console.print(f"[yellow]{ICONS['warn']} {message}")

def err(message: str) -> None:  # pragma: no cover - simple wrapper
    console.print(f"[red]{ICONS['bad']} {message}")

def handle_error(exc: Exception) -> None:
    """Print an error message and exit."""
    err(f"An unexpected error occurred: {exc}")
    sys.exit(1)

def section(title: str) -> None:  # pragma: no cover - simple wrapper
    console.rule(f"[bold yellow]{title}")

# Optional capability flags
try:
    # Check if Rich is available
    import rich
    HAS_RICH = True
except Exception:
    HAS_RICH = False

TERMINAL_PROMPT = ">_"

COMPACT_SHIP_ASCII_BASE = [
"              |    |    |                ",
"             )_)  )_)  )_)               ",
"            )___))___))___)\\             ",
"           )____)____)_____)\\\\           ",
"         _____|____|____|____\\\\\\__       ",
"---------\\                   /---------  ",
"  ^^^^^ ^^^^^^^^^^^^^^^^^^^^^           ",
"    ^^^^      ^^^^     ^^^    ^^        ",
"         ^^^^      ^^^               ",
]

VICTORIA_TEXT = """
██╗   ██╗██╗ ██████╗████████╗ ██████╗ ██████╗ ██╗ █████╗ 
██║   ██║██║██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗██║██╔══██╗
██║   ██║██║██║        ██║   ██║   ██║██████╔╝██║███████║
╚██╗ ██╔╝██║██║        ██║   ██║   ██║██╔══██╗██║██╔══██║
 ╚████╔╝ ██║╚██████╗   ██║   ╚██████╔╝██║  ██║██║██║  ██║
  ╚═══╝  ╚═╝ ╚═════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝
"""

TIPS_BULLETS = [
    "• Put data files in the Victoria folder",
    "• Ask any question you like (e.g., \"Hey Victoria, Analyze the top-performing sites for this campaign\")",
    "• Report bugs to the support channel or the GitHub repo",
]

TIPS_CHECKED = [
    "✅ Put data files in the Victoria folder",
    "✅ Ask any question you like (e.g., \"Hey Victoria, Analyze the top-performing sites for this campaign\")",
    "✅ Report bugs to the support channel or the GitHub repo",
]


LICENSE_ACCEPTANCE_KEY = "VICTORIA_LICENSE_ACCEPTED"
_LICENSE_ACCEPTED_VALUES = {"yes", "true", "1", "accepted"}
LICENSE_NOTICE_TITLE = "Victoria Terminal License Agreement"
LICENSE_FILE_NAME = "LICENSE"
LICENSE_NOTICE_REMINDER = (
    "You must accept these terms to continue. Type 'accept' to agree or 'decline' to exit."
)
LICENSE_ACCEPT_PROMPT = "Type 'accept' to agree or 'decline' to exit: "


# ──────────────────────────────────────────────────────────────────────────────
# License acceptance helpers                                                    |
# ──────────────────────────────────────────────────────────────────────────────

def _resolve_app_home(app_home: Path | None = None) -> Path:
    if app_home is not None:
        return app_home
    env_home = os.environ.get("VICTORIA_HOME")
    if env_home:
        return Path(env_home).expanduser()
    return APP_HOME


_LICENSE_TEXT_CACHE: str | None = None


def _get_license_text() -> str:
    global _LICENSE_TEXT_CACHE
    if _LICENSE_TEXT_CACHE is not None:
        return _LICENSE_TEXT_CACHE

    script_dir = Path(__file__).resolve().parent
    candidates = (
        script_dir / LICENSE_FILE_NAME,
        Path.cwd() / LICENSE_FILE_NAME,
        _resolve_app_home() / LICENSE_FILE_NAME,
    )
    for candidate in candidates:
        if candidate.is_file():
            _LICENSE_TEXT_CACHE = candidate.read_text(encoding="utf-8")
            return _LICENSE_TEXT_CACHE

    candidate_list = ", ".join(str(path) for path in candidates)
    raise FileNotFoundError(
        "Victoria Terminal requires the LICENSE file to display the agreement. "
        f"Expected to find it in one of: {candidate_list}"
    )


def _is_license_accepted(*, app_home: Path | None = None) -> bool:
    value = os.environ.get(LICENSE_ACCEPTANCE_KEY, "").strip().lower()
    if value in _LICENSE_ACCEPTED_VALUES:
        return True
    resolved_home = _resolve_app_home(app_home)
    env_path = resolved_home / ENV_FILENAME
    if not env_path.exists():
        return False
    stored_value = parse_env_file(env_path).get(LICENSE_ACCEPTANCE_KEY, "")
    if stored_value:
        os.environ.setdefault(LICENSE_ACCEPTANCE_KEY, stored_value)
    return stored_value.strip().lower() in _LICENSE_ACCEPTED_VALUES


def _persist_license_acceptance(*, app_home: Path | None = None) -> None:
    resolved_home = _resolve_app_home(app_home)
    env_path = resolved_home / ENV_FILENAME
    env_path.parent.mkdir(parents=True, exist_ok=True)
    if not env_path.exists():
        env_path.touch()
    set_key(str(env_path), LICENSE_ACCEPTANCE_KEY, "yes")
    os.environ[LICENSE_ACCEPTANCE_KEY] = "yes"


def _display_license_notice_rich() -> None:
    console.clear()
    title = Text(LICENSE_NOTICE_TITLE, style="bold bright_white")
    reminder = Text(LICENSE_NOTICE_REMINDER, style="bright_yellow")
    license_text = Text(_get_license_text().rstrip(), style="bright_white")
    content = Group(
        Align.center(title),
        Text("\n"),
        license_text,
        Text("\n"),
        Align.left(reminder),
    )
    panel = Panel(content, border_style="bright_cyan", padding=(1, 2))
    console.print(panel)


def _display_license_notice_colorama() -> None:
    _clear_basic()
    license_text = _get_license_text().rstrip()
    try:
        print(f"{Fore.WHITE}{Style.BRIGHT}{LICENSE_NOTICE_TITLE.center(80)}{Style.RESET_ALL}\n")
        for line in license_text.splitlines():
            print(f"{Fore.WHITE}{line}{Style.RESET_ALL}")
        print()
        print(f"{Fore.YELLOW}{LICENSE_NOTICE_REMINDER}{Style.RESET_ALL}")
        print()
    except Exception:
        print(LICENSE_NOTICE_TITLE.center(80))
        print()
        print(license_text)
        print()
        print(LICENSE_NOTICE_REMINDER)
        print()


def _display_license_notice_basic() -> None:
    _clear_basic()
    print(LICENSE_NOTICE_TITLE.center(80))
    print()
    print(_get_license_text())
    print()
    print(LICENSE_NOTICE_REMINDER)
    print()


def _prompt_license_response(mode: str) -> str:
    try:
        if mode == "rich":
            return console.input(f"[cyan]{LICENSE_ACCEPT_PROMPT}[/cyan]").strip()
        if mode == "colorama":
            try:
                return input(f"{Fore.CYAN}{LICENSE_ACCEPT_PROMPT}{Style.RESET_ALL}").strip()
            except Exception:
                return input(LICENSE_ACCEPT_PROMPT).strip()
        return input(LICENSE_ACCEPT_PROMPT).strip()
    except (KeyboardInterrupt, EOFError):
        _handle_license_decline(mode, cancelled=True)
        return ""


def _notify_invalid_response(mode: str) -> None:
    message = "Please respond with 'accept' or 'decline'."
    if mode == "rich":
        console.print(f"[yellow]{message}[/yellow]")
    else:
        try:
            print(f"{Fore.YELLOW}{message}{Style.RESET_ALL}")
        except Exception:
            print(message)


def _acknowledge_license_acceptance(mode: str) -> None:
    message = "License accepted. Continuing startup..."
    if mode == "rich":
        console.print(f"[green]{message}[/green]")
    else:
        try:
            print(f"{Fore.GREEN}{message}{Style.RESET_ALL}")
        except Exception:
            print(message)
    time.sleep(1.0)


def _handle_license_decline(mode: str, *, cancelled: bool = False) -> None:
    if cancelled:
        message = "Victoria launch cancelled before accepting the license."
    else:
        message = "Victoria Terminal requires license acceptance to continue. Exiting."
    if mode == "rich":
        console.print(f"[red]{message}[/red]")
    else:
        try:
            print(f"{Fore.RED}{message}{Style.RESET_ALL}")
        except Exception:
            print(message)
    sys.exit(0)


def _ensure_license_acceptance(mode: str, *, app_home: Path | None = None) -> None:
    resolved_home = _resolve_app_home(app_home)
    if _is_license_accepted(app_home=resolved_home):
        return
    display_map = {
        "rich": _display_license_notice_rich,
        "colorama": _display_license_notice_colorama,
        "basic": _display_license_notice_basic,
    }
    display = display_map.get(mode, _display_license_notice_basic)
    display()
    accept_responses = {"accept", "a", "yes", "y"}
    decline_responses = {"decline", "d", "no", "n"}
    while True:
        response = _prompt_license_response(mode).lower()
        if response in accept_responses:
            _persist_license_acceptance(app_home=resolved_home)
            _acknowledge_license_acceptance(mode)
            break
        if response in decline_responses:
            _handle_license_decline(mode)
        _notify_invalid_response(mode)


# ──────────────────────────────────────────────────────────────────────────────
# Intro Sequence (two screens + enter between each)                             |
# ──────────────────────────────────────────────────────────────────────────────

def banner_sequence() -> None:
    """
    Show the intro sequence:
      1) Ship + Victoria art + short wave animation → press Enter
      2) 'Victoria Terminal' + Tips animate to checkmarks → press Enter
      3) Show short spinner → proceed to launch
    """
    app_home = _resolve_app_home()
    use_rich = HAS_RICH and hasattr(console, "is_terminal") and console.is_terminal and sys.stdout.isatty()

    if use_rich:
        _display_rich_welcome()
        _animate_waves_rich(duration=1.8)
        _wait_for_enter_rich("Press Enter to continue...")
        _display_rich_tips(initial_bullets=True)
        _animate_tips_rich()
        _wait_for_enter_rich("Press Enter to continue...")
        _ensure_license_acceptance("rich", app_home=app_home)
        _spinner_rich("Launching CRUSH…", duration=1.8)
        console.clear()
        return

    if 'Fore' in globals() and 'Style' in globals():
        _display_colorama_welcome()
        _animate_waves_colorama(duration=1.2)
        _wait_for_enter_basic("Press Enter to continue...")
        _display_colorama_tips(initial_bullets=True)
        _animate_tips_colorama()
        _wait_for_enter_basic("Press Enter to continue...")
        _ensure_license_acceptance("colorama", app_home=app_home)
        _spinner_colorama("Launching CRUSH…", duration=1.5)
        _clear_basic()
        return

    _display_basic_welcome()
    time.sleep(1.0)
    _wait_for_enter_basic("Press Enter to continue...")
    _display_basic_tips(initial_bullets=True)
    time.sleep(0.8)
    _display_basic_tips(initial_bullets=False)  # swap to checkmarks
    _wait_for_enter_basic("Press Enter to continue...")
    _ensure_license_acceptance("basic", app_home=app_home)
    time.sleep(0.8)  # minimal spinner stand-in
    _clear_basic()


# ── Rich implementations ─────────────────────────────────────────────────────

def _ship_renderable(wave_offset: int = 0) -> Text:
    # Build ship art with shifting waves
    lines = COMPACT_SHIP_ASCII_BASE.copy()
    # shift last three lines (waves)
    for idx in (-3, -2, -1):
        if abs(idx) <= len(lines):
            padding = " " * (wave_offset % 6)
            line = lines[idx].strip()
            lines[idx] = f"{padding}{line}"
    return Text("\n".join(lines), style="bright_cyan")

def _display_rich_welcome() -> None:
    console.clear()

    prompt_text = Text(TERMINAL_PROMPT, style="bold bright_green")

    victoria_lines = VICTORIA_TEXT.strip().split("\n")
    victoria_text = Text()
    for i, line in enumerate(victoria_lines):
        color = "bright_magenta" if i % 2 == 0 else "magenta"
        victoria_text.append(line + "\n", style=f"bold {color}")

    subtitle = Text("AdTech Data Navigation Terminal", style="italic bright_white")

    content = Group(
        Align.left(prompt_text),
        Text("\n"),
        _ship_renderable(0),
        Text("\n"),
        victoria_text,
        Text("\n"),
        Align.center(subtitle),
    )

    panel = Panel(
        Align.center(content),
        border_style="bright_cyan",
        padding=(1, 2),
        title="[bold bright_white]⚓ Victoria ⚓[/bold bright_white]",
        title_align="center",
        subtitle="[dim]Welcome[/dim]",
        subtitle_align="center",
    )
    console.print(panel)
    console.print()

def _animate_waves_rich(duration: float = 1.8) -> None:
    """Short wave animation before the first Enter prompt."""
    start = time.time()
    offset = 0
    with Live(refresh_per_second=16, console=console, screen=False):
        while time.time() - start < duration:
            offset = (offset + 1) % 6
            # Re-render the whole welcome panel with updated ship
            victoria_lines = VICTORIA_TEXT.strip().split("\n")
            victoria_text = Text()
            for i, line in enumerate(victoria_lines):
                color = "bright_magenta" if i % 2 == 0 else "magenta"
                victoria_text.append(line + "\n", style=f"bold {color}")
            prompt_text = Text(TERMINAL_PROMPT, style="bold bright_green")
            subtitle = Text("AdTech Data Navigation Terminal", style="italic bright_white")

            content = Group(
                Align.left(prompt_text),
                Text("\n"),
                _ship_renderable(offset),
                Text("\n"),
                victoria_text,
                Text("\n"),
                Align.center(subtitle),
            )

            panel = Panel(
                Align.center(content),
                border_style="bright_cyan",
                padding=(1, 2),
                title="[bold bright_white]⚓ Victoria ⚓[/bold bright_white]",
                title_align="center",
                subtitle="[dim]Welcome[/dim]",
                subtitle_align="center",
            )
            console.clear()
            console.print(panel)
            time.sleep(0.06)

def _display_rich_tips(*, initial_bullets: bool = True) -> None:
    console.clear()
    title = Text("Victoria Terminal", style="bold bright_white")
    items = TIPS_BULLETS if initial_bullets else TIPS_CHECKED
    tips_text = Text()
    for tip in items:
        tips_text.append(tip + "\n", style="bright_white")

    content = Group(
        Align.center(title),
        Text("\n"),
        Align.center(Text("TIPS", style="dim cyan")),
        Text("\n"),
        Align.center(tips_text),
    )

    panel = Panel(
        Align.center(content),
        border_style="bright_cyan",
        padding=(1, 2),
        title="[bold bright_white]⚓ Victoria Terminal ⚓[/bold bright_white]",
        title_align="center",
        subtitle="[dim]TIPS[/dim]",
        subtitle_align="center",
    )
    console.print(panel)
    console.print()

def _animate_tips_rich() -> None:
    """Animate bullets → checkmarks, one by one."""
    # Build incremental frames
    frames = []
    for i in range(1, len(TIPS_BULLETS) + 1):
        current = TIPS_CHECKED[:i] + TIPS_BULLETS[i:]
        frames.append(current)

    with Live(refresh_per_second=12, console=console, screen=False):
        for frame in frames:
            title = Text("Victoria Terminal", style="bold bright_white")
            tips_text = Text()
            for tip in frame:
                tips_text.append(tip + "\n", style="bright_white")
            content = Group(
                Align.center(title),
                Text("\n"),
                Align.center(Text("TIPS", style="dim cyan")),
                Text("\n"),
                Align.center(tips_text),
            )
            panel = Panel(
                Align.center(content),
                border_style="bright_cyan",
                padding=(1, 2),
                title="[bold bright_white]⚓ Victoria Terminal ⚓[/bold bright_white]",
                title_align="center",
                subtitle="[dim]TIPS[/dim]",
                subtitle_align="center",
            )
            console.clear()
            console.print(panel)
            time.sleep(0.35)

def _spinner_rich(message: str, duration: float = 1.8) -> None:
    spinner_frames = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
    start = time.time()
    idx = 0
    with Live(refresh_per_second=16, console=console, screen=False):
        while time.time() - start < duration:
            line = Text(f"{spinner_frames[idx % len(spinner_frames)]} {message}", style="cyan")
            panel = Panel(Align.center(line), border_style="bright_cyan", padding=(1,2))
            console.clear()
            console.print(panel)
            idx += 1
            time.sleep(0.07)

def _wait_for_enter_rich(prompt: str) -> None:
    try:
        console.print(f"[cyan]{prompt}[/cyan]")
        input()
        console.clear()
    except (KeyboardInterrupt, EOFError):
        console.print("\n[yellow]Startup cancelled[/yellow]")
        sys.exit(0)

# ── Colorama implementations ──────────────────────────────────────────────────

def _display_colorama_welcome() -> None:
    _clear_basic()
    print(f"{Fore.GREEN}{Style.BRIGHT}{TERMINAL_PROMPT}\n")
    print(f"{Fore.CYAN}{Style.BRIGHT}" + "\n".join(COMPACT_SHIP_ASCII_BASE))
    print(f"{Fore.MAGENTA}{Style.BRIGHT}{VICTORIA_TEXT}")
    print(f"{Fore.WHITE}{Style.NORMAL}{'AdTech Data Navigation Terminal'.center(80)}\n{Style.RESET_ALL}")

def _animate_waves_colorama(duration: float = 1.2) -> None:
    start = time.time()
    offset = 0
    while time.time() - start < duration:
        _clear_basic()
        print(f"{Fore.GREEN}{Style.BRIGHT}{TERMINAL_PROMPT}\n")
        lines = COMPACT_SHIP_ASCII_BASE.copy()
        for idx in (-3, -2, -1):
            if abs(idx) <= len(lines):
                padding = " " * (offset % 6)
                lines[idx] = f"{padding}{lines[idx].strip()}"
        print(f"{Fore.CYAN}{Style.BRIGHT}" + "\n".join(lines))
        print(f"{Fore.MAGENTA}{Style.BRIGHT}{VICTORIA_TEXT}")
        print(f"{Fore.WHITE}{Style.NORMAL}{'AdTech Data Navigation Terminal'.center(80)}\n{Style.RESET_ALL}")
        offset += 1
        time.sleep(0.08)

def _display_colorama_tips(*, initial_bullets: bool = True) -> None:
    _clear_basic()
    print(f"{Fore.WHITE}{Style.BRIGHT}{'Victoria Terminal'.center(80)}{Style.RESET_ALL}\n")
    print(f"{Fore.CYAN}{Style.DIM}{'TIPS'.center(80)}{Style.RESET_ALL}\n")
    items = TIPS_BULLETS if initial_bullets else TIPS_CHECKED
    for tip in items:
        print(f"{Fore.WHITE}{tip}{Style.RESET_ALL}")
    print()

def _animate_tips_colorama() -> None:
    for i in range(1, len(TIPS_BULLETS) + 1):
        # redraw with partial checkmarks
        _clear_basic()
        print(f"{Fore.WHITE}{Style.BRIGHT}{'Victoria Terminal'.center(80)}{Style.RESET_ALL}\n")
        print(f"{Fore.CYAN}{Style.DIM}{'TIPS'.center(80)}{Style.RESET_ALL}\n")
        for idx, tip in enumerate(TIPS_BULLETS):
            if idx < i:
                print(f"{Fore.WHITE}{TIPS_CHECKED[idx]}{Style.RESET_ALL}")
            else:
                print(f"{Fore.WHITE}{tip}{Style.RESET_ALL}")
        print()
        time.sleep(0.25)

def _spinner_colorama(message: str, duration: float = 1.5) -> None:
    frames = "|/-\\"
    start = time.time()
    i = 0
    while time.time() - start < duration:
        print(f"\r{Fore.CYAN}{frames[i % len(frames)]} {message}{Style.RESET_ALL}", end="", flush=True)
        time.sleep(0.08)
        i += 1
    print()

# ── Basic implementations ─────────────────────────────────────────────────────

def _display_basic_welcome() -> None:
    _clear_basic()
    print(TERMINAL_PROMPT)
    print()
    print("\n".join(COMPACT_SHIP_ASCII_BASE))
    print(VICTORIA_TEXT)
    print("AdTech Data Navigation Terminal".center(80))
    print()

def _display_basic_tips(*, initial_bullets: bool = True) -> None:
    _clear_basic()
    print("Victoria Terminal".center(80))
    print("TIPS".center(80))
    print()
    items = TIPS_BULLETS if initial_bullets else TIPS_CHECKED
    for tip in items:
        print(tip)
    print()

def _wait_for_enter_basic(prompt: str) -> None:
    try:
        print(f"{Fore.CYAN}{prompt}{Style.RESET_ALL}")
    except Exception:
        print(prompt)
    try:
        input()
    except (KeyboardInterrupt, EOFError):
        print("\nStartup cancelled")
        sys.exit(0)

def _clear_basic() -> None:
    # Clear for most terminals
    print("\033[2J\033[H", end="")

# ──────────────────────────────────────────────────────────────────────────────
# Setup / CRUSH helpers                                                         |
# ──────────────────────────────────────────────────────────────────────────────

def initialize_colorama() -> None:
    """Initialise colorama when not running under pytest."""
    if "PYTEST_CURRENT_TEST" not in os.environ:
        colorama_init()

_DEF_ENV_PATTERN = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")

def resource_path(name: str | Path) -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base / name

def parse_env_file(path: Path) -> dict[str, str]:
    """Parse a ``.env`` style file into a dictionary."""
    if not path.exists():
        return {}
    values = dotenv_values(path)
    return {key: str(value) for key, value in values.items() if value is not None}

def load_environment(
    app_home: Path = APP_HOME,
    env: MutableMapping[str, str] | None = None,
) -> dict[str, str]:
    """Load environment variables from ``.env`` without overriding existing values."""
    env_path = app_home / ENV_FILENAME
    if not env_path.exists():
        return {}
    values = parse_env_file(env_path)
    if env is None:
        load_dotenv(env_path, override=False)
    target_env: MutableMapping[str, str] = env if env is not None else os.environ
    for key, value in values.items():
        target_env.setdefault(key, value)
    info(f"Loaded environment variables from {env_path}")
    return values

def _prompt_value(prompt: str, *, secret: bool = False) -> str | None:
    """Prompt the user for a value, returning ``None`` when skipped."""
    try:
        response = console.input(prompt, password=secret)
    except EOFError:
        warn("Input stream closed; continuing without updating the value.")
        return None
    value = response.strip()
    return value or None

def _mask_secret(value: str) -> str:
    """Return a partially masked version of ``value`` for display purposes."""
    if not value:
        return ""
    if len(value) <= 4:
        return "•" * len(value)
    visible = min(4, len(value) - 2)
    prefix = value[: visible // 2]
    suffix = value[-(visible - len(prefix)) :]
    masked_length = max(len(value) - len(prefix) - len(suffix), 0)
    return f"{prefix}{'•' * masked_length}{suffix}"

def run_setup_wizard(
    *,
    app_home: Path = APP_HOME,
    env: MutableMapping[str, str] | None = None,
    force: bool = False,
) -> bool:
    """Guide the user through configuring credentials in ``.env``."""
    env_map = env if env is not None else os.environ
    env_path = app_home / ENV_FILENAME
    env_path.parent.mkdir(parents=True, exist_ok=True)

    existing_values = parse_env_file(env_path)
    for key, value in existing_values.items():
        env_map.setdefault(key, value)

    needs_openrouter = not env_map.get("OPENROUTER_API_KEY")
    if not (force or needs_openrouter):
        return False

    section("Victoria setup wizard")
    info(
        "Victoria stores configuration in your shared workspace so future runs can reuse it."
    )
    info(
        "On your host computer this folder is typically [bold]~/Victoria[/bold]. "
        f"Inside the container it is mounted at: [bold]{app_home}[/bold]"
    )
    info(f"Secrets will be written to [bold]{env_path}[/bold].")

    updated = False

    def store_value(key: str, value: str) -> None:
        nonlocal updated
        env_map[key] = value
        env_path.touch(exist_ok=True)
        set_key(str(env_path), key, value)
        good(f"Stored {key} in {env_path}")
        updated = True

    openrouter_key = env_map.get("OPENROUTER_API_KEY")
    if force or not openrouter_key:
        warn(
            "Provide your OpenRouter API key to enable remote models. "
            "Press Enter to keep the existing key or skip for now."
        )
        if openrouter_key:
            masked = _mask_secret(openrouter_key)
            prompt_text = (
                f"OpenRouter API key [{masked}] (press Enter to keep current): "
            )
        else:
            prompt_text = "OpenRouter API key (press Enter to skip): "
        value = _prompt_value(prompt_text)
        if value:
            store_value("OPENROUTER_API_KEY", value)
        elif openrouter_key:
            info("Keeping existing OpenRouter API key.")
        else:
            warn("Continuing without an OpenRouter API key. Remote models remain unavailable.")

    if updated:
        good(f"Setup complete. Updated values saved to {env_path}.")
    else:
        info("No changes were made to existing credentials.")

    if not env_map.get("OPENROUTER_API_KEY"):
        warn(
            "Remote model access is disabled until an OpenRouter API key is configured."
        )

    return updated

def prompt_for_missing_credentials(
    *,
    app_home: Path = APP_HOME,
    env: MutableMapping[str, str] | None = None,
) -> bool:
    """Backward compatible wrapper for :func:`run_setup_wizard`."""
    return run_setup_wizard(app_home=app_home, env=env)

def ensure_app_home(app_home: Path = APP_HOME) -> Path:
    """Ensure the Victoria home directory exists with bundled documentation."""
    app_home.mkdir(parents=True, exist_ok=True)
    for relative in SUPPORT_FILES:
        src = resource_path(relative)
        dest = app_home / relative.name
        if src.exists() and not dest.exists():
            shutil.copy2(src, dest)
    return app_home

def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)

def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

def substitute_env(obj: Any, env: Mapping[str, str] | None = None) -> Any:
    """Replace ``${VAR}`` tokens with values from ``env``."""
    env_map = env or os.environ
    if isinstance(obj, dict):
        return {key: substitute_env(value, env_map) for key, value in obj.items()}
    if isinstance(obj, list):
        return [substitute_env(value, env_map) for value in obj]
    if isinstance(obj, str):
        def repl(match: re.Match[str]) -> str:
            var = match.group(1)
            value = env_map.get(var)
            return value if value is not None else match.group(0)
        return _DEF_ENV_PATTERN.sub(repl, obj)
    return obj

def generate_crush_config(
    *,
    app_home: Path = APP_HOME,
    template_path: Path | None = None,
    env: Mapping[str, str] | None = None,
) -> Path:
    """Build the Crush configuration from the bundled template."""
    template = template_path or resource_path(CRUSH_TEMPLATE)
    if not template.exists():
        raise FileNotFoundError(f"Missing Crush template at {template}")
    config = _read_json(template)
    resolved = substitute_env(config, env)
    output_path = app_home / CRUSH_CONFIG_NAME
    _write_json(output_path, resolved)
    good(f"Configuration written to {output_path}")
    return output_path

def remove_local_duckdb(app_home: Path = APP_HOME) -> None:
    """Remove the cached DuckDB file so each run starts fresh."""
    db_path = app_home / "adtech.duckdb"
    try:
        if db_path.exists():
            db_path.unlink()
            info(f"Removed local database: {db_path}")
    except Exception as exc:  # pragma: no cover - best effort cleanup
        warn(f"Could not remove {db_path}: {exc}")

def preflight_crush() -> None:
    """Validate that Crush can be launched."""
    section("System preflight check")
    info(f"Checking for {CRUSH_COMMAND} CLI")
    if shutil.which(CRUSH_COMMAND) is None:
        err(
            f"Missing '{CRUSH_COMMAND}' command-line tool. "
            "Rebuild the Victoria container or install the CLI in your environment."
        )
        sys.exit(1)
    good(f"{CRUSH_COMMAND} CLI tool detected")
    if os.environ.get("OPENROUTER_API_KEY"):
        good("OpenRouter API key configured")
    else:
        warn(
            "OPENROUTER_API_KEY not configured. Remote models will be unavailable until it is set."
        )
    good("All systems ready")

def launch_crush(*, app_home: Path = APP_HOME) -> None:
    """Launch Crush with the generated configuration."""
    section("Mission launch")
    info("Launching Crush...")
    cmd = [CRUSH_COMMAND, "-c", str(app_home), "--yolo"]
    try:
        if os.name == "nt":
            proc = subprocess.run(cmd, check=False)
            if proc.returncode != 0:
                err(f"Crush exited with {proc.returncode}")
                sys.exit(proc.returncode)
        else:
            os.execvp(CRUSH_COMMAND, cmd)
    except FileNotFoundError:
        err(
            f"'{CRUSH_COMMAND}' command not found in PATH. "
            "Rebuild the Victoria container or install the CLI in your environment."
        )
        sys.exit(1)
    except Exception as exc:  # pragma: no cover - runtime errors
        err(f"Failed to launch Crush: {exc}")
        sys.exit(1)

def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments for the entry point."""
    parser = argparse.ArgumentParser(
        description=("Victoria container entry point. Ensures configuration exists and launches Crush.")
    )
    parser.add_argument(
        "--app-home",
        type=Path,
        default=APP_HOME,
        help=("Directory to use for Victoria configuration (defaults to ~/Victoria or $VICTORIA_HOME)."),
    )
    parser.add_argument(
        "--reconfigure",
        action="store_true",
        help="Run the setup wizard even if credentials already exist.",
    )
    parser.add_argument(
        "--skip-launch",
        action="store_true",
        help="Prepare configuration without launching Crush.",
    )
    parser.add_argument(
        "--no-banner",
        action="store_true",
        help="Skip the animated launch banner (useful for non-interactive runs).",
    )
    parser.add_argument(
        "--acccept-license",
        action="store_true",
        help=(
            "Automatically accept the Victoria Terminal license "
            "(required when using --no-banner)."
        ),
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser.parse_args(argv)

def main(argv: Sequence[str] | None = None) -> None:
    """Entry point for launching the Victoria terminal."""
    initialize_colorama()
    args = parse_args(argv)

    app_home = args.app_home.expanduser()
    os.environ["VICTORIA_HOME"] = str(app_home)

    if args.no_banner and not args.acccept_license:
        err(
            "Using --no-banner requires --acccept-license to confirm acceptance "
            "of the Victoria Terminal license."
        )
        sys.exit(2)

    # Intro: two screens with Enter between each, spinner before launch
    if not args.no_banner:
        banner_sequence()

    ensure_app_home(app_home)
    if args.no_banner and args.acccept_license:
        _persist_license_acceptance(app_home=app_home)
    load_environment(app_home)
    run_setup_wizard(app_home=app_home, force=args.reconfigure)
    generate_crush_config(app_home=app_home)
    remove_local_duckdb(app_home=app_home)
    info(
        "Place files to analyze in the Victoria folder on your host (~/Victoria by default). "
        f"Inside the container that directory is available at: {app_home}"
    )
    preflight_crush()
    if args.skip_launch:
        return
    launch_crush(app_home=app_home)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:  # pragma: no cover - user interaction
        console.print("\n[yellow]Victoria launch cancelled.")
        sys.exit(130)
    except Exception as exc:  # pragma: no cover - top-level safety
        handle_error(exc)
