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

import os
import pathlib
import sys
from pathlib import Path

import pytest

# Ensure the project root is importable for tests without packaging the module.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


@pytest.fixture(autouse=True)
def force_posix_path(monkeypatch):
    """
    On non-Windows systems, pytest can crash with a NotImplementedError when
    trying to report a test failure that involves a test where os.name is
    mocked to 'nt'. This fixture prevents the crash by ensuring that
    pathlib.Path always resolves to PosixPath.
    """
    if os.name != "nt":
        monkeypatch.setattr(pathlib, "Path", pathlib.PosixPath)
