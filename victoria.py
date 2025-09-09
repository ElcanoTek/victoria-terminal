#!/usr/bin/env python3
"""Victoria - AdTech Data Navigation

Simplified cross-platform launcher for the Victoria data toolkit.  It detects
required tools, builds a configuration file from templates and environment
variables, then launches the chosen data exploration mode.
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
from typing import Dict, Any, Callable, List

from colorama import init as colorama_init
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

# ---------------------------------------------------------------------------
# Basic setup
# ---------------------------------------------------------------------------

VICTORIA_FILE = "VICTORIA.md"
CONFIGS_DIR = Path("configs")

home_dir = os.path.expanduser("~")
APP_HOME = Path(home_dir) / "Victoria"
APP_HOME.mkdir(exist_ok=True)
os.environ.setdefault("VICTORIA_HOME", str(APP_HOME))
SETUP_SENTINEL = APP_HOME / ".first_run_complete"

colorama_init()  # Enable ANSI colors on Windows
console = Console()

# ---------------------------------------------------------------------------
# Messaging
# ---------------------------------------------------------------------------

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

def section(title: str) -> None:
    console.rule(f"[bold yellow]{title}")

def banner() -> None:
    console.print(Panel.fit(
        "[bold cyan]VICTORIA[/bold cyan]\n[cyan]AdTech Data Navigation[/cyan]",
        border_style="cyan"))

def restart_app(
    _sys_executable: str = sys.executable,
    _sys_argv: list[str] = sys.argv,
    _os_name: str = os.name,
    _os_execv: Callable[..., None] = os.execv,
    _subprocess_Popen: Callable[..., Any] = subprocess.Popen,
    _sys_exit: Callable[[int], None] = sys.exit,
    _info: Callable[[str], None] = info,
) -> None:
    """Restart the application to apply changes to the environment."""
    _info("Prerequisites installed. Restarting Victoria to apply changes...")
    if _os_name == "nt":
        # On Windows, Popen is used to launch a new instance of the app.
        # The new process runs independently. We then exit the current process.
        _subprocess_Popen(_sys_argv)
        _sys_exit(0)
    else:
        # On macOS/Linux, execv replaces the current process with a new one,
        # inheriting the same process ID.
        _os_execv(_sys_executable, _sys_argv)


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
    preflight: Callable[[Tool, bool, bool], None]
    launcher: Callable[[Tool], None]


def preflight_crush(
    tool: Tool,
    use_local_model: bool,
    just_installed: bool,
    _which: Callable[[str], str | None] = shutil.which,
    _os_environ: dict = os.environ,
    _info: Callable[[str], None] = info,
    _good: Callable[[str], None] = good,
    _warn: Callable[[str], None] = warn,
    _err: Callable[[str], None] = err,
    _sys_exit: Callable[[int], None] = sys.exit,
    _section: Callable[[str], None] = section,
    _Progress: type = Progress,
    _restart_app: Callable[[], None] = restart_app,
) -> None:
    _section("System preflight check")
    with _Progress(SpinnerColumn(), TextColumn("{task.description}"), transient=True) as progress:
        progress.add_task("Verifying prerequisites", total=None)
        if _which(tool.command) is None:
            if just_installed:
                _restart_app()
            _err(f"Missing '{tool.command}' command-line tool. Run first-time setup or install it manually.")
            _sys_exit(1)
    _good(f"{tool.command} CLI tool detected")
    has_key = bool(_os_environ.get("OPENROUTER_API_KEY"))
    if not use_local_model and not has_key:
        _warn("OPENROUTER_API_KEY not configured. Email brad@elcanotek.com to obtain one.")
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
        _err(f"'{tool.command}' command not found in PATH")
        _sys_exit(1)
    except Exception as exc:  # pragma: no cover - runtime errors
        _err(f"Failed to launch {tool.name}: {exc}")
        _sys_exit(1)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def resource_path(name: str | Path) -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base / name

def ensure_default_files(
    _APP_HOME: Path = APP_HOME,
    _CONFIGS_DIR: Path = CONFIGS_DIR,
    _VICTORIA_FILE: str = VICTORIA_FILE,
    _resource_path: Callable[[str | Path], Path] = resource_path,
    _shutil_copy: Callable[[Path, Path], None] = shutil.copy,
) -> None:
    crush_dir = _CONFIGS_DIR / "crush"
    files = [
        (crush_dir / ".crushignore", ".crushignore"),
        (crush_dir / "CRUSH.md", "CRUSH.md"),
        (Path(_VICTORIA_FILE), _VICTORIA_FILE),
    ]
    for rel_path, fname in files:
        src = _resource_path(rel_path)
        dst = _APP_HOME / fname
        if src.exists() and not dst.exists():
            _shutil_copy(src, dst)

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Victoria launcher")
    return parser.parse_args()

# ---------------------------------------------------------------------------
# First-time setup
# ---------------------------------------------------------------------------

def run_setup_scripts(
    use_local_model: bool,
    _resource_path: Callable[[str | Path], Path] = resource_path,
    _subprocess_run: Callable[..., subprocess.CompletedProcess] = subprocess.run,
    _err: Callable[[str], None] = err,
    _info: Callable[[str], None] = info,
    _warn: Callable[[str], None] = warn,
    _os_name: str = os.name,
    _sys_platform: str = sys.platform,
) -> None:
    deps = _resource_path("dependencies")
    if use_local_model:
        _info("Running setup without OpenRouter API key")
    if _os_name == "nt":
        scripts = ["install_prerequisites_windows.ps1", "set_env_windows.ps1"]
        for s in scripts:
            script = deps / s
            cmd = [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                (
                    f"Unblock-File -Path '{script}' -ErrorAction SilentlyContinue; "
                    f"& '{script}'"
                    f"{' -SkipOpenRouter' if use_local_model and s.startswith('set_env') else ''}"
                ),
            ]
            try:
                _subprocess_run(cmd, check=True)
            except Exception as exc:
                _err(f"Setup script failed: {exc}")
                break
    elif _sys_platform == "darwin":
        scripts = ["install_prerequisites_macos.sh", "set_env_macos_linux.sh"]
        for s in scripts:
            try:
                cmd = ["bash", str(deps / s)]
                if use_local_model and s.startswith("set_env"):
                    cmd.append("--skip-openrouter")
                _subprocess_run(cmd, check=True)
            except Exception as exc:
                _err(f"Setup script failed: {exc}")
                break
    elif _sys_platform.startswith("linux"):
        scripts = ["install_prerequisites_linux.sh", "set_env_macos_linux.sh"]
        for s in scripts:
            try:
                cmd = ["bash", str(deps / s)]
                if use_local_model and s.startswith("set_env"):
                    cmd.append("--skip-openrouter")
                _subprocess_run(cmd, check=True)
            except Exception as exc:
                _err(f"Setup script failed: {exc}")
                break
    else:
        _warn("Unsupported platform; run setup scripts manually from the dependencies folder.")
        return

def first_run_check(
    use_local_model: bool,
    _run_setup_scripts: Callable[[bool], None] = run_setup_scripts,
    _SETUP_SENTINEL: Path = SETUP_SENTINEL,
    _Prompt_ask: Callable[..., str] = Prompt.ask,
    _section: Callable[[str], None] = section,
) -> bool:
    if _SETUP_SENTINEL.exists():
        return False
    _section("First-time setup")
    if _Prompt_ask("Run first-time setup?", choices=["y", "n"], default="y") == "y":
        _run_setup_scripts(use_local_model)
        try:
            _SETUP_SENTINEL.write_text("done")
        except Exception:
            pass
        return True
    return False

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
    path_res = resource_path(CONFIGS_DIR / tool / name)
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
# Preflight and launch
# ---------------------------------------------------------------------------

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
    console.print("1. Full ocean expedition (Snowflake)")
    console.print("2. Coastal navigation (local files)")
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


TOOLS: Dict[str, Tool] = {
    "crush": Tool(
        name="Crush",
        command="crush",
        output_config="crush.json",
        config_builder=build_crush_config,
        preflight=preflight_crush,
        launcher=launch_crush,
    ),
}


def main(
    _parse_args: Callable = parse_args,
    _ensure_default_files: Callable = ensure_default_files,
    _banner: Callable = banner,
    _local_model_menu: Callable = local_model_menu,
    _first_run_check: Callable = first_run_check,
    _remove_local_duckdb: Callable = remove_local_duckdb,
    _course_menu: Callable = course_menu,
    _snowflake_env_missing: Callable = snowflake_env_missing,
    _generate_config: Callable = generate_config,
    _open_victoria_folder: Callable = open_victoria_folder,
    _console: Console = console,
    _err: Callable[[str], None] = err,
) -> None:
    _parse_args()
    _ensure_default_files()
    _console.clear()
    _banner()

    # For now, we'll default to the first tool, crush.
    # In the future, we could add a tool selection menu here.
    tool = TOOLS["crush"]

    use_local_model = _local_model_menu()
    just_installed = _first_run_check(use_local_model)
    _remove_local_duckdb()
    _console.print(f"[cyan]{ICONS['folder']} Place files to analyze in: [white]{APP_HOME}")

    tool.preflight(tool, use_local_model, just_installed)

    choice = _course_menu()
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
    _open_victoria_folder()
    tool.launcher(tool)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:  # pragma: no cover - user interaction
        console.print(f"\n[yellow]{ICONS['anchor']} Voyage cancelled. Fair winds!")
        sys.exit(130)
