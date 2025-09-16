#!/usr/bin/env python3
"""Victoria Terminal - AdTech Data Navigation.

This module orchestrates a Victoria terminal session. It follows a simple flow:
load environment values from ``~/Victoria/.env``, build a Crush configuration in
that same directory and finally hand control over to the Crush CLI. The
implementation is intentionally compact so future maintenance focuses on the
workflow rather than framework plumbing.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict

from rich.console import Console
from rich.prompt import Confirm

from common import (
    APP_HOME,
    CONFIGS_DIR,
    VICTORIA_FILE,
    __version__,
    banner,
    console,
    err,
    good,
    handle_error,
    info,
    initialize_colorama,
    load_dotenv,
    resource_path,
    section,
    warn,
)

CRUSH_CONFIG_NAME = "crush.json"
CRUSH_CONFIG_DIR = Path(CONFIGS_DIR) / "crush"
CRUSH_SUPPORT_FILES = {
    ".crushignore": CRUSH_CONFIG_DIR / ".crushignore",
    "CRUSH.md": CRUSH_CONFIG_DIR / "CRUSH.md",
}

SNOWFLAKE_ENV_VARS = [
    "SNOWFLAKE_ACCOUNT",
    "SNOWFLAKE_USER",
    "SNOWFLAKE_PASSWORD",
    "SNOWFLAKE_WAREHOUSE",
    "SNOWFLAKE_ROLE",
]

_env_token = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")


@dataclass
class Tool:
    """Simple description of a launchable tool."""

    name: str
    command: str
    output_config: str
    config_builder: Callable[[], Dict[str, Any]]
    preflight: Callable[["Tool"], None]
    launcher: Callable[["Tool"], None]


def preflight_crush(
    tool: Tool,
    _which: Callable[[str], str | None] = shutil.which,
    _os_environ: dict[str, str] = os.environ,
    _info: Callable[[str], None] = info,
    _good: Callable[[str], None] = good,
    _warn: Callable[[str], None] = warn,
    _err: Callable[[str], None] = err,
    _sys_exit: Callable[[int], None] = sys.exit,
    _section: Callable[[str], None] = section,
) -> None:
    """Validate that Crush can be launched."""

    _section("System preflight check")
    _info("Checking for Crush CLI")
    if _which(tool.command) is None:
        _err(
            f"Missing '{tool.command}' command-line tool. "
            "Rebuild the Victoria container or install the CLI in your environment."
        )
        _sys_exit(1)

    _good(f"{tool.command} CLI tool detected")

    if _os_environ.get("OPENROUTER_API_KEY"):
        _good("OpenRouter API key configured")
    else:
        _warn(
            "OPENROUTER_API_KEY not configured. Remote models will be unavailable until it is set."
        )

    _good("All systems ready")


def launch_crush(
    tool: Tool,
    _APP_HOME: Path = APP_HOME,
    _os_name: str = os.name,
    _execvp: Callable[..., None] = os.execvp,
    _subprocess_run: Callable[..., subprocess.CompletedProcess] = subprocess.run,
    _err: Callable[[str], None] = err,
    _info: Callable[[str], None] = info,
    _section: Callable[[str], None] = section,
    _sys_exit: Callable[[int], None] = sys.exit,
) -> None:
    """Launch Crush with the generated configuration."""

    _section("Mission launch")
    _info(f"Launching {tool.name}...")
    cmd = [tool.command, "-c", str(_APP_HOME), "--yolo"]
    try:
        if _os_name == "nt":
            proc = _subprocess_run(cmd)
            if proc.returncode != 0:
                _err(f"{tool.name} exited with {proc.returncode}")
                _sys_exit(proc.returncode)
        else:
            _execvp(tool.command, cmd)
    except FileNotFoundError:
        _err(
            f"'{tool.command}' command not found in PATH. "
            "Rebuild the Victoria container or install the CLI in your environment."
        )
        _sys_exit(1)
    except Exception as exc:  # pragma: no cover - runtime errors
        _err(f"Failed to launch {tool.name}: {exc}")
        _sys_exit(1)


def ensure_default_files(
    _APP_HOME: Path = APP_HOME,
    _resource_path: Callable[[str | Path], Path] = resource_path,
    _shutil_copy: Callable[[Path, Path], None] = shutil.copy,
    _VICTORIA_FILE: str = VICTORIA_FILE,
) -> None:
    """Ensure documentation and ignore files live next to the configuration."""

    for target_name, rel_path in CRUSH_SUPPORT_FILES.items():
        src = _resource_path(rel_path)
        dst = _APP_HOME / target_name
        if src.exists() and not dst.exists():
            _shutil_copy(src, dst)

    victoria_src = _resource_path(Path(_VICTORIA_FILE))
    victoria_dst = _APP_HOME / _VICTORIA_FILE
    if victoria_src.exists():
        _shutil_copy(victoria_src, victoria_dst)


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for the terminal."""

    parser = argparse.ArgumentParser(description="Victoria Terminal")
    parser.add_argument(
        "--check-credentials",
        dest="check_credentials",
        action="store_true",
        help="Warn if Snowflake credentials are missing before launch.",
    )
    parser.add_argument(
        "--skip-credential-check",
        dest="check_credentials",
        action="store_false",
        help="Skip the Snowflake credential warning prompt.",
    )
    parser.set_defaults(check_credentials=None)
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress informational messages.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser.parse_args()


