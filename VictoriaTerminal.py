#!/usr/bin/env python3
"""Victoria Terminal - AdTech Data Navigation"""

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
from typing import Any, Callable, Dict, List

from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn

from common import (
    APP_HOME,
    CONFIGS_DIR,
    SETUP_SENTINEL,
    VICTORIA_FILE,
    __version__,
    banner,
    console,
    err,
    good,
    info,
    resource_path,
    section,
    warn,
)


def which(cmd: str) -> str | None:
    return shutil.which(cmd)


# ---------------------------------------------------------------------------
# Tooling Definition
# ---------------------------------------------------------------------------


@dataclass
class Tool:
    name: str
    command: str
    output_config: str
    config_builder: Callable[[bool, bool, bool], Dict[str, Any]]
    preflight: Callable[[Tool, bool], None]
    launcher: Callable[[Tool], None]


def preflight_crush(
    tool: Tool,
    use_local_model: bool,
    _which: Callable[[str], str | None] = shutil.which,
    _os_environ: dict = os.environ,
    _info: Callable[[str], None] = info,
    _good: Callable[[str], None] = good,
    _warn: Callable[[str], None] = warn,
    _err: Callable[[str], None] = err,
    _sys_exit: Callable[[int], None] = sys.exit,
    _section: Callable[[str], None] = section,
    _Progress: type = Progress,
) -> None:
    _section("System preflight check")
    with _Progress(SpinnerColumn(), TextColumn("{task.description}"), transient=True) as progress:
        progress.add_task("Verifying prerequisites", total=None)
        if _which(tool.command) is None:
            _err(f"Missing '{tool.command}' command-line tool. Please run the Victoria Configurator first.")
            _sys_exit(1)
    _good(f"{tool.command} CLI tool detected")
    has_key = bool(_os_environ.get("OPENROUTER_API_KEY"))
    if not use_local_model and not has_key:
        _warn("OPENROUTER_API_KEY not configured. Please run the Victoria Configurator to set it up.")
        _sys_exit(1)
    if has_key:
        _good("OpenRouter API key configured")
    if use_local_model:
        _good("Local model provider selected")
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
    _section("Mission launch")
    _info(f"Launching {tool.name}...")
    cmd = [tool.command, "-c", str(_APP_HOME)]
    try:
        if _os_name == "nt":
            proc = _subprocess_run(cmd)
            if proc.returncode != 0:
                _err(f"{tool.name} exited with {proc.returncode}")
                _sys_exit(proc.returncode)
        else:
            _execvp(tool.command, cmd)
    except FileNotFoundError:
        _err(f"'{tool.command}' command not found in PATH. Please run the Victoria Configurator.")
        _sys_exit(1)
    except Exception as exc:  # pragma: no cover - runtime errors
        _err(f"Failed to launch {tool.name}: {exc}")
        _sys_exit(1)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def ensure_default_files(
    _APP_HOME: Path = APP_HOME,
    _CONFIGS_DIR: str = CONFIGS_DIR,
    _VICTORIA_FILE: str = VICTORIA_FILE,
    _resource_path: Callable[[str | Path], Path] = resource_path,
    _shutil_copy: Callable[[Path, Path], None] = shutil.copy,
) -> None:
    crush_dir = Path(_CONFIGS_DIR) / "crush"
    # These files are only copied if they don't exist.
    files_copy_if_missing = [
        (crush_dir / ".crushignore", ".crushignore"),
        (crush_dir / "CRUSH.md", "CRUSH.md"),
    ]
    for rel_path, fname in files_copy_if_missing:
        src = _resource_path(rel_path)
        dst = _APP_HOME / fname
        if src.exists() and not dst.exists():
            _shutil_copy(src, dst)

    # VICTORIA.md is always overwritten to ensure it's pristine.
    victoria_src = _resource_path(Path(_VICTORIA_FILE))
    victoria_dst = _APP_HOME / _VICTORIA_FILE
    if victoria_src.exists():
        _shutil_copy(victoria_src, victoria_dst)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Victoria Terminal")
    parser.add_argument(
        "--course",
        type=int,
        choices=[1, 2],
        default=None,
        help="The course to select (1 for Snowflake, 2 for local files).",
    )
    parser.add_argument(
        "--local-model",
        action="store_true",
        help="Use a local model.",
    )
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


# ---------------------------------------------------------------------------
# JSON handling
# ---------------------------------------------------------------------------


def read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


