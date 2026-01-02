#!/usr/bin/env python3
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

"""
Backwards-compatible entry point for Victoria Terminal.

This module re-exports the public API from the victoria_terminal package
for backwards compatibility. New code should import directly from the package:

    from victoria_terminal import main
    from victoria_terminal.config import generate_crush_config
    from victoria_terminal.ui import VictoriaUI
"""

from __future__ import annotations

# Re-export everything from the package for backwards compatibility
from victoria_terminal import *  # noqa: F401, F403
from victoria_terminal import (
    ENV_FILENAME,
    EmailNotValidError,
    _is_valid_email,
    _track_license_acceptance,
    generate_crush_config,
    launch_crush,
    load_environment,
    main,
    os,
    parse_args,
    parse_env_file,
    requests,
    resource_path,
    substitute_env,
    validate_email,
)
from victoria_terminal.cli import cli_main

if __name__ == "__main__":
    cli_main()
