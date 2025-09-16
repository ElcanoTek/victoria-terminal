import os
import pathlib
from unittest import mock

import pytest


class SimpleMocker:
    """Lightweight replacement for the ``pytest-mock`` fixture."""

    class _PatchProxy:
        def __init__(self, helper: "SimpleMocker") -> None:
            self._helper = helper

        def __call__(self, target: str, *args, **kwargs):
            patcher = mock.patch(target, *args, **kwargs)
            started = patcher.start()
            self._helper._patches.append(patcher)
            return started

        def object(self, target, attribute, *args, **kwargs):
            patcher = mock.patch.object(target, attribute, *args, **kwargs)
            started = patcher.start()
            self._helper._patches.append(patcher)
            return started

        def dict(self, in_dict, values=(), clear: bool = False):
            patcher = mock.patch.dict(in_dict, values, clear=clear)
            patcher.start()
            self._helper._patches.append(patcher)
            return patcher

    def __init__(self) -> None:
        self._patches: list[mock._patch] = []
        self.patch = SimpleMocker._PatchProxy(self)

    def stopall(self) -> None:
        for patcher in reversed(self._patches):
            patcher.stop()
        self._patches.clear()

    def Mock(self, *args, **kwargs):  # noqa: N802 - match pytest-mock API
        return mock.Mock(*args, **kwargs)

    def __getattr__(self, name):
        return getattr(mock, name)


@pytest.fixture
def mocker():
    helper = SimpleMocker()
    try:
        yield helper
    finally:
        helper.stopall()


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
