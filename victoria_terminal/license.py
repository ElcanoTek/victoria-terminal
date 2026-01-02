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

"""License acceptance and tracking for Victoria Terminal."""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import TYPE_CHECKING

import requests
from dotenv import set_key
from email_validator import EmailNotValidError, validate_email

from .config import parse_env_file, resource_path
from .constants import (
    ENV_FILENAME,
    LICENSE_ACCEPTANCE_KEY,
    LICENSE_ACCEPTED_VALUES,
    LICENSE_FILE_NAME,
    TELEMETRY_URL,
    __version__,
)

if TYPE_CHECKING:
    from .ui import VictoriaUI

# Cache for license text
_LICENSE_TEXT_CACHE: str | None = None


def _resolve_license_path() -> Path:
    """Locate the bundled license file."""
    env_path = os.environ.get("VICTORIA_LICENSE_PATH")
    if env_path:
        candidate = Path(env_path).expanduser()
        if candidate.is_file():
            return candidate
        candidate_with_name = candidate / LICENSE_FILE_NAME
        if candidate_with_name.is_file():
            return candidate_with_name

    license_path = resource_path(Path(LICENSE_FILE_NAME))
    if license_path.is_file():
        return license_path

    raise FileNotFoundError(
        "Victoria Terminal requires the LICENSE file to display the agreement. "
        f"Expected to find it at {license_path}"
    )


def get_license_text() -> str:
    """Get the license text, caching it for subsequent calls."""
    global _LICENSE_TEXT_CACHE
    if _LICENSE_TEXT_CACHE is not None:
        return _LICENSE_TEXT_CACHE

    license_path = _resolve_license_path()
    _LICENSE_TEXT_CACHE = license_path.read_text(encoding="utf-8")
    return _LICENSE_TEXT_CACHE


def is_license_accepted(app_home: Path) -> bool:
    """Check if the license has been accepted.

    Args:
        app_home: The Victoria home directory.

    Returns:
        True if the license has been accepted.
    """
    # Check environment variable first
    value = os.environ.get(LICENSE_ACCEPTANCE_KEY, "").strip().lower()
    if value in LICENSE_ACCEPTED_VALUES:
        return True

    # Check stored value in .env file
    env_path = app_home / ENV_FILENAME
    if not env_path.exists():
        return False

    stored_value = parse_env_file(env_path).get(LICENSE_ACCEPTANCE_KEY, "")
    if stored_value:
        os.environ.setdefault(LICENSE_ACCEPTANCE_KEY, stored_value)
    return stored_value.strip().lower() in LICENSE_ACCEPTED_VALUES


def persist_license_acceptance(app_home: Path) -> None:
    """Persist license acceptance to the .env file.

    Args:
        app_home: The Victoria home directory.
    """
    env_path = app_home / ENV_FILENAME
    env_path.parent.mkdir(parents=True, exist_ok=True)
    if not env_path.exists():
        env_path.touch()
    set_key(str(env_path), LICENSE_ACCEPTANCE_KEY, "yes")
    os.environ[LICENSE_ACCEPTANCE_KEY] = "yes"


def is_valid_email(email: str) -> bool:
    """Validate an email address using the email_validator library.

    Args:
        email: The email address to validate.

    Returns:
        True if the email is valid.
    """
    if not email:
        return False

    try:
        validate_email(email, check_deliverability=True)
    except EmailNotValidError:
        return False
    return True


def track_license_acceptance(email: str | None = None) -> None:
    """Send telemetry data to the configured webhook endpoint.

    Args:
        email: The user's email address (optional).
    """
    if not email:
        return

    if not is_valid_email(email):
        return

    payload = {
        "email": email,
        "event": "license_accepted",
        "timestamp": int(time.time()),
        "version": __version__,
    }

    try:
        requests.post(TELEMETRY_URL, json=payload, timeout=3)
    except requests.RequestException:
        # Fail silently - don't interrupt user experience for telemetry
        pass


def ensure_license_acceptance(app_home: Path, ui: "VictoriaUI") -> None:
    """Ensure the user has accepted the license, prompting if needed.

    Args:
        app_home: The Victoria home directory.
        ui: The UI instance for displaying prompts.
    """
    if is_license_accepted(app_home):
        return

    ui.display_license_notice()

    accept_responses = {"accept", "a", "yes", "y"}
    decline_responses = {"decline", "d", "no", "n"}

    while True:
        response = ui.prompt_license_response().lower()
        if response in accept_responses:
            persist_license_acceptance(app_home)
            ui.acknowledge_license_acceptance()

            # Collect email for license acceptance (only in interactive mode)
            if not ui.silent:
                while True:
                    email = ui.prompt_email()
                    if not email:
                        ui.err("Email address is required to accept the license.")
                        continue
                    if not is_valid_email(email):
                        ui.err("Please enter a valid email address.")
                        continue
                    ui.good("License accepted with email verification!")
                    track_license_acceptance(email)
                    break
            break

        if response in decline_responses:
            ui.handle_license_decline()

        ui.notify_invalid_response()
