import sys
from pathlib import Path
import pytest

# Add project root to path to allow importing victoria
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import victoria


@pytest.fixture
def full_mocks(mocker):
    """A fixture to provide a full set of mocks for victoria.main()."""
    mocker.patch.dict(victoria.TOOLS, {"crush": mocker.Mock()})

    args_mock = mocker.Mock()
    args_mock.tool = None
    args_mock.course = None
    args_mock.local_model = None # Set to None to test interactive menu
    args_mock.quiet = False

    mocks = {
        "_parse_args": mocker.Mock(return_value=args_mock),
        "_ensure_default_files": mocker.Mock(),
        "_banner": mocker.Mock(),
        "_local_model_menu": mocker.Mock(return_value=False),
        "_first_run_check": mocker.Mock(return_value=False),
        "_remove_local_duckdb": mocker.Mock(),
        "_course_menu": mocker.Mock(return_value="2"),
        "_tool_menu": mocker.Mock(return_value=victoria.TOOLS["crush"]),
        "_snowflake_env_missing": mocker.Mock(return_value=[]),
        "_generate_config": mocker.Mock(return_value=True),
        "_open_victoria_folder": mocker.Mock(),
        "_console": mocker.Mock(),
    }
    return mocks


def test_main_happy_path_local_files(full_mocks):
    """Test the main execution flow for the local files option."""
    victoria.main(**full_mocks)

    full_mocks["_local_model_menu"].assert_called_once()
    full_mocks["_first_run_check"].assert_called_once_with(False)
    victoria.TOOLS["crush"].preflight.assert_called_once_with(victoria.TOOLS["crush"], False)
    full_mocks["_course_menu"].assert_called_once()
    full_mocks["_generate_config"].assert_called_once_with(victoria.TOOLS["crush"], False, False)
    victoria.TOOLS["crush"].launcher.assert_called_once_with(victoria.TOOLS["crush"])
    full_mocks["_snowflake_env_missing"].assert_not_called()


def test_main_happy_path_snowflake(full_mocks):
    """Test the main execution flow for the Snowflake option."""
    full_mocks["_course_menu"].return_value = "1"
    full_mocks["_local_model_menu"].return_value = True

    victoria.main(**full_mocks)

    full_mocks["_course_menu"].assert_called_once()
    full_mocks["_snowflake_env_missing"].assert_called_once()
    full_mocks["_generate_config"].assert_called_once_with(victoria.TOOLS["crush"], True, True)
    victoria.TOOLS["crush"].launcher.assert_called_once_with(victoria.TOOLS["crush"])


def test_main_snowflake_missing_env_vars(full_mocks, mocker):
    """Test that the script exits if Snowflake env vars are missing."""
    mock_err = mocker.Mock()
    full_mocks["_course_menu"].return_value = "1"
    full_mocks["_snowflake_env_missing"].return_value = ["SNOWFLAKE_USER"]

    with pytest.raises(SystemExit) as excinfo:
        victoria.main(**full_mocks, _err=mock_err)

    assert excinfo.value.code == 1
    mock_err.assert_called_with("Missing Snowflake environment variables:")
    full_mocks["_console"].print.assert_called_with("  [red]SNOWFLAKE_USER")
    full_mocks["_generate_config"].assert_not_called()
    victoria.TOOLS["crush"].launcher.assert_not_called()


def test_main_config_generation_fails(full_mocks):
    """Test that the script exits if config generation fails."""
    full_mocks["_generate_config"].return_value = False

    with pytest.raises(SystemExit) as excinfo:
        victoria.main(**full_mocks)

    assert excinfo.value.code == 1
    victoria.TOOLS["crush"].launcher.assert_not_called()

def test_main_quiet_mode(full_mocks, mocker):
    """Test that quiet mode suppresses informational messages."""
    full_mocks["_parse_args"].return_value.quiet = True
    mock_info = mocker.patch("victoria.info")

    victoria.main(**full_mocks)

    mock_info.assert_not_called()


def test_main_unknown_tool(full_mocks, mocker):
    """Test that the script exits if an unknown tool is specified."""
    full_mocks["_parse_args"].return_value.tool = "unknown_tool"
    mock_err = mocker.Mock()

    with pytest.raises(SystemExit) as excinfo:
        victoria.main(**full_mocks, _err=mock_err)

    assert excinfo.value.code == 1
    mock_err.assert_called_with("Unknown tool: unknown_tool")
