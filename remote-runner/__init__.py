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

"""
Remote Runner (Host Shim) for Victoria Terminal.

This module provides the host-side component for remote orchestration
of Victoria Terminal containers via All-Time Quarterback.
"""

from .runner import Config, Runner, run_container

__all__ = ["Config", "Runner", "run_container"]
