#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Victoria - AdTech Data Navigation (Cross-platform Python launcher, pretty version)

- Auto-detects Snowflake env; falls back to local if incomplete
- Merges a JSON template (default `crush.template.json`) with `snowflake.mcp.json`
- Replaces ${ENV_VAR} tokens from the environment (cross-platform)
- Writes UTF-8 without BOM
- Cross-platform terminal compatibility with graceful degradation
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
import platform

# ------------------ Config ------------------
VICTORIA_FILE     = "VICTORIA.md"

# Launch command is configurable to allow swapping out crush later
TOOL_CMD = os.environ.get("VICTORIA_TOOL", "crush")
CONFIG_TEMPLATE = os.environ.get("VICTORIA_TEMPLATE", "crush.template.json")
SNOWFLAKE_FRAG  = "snowflake.mcp.json"
OUTPUT_CONFIG   = os.environ.get("VICTORIA_OUTPUT", f"{TOOL_CMD}.json")

APP_HOME = Path.home() / "Victoria"
APP_HOME.mkdir(exist_ok=True)
os.environ.setdefault("VICTORIA_HOME", str(APP_HOME))

def resource_path(name: str) -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base / name

def ensure_default_files():
    for fname in [".crushignore", "CRUSH.md", VICTORIA_FILE]:
        src = resource_path(fname)
        dst = APP_HOME / fname
        if src.exists() and not dst.exists():
            shutil.copy(src, dst)


def parse_args():
    parser = argparse.ArgumentParser(description="Victoria launcher")
    return parser.parse_args()

SNOWFLAKE_ENV_VARS = [
    "SNOWFLAKE_ACCOUNT",
    "SNOWFLAKE_USER",
    "SNOWFLAKE_PASSWORD",
    "SNOWFLAKE_WAREHOUSE",
    "SNOWFLAKE_ROLE",
]

# ------------------ Terminal Capability Detection ------------------
def _enable_windows_ansi():
    """Best-effort enable ANSI on Windows without external deps."""
    if os.name != "nt":
        return True
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        h = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE = -11
        mode = ctypes.c_uint32()
        if kernel32.GetConsoleMode(h, ctypes.byref(mode)):
            ENABLE_VTP = 0x0004
            success = kernel32.SetConsoleMode(h, mode.value | ENABLE_VTP)
            return bool(success)
    except Exception:
        pass
    return False

def detect_terminal_capabilities():
    """Detect what the current terminal can handle."""
    caps = {
        'colors': False,
        'emojis': False,
        'unicode_box': False,
        'colors_256': False,
        'is_tty': sys.stdout.isatty()
    }
    
    if not caps['is_tty']:
        return caps
    
    # Check if we can enable ANSI on Windows
    ansi_enabled = _enable_windows_ansi()
    
    # Basic color support
    term = os.environ.get('TERM', '').lower()
    colorterm = os.environ.get('COLORTERM', '').lower()
    
    # Check for color support
    if (ansi_enabled or os.name != 'nt' or 
        'color' in term or 'ansi' in term or 
        'xterm' in term or 'screen' in term or
        colorterm in ('truecolor', '24bit')):
        caps['colors'] = True
        
        # 256 color support
        if ('256' in term or 'xterm' in term or 
            colorterm in ('truecolor', '24bit') or
            os.environ.get('TERM_PROGRAM') in ('vscode', 'hyper', 'iterm')):
            caps['colors_256'] = True
    
    # Emoji support detection (heuristic)
    if (platform.system() == 'Darwin' or  # macOS generally supports emojis
        os.environ.get('TERM_PROGRAM') in ('vscode', 'hyper', 'iterm', 'wt') or  # Modern terminals
        'unicode' in os.environ.get('LANG', '').lower() or
        'utf-8' in os.environ.get('LANG', '').lower() or
        'utf8' in os.environ.get('LANG', '').lower()):
        caps['emojis'] = True
    
    # Unicode box drawing support (similar to emoji detection)
    caps['unicode_box'] = caps['emojis']  # Usually go together
    
    # Windows Terminal specific detection
    if os.name == 'nt' and os.environ.get('WT_SESSION'):
        caps['colors'] = True
        caps['colors_256'] = True
        caps['emojis'] = True
        caps['unicode_box'] = True
    
    return caps

