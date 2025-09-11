"""Shared utilities for Victoria tools."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from colorama import init as colorama_init
from rich.console import Console
from rich.panel import Panel

# ---------------------------------------------------------------------------
# Basic setup
# ---------------------------------------------------------------------------

__version__ = "2025.9.8"
VICTORIA_FILE = "VICTORIA.md"
CONFIGS_DIR = "configs"

home_dir = os.path.expanduser("~")
APP_HOME = Path(home_dir) / "Victoria"
APP_HOME.mkdir(exist_ok=True)
os.environ.setdefault("VICTORIA_HOME", str(APP_HOME))
SETUP_SENTINEL = APP_HOME / ".first_run_complete"


def load_dotenv(
    _APP_HOME: Path = APP_HOME,
    _os_environ: dict = os.environ,
) -> None:
    """Load environment variables from the .env file in the app home."""
    env_file = _APP_HOME / ".env"
    if not env_file.exists():
        return
    try:
        with env_file.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip("\"'")
                if key:
                    _os_environ.setdefault(key, value)
    except Exception:
        # Silently ignore errors in .env file parsing
        pass


load_dotenv()


colorama_init()  # Enable ANSI colors on Windows
console = Console()

# ---------------------------------------------------------------------------
# Messaging
# ---------------------------------------------------------------------------

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


def info(msg: str) -> None:  # pragma: no cover - simple wrapper
    console.print(f"[cyan]{ICONS['info']} {msg}")


def good(msg: str) -> None:  # pragma: no cover - simple wrapper
    console.print(f"[green]{ICONS['good']} {msg}")


def warn(msg: str) -> None:  # pragma: no cover - simple wrapper
    console.print(f"[yellow]{ICONS['warn']} {msg}")


def err(msg: str) -> None:  # pragma: no cover - simple wrapper
    console.print(f"[red]{ICONS['bad']} {msg}")


def handle_error(exc: Exception) -> None:
    """Prints an error message and waits for user input to exit."""
    err(f"An unexpected error occurred: {exc}")
    console.input("[red]Press Enter to exit...")
    sys.exit(1)


def section(title: str) -> None:
    console.rule(f"[bold yellow]{title}")


def banner() -> None:
    console.print(
        Panel.fit(
            "[bold cyan]VICTORIA[/bold cyan]\n[cyan]AdTech Data Navigation[/cyan]",
            border_style="cyan",
        )
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def resource_path(name: str | Path) -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base / name
