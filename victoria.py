#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Victoria - AdTech Data Navigation (Cross-platform Python launcher, ✨ pretty version)

- No dependency installer
- No environment variable setup
- Auto-detects Snowflake env; falls back to local if incomplete
- Fetches VICTORIA.md via SSH clone (private repo)
- Merges `crush.template.json` + `snowflake.mcp.json`
- Replaces ${ENV_VAR} tokens from the environment (cross-platform)
- Writes UTF-8 without BOM
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

# ------------------ ANSI / Emoji Support ------------------
def _enable_windows_ansi():
    """Best-effort enable ANSI on Windows without external deps."""
    if os.name != "nt":
        return
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        h = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE = -11
        mode = ctypes.c_uint32()
        if kernel32.GetConsoleMode(h, ctypes.byref(mode)):
            ENABLE_VTP = 0x0004
            kernel32.SetConsoleMode(h, mode.value | ENABLE_VTP)
    except Exception:
        pass

_enable_windows_ansi()

class T:
    _tty = sys.stdout.isatty()
    # Colors
    RED     = "\033[0;31m" if _tty else ""
    GREEN   = "\033[0;32m" if _tty else ""
    YELLOW  = "\033[1;33m" if _tty else ""
    BLUE    = "\033[0;34m" if _tty else ""
    MAGENTA = "\033[0;35m" if _tty else ""
    CYAN    = "\033[0;36m" if _tty else ""
    WHITE   = "\033[1;37m" if _tty else ""
    DIM     = "\033[2m"    if _tty else ""
    BOLD    = "\033[1m"    if _tty else ""
    NC      = "\033[0m"    if _tty else ""
    # Emojis
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
    MAG       = "🔎"

def clear_screen():
    try:
        os.system("cls" if os.name == "nt" else "clear")
    except Exception:
        pass

def which(cmd: str) -> Optional[str]:
    return shutil.which(cmd)

def info(msg: str):  print(f"{T.CYAN}{msg}{T.NC}")
def good(msg: str):  print(f"{T.GREEN}{msg}{T.NC}")
def warn(msg: str):  print(f"{T.YELLOW}{msg}{T.NC}")
def err(msg: str):   print(f"{T.RED}{msg}{T.NC}")
def dim(msg: str):   print(f"{T.DIM}{msg}{T.NC}")

def spinner(line: str, seconds: float = 1.0):
    if not sys.stdout.isatty():
        print(line)
        time.sleep(seconds)
        return
    frames = ["|", "/", "—", "\\"]
    start = time.time()
    i = 0
    while time.time() - start < seconds:
        sys.stdout.write(f"\r{T.BLUE}{frames[i % len(frames)]}{T.NC} {line}")
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1
    sys.stdout.write("\r   " + " " * len(line) + "\r")
    sys.stdout.flush()

def banner():
    print(f"{T.CYAN}{T.BOLD}{T.SHIP}  Victoria {T.WAVE} x crush {T.SPARKLES}{T.NC}")
    print(f"{T.WHITE}{T.BOLD}“Charting the Digital Seas of AdTech”{T.NC}")
    print(f"{T.DIM}----------------------------------------------{T.NC}")
    print(f"{T.CYAN}{T.BOLD}")
    print(r"¦¦+   ¦¦+¦¦+ ¦¦¦¦¦¦+¦¦¦¦¦¦¦¦+ ¦¦¦¦¦¦+ ¦¦¦¦¦¦+ ¦¦+ ¦¦¦¦¦+")
    print(r"¦¦¦   ¦¦¦¦¦¦¦¦+----++--¦¦+--+¦¦+---¦¦+¦¦+--¦¦+¦¦¦¦¦+--¦¦+")
    print(r"¦¦¦   ¦¦¦¦¦¦¦¦¦        ¦¦¦   ¦¦¦   ¦¦¦¦¦¦¦¦¦++¦¦¦¦¦¦¦¦¦¦¦")
    print(r"+¦¦+ ¦¦++¦¦¦¦¦¦        ¦¦¦   ¦¦¦   ¦¦¦¦¦+--¦¦+¦¦¦¦¦+--¦¦¦")
    print(r" +¦¦¦¦++ ¦¦¦+¦¦¦¦¦¦+   ¦¦¦   +¦¦¦¦¦¦++¦¦¦  ¦¦¦¦¦¦¦¦¦  ¦¦¦")
    print(r"  +---+  +-+ +-----+   +-+    +-----+ +-+  +-++-++-+  +-+")
    print(f"{T.NC}")
    print()