def get_terminal_width():
    """Return a sensible terminal width.

    Some CI environments define the COLUMNS environment variable as 0 which
    causes ``os.get_terminal_size`` to return ``0``.  That value propagates to
    tests expecting a positive width and triggers failures.  We treat any width
    less than or equal to zero as missing and fall back to a default.
    """
    try:
        width = shutil.get_terminal_size(fallback=(80, 24)).columns
        return width if width > 0 else 80
    except Exception:
        return 80

# Initialize terminal capabilities
TERM_CAPS = detect_terminal_capabilities()

class T:
    _tty = TERM_CAPS['is_tty']
    _width = get_terminal_width()
    
    # Basic colors (16-color compatible)
    if TERM_CAPS['colors']:
        RED     = "\033[0;31m"
        GREEN   = "\033[0;32m"
        YELLOW  = "\033[1;33m"
        BLUE    = "\033[0;34m"
        MAGENTA = "\033[0;35m"
        CYAN    = "\033[0;36m"
        WHITE   = "\033[1;37m"
        
        # Enhanced colors if 256-color support
        if TERM_CAPS['colors_256']:
            RED     = "\033[38;5;196m"
            GREEN   = "\033[38;5;46m"
            YELLOW  = "\033[38;5;226m"
            BLUE    = "\033[38;5;39m"
            MAGENTA = "\033[38;5;201m"
            CYAN    = "\033[38;5;51m"
            WHITE   = "\033[38;5;231m"
            CYAN_LIGHT = "\033[38;5;87m"
            CYAN_DARK  = "\033[38;5;23m"
        else:
            CYAN_LIGHT = "\033[0;36m"
            CYAN_DARK  = "\033[0;36m"
            
        DIM     = "\033[2m"
        BOLD    = "\033[1m"
        ITALIC  = "\033[3m"
        UNDER   = "\033[4m"
        NC      = "\033[0m"
    else:
        # No color support
        RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = ""
        CYAN_LIGHT = CYAN_DARK = DIM = BOLD = ITALIC = UNDER = NC = ""
    
    # Emojis with ASCII fallbacks
    if TERM_CAPS['emojis']:
        SHIP      = "🚢"
        WAVE      = "🌊"
        COMPASS   = "🧭"
        SPARKLES  = "✨"
        ROCKET    = "🚀"
        CHECK     = "✅"
        WARN      = "⚠️"
        ERROR     = "❌"
        GEAR      = "⚙️"
        BOOK      = "📘"
        MAG       = "🔍"
        ANCHOR    = "⚓"
        STAR      = "⭐"
        CROWN     = "👑"
        TELESCOPE = "🔭"
        MAP       = "🗺️"
        KEY       = "🗝️"
        FIRE      = "🔥"
        TARGET    = "🎯"
        CHART     = "📊"
        FOLDER    = "📁"
        LIGHTNING = "⚡"
        SHIELD    = "🛡️"
        WRENCH    = "🔧"
        PACKAGE   = "📦"
        HOME      = "🏠"
        PIRATE    = "🏴‍☠️"
        CYCLONE   = "🌀"
    else:
        # ASCII fallbacks
        SHIP      = "[SHIP]"
        WAVE      = "~"
        COMPASS   = "[NAV]"
        SPARKLES  = "*"
        ROCKET    = ">>>"
        CHECK     = "[OK]"
        WARN      = "[!]"
        ERROR     = "[X]"
        GEAR      = "[*]"
        BOOK      = "[DOC]"
        MAG       = "(?)"
        ANCHOR    = "[#]"
        STAR      = "*"
        CROWN     = "[^]"
        TELESCOPE = "[o]"
        MAP       = "[MAP]"
        KEY       = "[KEY]"
        FIRE      = "[!]"
        TARGET    = "[+]"
        CHART     = "[CHT]"
        FOLDER    = "[DIR]"
        LIGHTNING = "[!]"
        SHIELD    = "[#]"
        WRENCH    = "[+]"
        PACKAGE   = "[PKG]"
        HOME      = "[HOME]"
        PIRATE    = "[PIRATE]"
        CYCLONE   = "[~]"

