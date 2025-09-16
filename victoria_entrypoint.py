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
from rich.console import Console
from rich.panel import Panel

__version__ = "2025.9.8"
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
SNOWFLAKE_ENV_VARS: tuple[str, ...] = (
    "SNOWFLAKE_ACCOUNT",
    "SNOWFLAKE_USER",
    "SNOWFLAKE_PASSWORD",
    "SNOWFLAKE_WAREHOUSE",
    "SNOWFLAKE_ROLE",
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

    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            values[key] = value
    return values


def load_environment(
    app_home: Path = APP_HOME,
    env: MutableMapping[str, str] | None = None,
) -> dict[str, str]:
    """Load environment variables from ``.env`` without overriding existing values."""

    env_path = app_home / ENV_FILENAME
    if not env_path.exists():
        return {}

    values = parse_env_file(env_path)
    target_env: MutableMapping[str, str] = env if env is not None else os.environ
    for key, value in values.items():
        target_env.setdefault(key, value)

    info(f"Loaded environment variables from {env_path}")
    return values


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


def snowflake_env_missing(env: Mapping[str, str] | None = None) -> list[str]:
    """Return Snowflake variables that are not present in ``env``."""

    env_map = env or os.environ
    return [name for name in SNOWFLAKE_ENV_VARS if not env_map.get(name)]


def check_snowflake_credentials(env: Mapping[str, str] | None = None) -> None:
    """Report whether Snowflake credentials appear to be configured."""

    section("Snowflake credential check")
    missing = snowflake_env_missing(env)
    if missing:
        warn(
            "Snowflake credentials are not fully configured (missing: "
            + ", ".join(missing)
            + "). Continuing without Snowflake access."
        )
    else:
        good("Snowflake credentials detected")


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
        warn("OPENROUTER_API_KEY not configured. Remote models will be unavailable until it is set.")

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
        description="Victoria container entry point. Ensures configuration exists and launches Crush."
    )
    parser.add_argument(
        "--app-home",
        type=Path,
        default=APP_HOME,
        help="Directory to use for Victoria configuration (defaults to ~/Victoria or $VICTORIA_HOME).",
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
    generate_crush_config(app_home=app_home)
    check_snowflake_credentials()
    remove_local_duckdb(app_home=app_home)
    info(f"Place files to analyze in: {app_home}")
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
