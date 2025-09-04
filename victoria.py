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
from pathlib import Path
from typing import Dict, Any, Callable

from colorama import init as colorama_init
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

# ---------------------------------------------------------------------------
# Basic setup
# ---------------------------------------------------------------------------

VICTORIA_FILE = "VICTORIA.md"
TOOL_CMD = os.environ.get("VICTORIA_TOOL", "crush")
OUTPUT_CONFIG = os.environ.get("VICTORIA_OUTPUT", f"{TOOL_CMD}.json")
CONFIGS_DIR = Path("configs")

APP_HOME = Path.home() / "Victoria"
APP_HOME.mkdir(exist_ok=True)
os.environ.setdefault("VICTORIA_HOME", str(APP_HOME))
SETUP_SENTINEL = APP_HOME / ".first_run_complete"

colorama_init()  # Enable ANSI colors on Windows
console = Console()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def resource_path(name: str | Path) -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base / name

def ensure_default_files() -> None:
    crush_dir = CONFIGS_DIR / "crush"
    files = [
        (crush_dir / ".crushignore", ".crushignore"),
        (crush_dir / "CRUSH.md", "CRUSH.md"),
        (Path(VICTORIA_FILE), VICTORIA_FILE),
    ]
    for rel_path, fname in files:
        src = resource_path(rel_path)
        dst = APP_HOME / fname
        if src.exists() and not dst.exists():
            shutil.copy(src, dst)

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Victoria launcher")
    return parser.parse_args()

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

# ---------------------------------------------------------------------------
# First-time setup
# ---------------------------------------------------------------------------

def run_setup_scripts() -> None:
    deps = resource_path("dependencies")
    if os.name == "nt":
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
                ),
            ]
            try:
                subprocess.run(cmd, check=True)
            except Exception as exc:
                err(f"Setup script failed: {exc}")
                break
    elif sys.platform == "darwin":
        scripts = ["install_prerequisites_macos.sh", "set_env_macos_linux.sh"]
        for s in scripts:
            try:
                subprocess.run(["bash", str(deps / s)], check=True)
            except Exception as exc:
                err(f"Setup script failed: {exc}")
                break
    elif sys.platform.startswith("linux"):
        scripts = ["install_prerequisites_linux.sh", "set_env_macos_linux.sh"]
        for s in scripts:
            try:
                subprocess.run(["bash", str(deps / s)], check=True)
            except Exception as exc:
                err(f"Setup script failed: {exc}")
                break
    else:
        warn("Unsupported platform; run setup scripts manually from the dependencies folder.")
        return

def first_run_check() -> None:
    if SETUP_SENTINEL.exists():
        return
    section("First-time setup")
    if Prompt.ask("Run first-time setup?", choices=["y", "n"], default="y") == "y":
        run_setup_scripts()
        try:
            SETUP_SENTINEL.write_text("done")
        except Exception:
            pass

# ---------------------------------------------------------------------------
# Terminal helpers (minimal implementation for tests)
# ---------------------------------------------------------------------------

def detect_terminal_capabilities() -> Dict[str, Any]:
    return {
        "colors": True,
        "emojis": True,
        "unicode_box": True,
        "colors_256": True,
        "is_tty": sys.stdout.isatty(),
    }


def get_terminal_width() -> int:
    return shutil.get_terminal_size(fallback=(80, 24)).columns

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


CONFIG_BUILDERS: Dict[str, Callable[[bool, bool, bool], Dict[str, Any]]] = {
    "crush": build_crush_config,
}


def build_config(tool: str, include_snowflake: bool, strict_env: bool, local_model: bool) -> Dict[str, Any]:
    builder = CONFIG_BUILDERS.get(tool)
    if not builder:
        raise ValueError(f"Unsupported tool: {tool}")
    return builder(include_snowflake, strict_env, local_model)

def generate_config(include_snowflake: bool, use_local_model: bool) -> bool:
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task("Building configuration", total=None)
            cfg = build_config(TOOL_CMD, include_snowflake, strict_env=include_snowflake, local_model=use_local_model)
            out_path = APP_HOME / OUTPUT_CONFIG
            write_json(out_path, cfg)
        good(f"Configuration written to {out_path}")
        return True
    except Exception as ex:  # pragma: no cover - runtime errors
        err(f"Configuration generation failed: {ex}")
        return False

# ---------------------------------------------------------------------------
# Preflight and launch
# ---------------------------------------------------------------------------

def which(cmd: str) -> str | None:
    return shutil.which(cmd)

def preflight(use_local_model: bool) -> None:
    section("System preflight check")
    with Progress(SpinnerColumn(), TextColumn("{task.description}"), transient=True) as progress:
        progress.add_task("Verifying prerequisites", total=None)
        if which(TOOL_CMD) is None:
            err(f"Missing '{TOOL_CMD}' command-line tool")
            sys.exit(1)
        if not use_local_model and not os.environ.get("OPENROUTER_API_KEY"):
            err("OPENROUTER_API_KEY not configured")
            sys.exit(1)
    good(f"{TOOL_CMD} CLI tool detected")
    if use_local_model:
        good("Local model provider selected")
    else:
        good("OpenRouter API key configured")
    good("All systems ready")

def launch_tool() -> None:
    section("Mission launch")
    info(f"Launching {TOOL_CMD}...")
    cmd = [TOOL_CMD, "-c", str(APP_HOME)]
    try:
        if os.name == "nt":
            proc = subprocess.run(cmd)
            if proc.returncode != 0:
                err(f"{TOOL_CMD} exited with {proc.returncode}")
                sys.exit(proc.returncode)
        else:
            os.execvp(TOOL_CMD, cmd)
    except FileNotFoundError:
        err(f"'{TOOL_CMD}' command not found in PATH")
        sys.exit(1)
    except Exception as exc:  # pragma: no cover - runtime errors
        err(f"Failed to launch {TOOL_CMD}: {exc}")
        sys.exit(1)

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

def main() -> None:
    parse_args()
    ensure_default_files()
    console.clear()
    banner()
    first_run_check()
    remove_local_duckdb()
    console.print(f"[cyan]{ICONS['folder']} Place files to analyze in: [white]{APP_HOME}")
    use_local_model = local_model_menu()
    preflight(use_local_model)
    choice = course_menu()
    if choice == "1":
        missing = snowflake_env_missing()
        if missing:
            err("Missing Snowflake environment variables:")
            for v in missing:
                console.print(f"  [red]{v}")
            sys.exit(1)
        if not generate_config(True, use_local_model):
            sys.exit(1)
    else:
        if not generate_config(False, use_local_model):
            sys.exit(1)
    open_victoria_folder()
    launch_tool()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:  # pragma: no cover - user interaction
        console.print(f"\n[yellow]{ICONS['anchor']} Voyage cancelled. Fair winds!")
        sys.exit(130)
