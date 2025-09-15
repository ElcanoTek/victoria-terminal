#!/usr/bin/env python3
"""Victoria Configurator - First-time setup and prerequisite installer."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Callable

from rich.prompt import Confirm, Prompt

from common import (APP_HOME, SETUP_SENTINEL, banner, console, err, good,
                    handle_error, info, initialize_colorama, resource_path,
                    section, warn)


def check_for_existing_tools(
    _shutil_which: Callable[[str], str | None] = shutil.which,
    _Confirm_ask: Callable[..., bool] = Confirm.ask,
    _info: Callable[[str], None] = info,
    _good: Callable[[str], None] = good,
) -> bool:
    """Check if crush and uv are already installed and ask user what to do."""
    crush_path = _shutil_which("crush")
    uv_path = _shutil_which("uv")

    if crush_path and uv_path:
        _good("Found existing installations of 'crush' and 'uv'.")
        _info(f"  - crush: {crush_path}")
        _info(f"  - uv: {uv_path}")
        return _Confirm_ask(
            "Do you want Victoria to manage these dependencies for you? "
            "Choose [b]Yes[/b] for the recommended setup.",
            default=True,
        )
    return True


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


def upgrade_dependencies(
    _subprocess_run: Callable[..., subprocess.CompletedProcess] = subprocess.run,
    _err: Callable[[str], None] = err,
    _info: Callable[[str], None] = info,
    _good: Callable[[str], None] = good,
    _warn: Callable[[str], None] = warn,
    _os_name: str = os.name,
    _sys_platform: str = sys.platform,
    _APP_HOME: Path = APP_HOME,
) -> None:
    """Run dependency upgrade scripts."""
    info("Upgrading dependencies...")
    deps = _APP_HOME / "dependencies"

    # Upgrade system prerequisites (crush, uv)
    if _os_name == "nt":
        script = deps / "install_prerequisites_windows.ps1"
        cmd = [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            f"Unblock-File -Path '{script}' -ErrorAction SilentlyContinue; & '{script}' -Upgrade",
        ]
        try:
            _subprocess_run(cmd, check=True)
        except Exception as exc:
            _err(f"Prerequisite upgrade script failed: {exc}")
    elif _sys_platform == "darwin" or _sys_platform.startswith("linux"):
        is_macos = _sys_platform == "darwin"
        install_script = (
            "install_prerequisites_macos.sh"
            if is_macos
            else "install_prerequisites_linux.sh"
        )
        script_path = deps / install_script
        try:
            cmd = ["bash", str(script_path), "--upgrade"]
            _subprocess_run(cmd, check=True)
        except Exception as exc:
            _err(f"Prerequisite upgrade script failed: {exc}")
    else:
        _warn("Unsupported platform for automatic upgrade.")

    # Upgrade Python packages
    info("Upgrading Python packages...")
    venv_python = _APP_HOME / "venv" / ("Scripts" if _os_name == "nt" else "bin") / "python"
    requirements_file = _APP_HOME / "requirements.txt"
    try:
        cmd = [str(venv_python), "-m", "pip", "install", "--upgrade", "-r", str(requirements_file)]
        _subprocess_run(cmd, check=True)
        good("Python packages upgraded successfully.")
    except Exception as exc:
        _err(f"Python package upgrade failed: {exc}")


def first_run_check(
    use_local_model: bool,
    force_install_deps: bool,
    _run_setup_scripts: Callable[[bool], None] = run_setup_scripts,
    _upgrade_dependencies: Callable[[], None] = upgrade_dependencies,
    _SETUP_SENTINEL: Path = SETUP_SENTINEL,
    _Prompt_ask: Callable[..., str] = Prompt.ask,
    _section: Callable[[str], None] = section,
    _update_path_from_install: Callable[[], None] = update_path_from_install,
    _info: Callable[[str], None] = info,
    _good: Callable[[str], None] = good,
    _warn: Callable[[str], None] = warn,
    _check_for_existing_tools: Callable[[], bool] = check_for_existing_tools,
) -> bool:
    """Check if this is the first run and execute setup if needed."""
    setup_needed = True
    if _SETUP_SENTINEL.exists():
        _warn("Setup has already been completed.")
        choice = _Prompt_ask(
            "What would you like to do?",
            choices=["r", "u", "n"],
            prompt="[r]e-run setup, [u]pgrade dependencies, or [n]othing?",
            default="n",
        )
        if choice == "n":
            setup_needed = False
        elif choice == "u":
            _section("Upgrading Dependencies")
            _upgrade_dependencies()
            _good("Upgrade process finished.")
            return False  # Exit after upgrade.

    if not setup_needed:
        _info("Exiting configurator. You can run the Crush Launcher directly.")
        return False

    _section("System Prerequisite Installation")

    install_deps = True
    if not force_install_deps:
        install_deps = _check_for_existing_tools()

    if install_deps:
        _run_setup_scripts(use_local_model)
        _update_path_from_install()
        _good("Prerequisite installation process finished.")
    else:
        _info("Skipping automatic dependency installation.")
        _info("Please ensure 'crush' and 'uv' are correctly installed and in your PATH.")

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

    parser = argparse.ArgumentParser(
        description="Victoria Configurator - Setup and manage dependencies."
    )
    parser.add_argument(
        "--force-install-deps",
        action="store_true",
        help="Force the installation of system dependencies (crush, uv), "
        "bypassing checks for existing installations.",
    )
    args = parser.parse_args()

    banner()
    section("Model provider selection")
    choice = Prompt.ask(
        "Will you be using a locally hosted model (LM Studio)? "
        "Select 'n' if you have an OpenRouter API key.",
        choices=["y", "n"],
        default="n",
    )
    use_local_model = choice == "y"
    first_run_check(use_local_model, args.force_install_deps)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Setup cancelled.")
        sys.exit(130)
    except Exception as e:
        handle_error(e)
