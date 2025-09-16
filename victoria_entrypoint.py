#!/usr/bin/env python3
"""Unified entry point for the Victoria Terminal experience."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, MutableMapping, Sequence

from colorama import init as colorama_init
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt

__version__ = "2025.9.8"
VICTORIA_FILE = "VICTORIA.md"
CONFIGS_DIR = "configs"
CRUSH_TEMPLATE = Path(CONFIGS_DIR) / "crush" / "crush.template.json"
CRUSH_CONFIG_NAME = "crush.json"
SUPPORT_FILES: tuple[Path, ...] = (
    Path(CONFIGS_DIR) / "crush" / "CRUSH.md",
    Path(VICTORIA_FILE),
)

ENV_FILENAME = ".env"
SHARED_CONFIG_ITEMS: tuple[str, ...] = (ENV_FILENAME, CRUSH_CONFIG_NAME, "prompts")
SNOWFLAKE_ENV_VARS: tuple[str, ...] = (
    "SNOWFLAKE_ACCOUNT",
    "SNOWFLAKE_USER",
    "SNOWFLAKE_PASSWORD",
    "SNOWFLAKE_WAREHOUSE",
    "SNOWFLAKE_ROLE",
)
SNOWFLAKE_PROMPTS: dict[str, str] = {
    "SNOWFLAKE_ACCOUNT": "Snowflake account identifier",
    "SNOWFLAKE_USER": "Snowflake username",
    "SNOWFLAKE_PASSWORD": "Snowflake password",
    "SNOWFLAKE_WAREHOUSE": "Snowflake warehouse",
    "SNOWFLAKE_ROLE": "Snowflake role",
}

APP_HOME = Path(os.path.expanduser("~")) / "Victoria"
APP_HOME.mkdir(exist_ok=True)
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


_ENV_TOKEN = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")


def resource_path(name: str | Path) -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base / name


def load_dotenv(
    app_home: Path = APP_HOME,
    env: MutableMapping[str, str] | None = None,
) -> None:
    """Load environment variables from ``.env`` without overriding existing values."""

    env_file = app_home / ENV_FILENAME
    if not env_file.exists():
        return

    target_env: MutableMapping[str, str] = env if env is not None else os.environ
    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            target_env.setdefault(key, value)


load_dotenv()


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


def _serialize_env_value(key: str, value: str) -> str:
    if value == "":
        return f"{key}="
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'{key}="{escaped}"'


def write_env_file(
    path: Path,
    values: Mapping[str, str],
    order: Iterable[str] | None = None,
) -> None:
    """Write environment values to ``path`` in a deterministic order."""

    preferred_order = list(order or (["OPENROUTER_API_KEY", *SNOWFLAKE_ENV_VARS]))
    seen: set[str] = set()
    lines = [
        "# Victoria environment configuration",
        "# Generated by victoria_entrypoint.py",
    ]
    for key in preferred_order:
        lines.append(_serialize_env_value(key, values.get(key, "")))
        seen.add(key)
    for key in sorted(k for k in values if k not in seen):
        lines.append(_serialize_env_value(key, values[key]))

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def prompt_for_configuration(
    existing: Mapping[str, str],
    *,
    confirm: Callable[..., bool] | None = None,
    prompt: Callable[..., str] | None = None,
) -> dict[str, str]:
    """Collect configuration values interactively."""

    confirm_fn = confirm or Confirm.ask
    prompt_fn = prompt or Prompt.ask

    section("Victoria configuration")
    info(f"Configuration directory: {APP_HOME}")

    result = dict(existing)

    configure_openrouter = confirm_fn(
        "Configure OpenRouter API access?",
        default=bool(existing.get("OPENROUTER_API_KEY")),
    )
    if configure_openrouter:
        while True:
            key_default = existing.get("OPENROUTER_API_KEY", "")
            value = prompt_fn(
                "OpenRouter API key",
                default=key_default or None,
                show_default=bool(key_default),
            ).strip()
            if value:
                result["OPENROUTER_API_KEY"] = value
                break
            warn("OpenRouter API key cannot be empty when OpenRouter support is enabled.")
    else:
        result.pop("OPENROUTER_API_KEY", None)

    configure_snowflake = confirm_fn(
        "Configure Snowflake credentials?",
        default=all(existing.get(var) for var in SNOWFLAKE_ENV_VARS),
    )
    if configure_snowflake:
        for env_var in SNOWFLAKE_ENV_VARS:
            default = existing.get(env_var, "")
            prompt_label = SNOWFLAKE_PROMPTS.get(env_var, env_var)
            value = prompt_fn(
                prompt_label,
                default=default or None,
                show_default=bool(default),
            ).strip()
            result[env_var] = value
    else:
        for env_var in SNOWFLAKE_ENV_VARS:
            result.pop(env_var, None)

    return result


def sync_shared_configuration(
    shared_home: Path,
    *,
    local_home: Path = APP_HOME,
    overwrite: bool = False,
    items: Iterable[str] = SHARED_CONFIG_ITEMS,
) -> list[Path]:
    """Copy configuration items from ``shared_home`` into ``local_home``."""

    copied: list[Path] = []
    try:
        if shared_home.resolve() == local_home.resolve():
            return copied
    except FileNotFoundError:
        pass

    if not shared_home.exists():
        return copied

    local_home.mkdir(parents=True, exist_ok=True)

    for name in items:
        src = shared_home / name
        if not src.exists():
            continue
        dest = local_home / name
        if src.is_dir():
            if dest.exists():
                if not overwrite:
                    continue
                shutil.rmtree(dest)
            shutil.copytree(src, dest)
            copied.append(dest)
        else:
            if dest.exists() and not overwrite:
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            copied.append(dest)

    if copied:
        info("Synchronized shared configuration: " + ", ".join(path.name for path in copied))
    return copied


def ensure_configuration(
    *,
    force_reconfigure: bool = False,
    interactive: bool = True,
    shared_home: Path | None = None,
    app_home: Path = APP_HOME,
) -> bool:
    """Ensure configuration exists and optionally create it interactively."""

    env_path = app_home / ENV_FILENAME

    if shared_home is not None:
        sync_shared_configuration(shared_home, local_home=app_home, overwrite=force_reconfigure)

    existing_values = parse_env_file(env_path)

    if env_path.exists() and not force_reconfigure:
        info(f"Using configuration from {env_path}")
        load_dotenv(app_home=app_home)
        return True

    if force_reconfigure and env_path.exists():
        env_path.unlink()

    if not interactive:
        warn("Configuration file not found and interactive mode disabled.")
        return False

    values = prompt_for_configuration(existing_values)
    write_env_file(env_path, values)
    good(f"Configuration written to {env_path}")
    load_dotenv(app_home=app_home)
    return True


def ensure_default_files(app_home: Path = APP_HOME) -> None:
    """Ensure documentation files live next to the configuration."""

    for relative in SUPPORT_FILES:
        src = resource_path(relative)
        dest = app_home / relative.name
        if src.exists() and not dest.exists():
            shutil.copy2(src, dest)


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def substitute_env(
    obj: Any,
    env: Mapping[str, str] | None = None,
    *,
    strict: bool = False,
) -> Any:
    """Replace ``${VAR}`` tokens with values from ``env``."""

    env_map = env or os.environ

    if isinstance(obj, dict):
        return {key: substitute_env(value, env_map, strict=strict) for key, value in obj.items()}
    if isinstance(obj, list):
        return [substitute_env(value, env_map, strict=strict) for value in obj]
    if isinstance(obj, str):

        def repl(match: re.Match[str]) -> str:
            var = match.group(1)
            value = env_map.get(var)
            if value is None:
                if strict:
                    raise KeyError(f"Environment variable {var} is required but not set")
                return match.group(0)
            return value

        return _ENV_TOKEN.sub(repl, obj)
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


def open_victoria_folder(app_home: Path = APP_HOME) -> None:
    """Open the Victoria directory in the host file manager."""

    try:
        if os.name == "nt":
            os.startfile(str(app_home))  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.run(["open", str(app_home)], check=False)
        else:
            subprocess.run(["xdg-open", str(app_home)], check=False)
    except Exception as exc:  # pragma: no cover - OS dependent
        warn(f"Could not open Victoria folder: {exc}")


def preflight_crush(command: str = "crush") -> None:
    """Validate that Crush can be launched."""

    section("System preflight check")
    info(f"Checking for {command} CLI")
    if shutil.which(command) is None:
        err(
            f"Missing '{command}' command-line tool. "
            "Rebuild the Victoria container or install the CLI in your environment."
        )
        sys.exit(1)

    good(f"{command} CLI tool detected")

    if os.environ.get("OPENROUTER_API_KEY"):
        good("OpenRouter API key configured")
    else:
        warn("OPENROUTER_API_KEY not configured. Remote models will be unavailable until it is set.")

    good("All systems ready")


def launch_crush(command: str = "crush", *, app_home: Path = APP_HOME) -> None:
    """Launch Crush with the generated configuration."""

    section("Mission launch")
    info("Launching Crush...")
    cmd = [command, "-c", str(app_home), "--yolo"]
    try:
        if os.name == "nt":
            proc = subprocess.run(cmd, check=False)
            if proc.returncode != 0:
                err(f"Crush exited with {proc.returncode}")
                sys.exit(proc.returncode)
        else:
            os.execvp(command, cmd)
    except FileNotFoundError:
        err(
            f"'{command}' command not found in PATH. "
            "Rebuild the Victoria container or install the CLI in your environment."
        )
        sys.exit(1)
    except Exception as exc:  # pragma: no cover - runtime errors
        err(f"Failed to launch Crush: {exc}")
        sys.exit(1)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments for the entry point."""

    parser = argparse.ArgumentParser(
        description="Victoria container entry point. Ensures configuration exists and launches the terminal."
    )
    parser.add_argument(
        "--shared-home",
        type=Path,
        default=os.environ.get("VICTORIA_SHARED_HOME"),
        help="Optional directory containing shared Victoria configuration to sync before launch.",
    )
    parser.add_argument(
        "--reconfigure",
        action="store_true",
        help="Force interactive configuration even if an existing .env file is present.",
    )
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Fail instead of prompting when configuration is missing.",
    )
    parser.add_argument(
        "--skip-launch",
        action="store_true",
        help="Only ensure configuration exists; do not start Victoria Terminal.",
    )
    parser.add_argument(
        "--skip-credential-check",
        action="store_true",
        help="Skip the Snowflake credential warning prompt.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress optional informational messages and skip opening the Victoria folder.",
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

    banner()

    shared_home = args.shared_home
    shared_path = Path(shared_home).expanduser() if shared_home else None

    configured = ensure_configuration(
        force_reconfigure=args.reconfigure,
        interactive=not args.non_interactive,
        shared_home=shared_path,
    )
    if not configured:
        err(
            "Victoria is not configured. Provide a shared ~/Victoria directory or rerun with interactive prompts."
        )
        sys.exit(1)

    ensure_default_files()
    generate_crush_config()

    if not args.skip_credential_check:
        check_snowflake_credentials()

    remove_local_duckdb()
    if not args.quiet:
        info(f"Place files to analyze in: {APP_HOME}")

    preflight_crush()

    if args.skip_launch:
        return

    if not args.quiet:
        open_victoria_folder()

    launch_crush()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:  # pragma: no cover - user interaction
        console.print("\n[yellow]Victoria launch cancelled.")
        sys.exit(130)
    except Exception as exc:  # pragma: no cover - top-level safety
        handle_error(exc)
