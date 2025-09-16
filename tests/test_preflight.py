import sys
from pathlib import Path
from unittest.mock import Mock

import pytest

# Add project root to path to allow importing victoria
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from VictoriaTerminal import Tool, preflight_crush


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
            _which=lambda cmd: None,
            _err=mock_err,
            _sys_exit=mock_sys_exit,
        )

    assert excinfo.value.code == 1
    mock_err.assert_called_with(
        "Missing 'crush' command-line tool. Rebuild the Victoria container or install the CLI in your environment."
    )
def test_preflight_warns_when_key_missing(mocker, mock_tool):
    """Preflight should warn about missing OpenRouter credentials but continue."""

    mock_warn = mocker.Mock()
    mock_sys_exit = mocker.Mock()

    preflight_crush(
        mock_tool,
        _which=lambda cmd: "/bin/crush",
        _os_environ={},
        _warn=mock_warn,
        _sys_exit=mock_sys_exit,
    )

    mock_warn.assert_called_once()
    mock_sys_exit.assert_not_called()


def test_preflight_reports_key_present(mocker, mock_tool):
    """A configured API key should be acknowledged."""

    mock_good = mocker.Mock()

    preflight_crush(
        mock_tool,
        _which=lambda cmd: "/bin/crush",
        _os_environ={"OPENROUTER_API_KEY": "fake-key"},
        _good=mock_good,
    )

    assert any("OpenRouter API key configured" in str(call.args[0]) for call in mock_good.call_args_list)
