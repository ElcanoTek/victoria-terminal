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

"""Victoria Terminal - Container-first interface for advertising data analysis."""

from __future__ import annotations

# Re-export public API for backwards compatibility
from .cli import get_app_home, launch_crush, main, parse_args
from .config import (
    copy_crush_local_config,
    ensure_app_home,
    generate_crush_config,
    load_environment,
    parse_env_file,
    remove_cache_folders,
    remove_local_duckdb,
    resource_path,
    substitute_env,
)
from .constants import (
    CRUSH_CONFIG_NAME,
    CRUSH_TEMPLATE,
    ENV_FILENAME,
    __version__,
)
from .license import (
    is_license_accepted,
    is_valid_email,
    persist_license_acceptance,
    track_license_acceptance,
)

# Re-export for backwards compatibility with tests
import os as os
import requests as requests
from email_validator import EmailNotValidError, validate_email

# Backwards compatibility: internal function aliases
_is_valid_email = is_valid_email
_track_license_acceptance = track_license_acceptance

__all__ = [
    # Version
    "__version__",
    # CLI
    "main",
    "parse_args",
    "get_app_home",
    "launch_crush",
    # Config
    "parse_env_file",
    "load_environment",
    "substitute_env",
    "ensure_app_home",
    "generate_crush_config",
    "copy_crush_local_config",
    "remove_cache_folders",
    "remove_local_duckdb",
    "resource_path",
    # License
    "is_license_accepted",
    "persist_license_acceptance",
    "is_valid_email",
    "track_license_acceptance",
    # Constants
    "ENV_FILENAME",
    "CRUSH_CONFIG_NAME",
    "CRUSH_TEMPLATE",
    # Backwards compatibility
    "_is_valid_email",
    "_track_license_acceptance",
    "validate_email",
    "EmailNotValidError",
    "os",
    "requests",
]