# ------------------ JSON I/O ------------------
def read_json(path: Path) -> Dict[str, Any]:
    # tolerate BOM in templates/fragments
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
    """
    Recursively replace ${VAR} in strings with os.environ['VAR'].
    If strict=True, raise if any referenced VAR is missing.
    """
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
                return m.group(0)  # leave placeholder intact
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

    info(f"{T.BOOK} Downloading {VICTORIA_FILE} from private repo via SSH…")
    temp_dir = Path(tempfile.mkdtemp(prefix="victoria_clone_"))
    try:
        spinner("Cloning victoria-main (SSH)", 0.9)
        res = subprocess.run(
            ["git", "clone", "--depth", "1", "--branch", VICTORIA_BRANCH, VICTORIA_REPO_SSH, str(temp_dir)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        if res.returncode != 0:
            err(f"{T.ERROR} Git clone failed. Ensure your SSH key can access GitHub.")
            dim("Hint: ssh -T git@github.com")
            return False

        src = temp_dir / VICTORIA_FILE
        if not src.exists():
            err(f"{T.ERROR} {VICTORIA_FILE} not found in repo.")
            return False

        shutil.copy2(src, target)
        size = target.stat().st_size
        good(f"{T.CHECK} {VICTORIA_FILE} downloaded!")
        info(f"   {T.MAG} Size: {size} bytes")
        info(f"   {T.MAG} Location: ./{VICTORIA_FILE}")
        print(f"{T.MAGENTA}   {T.MAG} Preview (first 3 lines):{T.NC}")
        try:
            with target.open("r", encoding="utf-8", errors="ignore") as f:
                for i, line in enumerate(f):
                    if i >= 3: break
                    print("      " + line.rstrip("\n"))
        except Exception:
            pass
        return True
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def prompt_update_victoria():
    print(f"{T.YELLOW}{T.BOLD}📘 VICTORIA.md Update Check{T.NC}\n")
    target = Path(VICTORIA_FILE)
    if target.exists():
        print(f"{T.CYAN}{VICTORIA_FILE} already exists in this directory.{T.NC}")
        choice = input(f"{T.WHITE}{T.BOLD}Update to latest from private repo? [y/N]: {T.NC}").strip().lower()
        if choice in ("y", "yes"):
            ensure_victoria_md()
        else:
            print(f"{T.GREEN}Using existing {VICTORIA_FILE}.{T.NC}")
    else:
        print(f"{T.CYAN}{VICTORIA_FILE} not found in this directory.{T.NC}")
        choice = input(f"{T.WHITE}{T.BOLD}Download it now via SSH? [Y/n]: {T.NC}").strip().lower()
        if choice in ("n", "no"):
            print(f"{T.YELLOW}Skipping {VICTORIA_FILE} download.{T.NC}")
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
        # Merge into base["mcp"]
        base.setdefault("mcp", {})
        if "mcp" in frag and isinstance(frag["mcp"], dict):
            deep_merge(base["mcp"], frag["mcp"])
        else:
            deep_merge(base["mcp"], frag)
    # Substitute ${VAR} across the entire config
    return substitute_env(base, strict=strict_env)

def generate_crush_config(include_snowflake: bool) -> bool:
    try:
        # strict_env=True for Snowflake path (require vars), False for local
        cfg = build_config(include_snowflake, strict_env=include_snowflake)
        write_json(Path(OUTPUT_CONFIG), cfg)
        return True
    except Exception as ex:
        err(f"{T.ERROR} Generate config failed: {ex}")
        return False

# ------------------ Preflight & Launch ------------------
def preflight():
    spinner(f"{T.GEAR} Initializing", 0.6)
    if which("crush") is None:
        err(f"{T.ERROR} Missing 'crush'. Install from https://github.com/charmbracelet/crush")
        sys.exit(1)
    if not os.environ.get("OPENROUTER_API_KEY"):
        err(f"{T.ERROR} OPENROUTER_API_KEY not set.")
        if os.name == "nt":
            dim('Set persistently (PowerShell): [Environment]::SetEnvironmentVariable("OPENROUTER_API_KEY","your_api_key_here","User")')
        else:
            dim('Set in shell: export OPENROUTER_API_KEY="your_api_key_here"')
        sys.exit(1)

def launch_crush():
    info(f"{T.ROCKET} Launching crush...")
    try:
        if os.name == "nt":
            # On Windows, exec* doesn't replace the current process. Block instead.
            proc = subprocess.run(["crush"])
            if proc.returncode != 0:
                err(f"{T.ERROR} crush exited with code {proc.returncode}")
                sys.exit(proc.returncode)
        else:
            # On POSIX, replace the current process so the shell prompt doesn't reappear
            os.execvp("crush", ["crush"])
    except FileNotFoundError:
        err(f"{T.ERROR} 'crush' not found on PATH.")
        sys.exit(1)
    except Exception as e:
        err(f"{T.ERROR} Failed to launch crush: {e}")
        sys.exit(1)


# ------------------ Course selection ------------------
def course_menu() -> str:
    print()
    print(f"{T.YELLOW}{T.BOLD}🧭 COURSE SELECTION{T.NC}")
    print(f"{T.DIM}———————————————{T.NC}")
    spinner(f"{T.CYAN}Booting nav systems…{T.NC}", 0.7)
    print()
    print(f"{T.WHITE}{T.BOLD}Choose your data exploration voyage:{T.NC}\n")
    print(f"{T.GREEN}{T.BOLD}[1]{T.NC} {T.CYAN}🌊 Full Ocean Expedition{T.NC} — Connect to Snowflake + Local Data")
    print(f"    {T.MAGENTA}•{T.NC} Access enterprise Snowflake databases")
    print(f"    {T.MAGENTA}•{T.NC} Query local CSV/Excel files via MotherDuck")
    print(f"    {T.MAGENTA}•{T.NC} Complete programmatic advertising analytics\n")
    print(f"{T.YELLOW}{T.BOLD}[2]{T.NC} {T.CYAN}🏖️  Coastal Navigation{T.NC} — Local Data Only")
    print(f"    {T.MAGENTA}•{T.NC} Query local CSV/Excel files via MotherDuck")
    print(f"    {T.MAGENTA}•{T.NC} Fast startup, no external dependencies")
    print(f"    {T.MAGENTA}•{T.NC} Perfect for local data analysis\n")

    while True:
        choice = input(f"{T.WHITE}{T.BOLD}Select your course [1-2]: {T.NC}").strip()
        if choice in ("1", "2"):
            return choice
        err("Invalid selection. Please choose 1 or 2.")

# ------------------ Main ------------------
def main():
    clear_screen()
    banner()
    prompt_update_victoria()
    preflight()

    choice = course_menu()

    if choice == "1":
        missing = snowflake_env_missing()
        if missing:
            print()
            err("⚠️  NAVIGATION WARNING")
            warn("Missing Snowflake environment variables:")
            for v in missing:
                err(f"  • {v}")
            print()
            info("Please set these variables before continuing:")
            print('  export SNOWFLAKE_ACCOUNT="your_account"')
            print('  export SNOWFLAKE_USER="your_user"')
            print('  export SNOWFLAKE_PASSWORD="your_password"')
            print('  export SNOWFLAKE_WAREHOUSE="your_warehouse"')
            print('  export SNOWFLAKE_ROLE="your_role"')
            print()
            warn("See SNOWFLAKE_INSTALL.md for detailed setup instructions.")
            sys.exit(1)

        good(f"{T.CHECK} Snowflake credentials detected")
        spinner("Generating configuration with Snowflake…", 0.7)
        if not generate_crush_config(include_snowflake=True):
            sys.exit(1)
        print()
        info("🌐 Launching Victoria with full data access…")
        launch_crush()

    else:
        print()
        warn("🏖️  COASTAL NAVIGATION SELECTED")
        info("Preparing for local data exploration…")
        good(f"{T.CHECK} Local data access ready")
        spinner("Generating configuration for local data access…", 0.6)
        if not generate_crush_config(include_snowflake=False):
            sys.exit(1)
        print()
        info("🪪 Launching Victoria with local data access…")
        launch_crush()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAborted by user.")
        sys.exit(130)
