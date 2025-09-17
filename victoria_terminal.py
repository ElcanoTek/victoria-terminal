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
from pathlib import Path
from typing import Any, Mapping, MutableMapping, Sequence

from colorama import init as colorama_init
from dotenv import dotenv_values, load_dotenv, set_key
from rich.console import Console
from rich.panel import Panel

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

console = Console()

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


def banner() -> None:  # pragma: no cover - simple wrapper
    console.print(
        Panel.fit(
            "[bold cyan]VICTORIA[/bold cyan]\n[cyan]AdTech Data Navigation[/cyan]",
            border_style="cyan",
        )
    )


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
    """Guide the user through configuring credentials in ``.env``.

    Parameters
    ----------
    app_home:
        Victoria's shared workspace directory.
    env:
        Mapping used to read/write environment variables. Defaults to :mod:`os.environ`.
    force:
        When ``True`` the wizard prompts for all credentials even if they already exist.

    Returns
    -------
    bool
        ``True`` if the ``.env`` file was updated, otherwise ``False``.
    """

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
        value = _prompt_value(prompt_text, secret=True)
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
        description=(
            "Victoria container entry point. Ensures configuration exists " "and launches Crush."
        )
    )
    parser.add_argument(
        "--app-home",
        type=Path,
        default=APP_HOME,
        help=(
            "Directory to use for Victoria configuration "
            "(defaults to ~/Victoria or $VICTORIA_HOME)."
        ),
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

    banner()
    ensure_app_home(app_home)
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
