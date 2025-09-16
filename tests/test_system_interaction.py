import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from VictoriaTerminal import ensure_default_files, launch_crush
from victoria_entrypoint import ensure_configuration, parse_env_file, sync_shared_configuration


def test_sync_shared_configuration_copies_files(tmp_path):
    shared = tmp_path / "shared"
    shared.mkdir()
    env_src = shared / ".env"
    env_src.write_text("OPENROUTER_API_KEY=shared\n", encoding="utf-8")
    local = tmp_path / "local"

    changed = sync_shared_configuration(shared, local_home=local, _info=lambda msg: None)

    assert (local / ".env").exists()
    assert changed == [local / ".env"]


def test_sync_shared_configuration_respects_overwrite(tmp_path):
    shared = tmp_path / "shared"
    shared.mkdir()
    (shared / ".env").write_text("OPENROUTER_API_KEY=shared\n", encoding="utf-8")
    local = tmp_path / "local"
    local.mkdir()
    dest = local / ".env"
    dest.write_text("OPENROUTER_API_KEY=local\n", encoding="utf-8")

    skipped = sync_shared_configuration(shared, local_home=local, _info=lambda msg: None)
    assert skipped == []
    assert dest.read_text(encoding="utf-8") == "OPENROUTER_API_KEY=local\n"

    overwritten = sync_shared_configuration(
        shared, local_home=local, overwrite=True, _info=lambda msg: None
    )
    assert overwritten == [dest]
    assert dest.read_text(encoding="utf-8") == "OPENROUTER_API_KEY=shared\n"


def test_ensure_configuration_requires_interactive(tmp_path, mocker):
    env_path = tmp_path / ".env"
    warn = mocker.Mock()
    write = mocker.Mock()

    configured = ensure_configuration(
        interactive=False,
        _APP_HOME=tmp_path,
        _parse_env_file=lambda path: {},
        _write_env_file=write,
        _prompt_for_configuration=mocker.Mock(),
        _load_dotenv=mocker.Mock(),
        _good=mocker.Mock(),
        _info=mocker.Mock(),
        _warn=warn,
    )

    assert configured is False
    warn.assert_called_once()
    write.assert_not_called()
    assert not env_path.exists()


def test_ensure_configuration_uses_existing_env(tmp_path, mocker):
    env_path = tmp_path / ".env"
    env_path.write_text("OPENROUTER_API_KEY=existing\n", encoding="utf-8")
    info = mocker.Mock()
    load_dotenv_mock = mocker.Mock()

    configured = ensure_configuration(
        interactive=True,
        _APP_HOME=tmp_path,
        _parse_env_file=parse_env_file,
        _write_env_file=mocker.Mock(),
        _prompt_for_configuration=mocker.Mock(),
        _load_dotenv=load_dotenv_mock,
        _good=mocker.Mock(),
        _info=info,
        _warn=mocker.Mock(),
    )

    assert configured is True
    info.assert_called_once()
    load_dotenv_mock.assert_called_once()


def test_launch_tool_unix(mocker):
    mock_execvp = mocker.Mock()
    mock_sys_exit = mocker.Mock()
    mock_tool = mocker.Mock()
    mock_tool.command = "crush"

    fake_home = Path("/fake/home/Victoria")
    launch_crush(
        mock_tool,
        _APP_HOME=fake_home,
        _os_name="posix",
        _execvp=mock_execvp,
        _sys_exit=mock_sys_exit,
    )

    mock_execvp.assert_called_once_with("crush", ["crush", "-c", str(fake_home)])
    mock_sys_exit.assert_not_called()


def test_launch_tool_windows(mocker):
    mock_run = mocker.Mock(return_value=mocker.Mock(returncode=0))
    mock_sys_exit = mocker.Mock()
    mock_tool = mocker.Mock()
    mock_tool.command = "crush"

    fake_home = Path("/fake/home/Victoria")
    launch_crush(
        mock_tool,
        _APP_HOME=fake_home,
        _os_name="nt",
        _subprocess_run=mock_run,
        _sys_exit=mock_sys_exit,
    )

    mock_run.assert_called_once_with(["crush", "-c", str(fake_home)])
    mock_sys_exit.assert_not_called()


def test_launch_tool_not_found(mocker):
    mock_err = mocker.Mock()
    mock_sys_exit = mocker.Mock(side_effect=SystemExit(1))
    mock_tool = mocker.Mock()
    mock_tool.command = "crush"

    with pytest.raises(SystemExit) as excinfo:
        launch_crush(
            mock_tool,
            _os_name="posix",
            _execvp=mocker.Mock(side_effect=FileNotFoundError),
            _err=mock_err,
            _sys_exit=mock_sys_exit,
        )

    assert excinfo.value.code == 1
    mock_err.assert_called_with(
        "'crush' command not found in PATH. Rebuild the Victoria container or install the CLI in your environment."
    )


def test_ensure_default_files(mocker, tmp_path):
    mock_app_home = tmp_path / "Victoria"
    mock_app_home.mkdir()
    mock_resource_dir = tmp_path / "resources"
    mock_resource_dir.mkdir()

    (mock_app_home / "CRUSH.md").touch()

    mock_copy = mocker.Mock()

    def mock_resource_path_func(p):
        src_file = mock_resource_dir / p
        if not src_file.parent.exists():
            src_file.parent.mkdir(parents=True, exist_ok=True)
        src_file.touch()
        return src_file

    ensure_default_files(
        _APP_HOME=mock_app_home,
        _VICTORIA_FILE="VICTORIA.md",
        _resource_path=mock_resource_path_func,
        _shutil_copy=mock_copy,
    )

    assert mock_copy.call_count == 2
    copied_files = [call.args[1].name for call in mock_copy.call_args_list]
    assert "CRUSH.md" not in copied_files
    assert ".crushignore" in copied_files
    assert "VICTORIA.md" in copied_files
