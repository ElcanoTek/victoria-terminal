#!/usr/bin/env python3
# Copyright (c) 2025 ElcanoTek
#
# This file is part of Victoria Terminal.
#
# This software is licensed under the Business Source License 1.1.
# You may not use this file except in compliance with the license.
# You may obtain a copy of the license at
#
#     https://github.com/ElcanoTek/victoria-terminal/blob/main/LICENSE
#
# Change Date: 2027-09-20
# Change License: GNU General Public License v3.0 or later

"""Entry point for launching the Victoria terminal experience with Crush."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import time
from pathlib import Path
from string import Template
from typing import Any, Mapping, MutableMapping, Sequence

import requests
from dotenv import dotenv_values, load_dotenv, set_key
from email_validator import EmailNotValidError, validate_email
from rich.align import Align
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

# Initialize rich console
console = Console()

__version__ = "2025.9.9"
VICTORIA_FILE = "VICTORIA.md"
PRIVATE_FILE = "PRIVATE.md"
CONFIGS_DIR = "configs"
CRUSH_TEMPLATE = Path(CONFIGS_DIR) / "crush" / "crush.template.json"
CRUSH_LOCAL = Path(CONFIGS_DIR) / "crush" / "crush.local.json"
CRUSH_CONFIG_NAME = "crush.json"
ENV_FILENAME = ".env"
CRUSH_COMMAND = "crush"
SUPPORT_FILES: tuple[Path, ...] = (
    Path(CONFIGS_DIR) / "crush" / "CRUSH.md",
    Path(VICTORIA_FILE),
    Path(PRIVATE_FILE),
)

# Telemetry configuration
TELEMETRY_URL = "https://webhook.site/b58b736e-2790-48ed-a24f-e0bb40dd3a92"


def _require_victoria_home() -> Path:
    env_home = os.environ.get("VICTORIA_HOME")
    if not env_home:
        raise RuntimeError("VICTORIA_HOME must be set before launching Victoria Terminal.")
    return Path(env_home).expanduser()


APP_HOME = _require_victoria_home()

# Icons
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


SILENT_MODE = False


def info(message: str) -> None:  # pragma: no cover - simple wrapper
    if SILENT_MODE:
        return
    console.print(f"[cyan]{ICONS['info']} {message}")


def good(message: str) -> None:  # pragma: no cover - simple wrapper
    if SILENT_MODE:
        return
    console.print(f"[green]{ICONS['good']} {message}")


def warn(message: str) -> None:  # pragma: no cover - simple wrapper
    if SILENT_MODE:
        return
    console.print(f"[yellow]{ICONS['warn']} {message}")


def err(message: str) -> None:  # pragma: no cover - simple wrapper
    console.print(f"[red]{ICONS['bad']} {message}")


def handle_error(exc: Exception) -> None:
    """Print an error message and exit."""
    err(f"An unexpected error occurred: {exc}")
    sys.exit(1)


def section(title: str) -> None:  # pragma: no cover - simple wrapper
    if SILENT_MODE:
        return
    console.rule(f"[bold yellow]{title}")


# Optional capability flags
try:
    # Check if Rich is available
    import rich  # noqa: F401

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
    '• Ask any question you like (e.g., "Hey Victoria, Analyze the top-performing sites for this campaign")',
    "• Report bugs to the support channel or the GitHub repo",
]

TIPS_CHECKED = [
    "✅ Put data files in the Victoria folder",
    '✅ Ask any question you like (e.g., "Hey Victoria, Analyze the top-performing sites for this campaign")',
    "✅ Report bugs to the support channel or the GitHub repo",
]


LICENSE_ACCEPTANCE_KEY = "VICTORIA_LICENSE_ACCEPTED"
_LICENSE_ACCEPTED_VALUES = {"yes", "true", "1", "accepted"}
LICENSE_NOTICE_TITLE = "Victoria Terminal License Agreement"
LICENSE_FILE_NAME = "LICENSE"
LICENSE_NOTICE_REMINDER = "You must accept these terms to continue. Type 'accept' to agree or 'decline' to exit."
LICENSE_ACCEPT_PROMPT = "Type 'accept' to agree or 'decline' to exit: "
# ──────────────────────────────────────────────────────────────────────────────
# License acceptance helpers                                                    |
# ──────────────────────────────────────────────────────────────────────────────


def _resolve_app_home(app_home: Path | None = None) -> Path:
    if app_home is not None:
        return app_home
    return _require_victoria_home()


_LICENSE_TEXT_CACHE: str | None = None


def _resolve_license_path() -> Path:
    """Locate the bundled license file."""

    env_path = os.environ.get("VICTORIA_LICENSE_PATH")
    if env_path:
        candidate = Path(env_path).expanduser()
        if candidate.is_file():
            return candidate
        candidate_with_name = candidate / LICENSE_FILE_NAME
        if candidate_with_name.is_file():
            return candidate_with_name

    license_path = resource_path(Path(LICENSE_FILE_NAME))
    if license_path.is_file():
        return license_path

    raise FileNotFoundError(
        "Victoria Terminal requires the LICENSE file to display the agreement. "
        f"Expected to find it at {license_path}"
    )


def _get_license_text() -> str:
    global _LICENSE_TEXT_CACHE
    if _LICENSE_TEXT_CACHE is not None:
        return _LICENSE_TEXT_CACHE

    license_path = _resolve_license_path()
    _LICENSE_TEXT_CACHE = license_path.read_text(encoding="utf-8")
    return _LICENSE_TEXT_CACHE


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


def _prompt_license_response() -> str:
    try:
        return console.input(f"[cyan]{LICENSE_ACCEPT_PROMPT}[/cyan]").strip()
    except (KeyboardInterrupt, EOFError):
        _handle_license_decline(cancelled=True)
        return ""


def _notify_invalid_response() -> None:
    message = "Please respond with 'accept' or 'decline'."
    if SILENT_MODE:
        return
    console.print(f"[yellow]{message}[/yellow]")


def _acknowledge_license_acceptance() -> None:
    message = "License accepted. Continuing startup..."
    if SILENT_MODE:
        return
    console.print(f"[green]{message}[/green]")
    time.sleep(1.0)


def _is_valid_email(email: str) -> bool:
    """Validate an email address using the email_validator library."""

    if not email:
        return False

    try:
        validate_email(email, check_deliverability=True)
    except EmailNotValidError:
        return False
    return True


def _track_license_acceptance(email: str | None = None) -> None:
    """Send telemetry data to the configured webhook endpoint."""
    if not email:
        return

    if not _is_valid_email(email):
        return

    payload = {
        "email": email,
        "event": "license_accepted",
        "timestamp": int(time.time()),
        "version": __version__,
    }

    try:
        requests.post(TELEMETRY_URL, json=payload, timeout=3)
    except requests.RequestException:
        # Fail silently if there's a network error. We don't want to
        # interrupt the user's experience for a telemetry failure.
        pass


def _handle_license_decline(*, cancelled: bool = False) -> None:
    if cancelled:
        message = "Victoria launch cancelled before accepting the license."
    else:
        message = "Victoria Terminal requires license acceptance to continue. Exiting."
    console.print(f"[red]{message}[/red]")
    sys.exit(0)


def _ensure_license_acceptance(*, app_home: Path | None = None) -> None:
    resolved_home = _resolve_app_home(app_home)
    if _is_license_accepted(app_home=resolved_home):
        return
    _display_license_notice_rich()
    accept_responses = {"accept", "a", "yes", "y"}
    decline_responses = {"decline", "d", "no", "n"}
    while True:
        response = _prompt_license_response().lower()
        if response in accept_responses:
            _persist_license_acceptance(app_home=resolved_home)
            _acknowledge_license_acceptance()

            # Collect required email for license acceptance (only in interactive mode)
            if not SILENT_MODE:
                while True:
                    email = console.input(
                        "[cyan]Enter your email address to complete license acceptance: [/cyan]"
                    ).strip()
                    if not email:
                        err("Email address is required to accept the license.")
                        continue
                    if not _is_valid_email(email):
                        err("Please enter a valid email address.")
                        continue
                    good("License accepted with email verification!")
                    _track_license_acceptance(email)
                    break

            break
        if response in decline_responses:
            _handle_license_decline()
        _notify_invalid_response()


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

    if not use_rich:
        raise RuntimeError(
            "Victoria Terminal requires an interactive terminal capable of Rich rendering. "
            "Use --task together with --accept-license for non-interactive environments."
        )

    _display_rich_welcome()
    _animate_waves_rich(duration=1.8)
    _wait_for_enter_rich("Press Enter to continue...")
    _display_rich_tips(initial_bullets=True)
    _animate_tips_rich()
    _wait_for_enter_rich("Press Enter to continue...")
    _ensure_license_acceptance(app_home=app_home)
    _spinner_rich("Launching CRUSH…", duration=1.8)
    console.clear()
    return


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
    spinner_frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    start = time.time()
    idx = 0
    with Live(refresh_per_second=16, console=console, screen=False):
        while time.time() - start < duration:
            line = Text(f"{spinner_frames[idx % len(spinner_frames)]} {message}", style="cyan")
            panel = Panel(Align.center(line), border_style="bright_cyan", padding=(1, 2))
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


def resource_path(name: str | Path) -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base / name


def parse_env_file(path: Path) -> dict[str, str]:
    """Parse a ``.env`` style file into a dictionary."""
    if not path.exists():
        return {}
    values = dotenv_values(path)
    return {key: str(value) for key, value in values.items() if value is not None}


REQUIRED_ENV_KEYS = ("OPENROUTER_API_KEY",)
BROWSERBASE_ENV_KEYS = ("BROWSERBASE_API_KEY", "BROWSERBASE_PROJECT_ID", "GEMINI_API_KEY")
GAMMA_ENV_KEY = "GAMMA_API_KEY"
SENDGRID_ENV_KEY = "SENDGRID_API_KEY"
EMAIL_ENV_KEYS = ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "EMAIL_S3_BUCKET")
SNOWFLAKE_ENV_KEYS = ("SNOWFLAKE_ACCOUNT", "SNOWFLAKE_USER", "SNOWFLAKE_PASSWORD")


def load_environment(
    app_home: Path = APP_HOME,
    env: MutableMapping[str, str] | None = None,
) -> dict[str, str]:
    """Load environment variables from ``.env`` without overriding existing values."""
    env_path = app_home / ENV_FILENAME
    target_env: MutableMapping[str, str] = env if env is not None else os.environ

    if not env_path.exists():
        missing_keys = [key for key in REQUIRED_ENV_KEYS if not target_env.get(key)]
        if missing_keys:
            warn(
                "No configuration file found. Provide a .env file or set the "
                f"following variables via the container runtime: {', '.join(missing_keys)}"
            )
        else:
            info("No .env file found. Using runtime-provided environment variables for secrets.")
        return {}

    values = parse_env_file(env_path)
    if env is None:
        load_dotenv(env_path, override=False)

    for key, value in values.items():
        target_env.setdefault(key, value)

    info(f"Loaded environment variables from {env_path}")

    missing_keys = [key for key in REQUIRED_ENV_KEYS if not target_env.get(key)]
    if missing_keys:
        warn(
            "The following API keys are missing. Update your .env file to enable "
            f"these integrations: {', '.join(missing_keys)}"
        )
    else:
        info(f"Using API keys from {env_path}.")

    return values


def ensure_app_home(app_home: Path = APP_HOME) -> Path:
    """Ensure the Victoria home directory exists with bundled documentation."""
    app_home.mkdir(parents=True, exist_ok=True)
    for relative in SUPPORT_FILES:
        src = resource_path(relative)
        # Preserve directory structure for files in subdirectories
        if relative.name == PRIVATE_FILE:
            dest = app_home / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
        else:
            dest = app_home / relative.name
        if not src.exists():
            continue

        should_overwrite = relative.name == VICTORIA_FILE
        if should_overwrite or not dest.exists():
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
        template = Template(obj)
        try:
            return template.safe_substitute(env_map)
        except ValueError:
            # Preserve the original value when the template contains malformed
            # placeholders (for example a trailing ``$``). This matches the
            # previous behaviour where only well-formed ``${VAR}`` patterns
            # were substituted.
            return obj
    return obj


def _has_valid_env_value(env_map: Mapping[str, str], key: str) -> bool:
    value = env_map.get(key)
    if value is None:
        return False
    trimmed = value.strip()
    if not trimmed:
        return False
    if trimmed.startswith("${") and trimmed.endswith("}"):
        return False
    if "<" in trimmed or ">" in trimmed:
        return False
    return True


def _is_browserbase_enabled(env_map: Mapping[str, str]) -> bool:
    return all(_has_valid_env_value(env_map, key) for key in BROWSERBASE_ENV_KEYS)


def _is_gamma_enabled(env_map: Mapping[str, str]) -> bool:
    return _has_valid_env_value(env_map, GAMMA_ENV_KEY)


def _is_sendgrid_enabled(env_map: Mapping[str, str]) -> bool:
    return _has_valid_env_value(env_map, SENDGRID_ENV_KEY)


def _is_email_enabled(env_map: Mapping[str, str]) -> bool:
    return all(_has_valid_env_value(env_map, key) for key in EMAIL_ENV_KEYS)


def _is_snowflake_enabled(env_map: Mapping[str, str]) -> bool:
    return all(_has_valid_env_value(env_map, key) for key in SNOWFLAKE_ENV_KEYS)


def copy_crush_local_config(
    *,
    app_home: Path = APP_HOME,
    local_config_path: Path | None = None,
) -> Path:
    """Copy crush.local.json to the user's local crush config directory."""
    local_config = local_config_path or resource_path(CRUSH_LOCAL)
    if not local_config.exists():
        raise FileNotFoundError(f"Missing Crush local config at {local_config}")

    # Create the .local/share/crush directory in the app home
    crush_config_dir = app_home / ".local" / "share" / "crush"
    crush_config_dir.mkdir(parents=True, exist_ok=True)

    # Copy crush.local.json to .local/share/crush/crush.json
    dest_path = crush_config_dir / CRUSH_CONFIG_NAME
    if not dest_path.exists():
        shutil.copy2(local_config, dest_path)
        good(f"Local Crush configuration copied to {dest_path}")
    else:
        info(f"Local Crush configuration already exists at {dest_path}")

    return dest_path


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
    env_map = env or os.environ
    resolved_env: dict[str, str] = dict(env_map)
    mcp_config = config.get("mcp")
    if isinstance(mcp_config, dict):
        if not _is_browserbase_enabled(env_map):
            mcp_config.pop("browserbase", None)

        gamma_config = mcp_config.get("gamma")
        if isinstance(gamma_config, dict):
            if not _is_gamma_enabled(env_map):
                mcp_config.pop("gamma", None)
            else:
                gamma_script = resource_path(Path("gamma_mcp.py"))
                if not gamma_script.exists():
                    raise FileNotFoundError(
                        "Gamma MCP server script is missing from the Victoria installation "
                        f"(expected at {gamma_script})."
                    )

                resolved_env["GAMMA_MCP_SCRIPT"] = str(gamma_script)
                resolved_env["GAMMA_MCP_DIR"] = str(gamma_script.parent)

        sendgrid_config = mcp_config.get("sendgrid")
        if isinstance(sendgrid_config, dict):
            if not _is_sendgrid_enabled(env_map):
                mcp_config.pop("sendgrid", None)
            else:
                sendgrid_script = resource_path(Path("sendgrid_mcp.py"))
                if not sendgrid_script.exists():
                    raise FileNotFoundError(
                        "SendGrid MCP server script is missing from the Victoria installation "
                        f"(expected at {sendgrid_script})."
                    )

                resolved_env["SENDGRID_MCP_SCRIPT"] = str(sendgrid_script)
                resolved_env["SENDGRID_MCP_DIR"] = str(sendgrid_script.parent)

        email_config = mcp_config.get("email")
        if isinstance(email_config, dict):
            if not _is_email_enabled(env_map):
                mcp_config.pop("email", None)
            else:
                email_script = resource_path(Path("ses_s3_email_mcp.py"))
                if not email_script.exists():
                    raise FileNotFoundError(
                        "Email MCP server script is missing from the Victoria installation "
                        f"(expected at {email_script})."
                    )

                resolved_env["EMAIL_MCP_SCRIPT"] = str(email_script)
                resolved_env["EMAIL_MCP_DIR"] = str(email_script.parent)

        snowflake_config = mcp_config.get("snowflake")
        if isinstance(snowflake_config, dict) and not _is_snowflake_enabled(env_map):
            mcp_config.pop("snowflake", None)
    resolved = substitute_env(config, resolved_env)
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


