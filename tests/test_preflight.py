#!/usr/bin/env python3
import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location("victoria", Path(__file__).resolve().parent.parent / "victoria.py")
victoria = importlib.util.module_from_spec(spec)
spec.loader.exec_module(victoria)


def _mock_which(cmd: str) -> str:
    return "/bin/true"


def test_preflight_requires_key_when_not_local(monkeypatch):
    monkeypatch.setattr(victoria, "which", _mock_which)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    with pytest.raises(SystemExit):
        victoria.preflight(False)


def test_preflight_allows_local_without_key(monkeypatch):
    monkeypatch.setattr(victoria, "which", _mock_which)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    victoria.preflight(True)
