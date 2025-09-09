import os
import pytest
import pathlib

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
