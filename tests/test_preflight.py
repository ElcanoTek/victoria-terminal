import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock

import pytest

# Add project root to path to allow importing victoria
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from VictoriaTerminal import preflight_crush, Tool


@pytest.fixture
def mock_tool(mocker):
    """Fixture for a mocked Tool object."""
    tool = Mock(spec=Tool)
    tool.command = "crush"
    return tool


def test_preflight_fails_if_command_missing(mocker, mock_tool):
    """Test that preflight fails if the command-line tool is not found."""
    mock_err = mocker.Mock()
    mock_sys_exit = mocker.Mock(side_effect=SystemExit(1))

    with pytest.raises(SystemExit) as excinfo:
        preflight_crush(
            mock_tool,
            use_local_model=False,
            _which=lambda cmd: None,
            _err=mock_err,
            _sys_exit=mock_sys_exit,
            _Progress=MagicMock(),
        )

    assert excinfo.value.code == 1
    mock_err.assert_called_with("Missing 'crush' command-line tool. Please run the Victoria Configurator first.")


def test_preflight_requires_key_when_not_local(mocker, mock_tool):
    """Test that preflight fails if OPENROUTER_API_KEY is missing for non-local models."""
    mock_warn = mocker.Mock()
    mock_sys_exit = mocker.Mock(side_effect=SystemExit(1))

    with pytest.raises(SystemExit) as excinfo:
        preflight_crush(
            mock_tool,
            use_local_model=False,
            _which=lambda cmd: "/bin/crush",
            _os_environ={},
            _warn=mock_warn,
            _sys_exit=mock_sys_exit,
            _Progress=MagicMock(),
        )

    assert excinfo.value.code == 1
    mock_warn.assert_called_with("OPENROUTER_API_KEY not configured. Please run the Victoria Configurator to set it up.")


def test_preflight_allows_local_without_key(mocker, mock_tool):
    """Test that preflight succeeds without an API key for local models."""
    mock_sys_exit = mocker.Mock()

    preflight_crush(
        mock_tool,
        use_local_model=True,
        _which=lambda cmd: "/bin/crush",
        _os_environ={},
        _sys_exit=mock_sys_exit,
        _Progress=MagicMock(),
    )

    mock_sys_exit.assert_not_called()


def test_preflight_succeeds_with_key_and_command(mocker, mock_tool):
    """Test the happy path where command exists and key is present."""
    mock_sys_exit = mocker.Mock()
    mock_env = {"OPENROUTER_API_KEY": "fake-key"}

    preflight_crush(
        mock_tool,
        use_local_model=False,
        _which=lambda cmd: "/bin/crush",
        _os_environ=mock_env,
        _sys_exit=mock_sys_exit,
        _Progress=MagicMock(),
    )

    mock_sys_exit.assert_not_called()
