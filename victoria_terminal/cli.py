# Copyright (c) 2025 ElcanoTek
#
# This file is part of Victoria Terminal.
#
# This software is licensed under the Business Source License 1.1.
# You may not use this file except in compliance with the license.
# You may obtain a copy of the license at
#
#     https://github.com/ElcanoTek/victoria-terminal/blob/main/LICENSE
#
# Change Date: 2027-09-20
# Change License: GNU General Public License v3.0 or later
# License Notes: 2026-01-02

"""CLI entry point for Victoria Terminal."""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path
from typing import Sequence

from rich.console import Console

from .config import (
    copy_crush_local_config,
    ensure_app_home,
    generate_crush_config,
    load_environment,
    remove_cache_folders,
    remove_local_duckdb,
)
from .constants import CRUSH_COMMAND, __version__
from .license import ensure_license_acceptance, persist_license_acceptance
from .ui import VictoriaUI, check_rich_terminal


def get_app_home() -> Path:
    """Get the Victoria home directory from environment.

    Returns:
        Path to the Victoria home directory.

    Raises:
        RuntimeError: If VICTORIA_HOME is not set.
    """
    env_home = os.environ.get("VICTORIA_HOME")
    if not env_home:
        raise RuntimeError("VICTORIA_HOME must be set before launching Victoria Terminal.")
    return Path(env_home).expanduser()


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments for the entry point.

    Args:
        argv: Command line arguments (defaults to sys.argv[1:]).

    Returns:
        Parsed argument namespace.
    """
    if argv is None:
        argv_list: list[str] = list(sys.argv[1:])
    else:
        argv_list = list(argv)

    parser = argparse.ArgumentParser(
        description="Victoria container entry point. Ensures configuration exists and launches Crush."
    )
    parser.add_argument(
        "--accept-license",
        dest="accept_license",
        action="store_true",
        help="Automatically accept the Victoria Terminal license (required when using --task).",
    )
    parser.add_argument(
        "--task",
        metavar="PROMPT",
        help=(
            "Run a single Crush task non-interactively. Skips the onboarding "
            "sequence, requires --accept-license, and forwards PROMPT to 'crush run'."
        ),
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    # Strip leading -- separator (from container entrypoint)
    normalized_args = [arg for arg in argv_list if arg != "--"]

    return parser.parse_args(normalized_args)


def preflight_crush(ui: VictoriaUI) -> None:
    """Validate that Crush can be launched.

    Args:
        ui: The UI instance for displaying messages.
    """
    ui.section("System preflight check")
    ui.info(f"Checking for {CRUSH_COMMAND} CLI")

    if shutil.which(CRUSH_COMMAND) is None:
        ui.err(
            f"Missing '{CRUSH_COMMAND}' command-line tool. "
            "Rebuild the Victoria container or install the CLI in your environment."
        )
        sys.exit(1)

    ui.good(f"{CRUSH_COMMAND} CLI tool detected")

    if os.environ.get("OPENROUTER_API_KEY"):
        ui.good("OpenRouter API key configured")
    else:
        ui.warn("OPENROUTER_API_KEY not configured. Remote models will be unavailable until it is set.")

    ui.good("All systems ready")


def launch_crush(
    *,
    app_home: Path,
    config_dir: Path | None = None,
    task_prompt: str | None = None,
    ui: VictoriaUI | None = None,
) -> None:
    """Launch Crush with the generated configuration.

    Args:
        app_home: The Victoria home directory.
        config_dir: Path to the config directory (defaults to app_home/.config/victoria).
        task_prompt: If provided, run in non-interactive task mode.
        ui: Optional UI instance for displaying messages.
    """
    from .constants import VICTORIA_CONFIG_DIR

    if ui:
        ui.section("Mission launch")
        ui.info("Launching Crush...")

    # Set CRUSH_GLOBAL_CONFIG to point Crush directly to our config directory
    if config_dir is None:
        config_dir = app_home / VICTORIA_CONFIG_DIR
    os.environ["CRUSH_GLOBAL_CONFIG"] = str(config_dir)

    cmd = [CRUSH_COMMAND, "-c", str(app_home)]
    if task_prompt is None:
        cmd.insert(1, "--yolo")
    else:
        cmd.extend(["run", "-q", task_prompt])

    try:
        os.execvp(CRUSH_COMMAND, cmd)
    except FileNotFoundError:
        if ui:
            ui.err(
                f"'{CRUSH_COMMAND}' command not found in PATH. "
                "Rebuild the Victoria container or install the CLI in your environment."
            )
        sys.exit(1)
    except Exception as exc:  # pragma: no cover
        if ui:
            ui.err(f"Failed to launch Crush: {exc}")
        sys.exit(1)


def main(argv: Sequence[str] | None = None) -> None:
    """Entry point for launching the Victoria terminal.

    Args:
        argv: Command line arguments (defaults to sys.argv[1:]).
    """
    args = parse_args(argv)
    app_home = get_app_home()
    os.environ["VICTORIA_HOME"] = str(app_home)

    # Determine if running in task mode
    raw_task_prompt = getattr(args, "task", None)
    task_prompt: str | None = None
    task_mode = False

    if raw_task_prompt is not None:
        task_prompt = raw_task_prompt.strip() if raw_task_prompt else ""
        if not task_prompt:
            console = Console()
            console.print("[red]❌ --task requires a non-empty prompt to run.[/red]")
            sys.exit(2)
        if not args.accept_license:
            console = Console()
            console.print(
                "[red]❌ --task requires --accept-license to confirm acceptance "
                "of the Victoria Terminal license.[/red]"
            )
            sys.exit(2)
        task_mode = True

    # Initialize UI (silent in task mode)
    ui = VictoriaUI(silent=task_mode)

    # Run interactive intro sequence
    if not task_mode:
        if not check_rich_terminal():
            raise RuntimeError(
                "Victoria Terminal requires an interactive terminal capable of Rich rendering. "
                "Use --task together with --accept-license for non-interactive environments."
            )
        ui.banner_sequence()
        ensure_license_acceptance(app_home, ui)
        ui.spinner("Launching CRUSH…", duration=1.8)
        ui.clear()

    # Setup configuration
    remove_cache_folders(app_home, ui=ui)
    ensure_app_home(app_home, ui=ui)

    if args.accept_license:
        persist_license_acceptance(app_home)

    load_environment(app_home, ui=ui)
    config_dir = generate_crush_config(app_home=app_home, ui=ui)
    copy_crush_local_config(app_home=app_home, ui=ui)
    remove_local_duckdb(app_home, ui=ui)

    ui.info(
        "Place files to analyze in the Victoria folder on your host (~/Victoria by default). "
        f"Inside the container that directory is available at: {app_home}"
    )

    # Launch Crush
    preflight_crush(ui)
    launch_crush(
        app_home=app_home,
        config_dir=config_dir,
        task_prompt=task_prompt if task_mode else None,
        ui=ui,
    )


def cli_main() -> None:
    """CLI entry point with exception handling."""
    console = Console()
    try:
        main()
    except KeyboardInterrupt:  # pragma: no cover
        console.print("\n[yellow]Victoria launch cancelled.")
        sys.exit(130)
    except Exception as exc:  # pragma: no cover
        console.print(f"[red]❌ An unexpected error occurred: {exc}")
        sys.exit(1)