def clear_screen():
    try:
        os.system("cls" if os.name == "nt" else "clear")
    except Exception:
        pass

def which(cmd: str) -> Optional[str]:
    return shutil.which(cmd)

def info(msg: str):  print(f"{T.CYAN}[i] {msg}{T.NC}")
def good(msg: str):  print(f"{T.GREEN}{T.CHECK} {msg}{T.NC}")
def warn(msg: str):  print(f"{T.YELLOW}{T.WARN} {msg}{T.NC}")
def err(msg: str):   print(f"{T.RED}{T.ERROR} {msg}{T.NC}")
def dim(msg: str):   print(f"{T.DIM}    {msg}{T.NC}")

def progress_bar(progress: float, width: int = 40, style: str = "blocks") -> str:
    """Create a progress bar that works across all terminals."""
    filled = int(progress * width)
    
    if style == "ocean" and TERM_CAPS['emojis']:
        bar = T.WAVE * filled + "." * (width - filled)
        return f"[{bar}] {progress*100:5.1f}%"
    elif style == "ship" and TERM_CAPS['emojis']:
        pos = int(progress * (width - 1))
        bar = "~" * pos + T.SHIP + "~" * max(0, width - pos - 1)
        return f"[{T.BLUE}{bar}{T.NC}] {progress*100:5.1f}%"
    else:  # ASCII blocks - works everywhere
        filled_char = "#" if not TERM_CAPS['unicode_box'] else "█"
        empty_char = "." if not TERM_CAPS['unicode_box'] else "░"
        bar = filled_char * filled + empty_char * (width - filled)
        return f"[{T.CYAN}{bar}{T.NC}] {progress*100:5.1f}%"

def ship_loading_animation(message: str, duration: float = 3.0):
    """Cross-platform loading animation with graceful degradation."""
    if not T._tty:
        print(f"{T.SHIP} {message}")
        time.sleep(duration)
        return
    
    if TERM_CAPS['emojis']:
        phases = [
            (f"{T.HOME} Preparing to set sail...", 0.3),
            (f"{T.ANCHOR} Raising anchor...", 0.4),
            (f"{T.WAVE} Entering open waters...", 0.5),
            (f"{T.COMPASS} Navigating the data seas...", 0.8),
            (f"{T.PIRATE} Discovering treasure...", 0.6),
            (f"{T.SHIP} Approaching destination...", 0.4),
        ]
    else:
        phases = [
            ("[PREP] Preparing to set sail...", 0.3),
            ("[LIFT] Raising anchor...", 0.4),
            ("[SAIL] Entering open waters...", 0.5),
            ("[NAV]  Navigating the data seas...", 0.8),
            ("[FIND] Discovering treasure...", 0.6),
            ("[DOCK] Approaching destination...", 0.4),
        ]
    
    total_phases = len(phases)
    
    for i, (phase_msg, phase_duration) in enumerate(phases):
        phase_progress = (i + 1) / total_phases
        
        # Animate this phase
        steps = max(3, int(phase_duration * 5))  # Reduced for compatibility
        for step in range(steps):
            step_progress = (i + (step / steps)) / total_phases
            
            # Simple wave animation
            if TERM_CAPS['emojis']:
                wave_chars = [T.WAVE, "~", "~", "~"]
                wave_offset = int((time.time() * 2) % len(wave_chars))
                waves = wave_chars[wave_offset] * 3
            else:
                wave_chars = ["~", "-", "=", "-"]
                wave_offset = int((time.time() * 2) % len(wave_chars))
                waves = wave_chars[wave_offset] * 3
            
            # Display
            sys.stdout.write(f"\r{T.CYAN}{waves}{T.NC} {phase_msg}")
            sys.stdout.write(f" {progress_bar(step_progress, 20, 'blocks')}")
            sys.stdout.flush()
            
            time.sleep(phase_duration / steps)
    
    # Final completion
    sys.stdout.write(f"\r{T.GREEN}{T.STAR} {message} - Complete!{T.NC}")
    sys.stdout.write(" " * 20)  # Clear remaining chars
    print()