def read_json(path: Path) -> Dict[str, Any]:
    """Read JSON from ``path`` handling UTF-8 BOMs."""

    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def write_json(path: Path, obj: Dict[str, Any]) -> None:
    """Write JSON to ``path`` in a deterministic format."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(obj, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def deep_merge(dst: Dict[str, Any], src: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge ``src`` into ``dst``."""

    for key, value in src.items():
        if key in dst and isinstance(dst[key], dict) and isinstance(value, dict):
            deep_merge(dst[key], value)
        elif key in dst and isinstance(dst[key], list) and isinstance(value, list):
            dst[key].extend(value)
        else:
            dst[key] = value
    return dst


def substitute_env(obj: Any, strict: bool = False) -> Any:
    """Replace ``${VAR}`` tokens with environment values."""

    if isinstance(obj, dict):
        return {key: substitute_env(value, strict) for key, value in obj.items()}
    if isinstance(obj, list):
        return [substitute_env(value, strict) for value in obj]
    if isinstance(obj, str):

        def repl(match: re.Match[str]) -> str:
            var = match.group(1)
            value = os.environ.get(var)
            if value is None:
                if strict:
                    raise KeyError(f"Environment variable {var} is required but not set")
                return match.group(0)
            return value

        return _env_token.sub(repl, obj)
    return obj


def load_tool_config(tool: str, name: str) -> Dict[str, Any]:
    """Load a configuration fragment from ``~/Victoria`` or packaged defaults."""

    home_candidate = APP_HOME / CONFIGS_DIR / tool / name
    package_candidate = resource_path(Path(CONFIGS_DIR) / tool / name)
    path = home_candidate if home_candidate.exists() else package_candidate
    if not path.exists():
        raise FileNotFoundError(f"Missing {name} for {tool}")
    return read_json(path)


def build_crush_config() -> Dict[str, Any]:
    """Construct the Crush configuration for the requested session."""

    config = load_tool_config("crush", "crush.template.json")
    return substitute_env(config, strict=False)


def generate_config(tool: Tool) -> bool:
    """Build and persist the Crush configuration."""

    try:
        config = tool.config_builder()
        output_path = APP_HOME / tool.output_config
        write_json(output_path, config)
        good(f"Configuration written to {output_path}")
        return True
    except Exception as exc:  # pragma: no cover - runtime errors
        err(f"Configuration generation failed: {exc}")
        return False


def snowflake_env_missing() -> list[str]:
    """Return Snowflake variables that are not present in the environment."""

    return [name for name in SNOWFLAKE_ENV_VARS if not os.environ.get(name)]


def snowflake_credentials_prompt(default: bool = False) -> bool:
    """Ask whether to verify Snowflake credentials before launching."""

    section("Snowflake credential check")
    return Confirm.ask(
        "Check for Snowflake credentials before launch?",
        default=default,
    )


def remove_local_duckdb() -> None:
    """Remove the cached DuckDB file so each run starts fresh."""

    db_path = APP_HOME / "adtech.duckdb"
    try:
        if db_path.exists():
            db_path.unlink()
            info(f"Removed local database: {db_path}")
    except Exception as exc:  # pragma: no cover - best effort cleanup
        warn(f"Could not remove {db_path}: {exc}")


def open_victoria_folder() -> None:
    """Open the Victoria directory in the host file manager."""

    try:
        if os.name == "nt":
            os.startfile(str(APP_HOME))  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.run(["open", str(APP_HOME)], check=False)
        else:
            subprocess.run(["xdg-open", str(APP_HOME)], check=False)
    except Exception as exc:  # pragma: no cover - OS dependent
        warn(f"Could not open Victoria folder: {exc}")


TOOL = Tool(
    name="Crush",
    command="crush",
    output_config=CRUSH_CONFIG_NAME,
    config_builder=build_crush_config,
    preflight=preflight_crush,
    launcher=launch_crush,
)


def main(
    _parse_args: Callable[[], argparse.Namespace] = parse_args,
    _ensure_default_files: Callable[[], None] = ensure_default_files,
    _banner: Callable[[], None] = banner,
    _credential_prompt: Callable[[bool], bool] = snowflake_credentials_prompt,
    _remove_local_duckdb: Callable[[], None] = remove_local_duckdb,
    _snowflake_env_missing: Callable[[], list[str]] = snowflake_env_missing,
    _generate_config: Callable[[Tool], bool] = generate_config,
    _open_victoria_folder: Callable[[], None] = open_victoria_folder,
    _console: Console = console,
    _info: Callable[[str], None] = info,
    _warn: Callable[[str], None] = warn,
    _good: Callable[[str], None] = good,
    _load_dotenv: Callable[[], None] = load_dotenv,
) -> None:
    """Entry point for launching the Victoria terminal."""

    initialize_colorama()
    _load_dotenv()
    args = _parse_args()

    info_printer = _info if not args.quiet else (lambda _msg: None)

    _ensure_default_files()
    _console.clear()
    _banner()

    tool = TOOL

    _remove_local_duckdb()
    info_printer(f"Place files to analyze in: {APP_HOME}")

    tool.preflight(tool)

    check_credentials = (
        args.check_credentials
        if getattr(args, "check_credentials", None) is not None
        else _credential_prompt()
    )
    if check_credentials:
        missing = _snowflake_env_missing()
        if missing:
            _warn(
                "Snowflake credentials are not fully configured (missing: "
                + ", ".join(missing)
                + "). Continuing without Snowflake access."
            )
        else:
            _good("Snowflake credentials detected")

    if not _generate_config(tool):
        sys.exit(1)

    if not args.quiet:
        _open_victoria_folder()

    tool.launcher(tool)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:  # pragma: no cover - user interaction
        console.print("\n[yellow]Voyage cancelled. Fair winds!")
        sys.exit(130)
    except Exception as exc:  # pragma: no cover - user interaction
        handle_error(exc)
