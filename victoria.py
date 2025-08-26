#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Victoria - AdTech Data Navigation (Cross-platform Python launcher, ✨ pretty version)

- Auto-detects Snowflake env; falls back to local if incomplete
- Fetches VICTORIA.md via SSH clone (private repo)
- Merges `crush.template.json` + `snowflake.mcp.json`
- Replaces ${ENV_VAR} tokens from the environment (cross-platform)
- Writes UTF-8 without BOM
- Cross-platform terminal compatibility with graceful degradation
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
import platform

# ------------------ Config ------------------
VICTORIA_REPO_SSH = "git@github.com:ElcanoTek/victoria-main.git"
VICTORIA_BRANCH   = "main"
VICTORIA_FILE     = "VICTORIA.md"

CRUSH_TEMPLATE    = "crush.template.json"
SNOWFLAKE_FRAG    = "snowflake.mcp.json"
OUTPUT_CONFIG     = "crush.json"

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
    try:
        return os.get_terminal_size().columns
    except:
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

def clear_screen():
    try:
        os.system("cls" if os.name == "nt" else "clear")
    except Exception:
        pass

def which(cmd: str) -> Optional[str]:
    return shutil.which(cmd)

def center_text(text: str, width: int = None) -> str:
    if width is None:
        width = T._width
    # Remove ANSI codes for length calculation
    clean_text = re.sub(r'\033\[[0-9;]*m', '', text)
    padding = max(0, (width - len(clean_text)) // 2)
    return " " * padding + text

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
            ("🏠 Preparing to set sail...", 0.3),
            ("⚓ Raising anchor...", 0.4),
            ("🌊 Entering open waters...", 0.5),
            ("🧭 Navigating the data seas...", 0.8),
            ("🏴‍☠️ Discovering treasure...", 0.6),
            ("🚢 Approaching destination...", 0.4),
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
                wave_chars = ["🌊", "~", "~", "~"]
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
        frames = ["🌊", "🌀", "⚓", "🧭", "⭐", "🚢"]
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
    """Cross-platform banner with ASCII fallbacks."""
    width = min(T._width, 80)  # Cap width for readability
    
    # Border characters
    if TERM_CAPS['unicode_box']:
        h_line = "═"
        corner_tl, corner_tr = "╔", "╗"
        corner_bl, corner_br = "╚", "╝"
        v_line = "║"
    else:
        h_line = "="
        corner_tl = corner_tr = corner_bl = corner_br = "+"
        v_line = "|"
    
    print(f"\n{T.CYAN}{h_line * width}{T.NC}")
    
    # Main title
    if TERM_CAPS['emojis']:
        title_line1 = f"{T.CYAN}{T.BOLD}{T.SHIP} VICTORIA {T.WAVE} ADTECH DATA NAVIGATION {T.SPARKLES}{T.NC}"
        title_line2 = f"{T.CYAN_LIGHT}\"Charting the Digital Seas of Programmatic Advertising\"{T.NC}"
    else:
        title_line1 = f"{T.CYAN}{T.BOLD}*** VICTORIA - ADTECH DATA NAVIGATION ***{T.NC}"
        title_line2 = f"{T.CYAN}\"Charting the Digital Seas of Programmatic Advertising\"{T.NC}"
    
    print(center_text(title_line1, width))
    print(center_text(title_line2, width))
    print(f"{T.CYAN}{h_line * width}{T.NC}")
    
    # ASCII art - simplified for compatibility
    if TERM_CAPS['unicode_box'] and width >= 60:
        print(f"{T.CYAN}{T.BOLD}")
        ascii_art = [
            "╔══════════════════════════════════════════════════════════════╗",
            "║  ██╗   ██╗██╗ ██████╗████████╗ ██████╗ ██████╗ ██╗ █████╗   ║",
            "║  ██║   ██║██║██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗██║██╔══██╗  ║",
            "║  ██║   ██║██║██║        ██║   ██║   ██║██████╔╝██║███████║  ║",
            "║  ╚██╗ ██╔╝██║██║        ██║   ██║   ██║██╔══██╗██║██╔══██║  ║",
            "║   ╚████╔╝ ██║╚██████╗   ██║   ╚██████╔╝██║  ██║██║██║  ██║  ║",
            "║    ╚═══╝  ╚═╝ ╚═════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝  ║",
            "╚══════════════════════════════════════════════════════════════╝"
        ]
        for line in ascii_art:
            print(center_text(line, width))
    else:
        # Simple ASCII art for narrow terminals or no Unicode support
        print(f"{T.CYAN}{T.BOLD}")
        simple_art = [
            "+----------------------------------------------------------+",
            "|  V I C T O R I A   -   D A T A   N A V I G A T O R      |",
            "|                                                          |",
            "|      Your AdTech Analytics Command Center                |",
            "+----------------------------------------------------------+"
        ]
        for line in simple_art:
            print(center_text(line, width))
    
    print(f"{T.NC}")
    
    # Status indicators
    print(center_text(f"{T.GREEN}{T.FIRE} SYSTEM STATUS{T.NC}", width))
    if TERM_CAPS['unicode_box']:
        print(center_text(f"{T.CYAN}━━━━━━━━━━━━━━━━{T.NC}", width))
    else:
        print(center_text(f"{T.CYAN}----------------{T.NC}", width))
    
    print(center_text(f"{T.GREEN}{T.LIGHTNING} Engine: {T.WHITE}Online{T.NC}", width))
    print(center_text(f"{T.BLUE}{T.COMPASS} Navigation: {T.WHITE}Ready{T.NC}", width))
    print(center_text(f"{T.MAGENTA}{T.GEAR} AI Systems: {T.WHITE}Activated{T.NC}", width))
    print(f"{T.CYAN}{h_line * width}{T.NC}\n")

def section_header(title: str, icon: str = None) -> None:
    """Create section headers with fallbacks."""
    width = min(T._width, 80)
    
    if icon is None:
        icon = T.TARGET
    
    title_with_icon = f"{icon} {title.upper()} {icon}"
    
    if TERM_CAPS['unicode_box']:
        print(f"\n{T.YELLOW}┌{'─' * (width-2)}┐{T.NC}")
        print(f"{T.YELLOW}│{center_text(f'{T.BOLD}{T.WHITE}{title_with_icon}{T.NC}', width-2)}{T.YELLOW}│{T.NC}")
        print(f"{T.YELLOW}└{'─' * (width-2)}┘{T.NC}")
    else:
        print(f"\n{T.YELLOW}+{'-' * (width-2)}+{T.NC}")
        print(f"{T.YELLOW}|{center_text(f'{T.BOLD}{T.WHITE}{title_with_icon}{T.NC}', width-2)}{T.YELLOW}|{T.NC}")
        print(f"{T.YELLOW}+{'-' * (width-2)}+{T.NC}")

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

# ------------------ VICTORIA.md via SSH ------------------
def ensure_victoria_md() -> bool:
    root = Path.cwd()
    target = root / VICTORIA_FILE
    if target.exists():
        return True

    if which("git") is None:
        warn("Git not found. Skipping VICTORIA.md fetch.")
        return False

    section_header("TREASURE ACQUISITION", T.BOOK)
    info(f"Downloading {VICTORIA_FILE} from private repository...")
    
    temp_dir = Path(tempfile.mkdtemp(prefix="victoria_clone_"))
    try:
        ship_loading_animation("Cloning victoria-main repository via SSH", 2.5)
        
        res = subprocess.run(
            ["git", "clone", "--depth", "1", "--branch", VICTORIA_BRANCH, VICTORIA_REPO_SSH, str(temp_dir)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        if res.returncode != 0:
            err("Git clone failed. Ensure your SSH key can access GitHub.")
            dim("Hint: Test with 'ssh -T git@github.com'")
            return False

        src = temp_dir / VICTORIA_FILE
        if not src.exists():
            err(f"{VICTORIA_FILE} not found in repository.")
            return False

        shutil.copy2(src, target)
        size = target.stat().st_size
        
        success_animation(f"{VICTORIA_FILE} successfully acquired!")
        print(f"{T.CYAN}{T.CHART} File size: {T.WHITE}{size:,} bytes{T.NC}")
        print(f"{T.CYAN}{T.MAP} Location: {T.WHITE}./{VICTORIA_FILE}{T.NC}")
        
        # Preview
        print(f"\n{T.MAGENTA}{T.BOOK} DOCUMENT PREVIEW{T.NC}")
        print(f"{T.CYAN}{'-' * 50}{T.NC}")
        try:
            with target.open("r", encoding="utf-8", errors="ignore") as f:
                for i, line in enumerate(f):
                    if i >= 3: break
                    if TERM_CAPS['colors']:
                        typewriter_effect(f"   {line.rstrip()}", 0.01)
                    else:
                        print(f"   {line.rstrip()}")
        except Exception:
            pass
        print(f"{T.CYAN}{'-' * 50}{T.NC}")
        
        return True
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def prompt_update_victoria():
    section_header("KNOWLEDGE BASE STATUS", T.BOOK)
    
    target = Path(VICTORIA_FILE)
    if target.exists():
        info(f"{VICTORIA_FILE} already exists in current directory")
        
        if TERM_CAPS['unicode_box']:
            print(f"\n{T.CYAN}┌─ Update Options ─────────────────────────┐{T.NC}")
            print(f"{T.CYAN}│{T.NC} {T.GREEN}[Y]{T.NC} Update to latest from private repo   {T.CYAN}│{T.NC}")
            print(f"{T.CYAN}│{T.NC} {T.YELLOW}[N]{T.NC} Use existing local copy (default)  {T.CYAN}│{T.NC}")
            print(f"{T.CYAN}└──────────────────────────────────────────┘{T.NC}")
        else:
            print(f"\n{T.CYAN}+- Update Options ---------------------+{T.NC}")
            print(f"{T.CYAN}|{T.NC} {T.GREEN}[Y]{T.NC} Update to latest from private repo {T.CYAN}|{T.NC}")
            print(f"{T.CYAN}|{T.NC} {T.YELLOW}[N]{T.NC} Use existing local copy (default){T.CYAN}|{T.NC}")
            print(f"{T.CYAN}+-------------------------------------+{T.NC}")
        
        choice = input(f"\n{T.BOLD}{T.WHITE}Update {VICTORIA_FILE}? [y/N]: {T.NC}").strip().lower()
        if choice in ("y", "yes"):
            ensure_victoria_md()
        else:
            good(f"Using existing {VICTORIA_FILE}")
    else:
        warn(f"{VICTORIA_FILE} not found in current directory")
        
        if TERM_CAPS['unicode_box']:
            print(f"\n{T.CYAN}┌─ Download Options ───────────────────────┐{T.NC}")
            print(f"{T.CYAN}│{T.NC} {T.GREEN}[Y]{T.NC} Download via SSH (recommended)      {T.CYAN}│{T.NC}")
            print(f"{T.CYAN}│{T.NC} {T.YELLOW}[N]{T.NC} Skip download and continue        {T.CYAN}│{T.NC}")
            print(f"{T.CYAN}└──────────────────────────────────────────┘{T.NC}")
        else:
            print(f"\n{T.CYAN}+- Download Options -------------------+{T.NC}")
            print(f"{T.CYAN}|{T.NC} {T.GREEN}[Y]{T.NC} Download via SSH (recommended)    {T.CYAN}|{T.NC}")
            print(f"{T.CYAN}|{T.NC} {T.YELLOW}[N]{T.NC} Skip download and continue      {T.CYAN}|{T.NC}")
            print(f"{T.CYAN}+-------------------------------------+{T.NC}")
        
        choice = input(f"\n{T.BOLD}{T.WHITE}Download {VICTORIA_FILE}? [Y/n]: {T.NC}").strip().lower()
        if choice in ("n", "no"):
            warn(f"Skipping {VICTORIA_FILE} download")
        else:
            ensure_victoria_md()

# ------------------ Config generation ------------------
def snowflake_env_missing() -> List[str]:
    return [v for v in SNOWFLAKE_ENV_VARS if not os.environ.get(v)]

def load_base_template() -> Dict[str, Any]:
    path = Path(CRUSH_TEMPLATE)
    if not path.exists():
        raise FileNotFoundError(f"Missing {CRUSH_TEMPLATE}")
    return read_json(path)

def load_snowflake_fragment() -> Dict[str, Any]:
    path = Path(SNOWFLAKE_FRAG)
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

def generate_crush_config(include_snowflake: bool) -> bool:
    try:
        ship_loading_animation("Generating navigation configuration", 2.0)
        cfg = build_config(include_snowflake, strict_env=include_snowflake)
        write_json(Path(OUTPUT_CONFIG), cfg)
        success_animation(f"Configuration written to {OUTPUT_CONFIG}")
        return True
    except Exception as ex:
        err(f"Configuration generation failed: {ex}")
        return False

# ------------------ Preflight & Launch ------------------
def preflight():
    section_header("SYSTEM PREFLIGHT CHECK", T.WRENCH)
    
    enhanced_spinner("Initializing navigation systems", 1.2)
    
    # Check crush
    if which("crush") is None:
        err("Missing 'crush' command-line tool")
        print(f"\n{T.CYAN}{T.PACKAGE} INSTALLATION REQUIRED{T.NC}")
        print(f"{T.WHITE}Install crush from: https://github.com/charmbracelet/crush{T.NC}")
        sys.exit(1)
    else:
        good("Crush CLI tool detected")
    
    # Check API key
    if not os.environ.get("OPENROUTER_API_KEY"):
        err("OPENROUTER_API_KEY not configured")
        print(f"\n{T.YELLOW}{T.KEY} API CONFIGURATION REQUIRED{T.NC}")
        print(f"{T.CYAN}{'-' * 60}{T.NC}")
        if os.name == "nt":
            print(f"{T.WHITE}PowerShell (Persistent):{T.NC}")
            print(f'{T.GREEN}[Environment]::SetEnvironmentVariable("OPENROUTER_API_KEY","your_key","User"){T.NC}')
        else:
            print(f"{T.WHITE}Shell Export:{T.NC}")
            print(f'{T.GREEN}export OPENROUTER_API_KEY="your_api_key_here"{T.NC}')
        print(f"{T.CYAN}{'-' * 60}{T.NC}")
        sys.exit(1)
    else:
        good("OpenRouter API key configured")
    
    success_animation("All systems ready for launch!")

def launch_crush():
    section_header("MISSION LAUNCH", T.ROCKET)
    
    ship_loading_animation("Preparing crush launch sequence", 2.0)
    
    print(f"\n{T.GREEN}{T.TARGET} LAUNCHING VICTORIA DATA NAVIGATOR{T.NC}")
    
    border_char = "=" if not TERM_CAPS['unicode_box'] else "═"
    print(f"{T.CYAN}{border_char * 50}{T.NC}")
    
    try:
        if os.name == "nt":
            proc = subprocess.run(["crush"])
            if proc.returncode != 0:
                err(f"Crush exited with error code {proc.returncode}")
                sys.exit(proc.returncode)
        else:
            os.execvp("crush", ["crush"])
    except FileNotFoundError:
        err("'crush' command not found in PATH")
        sys.exit(1)
    except Exception as e:
        err(f"Failed to launch crush: {e}")
        sys.exit(1)

def course_menu() -> str:
    section_header("NAVIGATION COURSE SELECTION", T.COMPASS)
    
    enhanced_spinner("Booting navigation systems", 1.5)
    
    print(f"\n{T.BOLD}{T.WHITE}Choose your data exploration voyage:{T.NC}\n")
    
    # Use appropriate border characters
    if TERM_CAPS['unicode_box']:
        border_chars = ("┌", "─", "┐", "│", "└", "┘", "├", "┤")
    else:
        border_chars = ("+", "-", "+", "|", "+", "+", "+", "+")
    
    tl, h, tr, v, bl, br, lt, rt = border_chars
    
    print(f"{T.CYAN}{tl}{h} EXPEDITION OPTIONS {h * (T._width - 22)}{tr}{T.NC}")
    print(f"{T.CYAN}{v}{T.NC}")
    print(f"{T.CYAN}{v}{T.NC} {T.GREEN}{T.BOLD}[1] {T.WAVE} FULL OCEAN EXPEDITION{T.NC}")
    print(f"{T.CYAN}{v}{T.NC}     {T.CYAN}{T.LIGHTNING} Enterprise Snowflake Database Access{T.NC}")
    print(f"{T.CYAN}{v}{T.NC}     {T.CYAN}{T.CHART} Local CSV/Excel via MotherDuck{T.NC}")
    print(f"{T.CYAN}{v}{T.NC}     {T.CYAN}{T.TARGET} Complete programmatic advertising analytics{T.NC}")
    print(f"{T.CYAN}{v}{T.NC}     {T.CYAN}{T.FIRE} Maximum data exploration capabilities{T.NC}")
    print(f"{T.CYAN}{v}{T.NC}")
    print(f"{T.CYAN}{lt}{h * (T._width - 2)}{rt}{T.NC}")
    print(f"{T.CYAN}{v}{T.NC}")
    print(f"{T.CYAN}{v}{T.NC} {T.YELLOW}{T.BOLD}[2] {T.ANCHOR} COASTAL NAVIGATION{T.NC}")
    print(f"{T.CYAN}{v}{T.NC}     {T.YELLOW}{T.FOLDER} Local CSV/Excel file analysis{T.NC}")
    print(f"{T.CYAN}{v}{T.NC}     {T.YELLOW}{T.LIGHTNING} Fast startup, zero external dependencies{T.NC}")
    print(f"{T.CYAN}{v}{T.NC}     {T.YELLOW}{T.MAG} Perfect for local data exploration{T.NC}")
    print(f"{T.CYAN}{v}{T.NC}     {T.YELLOW}{T.SHIELD} Ideal for testing and development{T.NC}")
    print(f"{T.CYAN}{v}{T.NC}")
    print(f"{T.CYAN}{bl}{h * (T._width - 2)}{br}{T.NC}")

    while True:
        choice = input(f"\n{T.BOLD}{T.WHITE}{T.TARGET} Select your navigation course [1-2]: {T.NC}").strip()
        if choice in ("1", "2"):
            return choice
        warn("Invalid selection. Please choose 1 or 2.")

# ------------------ Main ------------------
def main():
    clear_screen()
    banner()
    
    print(f"{T.GREEN}{T.ROCKET} Welcome to Victoria - Your AdTech Data Navigator!{T.NC}")
    
    # Show terminal capabilities for debugging (remove in production)
    if os.environ.get('VICTORIA_DEBUG'):
        print(f"{T.DIM}Debug: Terminal caps: {TERM_CAPS}{T.NC}")
    
    time.sleep(1)
    
    prompt_update_victoria()
    preflight()

    choice = course_menu()

    if choice == "1":
        section_header("FULL OCEAN EXPEDITION PREP", T.WAVE)
        
        enhanced_spinner("Checking Snowflake credentials", 1.0)
        
        missing = snowflake_env_missing()
        if missing:
            print(f"\n{T.RED}{T.WARN} NAVIGATION HAZARD DETECTED{T.NC}")
            
            border_char = "=" if not TERM_CAPS['unicode_box'] else "═"
            print(f"{T.YELLOW}{border_char * 60}{T.NC}")
            warn("Missing required Snowflake environment variables:")
            for v in missing:
                print(f"   {T.RED}{T.ERROR} {v}{T.NC}")
            
            print(f"\n{T.CYAN}{T.WRENCH} REQUIRED CONFIGURATION:{T.NC}")
            print(f"{T.CYAN}{'-' * 60}{T.NC}")
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
            print(f"{T.YELLOW}{border_char * 60}{T.NC}")
            sys.exit(1)

        success_animation("Snowflake credentials validated!")
        
        if not generate_crush_config(include_snowflake=True):
            sys.exit(1)
            
        print(f"\n{T.GREEN}{T.WAVE} FULL OCEAN EXPEDITION READY{T.NC}")
        print(f"{T.CYAN}Launching Victoria with complete data access...{T.NC}")
        launch_crush()

    else:  # choice == "2"
        section_header("COASTAL NAVIGATION PREP", T.ANCHOR)
        
        print(f"\n{T.YELLOW}{T.ANCHOR} COASTAL NAVIGATION MODE SELECTED{T.NC}")
        info("Preparing for local data exploration...")
        
        enhanced_spinner("Configuring local data access", 1.5)
        
        if not generate_crush_config(include_snowflake=False):
            sys.exit(1)
            
        success_animation("Local data configuration ready!")
        
        print(f"\n{T.CYAN}{T.ANCHOR} COASTAL NAVIGATION READY{T.NC}")
        print(f"{T.CYAN}Launching Victoria with local data access...{T.NC}")
        launch_crush()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{T.YELLOW}{T.ANCHOR} Voyage cancelled by captain's orders.{T.NC}")
        print(f"{T.DIM}Fair winds and following seas! {T.WAVE}{T.NC}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{T.RED}💥 Unexpected navigation error: {e}{T.NC}")
        print(f"{T.DIM}Check your charts and try again, Captain!{T.NC}")
        sys.exit(1)