def typewriter_effect(text: str, delay: float = 0.03):
    """Simulate typing effect - gracefully degrades to instant print."""
    if not T._tty or not TERM_CAPS['colors']:
        print(text)
        return
        
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def enhanced_spinner(message: str, duration: float = 1.0):
    """Cross-platform spinner with ASCII fallbacks."""
    if not T._tty:
        print(f"{message}")
        time.sleep(duration)
        return
    
    if TERM_CAPS['emojis']:
        frames = [T.WAVE, T.CYCLONE, T.ANCHOR, T.COMPASS, T.STAR, T.SHIP]
    else:
        frames = ["|", "/", "-", "\\", "*", "+"]
    
    start = time.time()
    i = 0
    while time.time() - start < duration:
        frame = frames[i % len(frames)]
        progress = (time.time() - start) / duration
        dots = "." * ((i % 3) + 1)
        
        sys.stdout.write(f"\r{T.CYAN}{frame}{T.NC} {message}{dots} {T.DIM}({progress*100:3.0f}%){T.NC}")
        sys.stdout.flush()
        time.sleep(0.15)
        i += 1
    
    sys.stdout.write(f"\r{T.GREEN}{T.CHECK}{T.NC} {message} complete!")
    sys.stdout.write(" " * 20)
    print()

def banner():
    """Minimal banner without borders or centering."""
    if TERM_CAPS['emojis']:
        print(f"{T.CYAN}{T.BOLD}{T.SHIP} VICTORIA {T.WAVE} ADTECH DATA NAVIGATION {T.SPARKLES}{T.NC}")
        print(f"{T.CYAN_LIGHT}\"Charting the Digital Seas of Programmatic Advertising\"{T.NC}")
    else:
        print(f"{T.CYAN}{T.BOLD}VICTORIA - ADTECH DATA NAVIGATION{T.NC}")
        print(f"{T.CYAN}\"Charting the Digital Seas of Programmatic Advertising\"{T.NC}")

    if TERM_CAPS['unicode_box']:
        ascii_art = [
            "██╗   ██╗██╗ ██████╗████████╗ ██████╗ ██████╗ ██╗ █████╗",
            "██║   ██║██║██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗██║██╔══██╗",
            "██║   ██║██║██║        ██║   ██║   ██║██████╔╝██║███████║",
            "╚██╗ ██╔╝██║██║        ██║   ██║   ██║██╔══██╗██║██╔══██║",
            " ╚████╔╝ ██║╚██████╗   ██║   ╚██████╔╝██║  ██║██║██║  ██║",
            "  ╚═══╝  ╚═╝ ╚═════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝",
        ]
    else:
        ascii_art = [
            "V I C T O R I A - D A T A - N A V I G A T O R",
            "Your AdTech Analytics Command Center",
        ]
    for line in ascii_art:
        print(f"{T.CYAN}{line}{T.NC}")
    print()

    print(f"{T.GREEN}{T.FIRE} System Status{T.NC}")
    print(f"{T.GREEN}{T.LIGHTNING} Engine: {T.WHITE}Online{T.NC}")
    print(f"{T.BLUE}{T.COMPASS} Navigation: {T.WHITE}Ready{T.NC}")
    print(f"{T.MAGENTA}{T.GEAR} AI Systems: {T.WHITE}Activated{T.NC}")
    print()

