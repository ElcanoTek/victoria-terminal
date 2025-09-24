# Copyright (c) 2025 ElcanoTek
#
# This file is part of Victoria Terminal.
#
# This software is licensed under the Business Source License 1.1.
# You may not use this file except in compliance with the license.
# You may obtain a copy of the license at
#
#     https://github.com/ElcanoTek/victoria-terminal/blob/main/LICENSE
#
# Change Date: 2027-09-20
# Change License: GNU General Public License v3.0 or later

"""Tests for the victoria_terminal module."""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

import victoria_terminal as entrypoint


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


def test_load_environment_returns_empty_when_file_absent(tmp_path: Path, mocker: pytest.MockFixture) -> None:
    warn = mocker.patch.object(entrypoint, "warn")

    assert entrypoint.load_environment(app_home=tmp_path, env={}) == {}
    warn.assert_called_once()


def test_load_environment_reports_missing_keys(tmp_path: Path, mocker: pytest.MockFixture) -> None:
    env_path = tmp_path / entrypoint.ENV_FILENAME
    env_path.write_text("# empty file\n", encoding="utf-8")
    env: dict[str, str] = {}
    warn = mocker.patch.object(entrypoint, "warn")

    entrypoint.load_environment(app_home=tmp_path, env=env)

    warn.assert_called_with(
        "The following API keys are missing. Update your .env file to enable " "these integrations: OPENROUTER_API_KEY"
    )


def test_load_environment_uses_values_from_env_file(tmp_path: Path, mocker: pytest.MockFixture) -> None:
    env_path = tmp_path / entrypoint.ENV_FILENAME
    env_path.write_text("OPENROUTER_API_KEY=from-file\n", encoding="utf-8")
    env: dict[str, str] = {}
    info = mocker.patch.object(entrypoint, "info")
    warn = mocker.patch.object(entrypoint, "warn")

    entrypoint.load_environment(app_home=tmp_path, env=env)

    assert env["OPENROUTER_API_KEY"] == "from-file"
    info.assert_any_call(f"Using API keys from {env_path}.")
    warn.assert_not_called()


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
        "VICTORIA_HOME": str(tmp_path),
    }

    template = entrypoint.resource_path(entrypoint.CRUSH_TEMPLATE)
    output = entrypoint.generate_crush_config(app_home=tmp_path, env=env_values, template_path=template)

    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["providers"]["openrouter"]["api_key"] == "test-key"

    python_lsp = data["lsp"]["python"]
    assert python_lsp["command"] == "python"
    assert python_lsp["args"] == ["-m", "pylsp"]
    assert "typescript" not in data["lsp"]

    motherduck_cfg = data["mcp"]["motherduck"]
    assert motherduck_cfg["command"] == "uvx"
    assert motherduck_cfg["args"] == [
        "mcp-server-motherduck",
        "--db-path",
        str(tmp_path / "adtech.duckdb"),
    ]
    assert "browserbase" not in data["mcp"]
    assert "gamma" not in data["mcp"]


def test_generate_crush_config_includes_browserbase_when_configured(tmp_path: Path) -> None:
    env_values = {
        "OPENROUTER_API_KEY": "test-key",
        "VICTORIA_HOME": str(tmp_path),
        "SMITHERY_BROWSERBASE_URL": "https://server.smithery.ai/@agent/browserbase",
    }

    template = entrypoint.resource_path(entrypoint.CRUSH_TEMPLATE)
    output = entrypoint.generate_crush_config(app_home=tmp_path, env=env_values, template_path=template)

    data = json.loads(output.read_text(encoding="utf-8"))
    browserbase_cfg = data["mcp"].get("browserbase")
    assert browserbase_cfg is not None
    assert browserbase_cfg["url"] == env_values["SMITHERY_BROWSERBASE_URL"]


def test_generate_crush_config_ignores_placeholder_browserbase_url(tmp_path: Path) -> None:
    env_values = {
        "OPENROUTER_API_KEY": "test-key",
        "VICTORIA_HOME": str(tmp_path),
        "SMITHERY_BROWSERBASE_URL": "https://<your-personal-smithery-url-here>",
    }

    template = entrypoint.resource_path(entrypoint.CRUSH_TEMPLATE)
    output = entrypoint.generate_crush_config(app_home=tmp_path, env=env_values, template_path=template)

    data = json.loads(output.read_text(encoding="utf-8"))
    assert "browserbase" not in data["mcp"]


