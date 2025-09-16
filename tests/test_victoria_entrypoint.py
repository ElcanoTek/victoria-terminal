"""Tests for the victoria_entrypoint module."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

import victoria_entrypoint as entrypoint


def test_parse_env_file_handles_comments(tmp_path: Path) -> None:
    env_path = tmp_path / entrypoint.ENV_FILENAME
    env_path.write_text(
        "FOO=bar\n" "# comment\n" "MALFORMED\n" 'QUOTED="some value"\n',
        encoding="utf-8",
    )

    values = entrypoint.parse_env_file(env_path)

    assert values == {"FOO": "bar", "QUOTED": "some value"}


def test_parse_env_file_missing_returns_empty(tmp_path: Path) -> None:
    env_path = tmp_path / entrypoint.ENV_FILENAME

    assert entrypoint.parse_env_file(env_path) == {}


def test_load_environment_preserves_existing_values(tmp_path: Path) -> None:
    env_path = tmp_path / entrypoint.ENV_FILENAME
    env_path.write_text("FOO=bar\nSHARED=value\n", encoding="utf-8")

    custom_env = {"SHARED": "existing"}

    values = entrypoint.load_environment(app_home=tmp_path, env=custom_env)

    assert values == {"FOO": "bar", "SHARED": "value"}
    assert custom_env["FOO"] == "bar"
    assert custom_env["SHARED"] == "existing"


def test_load_environment_returns_empty_when_file_absent(tmp_path: Path) -> None:
    assert entrypoint.load_environment(app_home=tmp_path, env={}) == {}


def test_substitute_env_handles_nested_structures() -> None:
    payload = {
        "list": ["${FIRST}", {"second": "${SECOND}"}, "plain"],
        "missing": "${MISSING}",
    }
    env = {"FIRST": "one", "SECOND": "two"}

    substituted = entrypoint.substitute_env(payload, env)

    assert substituted["list"][0] == "one"
    assert substituted["list"][1]["second"] == "two"
    assert substituted["list"][2] == "plain"
    assert substituted["missing"] == "${MISSING}"


def test_substitute_env_uses_process_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TOKEN", "value")

    assert entrypoint.substitute_env("${TOKEN}") == "value"


def test_generate_crush_config_substitutes_env(tmp_path: Path) -> None:
    env_values = {
        "OPENROUTER_API_KEY": "test-key",
        "SNOWFLAKE_ACCOUNT": "acct",
        "SNOWFLAKE_USER": "user",
        "SNOWFLAKE_PASSWORD": "password",
        "SNOWFLAKE_WAREHOUSE": "warehouse",
        "SNOWFLAKE_ROLE": "role",
        "VICTORIA_HOME": str(tmp_path),
    }

    template = entrypoint.resource_path(entrypoint.CRUSH_TEMPLATE)
    output = entrypoint.generate_crush_config(
        app_home=tmp_path, env=env_values, template_path=template
    )

    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["providers"]["openrouter"]["api_key"] == "test-key"

    assert data["lsp"]["python"]["command"] == "python -m pylsp"

    motherduck_cmd = data["mcp"]["motherduck"]["command"]
    assert motherduck_cmd[-1] == str(tmp_path / "adtech.duckdb")

    snowflake_cmd = data["mcp"]["snowflake"]["command"]
    assert snowflake_cmd == [
        "python",
        "-m",
        "mcp_snowflake_server",
        "--account",
        "acct",
        "--warehouse",
        "warehouse",
        "--user",
        "user",
        "--password",
        "password",
        "--role",
        "role",
    ]


def test_generate_crush_config_missing_template_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        entrypoint.generate_crush_config(app_home=tmp_path, template_path=tmp_path / "missing.json")


def test_ensure_app_home_copies_support_files(tmp_path: Path, mocker: pytest.MockFixture) -> None:
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    support_file = source_dir / "sample.txt"
    support_file.write_text("documentation", encoding="utf-8")

    destination = tmp_path / "dest"

    mocker.patch("victoria_entrypoint.SUPPORT_FILES", (Path("sample.txt"),))
    mocker.patch("victoria_entrypoint.resource_path", return_value=support_file)

    result = entrypoint.ensure_app_home(app_home=destination)

    copied = destination / "sample.txt"
    assert result == destination
    assert copied.exists()
    assert copied.read_text(encoding="utf-8") == "documentation"


def test_snowflake_env_missing_reports_missing_values() -> None:
    env = {
        "SNOWFLAKE_ACCOUNT": "acct",
        "SNOWFLAKE_USER": "user",
    }

    missing = entrypoint.snowflake_env_missing(env)

    assert missing == [
        "SNOWFLAKE_PASSWORD",
        "SNOWFLAKE_WAREHOUSE",
        "SNOWFLAKE_ROLE",
    ]


def test_parse_args_accepts_custom_app_home(tmp_path: Path) -> None:
    args = entrypoint.parse_args(["--app-home", str(tmp_path), "--skip-launch"])

    assert args.app_home == tmp_path
    assert args.skip_launch is True


def test_main_honours_skip_launch(
    tmp_path: Path, mocker: pytest.MockFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("VICTORIA_HOME", raising=False)

    mocker.patch("victoria_entrypoint.initialize_colorama")
    mocker.patch("victoria_entrypoint.banner")
    ensure_app_home = mocker.patch(
        "victoria_entrypoint.ensure_app_home", side_effect=lambda path: path
    )
    load_environment = mocker.patch("victoria_entrypoint.load_environment")
    generate_config = mocker.patch("victoria_entrypoint.generate_crush_config")
    mocker.patch("victoria_entrypoint.check_snowflake_credentials")
    mocker.patch("victoria_entrypoint.remove_local_duckdb")
    mocker.patch("victoria_entrypoint.info")
    mocker.patch("victoria_entrypoint.preflight_crush")
    launch_crush = mocker.patch("victoria_entrypoint.launch_crush")

    entrypoint.main(["--skip-launch", "--app-home", str(tmp_path)])

    assert os.environ["VICTORIA_HOME"] == str(tmp_path)
    ensure_app_home.assert_called_once_with(tmp_path)
    load_environment.assert_called_once_with(tmp_path)
    generate_config.assert_called_once_with(app_home=tmp_path)
    launch_crush.assert_not_called()