def section_header(title: str, icon: str = None) -> None:
    """Simple section header without borders."""
    icon = icon or T.TARGET
    print(f"\n{T.YELLOW}{icon} {title.upper()}{T.NC}")
    print(f"{T.YELLOW}{'-' * len(title)}{T.NC}")

def success_animation(message: str):
    """Cross-platform success message."""
    if not T._tty or not TERM_CAPS['colors']:
        print(f"{T.CHECK} {message}")
        return
        
    # Simple sparkle animation
    for i in range(3):
        if TERM_CAPS['emojis']:
            sparkles = T.SPARKLES * (i + 1)
            sys.stdout.write(f"\r{T.GREEN}{sparkles} {message} {sparkles}{T.NC}")
        else:
            stars = "*" * (i + 1)
            sys.stdout.write(f"\r{T.GREEN}{stars} {message} {stars}{T.NC}")
        sys.stdout.flush()
        time.sleep(0.3)
    
    print(f"\n{T.GREEN}{T.ROCKET} SUCCESS! {message}{T.NC}")

# ------------------ JSON I/O (unchanged) ------------------
def read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)

def write_json(path: Path, obj: Dict[str, Any]):
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
        def repl(m):
            var = m.group(1)
            val = os.environ.get(var)
            if val is None:
                if strict:
                    raise KeyError(f"Environment variable {var} is required but not set")
                return m.group(0)
            return val
        return _env_token.sub(repl, obj)
    return obj

# ------------------ Config generation ------------------
def snowflake_env_missing() -> List[str]:
    return [v for v in SNOWFLAKE_ENV_VARS if not os.environ.get(v)]

def load_base_template() -> Dict[str, Any]:
    path_home = APP_HOME / CONFIG_TEMPLATE
    path = path_home if path_home.exists() else resource_path(CONFIG_TEMPLATE)
    if not path.exists():
        raise FileNotFoundError(f"Missing {CONFIG_TEMPLATE}")
    return read_json(path)

def load_snowflake_fragment() -> Dict[str, Any]:
    path_home = APP_HOME / SNOWFLAKE_FRAG
    path = path_home if path_home.exists() else resource_path(SNOWFLAKE_FRAG)
    if not path.exists():
        raise FileNotFoundError(f"Missing {SNOWFLAKE_FRAG}")
    return read_json(path)

def build_config(include_snowflake: bool, strict_env: bool) -> Dict[str, Any]:
    base = load_base_template()
    if include_snowflake:
        frag = load_snowflake_fragment()
        base.setdefault("mcp", {})
        if "mcp" in frag and isinstance(frag["mcp"], dict):
            deep_merge(base["mcp"], frag["mcp"])
        else:
            deep_merge(base["mcp"], frag)
    return substitute_env(base, strict=strict_env)

def generate_config(include_snowflake: bool) -> bool:
    try:
        ship_loading_animation("Generating navigation configuration", 2.0)
        cfg = build_config(include_snowflake, strict_env=include_snowflake)
        out_path = APP_HOME / OUTPUT_CONFIG
        write_json(out_path, cfg)
        success_animation(f"Configuration written to {out_path}")
        return True
    except Exception as ex:
        err(f"Configuration generation failed: {ex}")
        return False


def generate_crush_config(include_snowflake: bool) -> bool:
    """Backwards compatibility wrapper."""
    return generate_config(include_snowflake)

