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

"""Pytest fixtures for Victoria Terminal tests."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import TYPE_CHECKING

import pytest

# Ensure the project root is importable for tests without packaging the module.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Set VICTORIA_HOME before importing the modules
TEST_APP_HOME = Path(__file__).resolve().parent / ".victoria-test-home"
os.environ.setdefault("VICTORIA_HOME", str(TEST_APP_HOME))
TEST_APP_HOME.mkdir(parents=True, exist_ok=True)

# Import from submodules  # noqa: E402
from email_validator import EmailNotValidError  # noqa: E402

import configurator.license as license_module  # noqa: E402
from configurator.cli import launch_crush, parse_args  # noqa: E402
from configurator.config import (  # noqa: E402
    generate_crush_config,
    load_environment,
    parse_env_file,
    resource_path,
    substitute_env,
)
from configurator.constants import CRUSH_CONFIG_NAME, CRUSH_TEMPLATE, ENV_FILENAME  # noqa: E402

if TYPE_CHECKING:
    from typing import Any, Callable


@pytest.fixture
def victoria_home(tmp_path: Path) -> Path:
    """Provide an isolated home directory for each test."""
    home = tmp_path / "victoria-home"
    home.mkdir()
    return home


@pytest.fixture
def module() -> SimpleNamespace:
    """Provide a namespace with all tested functions."""
    return SimpleNamespace(
        # Config functions
        parse_env_file=parse_env_file,
        load_environment=load_environment,
        substitute_env=substitute_env,
        generate_crush_config=generate_crush_config,
        resource_path=resource_path,
        # CLI functions
        parse_args=parse_args,
        launch_crush=launch_crush,
        # License functions
        _is_valid_email=license_module.is_valid_email,
        _track_license_acceptance=license_module.track_license_acceptance,
        # Constants
        ENV_FILENAME=ENV_FILENAME,
        CRUSH_TEMPLATE=CRUSH_TEMPLATE,
        CRUSH_CONFIG_NAME=CRUSH_CONFIG_NAME,
        # For mocking
        os=os,
        EmailNotValidError=EmailNotValidError,
    )


@pytest.fixture
def env_file(victoria_home: Path) -> Callable[[str], Path]:
    """Factory fixture to create .env files with custom content."""

    def _create(content: str) -> Path:
        env_path = victoria_home / ENV_FILENAME
        env_path.write_text(content, encoding="utf-8")
        return env_path

    return _create


@pytest.fixture
def crush_template() -> Path:
    """Return the path to the crush template file."""
    return resource_path(CRUSH_TEMPLATE)


@pytest.fixture
def generated_config(victoria_home: Path, crush_template: Path) -> Callable[[dict[str, str]], dict[str, Any]]:
    """Factory fixture to generate crush config and return parsed JSON."""

    def _generate(env_values: dict[str, str]) -> dict[str, Any]:
        env_values.setdefault("VICTORIA_HOME", str(victoria_home))
        config_dir = generate_crush_config(
            app_home=victoria_home,
            env=env_values,
            template_path=crush_template,
        )
        output = config_dir / CRUSH_CONFIG_NAME
        return json.loads(output.read_text(encoding="utf-8"))

    return _generate


@pytest.fixture
def mock_execvp(monkeypatch: pytest.MonkeyPatch) -> list[list[str]]:
    """Mock os.execvp and capture called commands."""
    calls: list[list[str]] = []

    def fake_execvp(cmd: str, argv: list[str]) -> None:
        calls.append(argv)
        raise SystemExit(0)

    monkeypatch.setattr(os, "execvp", fake_execvp)
    return calls


@pytest.fixture
def mock_requests_post(monkeypatch: pytest.MonkeyPatch) -> list[dict[str, Any]]:
    """Mock requests.post and capture payloads."""
    payloads: list[dict[str, Any]] = []

    def fake_post(url: str, json: dict[str, Any], timeout: int) -> None:
        payloads.append(dict(json))

    monkeypatch.setattr(license_module.requests, "post", fake_post)
    return payloads


@pytest.fixture
def mock_email_valid(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock email validation to always succeed."""
    monkeypatch.setattr(license_module, "validate_email", lambda *args, **kwargs: None)


@pytest.fixture
def mock_email_invalid(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock email validation to always fail."""

    def always_fail(*args: object, **kwargs: object) -> None:
        raise EmailNotValidError("invalid")

    monkeypatch.setattr(license_module, "validate_email", always_fail)
