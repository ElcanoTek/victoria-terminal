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

"""Automation for test and lint tasks."""
from __future__ import annotations

from pathlib import Path

import nox

PROJECT_ROOT = Path(__file__).parent
PYTHON_FILES = ["victoria_terminal.py", "tests", "noxfile.py"]

nox.options.sessions = ("lint", "tests")
nox.options.reuse_existing_virtualenvs = True


@nox.session
def lint(session: nox.Session) -> None:
    """Run formatters and static analysis."""

    session.install("black", "isort", "flake8")
    session.run("black", "--check", *PYTHON_FILES)
    session.run("isort", "--check-only", *PYTHON_FILES)
    session.run("flake8", *PYTHON_FILES)


@nox.session
def tests(session: nox.Session) -> None:
    """Execute the pytest suite."""

    session.install("-r", str(PROJECT_ROOT / "requirements.txt"))
    session.run("pytest", *session.posargs)