# ------------------ Preflight & Launch ------------------
def preflight():
    section_header("SYSTEM PREFLIGHT CHECK", T.WRENCH)

    enhanced_spinner("Initializing navigation systems", 1.2)

    # Check tool availability
    if which(TOOL_CMD) is None:
        err(f"Missing '{TOOL_CMD}' command-line tool")
        print(f"\n{T.CYAN}{T.PACKAGE} Installation required{T.NC}")
        sys.exit(1)
    else:
        good(f"{TOOL_CMD} CLI tool detected")

    # Check API key
    if not os.environ.get("OPENROUTER_API_KEY"):
        err("OPENROUTER_API_KEY not configured")
        print(f"\n{T.YELLOW}{T.KEY} Set OPENROUTER_API_KEY in your environment{T.NC}")
        if os.name == "nt":
            print(f'{T.GREEN}[Environment]::SetEnvironmentVariable("OPENROUTER_API_KEY","your_key","User"){T.NC}')
        else:
            print(f'{T.GREEN}export OPENROUTER_API_KEY="your_api_key_here"{T.NC}')
        sys.exit(1)
    else:
        good("OpenRouter API key configured")

    success_animation("All systems ready for launch!")

def launch_tool():
    section_header("MISSION LAUNCH", T.ROCKET)

    ship_loading_animation(f"Preparing {TOOL_CMD} launch sequence", 2.0)

    print(f"\n{T.GREEN}{T.TARGET} Launching Victoria Data Navigator{T.NC}")

    try:
        cmd = [TOOL_CMD, "-c", str(APP_HOME)]
        if os.name == "nt":
            proc = subprocess.run(cmd)
            if proc.returncode != 0:
                err(f"{TOOL_CMD} exited with error code {proc.returncode}")
                sys.exit(proc.returncode)
        else:
            os.execvp(TOOL_CMD, cmd)
    except FileNotFoundError:
        err(f"'{TOOL_CMD}' command not found in PATH")
        sys.exit(1)
    except Exception as e:
        err(f"Failed to launch {TOOL_CMD}: {e}")
        sys.exit(1)


def launch_crush():
    """Backwards compatibility wrapper."""
    return launch_tool()

def course_menu() -> str:
    section_header("NAVIGATION COURSE SELECTION", T.COMPASS)

    enhanced_spinner("Booting navigation systems", 1.5)

    print(f"\n{T.BOLD}{T.WHITE}Choose your data exploration voyage:{T.NC}\n")

    print(f"{T.GREEN}{T.BOLD}[1]{T.NC} {T.WAVE} FULL OCEAN EXPEDITION")
    print(f"    {T.CYAN}{T.LIGHTNING} Enterprise Snowflake Database Access{T.NC}")
    print(f"    {T.CYAN}{T.CHART} Local CSV/Excel via MotherDuck{T.NC}")
    print(f"    {T.CYAN}{T.TARGET} Complete programmatic advertising analytics{T.NC}")
    print(f"    {T.CYAN}{T.FIRE} Maximum data exploration capabilities{T.NC}\n")

    print(f"{T.YELLOW}{T.BOLD}[2]{T.NC} {T.ANCHOR} COASTAL NAVIGATION")
    print(f"    {T.YELLOW}{T.FOLDER} Local CSV/Excel file analysis{T.NC}")
    print(f"    {T.YELLOW}{T.LIGHTNING} Fast startup, zero external dependencies{T.NC}")
    print(f"    {T.YELLOW}{T.MAG} Perfect for local data exploration{T.NC}")
    print(f"    {T.YELLOW}{T.SHIELD} Ideal for testing and development{T.NC}\n")

    while True:
        choice = input(f"{T.BOLD}{T.WHITE}{T.TARGET} Select your navigation course [1-2]: {T.NC}").strip()
        if choice in ("1", "2"):
            return choice
        warn("Invalid selection. Please choose 1 or 2.")

# ------------------ Main ------------------
def remove_local_duckdb():
    """Remove local DuckDB file to ensure a clean start."""
    db_path = APP_HOME / "adtech.duckdb"
    try:
        if db_path.exists():
            db_path.unlink()
            info(f"Removed local database: {db_path}")
        else:
            info(f"No local database found at {db_path}")
    except Exception as e:
        warn(f"Could not remove {db_path}: {e}")