def write_json(path: Path, obj: Dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


def deep_merge(dst: Dict[str, Any], src: Dict[str, Any]) -> Dict[str, Any]:
    for k, v in src.items():
        if k in dst and isinstance(dst[k], dict) and isinstance(v, dict):
            deep_merge(dst[k], v)
        elif k in dst and isinstance(dst[k], list) and isinstance(v, list):
            dst[k].extend(v)
        else:
            dst[k] = v
    return dst


_env_token = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")


def substitute_env(obj: Any, strict: bool = False) -> Any:
    if isinstance(obj, dict):
        return {k: substitute_env(v, strict) for k, v in obj.items()}
    if isinstance(obj, list):
        return [substitute_env(v, strict) for v in obj]
    if isinstance(obj, str):
        def repl(m: re.Match[str]) -> str:
            var = m.group(1)
            val = os.environ.get(var)
            if val is None:
                if strict:
                    raise KeyError(f"Environment variable {var} is required but not set")
                return m.group(0)
            return val
        return _env_token.sub(repl, obj)
    return obj


# ---------------------------------------------------------------------------
# Config generation
# ---------------------------------------------------------------------------

SNOWFLAKE_ENV_VARS = [
    "SNOWFLAKE_ACCOUNT",
    "SNOWFLAKE_USER",
    "SNOWFLAKE_PASSWORD",
    "SNOWFLAKE_WAREHOUSE",
    "SNOWFLAKE_ROLE",
]


def snowflake_env_missing() -> list[str]:
    return [v for v in SNOWFLAKE_ENV_VARS if not os.environ.get(v)]


def load_tool_config(tool: str, name: str) -> Dict[str, Any]:
    path_home = APP_HOME / CONFIGS_DIR / tool / name
    path_res = resource_path(Path(CONFIGS_DIR) / tool / name)
    path = path_home if path_home.exists() else path_res
    if not path.exists():
        raise FileNotFoundError(f"Missing {name} for {tool}")
    return read_json(path)


def build_crush_config(include_snowflake: bool, strict_env: bool, local_model: bool) -> Dict[str, Any]:
    base = load_tool_config("crush", "crush.template.json")
    if include_snowflake:
        frag = load_tool_config("crush", "snowflake.mcp.json")
        base.setdefault("mcp", {})
        deep_merge(base["mcp"], frag.get("mcp", frag))
    if local_model:
        frag = load_tool_config("crush", "local.providers.json")
        providers = frag.get("providers")
        if providers:
            base.setdefault("providers", {})
            deep_merge(base["providers"], providers)
    return substitute_env(base, strict=strict_env)


def generate_config(tool: Tool, include_snowflake: bool, use_local_model: bool) -> bool:
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task("Building configuration", total=None)
            cfg = tool.config_builder(include_snowflake, strict_env=include_snowflake, local_model=use_local_model)
            out_path = APP_HOME / tool.output_config
            write_json(out_path, cfg)
        good(f"Configuration written to {out_path}")
        return True
    except Exception as ex:  # pragma: no cover - runtime errors
        err(f"Configuration generation failed: {ex}")
        return False


# ---------------------------------------------------------------------------
# Main workflow
# ---------------------------------------------------------------------------


def local_model_menu() -> bool:
    section("Model provider selection")
    choice = Prompt.ask(
        "Use locally hosted model (LM Studio)?",
        choices=["y", "n"],
        default="n",
    )
    return choice == "y"


def course_menu() -> str:
    section("Navigation course selection")
    console.print("1. Connect to Snowflake (for large-scale data)")
    console.print("2. Analyze local files (CSVs, Excel)")
    return Prompt.ask("Select course", choices=["1", "2"], default="2")


def remove_local_duckdb() -> None:
    db_path = APP_HOME / "adtech.duckdb"
    try:
        if db_path.exists():
            db_path.unlink()
            info(f"Removed local database: {db_path}")
    except Exception as exc:  # pragma: no cover - best effort cleanup
        warn(f"Could not remove {db_path}: {exc}")


def open_victoria_folder() -> None:
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
    output_config="crush.json",
    config_builder=build_crush_config,
    preflight=preflight_crush,
    launcher=launch_crush,
)


def main(
    _parse_args: Callable = parse_args,
    _ensure_default_files: Callable = ensure_default_files,
    _banner: Callable = banner,
    _local_model_menu: Callable = local_model_menu,
    _remove_local_duckdb: Callable = remove_local_duckdb,
    _course_menu: Callable = course_menu,
    _snowflake_env_missing: Callable = snowflake_env_missing,
    _generate_config: Callable = generate_config,
    _open_victoria_folder: Callable = open_victoria_folder,
    _console: Console = console,
    _err: Callable[[str], None] = err,
    _info: Callable[[str], None] = info,
) -> None:
    if not SETUP_SENTINEL.exists():
        _err("First-time setup has not been completed. Please run the Victoria Configurator first.")
        sys.exit(1)

    args = _parse_args()

    if args.quiet:
        _info = lambda msg: None

    _ensure_default_files()
    _console.clear()
    _banner()

    tool = TOOL

    use_local_model = args.local_model if args.local_model is not None else _local_model_menu()

    _remove_local_duckdb()
    _info(f"Place files to analyze in: {APP_HOME}")

    tool.preflight(tool, use_local_model)

    choice = str(args.course) if args.course else _course_menu()
    if choice == "1":
        missing = _snowflake_env_missing()
        if missing:
            _err("Missing Snowflake environment variables:")
            for v in missing:
                _console.print(f"  [red]{v}")
            sys.exit(1)
        if not _generate_config(tool, True, use_local_model):
            sys.exit(1)
    else:
        if not _generate_config(tool, False, use_local_model):
            sys.exit(1)

    if not args.quiet:
        _open_victoria_folder()

    tool.launcher(tool)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:  # pragma: no cover - user interaction
        console.print(f"\n[yellow]Voyage cancelled. Fair winds!")
        sys.exit(130)
