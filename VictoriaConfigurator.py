#!/usr/bin/env python3
"""Victoria Configurator - First-time setup and prerequisite installer."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Callable

from rich.prompt import Prompt

from common import (APP_HOME, SETUP_SENTINEL, banner, console, err, good,
                    handle_error, info, initialize_colorama, resource_path,
                    section, warn)


def update_path_from_install(
    _APP_HOME: Path = APP_HOME,
    _os_environ: dict = os.environ,
    _info: Callable[[str], None] = info,
    _warn: Callable[[str], None] = warn,
) -> None:
    """Check for a newly installed tool and update the PATH if found."""
    crush_path_file = _APP_HOME / ".crush_path"
    if not crush_path_file.is_file():
        return

    try:
        crush_executable = crush_path_file.read_text().strip()
        if crush_executable:
            crush_dir = str(Path(crush_executable).parent)
            if crush_dir not in _os_environ["PATH"].split(os.pathsep):
                _info(f"Adding {crush_dir} to PATH for this session")
                _os_environ["PATH"] = f"{crush_dir}{os.pathsep}{_os_environ['PATH']}"
        # Clean up the file after processing
        crush_path_file.unlink()
    except Exception as exc:
        _warn(f"Could not update PATH from install file: {exc}")


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
                    f"{' -SkipOpenRouter' if use_local_model and s.startswith('set_env') else ''}"  # noqa: E501
                ),
            ]
            try:
                _subprocess_run(cmd, check=True)
            except Exception as exc:
                _err(f"Setup script failed: {exc}")
                break
    elif _sys_platform == "darwin" or _sys_platform.startswith("linux"):
        is_macos = _sys_platform == "darwin"
        install_script = (
            "install_prerequisites_macos.sh"
            if is_macos
            else "install_prerequisites_linux.sh"
        )
        scripts = [install_script, "set_env_macos_linux.sh"]
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
        _warn(
            "Unsupported platform; run setup scripts manually "
            "from the dependencies folder."
        )
        return


def first_run_check(
    use_local_model: bool,
    _run_setup_scripts: Callable[[bool], None] = run_setup_scripts,
    _SETUP_SENTINEL: Path = SETUP_SENTINEL,
    _Prompt_ask: Callable[..., str] = Prompt.ask,
    _section: Callable[[str], None] = section,
    _update_path_from_install: Callable[[], None] = update_path_from_install,
    _info: Callable[[str], None] = info,
    _good: Callable[[str], None] = good,
    _warn: Callable[[str], None] = warn,
) -> bool:
    """Check if this is the first run and execute setup if needed."""
    setup_needed = True
    if _SETUP_SENTINEL.exists():
        _warn("Setup has already been completed.")
        if (
            _Prompt_ask(
                "Do you want to run the setup again?",
                choices=["y", "n"],
                default="n",
            )
            == "n"
        ):
            setup_needed = False

    if not setup_needed:
        _info("Exiting configurator. You can run the Crush Launcher directly.")
        return False

    _section("System Prerequisite Installation")
    _run_setup_scripts(use_local_model)
    _update_path_from_install()
    try:
        _SETUP_SENTINEL.write_text("done")
        _good("Configuration complete. You can now run the Crush Launcher.")
    except Exception:
        pass
    return True


def main() -> None:
    """Main entry point for the Victoria Configurator."""
    initialize_colorama()
    console.clear()
    banner()
    section("Model provider selection")
    choice = Prompt.ask(
        "Will you be using a locally hosted model (LM Studio)? "
        "Select 'n' if you have an OpenRouter API key.",
        choices=["y", "n"],
        default="n",
    )
    use_local_model = choice == "y"
    first_run_check(use_local_model)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Setup cancelled.")
        sys.exit(130)
    except Exception as e:
        handle_error(e)
