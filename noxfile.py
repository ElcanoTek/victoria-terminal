"""Automation for test and lint tasks."""

from __future__ import annotations

from pathlib import Path

import nox

PROJECT_ROOT = Path(__file__).parent
PYTHON_FILES = ["victoria_entrypoint.py", "tests", "noxfile.py"]

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
