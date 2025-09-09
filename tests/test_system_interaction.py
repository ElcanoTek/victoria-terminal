import sys
from pathlib import Path
import pytest
from unittest.mock import MagicMock

# Add project root to path to allow importing victoria
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import victoria


@pytest.mark.parametrize(
    "platform_name, os_name, scripts",
    [
        ("darwin", "posix", ["install_prerequisites_macos.sh", "set_env_macos_linux.sh"]),
        ("linux", "posix", ["install_prerequisites_linux.sh", "set_env_macos_linux.sh"]),
        ("nt", "nt", ["install_prerequisites_windows.ps1", "set_env_windows.ps1"]),
    ],
)
def test_run_setup_scripts(mocker, platform_name, os_name, scripts):
    """Test that the correct setup scripts are called for each platform."""
    mock_run = mocker.Mock(return_value=mocker.Mock(returncode=0))
    fake_deps = Path("/fake/deps")
    mock_resource_path = mocker.Mock(return_value=fake_deps)

    victoria.run_setup_scripts(
        use_local_model=False,
        _resource_path=mock_resource_path,
        _subprocess_run=mock_run,
        _os_name=os_name,
        _sys_platform=platform_name,
    )

    if os_name == "nt":
        assert mock_run.call_count == 2
        # We can do more detailed checks here if needed
    else:
        assert mock_run.call_count == len(scripts)
        for i, script_name in enumerate(scripts):
            assert mock_run.call_args_list[i].args[0] == ["bash", str(fake_deps / script_name)]


def test_run_setup_scripts_skip_openrouter(mocker):
    """Test that the skip openrouter flag is passed correctly."""
    mock_run = mocker.Mock(return_value=mocker.Mock(returncode=0))
    fake_deps = Path("/fake/deps")
    mock_resource_path = mocker.Mock(return_value=fake_deps)

    victoria.run_setup_scripts(
        use_local_model=True,
        _resource_path=mock_resource_path,
        _subprocess_run=mock_run,
        _os_name="posix",
        _sys_platform="darwin",
    )

    assert mock_run.call_count == 2
    assert mock_run.call_args_list[0].args[0] == ["bash", str(fake_deps / "install_prerequisites_macos.sh")]
    assert mock_run.call_args_list[1].args[0] == ["bash", str(fake_deps / "set_env_macos_linux.sh"), "--skip-openrouter"]


def test_launch_tool_unix(mocker):
    """Test launch_tool on a Unix-like system."""
    mock_execvp = mocker.Mock()
    mock_sys_exit = mocker.Mock()
    mock_tool = mocker.Mock()
    mock_tool.command = "crush"

    fake_home = Path("/fake/home/Victoria")
    victoria.launch_crush(
        mock_tool,
        _APP_HOME=fake_home,
        _os_name="posix",
        _execvp=mock_execvp,
        _sys_exit=mock_sys_exit,
    )

    mock_execvp.assert_called_once_with("crush", ["crush", "-c", str(fake_home)])
    mock_sys_exit.assert_not_called()


def test_launch_tool_windows(mocker):
    """Test launch_tool on Windows."""
    mock_run = mocker.Mock(return_value=mocker.Mock(returncode=0))
    mock_sys_exit = mocker.Mock()
    mock_tool = mocker.Mock()
    mock_tool.command = "crush"

    fake_home = Path("/fake/home/Victoria")
    victoria.launch_crush(
        mock_tool,
        _APP_HOME=fake_home,
        _os_name="nt",
        _subprocess_run=mock_run,
        _sys_exit=mock_sys_exit,
    )

    mock_run.assert_called_once_with(["crush", "-c", str(fake_home)])
    mock_sys_exit.assert_not_called()


def test_launch_tool_not_found(mocker):
    """Test launch_tool when the command is not found."""
    mock_err = mocker.Mock()
    mock_sys_exit = mocker.Mock(side_effect=SystemExit(1))
    mock_tool = mocker.Mock()
    mock_tool.command = "crush"

    with pytest.raises(SystemExit) as excinfo:
        victoria.launch_crush(
            mock_tool,
            _os_name="posix",
            _execvp=mocker.Mock(side_effect=FileNotFoundError),
            _err=mock_err,
            _sys_exit=mock_sys_exit,
        )

    assert excinfo.value.code == 1
    mock_err.assert_called_with("'crush' command not found in PATH")