def test_generate_crush_config_ignores_blank_browserbase_url(tmp_path: Path) -> None:
    env_values = {
        "OPENROUTER_API_KEY": "test-key",
        "VICTORIA_HOME": str(tmp_path),
        "SMITHERY_BROWSERBASE_URL": "   ",
    }

    template = entrypoint.resource_path(entrypoint.CRUSH_TEMPLATE)
    output = entrypoint.generate_crush_config(app_home=tmp_path, env=env_values, template_path=template)

    data = json.loads(output.read_text(encoding="utf-8"))
    assert "browserbase" not in data["mcp"]


def test_generate_crush_config_sets_gamma_paths(tmp_path: Path, mocker: pytest.MockFixture) -> None:
    env_values = {
        "OPENROUTER_API_KEY": "test-key",
        "VICTORIA_HOME": str(tmp_path),
        "GAMMA_API_KEY": "gamma-key",
    }

    template = entrypoint.resource_path(entrypoint.CRUSH_TEMPLATE)

    gamma_dir = tmp_path / "bundle"
    gamma_dir.mkdir()
    gamma_script = gamma_dir / "gamma-mcp.py"
    gamma_script.write_text("#!/usr/bin/env python3\n", encoding="utf-8")

    original_resource_path = entrypoint.resource_path

    def fake_resource_path(name: str | Path) -> Path:
        if Path(name) == Path("gamma-mcp.py"):
            return gamma_script
        return original_resource_path(name)

    mocker.patch("victoria_terminal.resource_path", side_effect=fake_resource_path)

    output = entrypoint.generate_crush_config(app_home=tmp_path, env=env_values, template_path=template)

    data = json.loads(output.read_text(encoding="utf-8"))
    gamma_cfg = data["mcp"]["gamma"]
    assert gamma_cfg["args"] == [str(gamma_script)]
    assert gamma_cfg["cwd"] == str(gamma_dir)
    assert gamma_cfg["env"]["PYTHONPATH"] == str(gamma_dir)
    assert gamma_cfg["env"]["GAMMA_API_KEY"] == env_values["GAMMA_API_KEY"]


def test_generate_crush_config_missing_template_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        entrypoint.generate_crush_config(app_home=tmp_path, template_path=tmp_path / "missing.json")


