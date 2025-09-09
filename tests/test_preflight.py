#!/usr/bin/env python3
import importlib.util
from pathlib import Path
from unittest.mock import MagicMock

import pytest

spec = importlib.util.spec_from_file_location("victoria", Path(__file__).resolve().parent.parent / "victoria.py")
victoria = importlib.util.module_from_spec(spec)
spec.loader.exec_module(victoria)


def _mock_which(cmd: str) -> str:
    return "/bin/true"


def test_preflight_requires_key_when_not_local(mocker):
    mock_warn = mocker.Mock()
    mock_sys_exit = mocker.Mock(side_effect=SystemExit(1))
    with pytest.raises(SystemExit):
        victoria.preflight(
            use_local_model=False,
            just_installed=False,
            _which=_mock_which,
            _os_environ={},
            _warn=mock_warn,
            _sys_exit=mock_sys_exit,
            _Progress=MagicMock(),
        )
    mock_warn.assert_called_with("OPENROUTER_API_KEY not configured. Email brad@elcanotek.com to obtain one.")


def test_preflight_allows_local_without_key(mocker):
    mock_warn = mocker.Mock()
    mock_sys_exit = mocker.Mock()
    victoria.preflight(
        use_local_model=True,
        just_installed=False,
        _which=_mock_which,
        _os_environ={},
        _warn=mock_warn,
        _sys_exit=mock_sys_exit,
        _Progress=MagicMock(),
    )
    mock_warn.assert_not_called()
    mock_sys_exit.assert_not_called()
