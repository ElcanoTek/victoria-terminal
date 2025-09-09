import sys
from pathlib import Path
import pytest

# Add project root to path to allow importing victoria
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from VictoriaConfigurator import first_run_check
from VictoriaTerminal import local_model_menu, course_menu, tool_menu


def test_local_model_menu_yes(mocker):
    """Test local_model_menu returns True when user enters 'y'."""
    mocker.patch("rich.prompt.Prompt.ask", return_value="y")
    assert local_model_menu() is True


def test_local_model_menu_no(mocker):
    """Test local_model_menu returns False when user enters 'n'."""
    mocker.patch("rich.prompt.Prompt.ask", return_value="n")
    assert local_model_menu() is False


def test_course_menu_one(mocker):
    """Test course_menu returns '1'."""
    mocker.patch("rich.prompt.Prompt.ask", return_value="1")
    assert course_menu() == "1"


def test_course_menu_two(mocker):
    """Test course_menu returns '2'."""
    mocker.patch("rich.prompt.Prompt.ask", return_value="2")
    assert course_menu() == "2"


def test_first_run_check_sentinel_exists(mocker):
    """Test first_run_check returns False if sentinel file exists."""
    mock_sentinel = mocker.Mock()
    mock_sentinel.exists.return_value = True
    mock_ask = mocker.Mock()
    mock_info = mocker.Mock()

    result = first_run_check(
        use_local_model=False,
        _SETUP_SENTINEL=mock_sentinel,
        _Prompt_ask=mock_ask,
        _info=mock_info,
    )
    assert result is False
    mock_ask.assert_not_called()
    mock_info.assert_called_once()


def test_first_run_check_user_says_no(mocker):
    """Test first_run_check returns False if user says no to setup."""
    mock_run_setup = mocker.Mock()
    mock_sentinel = mocker.Mock()
    mock_sentinel.exists.return_value = False
    mock_prompt_ask = mocker.Mock(return_value="n")

    result = first_run_check(
        use_local_model=False,
        _run_setup_scripts=mock_run_setup,
        _SETUP_SENTINEL=mock_sentinel,
        _Prompt_ask=mock_prompt_ask,
    )
    assert result is False
    mock_run_setup.assert_not_called()


def test_first_run_check_user_says_yes(mocker):
    """Test first_run_check runs setup and returns True if user says yes."""
    mock_run_setup = mocker.Mock()
    mock_sentinel = mocker.Mock()
    mock_sentinel.exists.return_value = False
    mock_prompt_ask = mocker.Mock(return_value="y")
    mock_update_path = mocker.Mock()
    mock_good = mocker.Mock()

    result = first_run_check(
        use_local_model=True,
        _run_setup_scripts=mock_run_setup,
        _SETUP_SENTINEL=mock_sentinel,
        _Prompt_ask=mock_prompt_ask,
        _update_path_from_install=mock_update_path,
        _good=mock_good,
    )

    assert result is True
    mock_run_setup.assert_called_once_with(True)
    mock_sentinel.write_text.assert_called_once_with("done")
    mock_update_path.assert_called_once()
    mock_good.assert_called_once()


def test_tool_menu_multiple_tools(mocker):
    """Test the tool selection menu with multiple tools."""
    mock_prompt = mocker.patch("rich.prompt.Prompt.ask", return_value="2")

    tool1 = mocker.Mock()
    tool1.name = "Tool 1"
    tool2 = mocker.Mock()
    tool2.name = "Tool 2"

    tools = {"tool1": tool1, "tool2": tool2}

    selected_tool = tool_menu(tools)

    assert selected_tool == tool2
    mock_prompt.assert_called_once_with("Select a tool", choices=["1", "2"], default="1")