def test_resolve_license_path_uses_resource_bundle(
    tmp_path: Path, mocker: pytest.MockFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("VICTORIA_LICENSE_PATH", raising=False)
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    license_file = bundle_dir / entrypoint.LICENSE_FILE_NAME
    license_file.write_text("terms", encoding="utf-8")

    mocker.patch.object(entrypoint, "resource_path", return_value=license_file)

    assert entrypoint._resolve_license_path() == license_file


def test_resolve_license_path_prefers_env_override(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    env_license = tmp_path / "custom-license.txt"
    env_license.write_text("terms", encoding="utf-8")
    monkeypatch.setenv("VICTORIA_LICENSE_PATH", str(env_license))

    assert entrypoint._resolve_license_path() == env_license


def test_resolve_license_path_raises_when_missing(
    tmp_path: Path, mocker: pytest.MockFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("VICTORIA_LICENSE_PATH", raising=False)
    mocker.patch.object(entrypoint, "resource_path", return_value=tmp_path / "missing")

    with pytest.raises(FileNotFoundError):
        entrypoint._resolve_license_path()


def test_ensure_app_home_copies_support_files(tmp_path: Path, mocker: pytest.MockFixture) -> None:
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    support_file = source_dir / "sample.txt"
    support_file.write_text("documentation", encoding="utf-8")

    destination = tmp_path / "dest"

    mocker.patch("victoria_terminal.SUPPORT_FILES", (Path("sample.txt"),))
    mocker.patch("victoria_terminal.resource_path", return_value=support_file)

    result = entrypoint.ensure_app_home(app_home=destination)

    copied = destination / "sample.txt"
    assert result == destination
    assert copied.exists()
    assert copied.read_text(encoding="utf-8") == "documentation"


def test_ensure_app_home_overwrites_victoria_manifest(tmp_path: Path, mocker: pytest.MockFixture) -> None:
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    manifest = source_dir / "VICTORIA.md"
    manifest.write_text("container version", encoding="utf-8")

    destination = tmp_path / "dest"
    destination.mkdir()
    existing_manifest = destination / "VICTORIA.md"
    existing_manifest.write_text("host edits", encoding="utf-8")

    mocker.patch("victoria_terminal.SUPPORT_FILES", (Path("VICTORIA.md"),))
    mocker.patch("victoria_terminal.resource_path", return_value=manifest)

    entrypoint.ensure_app_home(app_home=destination)

    assert existing_manifest.read_text(encoding="utf-8") == "container version"


def test_parse_args_accepts_custom_app_home(tmp_path: Path) -> None:
    args = entrypoint.parse_args(["--app-home", str(tmp_path), "--skip-launch"])

    assert args.app_home == tmp_path
    assert args.skip_launch is True


def test_parse_args_ignores_double_dash_separator() -> None:
    args = entrypoint.parse_args(["--", "--skip-launch"])

    assert args.skip_launch is True


def test_parse_args_sets_no_banner_flag() -> None:
    args = entrypoint.parse_args(["--no-banner"])

    assert args.no_banner is True


def test_parse_args_sets_acccept_license_flag() -> None:
    args = entrypoint.parse_args(["--acccept-license"])

    assert args.acccept_license is True


def test_main_honours_skip_launch(tmp_path: Path, mocker: pytest.MockFixture, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("VICTORIA_HOME", raising=False)

    mocker.patch("victoria_terminal.initialize_colorama")
    banner_sequence = mocker.patch("victoria_terminal.banner_sequence")
    ensure_app_home = mocker.patch("victoria_terminal.ensure_app_home", side_effect=lambda path: path)
    load_environment = mocker.patch("victoria_terminal.load_environment")
    generate_config = mocker.patch("victoria_terminal.generate_crush_config")
    mocker.patch("victoria_terminal.remove_local_duckdb")
    mocker.patch("victoria_terminal.info")
    mocker.patch("victoria_terminal.preflight_crush")
    launch_crush = mocker.patch("victoria_terminal.launch_crush")

    entrypoint.main(["--skip-launch", "--app-home", str(tmp_path)])

    assert os.environ["VICTORIA_HOME"] == str(tmp_path)
    ensure_app_home.assert_called_once_with(tmp_path)
    load_environment.assert_called_once_with(tmp_path)
    generate_config.assert_called_once_with(app_home=tmp_path)
    launch_crush.assert_not_called()
    banner_sequence.assert_called_once_with()


def test_main_skips_banner_when_flag_set(
    tmp_path: Path, mocker: pytest.MockFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("VICTORIA_HOME", raising=False)

    mocker.patch("victoria_terminal.initialize_colorama")
    banner_sequence = mocker.patch("victoria_terminal.banner_sequence")
    mocker.patch("victoria_terminal.ensure_app_home", side_effect=lambda path: path)
    mocker.patch("victoria_terminal.load_environment")
    mocker.patch("victoria_terminal.generate_crush_config")
    mocker.patch("victoria_terminal.remove_local_duckdb")
    mocker.patch("victoria_terminal.info")
    mocker.patch("victoria_terminal.preflight_crush")
    mocker.patch("victoria_terminal.launch_crush")
    persist_acceptance = mocker.patch("victoria_terminal._persist_license_acceptance")

    entrypoint.main(
        [
            "--skip-launch",
            "--no-banner",
            "--acccept-license",
            "--app-home",
            str(tmp_path),
        ]
    )

    banner_sequence.assert_not_called()
    persist_acceptance.assert_called_once_with(app_home=tmp_path)


def test_main_no_banner_requires_license_acceptance(
    tmp_path: Path, mocker: pytest.MockFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("VICTORIA_HOME", raising=False)

    mocker.patch("victoria_terminal.initialize_colorama")
    mocker.patch("victoria_terminal.ensure_app_home")
    mocker.patch("victoria_terminal.load_environment")
    mocker.patch("victoria_terminal.generate_crush_config")
    mocker.patch("victoria_terminal.remove_local_duckdb")
    mocker.patch("victoria_terminal.info")
    mocker.patch("victoria_terminal.preflight_crush")
    mocker.patch("victoria_terminal.launch_crush")
    err = mocker.patch("victoria_terminal.err")

    with pytest.raises(SystemExit) as excinfo:
        entrypoint.main(
            [
                "--skip-launch",
                "--no-banner",
                "--app-home",
                str(tmp_path),
            ]
        )

    assert excinfo.value.code == 2
    err.assert_called_once()