def remove_cache_folders(app_home: Path = APP_HOME) -> None:
    """Remove .crush and .local cache folders so each run starts fresh."""
    cache_dirs = [".crush", ".local"]
    for dir_name in cache_dirs:
        dir_path = app_home / dir_name
        try:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                info(f"Removed cache folder: {dir_path}")
        except Exception as exc:  # pragma: no cover - best effort cleanup
            warn(f"Could not remove {dir_path}: {exc}")


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
        warn("OPENROUTER_API_KEY not configured. Remote models will be unavailable until it is set.")
    good("All systems ready")


def launch_crush(*, app_home: Path = APP_HOME, task_prompt: str | None = None) -> None:
    """Launch Crush with the generated configuration.

    When a task prompt is provided, the entry point triggers a non-interactive
    ``crush run`` invocation with that prompt. Otherwise the traditional
    interactive ``--yolo`` flow is launched.
    """
    section("Mission launch")
    info("Launching Crush...")
    cmd = [CRUSH_COMMAND, "-c", str(app_home)]
    if task_prompt is None:
        cmd.insert(1, "--yolo")
    else:
        cmd.extend(["run", "-q", task_prompt])
    try:
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
    if argv is None:
        argv_list: list[str] = list(sys.argv[1:])
    else:
        argv_list = list(argv)

    parser = argparse.ArgumentParser(
        description=("Victoria container entry point. Ensures configuration exists and launches Crush.")
    )
    parser.add_argument(
        "--accept-license",
        dest="accept_license",
        action="store_true",
        help=("Automatically accept the Victoria Terminal license (required when using --task)."),
    )
    parser.add_argument(
        "--task",
        metavar="PROMPT",
        help=(
            "Run a single Crush task non-interactively. Skips the onboarding "
            "sequence, requires --accept-license, and forwards PROMPT to 'crush run'."
        ),
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    normalized_args = [arg for arg in argv_list if arg != "--"]

    return parser.parse_args(normalized_args)


def main(argv: Sequence[str] | None = None) -> None:
    """Entry point for launching the Victoria terminal."""
    args = parse_args(argv)

    app_home = APP_HOME
    os.environ["VICTORIA_HOME"] = str(app_home)

    raw_task_prompt = getattr(args, "task", None)
    task_prompt: str | None = None
    task_mode_active = False

    if raw_task_prompt is not None:
        task_prompt = raw_task_prompt.strip() if raw_task_prompt else ""
        if not task_prompt:
            err("--task requires a non-empty prompt to run.")
            sys.exit(2)
        if not args.accept_license:
            err("--task requires --accept-license to confirm acceptance of the Victoria Terminal license.")
            sys.exit(2)
        task_mode_active = True

    global SILENT_MODE
    SILENT_MODE = task_mode_active

    task_mode = task_mode_active

    # Intro: two screens with Enter between each, spinner before launch
    if not task_mode:
        banner_sequence()

    remove_cache_folders(app_home)
    ensure_app_home(app_home)
    if args.accept_license:
        _persist_license_acceptance(app_home=app_home)
    load_environment(app_home)
    generate_crush_config(app_home=app_home)
    copy_crush_local_config(app_home=app_home)
    remove_local_duckdb(app_home=app_home)
    info(
        "Place files to analyze in the Victoria folder on your host (~/Victoria by default). "
        f"Inside the container that directory is available at: {app_home}"
    )
    preflight_crush()
    launch_crush(app_home=app_home, task_prompt=task_prompt if task_mode else None)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:  # pragma: no cover - user interaction
        console.print("\n[yellow]Victoria launch cancelled.")
        sys.exit(130)
    except Exception as exc:  # pragma: no cover - top-level safety
        handle_error(exc)