def open_victoria_folder():
    """Open the Victoria data folder in the system file browser."""
    try:
        if os.name == "nt":
            os.startfile(str(APP_HOME))  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.run(["open", str(APP_HOME)], check=False)
        else:
            subprocess.run(["xdg-open", str(APP_HOME)], check=False)
    except Exception as e:
        warn(f"Could not open Victoria folder: {e}")

def main():
    parse_args()

    ensure_default_files()
    clear_screen()
    banner()
    remove_local_duckdb()

    print(f"{T.CYAN}{T.FOLDER} Place files to analyze in: {T.WHITE}{APP_HOME}{T.NC}")
    print(f"{T.DIM}file://{APP_HOME}{T.NC}")
    print(f"{T.GREEN}{T.ROCKET} Welcome to Victoria - Your AdTech Data Navigator!{T.NC}")
    
    # Show terminal capabilities for debugging (remove in production)
    if os.environ.get('VICTORIA_DEBUG'):
        print(f"{T.DIM}Debug: Terminal caps: {TERM_CAPS}{T.NC}")
    
    time.sleep(1)

    preflight()

    choice = course_menu()

    if choice == "1":
        section_header("FULL OCEAN EXPEDITION PREP", T.WAVE)
        
        enhanced_spinner("Checking Snowflake credentials", 1.0)
        
        missing = snowflake_env_missing()
        if missing:
            print(f"\n{T.RED}{T.WARN} NAVIGATION HAZARD DETECTED{T.NC}")
            warn("Missing required Snowflake environment variables:")
            for v in missing:
                print(f"   {T.RED}{T.ERROR} {v}{T.NC}")

            print(f"\n{T.CYAN}{T.WRENCH} REQUIRED CONFIGURATION:{T.NC}")
            env_vars = [
                'export SNOWFLAKE_ACCOUNT="your_account"',
                'export SNOWFLAKE_USER="your_username"',
                'export SNOWFLAKE_PASSWORD="your_password"',
                'export SNOWFLAKE_WAREHOUSE="your_warehouse"',
                'export SNOWFLAKE_ROLE="your_role"'
            ]
            for var in env_vars:
                if TERM_CAPS['colors']:
                    typewriter_effect(f"  {T.GREEN}{var}{T.NC}", 0.02)
                else:
                    print(f"  {var}")

            print(f"\n{T.MAGENTA}{T.BOOK} See SNOWFLAKE_INSTALL.md for detailed setup instructions{T.NC}")
            sys.exit(1)

        success_animation("Snowflake credentials validated!")
        
        if not generate_config(include_snowflake=True):
            sys.exit(1)

        print(f"\n{T.GREEN}{T.WAVE} FULL OCEAN EXPEDITION READY{T.NC}")
        print(f"{T.CYAN}Launching Victoria with complete data access...{T.NC}")
        open_victoria_folder()
        launch_tool()

    else:  # choice == "2"
        section_header("COASTAL NAVIGATION PREP", T.ANCHOR)
        
        print(f"\n{T.YELLOW}{T.ANCHOR} COASTAL NAVIGATION MODE SELECTED{T.NC}")
        info("Preparing for local data exploration...")
        
        enhanced_spinner("Configuring local data access", 1.5)
        
        if not generate_config(include_snowflake=False):
            sys.exit(1)

        success_animation("Local data configuration ready!")

        print(f"\n{T.CYAN}{T.ANCHOR} COASTAL NAVIGATION READY{T.NC}")
        print(f"{T.CYAN}Launching Victoria with local data access...{T.NC}")
        open_victoria_folder()
        launch_tool()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{T.YELLOW}{T.ANCHOR} Voyage cancelled by captain's orders.{T.NC}")
        print(f"{T.DIM}Fair winds and following seas! {T.WAVE}{T.NC}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{T.RED}{T.ERROR} Unexpected navigation error: {e}{T.NC}")
        print(f"{T.DIM}Check your charts and try again, Captain!{T.NC}")
        sys.exit(1)
