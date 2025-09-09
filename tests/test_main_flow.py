import sys
from pathlib import Path
import pytest
from unittest.mock import MagicMock

# Add project root to path to allow importing scripts
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from VictoriaTerminal import main as terminal_main, TOOL


@pytest.fixture
def full_mocks(mocker):
    """A fixture to provide a full set of mocks for VictoriaTerminal.main()."""
    # Replace the SETUP_SENTINEL object in the module where it's used
    mock_sentinel = MagicMock()
    mock_sentinel.exists.return_value = True
    mocker.patch('VictoriaTerminal.SETUP_SENTINEL', mock_sentinel)

    # Patch sys.argv to prevent argparse from reading pytest's args
    mocker.patch.object(sys, 'argv', ['VictoriaTerminal.py'])

    args_mock = MagicMock()
    args_mock.course = None
    args_mock.local_model = None
    args_mock.quiet = False

    # The mocks are returned in a dictionary to be passed to main()
    mocks = {
        "_parse_args": MagicMock(return_value=args_mock),
        "_ensure_default_files": MagicMock(),
        "_banner": MagicMock(),
        "_local_model_menu": MagicMock(return_value=False),
        "_remove_local_duckdb": MagicMock(),
        "_course_menu": MagicMock(return_value="2"),
        "_snowflake_env_missing": MagicMock(return_value=[]),
        "_generate_config": MagicMock(return_value=True),
        "_open_victoria_folder": MagicMock(),
        "_console": MagicMock(),
        "_err": MagicMock(),
        "_info": MagicMock()
    }

    # We create a mock tool and have the tool_menu return it.
    mock_tool = MagicMock()

    # We still need to patch the TOOL object as it's not a parameter to main,
    # and we need to access it for assertions.
    mocker.patch('VictoriaTerminal.TOOL', mock_tool)

    return mocks, args_mock, mock_tool


def test_main_happy_path_local_files(full_mocks):
    """Test the main execution flow for the local files option."""
    mocks, _, mock_tool = full_mocks
    terminal_main(**mocks)

    mocks["_local_model_menu"].assert_called_once()
    mock_tool.preflight.assert_called_once_with(mock_tool, False)
    mocks["_course_menu"].assert_called_once()
    mocks["_generate_config"].assert_called_once_with(mock_tool, False, False)
    mock_tool.launcher.assert_called_once_with(mock_tool)
    mocks["_snowflake_env_missing"].assert_not_called()


def test_main_happy_path_snowflake(full_mocks):
    """Test the main execution flow for the Snowflake option."""
    mocks, _, mock_tool = full_mocks
    mocks["_course_menu"].return_value = "1"
    mocks["_local_model_menu"].return_value = True

    terminal_main(**mocks)

    mocks["_course_menu"].assert_called_once()
    mocks["_snowflake_env_missing"].assert_called_once()
    mocks["_generate_config"].assert_called_once_with(mock_tool, True, True)
    mock_tool.launcher.assert_called_once_with(mock_tool)


def test_main_snowflake_missing_env_vars(full_mocks):
    """Test that the script exits if Snowflake env vars are missing."""
    mocks, _, mock_tool = full_mocks
    mocks["_course_menu"].return_value = "1"
    mocks["_snowflake_env_missing"].return_value = ["SNOWFLAKE_USER"]

    with pytest.raises(SystemExit) as excinfo:
        terminal_main(**mocks)

    assert excinfo.value.code == 1
    mocks["_err"].assert_called_with("Missing Snowflake environment variables:")
    mocks["_console"].print.assert_called_with("  [red]SNOWFLAKE_USER")
    mocks["_generate_config"].assert_not_called()
    mock_tool.launcher.assert_not_called()


def test_main_config_generation_fails(full_mocks):
    """Test that the script exits if config generation fails."""
    mocks, _, mock_tool = full_mocks
    mocks["_generate_config"].return_value = False

    with pytest.raises(SystemExit) as excinfo:
        terminal_main(**mocks)

    assert excinfo.value.code == 1
    mock_tool.launcher.assert_not_called()


def test_main_quiet_mode(full_mocks):
    """Test that quiet mode suppresses informational messages."""
    mocks, args_mock, _ = full_mocks
    args_mock.quiet = True

    terminal_main(**mocks)

    mocks["_open_victoria_folder"].assert_not_called()


def test_main_setup_not_run(full_mocks, mocker):
    """Test that the script exits if setup has not been run."""
    mocks, _, _ = full_mocks
    mocks["_err"].reset_mock() # Reset from other tests

    # Have the sentinel mock return False for this test
    mocker.patch('VictoriaTerminal.SETUP_SENTINEL.exists', return_value=False)

    with pytest.raises(SystemExit) as excinfo:
        terminal_main(**mocks)

    assert excinfo.value.code == 1
    mocks["_err"].assert_called_with("First-time setup has not been completed. Please run the Victoria Configurator first.")