def test_ensure_default_files(mocker, tmp_path):
    """Test that default files are copied if they don't exist."""
    mock_app_home = tmp_path / "Victoria"
    mock_app_home.mkdir()
    mock_resource_dir = tmp_path / "resources"
    mock_resource_dir.mkdir()

    # Create one of the destination files to test the if condition
    (mock_app_home / "CRUSH.md").touch()

    mock_copy = mocker.Mock()

    def mock_resource_path_func(p):
        # Create the source file so src.exists() is true
        src_file = mock_resource_dir / p
        # The parent dir for VICTORIA.md doesn't have a 'configs/crush' structure
        if not src_file.parent.exists():
            src_file.parent.mkdir(parents=True, exist_ok=True)
        src_file.touch()
        return src_file

    victoria.ensure_default_files(
        _APP_HOME=mock_app_home,
        _CONFIGS_DIR=Path("configs"),
        _VICTORIA_FILE="VICTORIA.md",
        _resource_path=mock_resource_path_func,
        _shutil_copy=mock_copy,
    )

    assert mock_copy.call_count == 2
    # Check that CRUSH.md was not copied because it already exists at the destination
    copied_files = [call.args[1].name for call in mock_copy.call_args_list]
    assert "CRUSH.md" not in copied_files
    assert ".crushignore" in copied_files
    assert "VICTORIA.md" in copied_files


def test_preflight_tool_missing(mocker):
    """Test preflight check when the tool is missing."""
    mock_err = mocker.Mock()
    mock_sys_exit = mocker.Mock(side_effect=SystemExit(1))
    mock_tool = mocker.Mock()
    mock_tool.command = "crush"

    with pytest.raises(SystemExit) as excinfo:
        victoria.preflight_crush(
            mock_tool,
            use_local_model=False,
            just_installed=False,
            _which=lambda cmd: None,
            _err=mock_err,
            _sys_exit=mock_sys_exit,
            _Progress=MagicMock(),  # Mock Progress to avoid terminal output
        )

    assert excinfo.value.code == 1
    mock_err.assert_called_with("Missing 'crush' command-line tool. Run first-time setup or install it manually.")


def test_preflight_tool_missing_just_installed(mocker):
    """Test preflight exits gracefully if tool is missing but was just installed."""
    mock_restart_app = mocker.Mock(side_effect=SystemExit(0))
    mock_tool = mocker.Mock()
    mock_tool.command = "crush"

    with pytest.raises(SystemExit) as excinfo:
        victoria.preflight_crush(
            mock_tool,
            use_local_model=False,
            just_installed=True,
            _which=lambda cmd: None,
            _Progress=MagicMock(),
            _restart_app=mock_restart_app,
        )

    assert excinfo.value.code == 0
    mock_restart_app.assert_called_once()


def test_restart_app_windows(mocker):
    """Test that restart_app on Windows calls Popen correctly."""
    mock_popen = mocker.Mock()
    mock_exit = mocker.Mock(side_effect=SystemExit(0))
    mock_sys_executable = "C:\\Python\\python.exe"
    mock_sys_argv = ["victoria.py", "--foo"]

    with pytest.raises(SystemExit):
        victoria.restart_app(
            _sys_executable=mock_sys_executable,
            _sys_argv=mock_sys_argv,
            _os_name="nt",
            _subprocess_Popen=mock_popen,
            _sys_exit=mock_exit,
            _info=lambda msg: None,
        )

    mock_popen.assert_called_once_with([mock_sys_executable] + mock_sys_argv)
    mock_exit.assert_called_once_with(0)


def test_restart_app_unix(mocker):
    """Test that restart_app on a Unix-like system calls execv correctly."""
    mock_execv = mocker.Mock()
    mock_sys_executable = "/usr/bin/python"
    mock_sys_argv = ["victoria.py", "--bar"]

    # We don't expect this to exit, as execv replaces the process
    victoria.restart_app(
        _sys_executable=mock_sys_executable,
        _sys_argv=mock_sys_argv,
        _os_name="posix",
        _os_execv=mock_execv,
        _sys_exit=mocker.Mock(),
        _info=lambda msg: None,
    )

    mock_execv.assert_called_once_with(mock_sys_executable, mock_sys_argv)
