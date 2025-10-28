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
from typing import Mapping

import pytest

TEST_APP_HOME = Path(__file__).resolve().parent / ".victoria-test-home"
os.environ.setdefault("VICTORIA_HOME", str(TEST_APP_HOME))
TEST_APP_HOME.mkdir(parents=True, exist_ok=True)

import victoria_terminal as entrypoint  # noqa: E402


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


def test_is_valid_email_accepts_common_formats(monkeypatch: pytest.MonkeyPatch) -> None:
    emails = [
        "user@example.com",
        "USER+tag@sub.example.co",
        "first.last@domain.io",
        "mixed-case@Example.Org",
    ]
    calls: list[tuple[str, bool]] = []

    def fake_validate(candidate: str, *, check_deliverability: bool) -> None:
        calls.append((candidate, check_deliverability))

    monkeypatch.setattr(entrypoint, "validate_email", fake_validate)

    for email in emails:
        assert entrypoint._is_valid_email(email) is True

    assert calls == [(email, True) for email in emails]


def test_is_valid_email_rejects_invalid_formats(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_validate(candidate: str, *, check_deliverability: bool) -> None:
        raise entrypoint.EmailNotValidError("invalid")

    monkeypatch.setattr(entrypoint, "validate_email", fake_validate)

    for email in [
        "plainaddress",
        "missing-domain@",
        "missing-at.example.com",
        "user@",
        "@example.com",
        "",
    ]:
        assert entrypoint._is_valid_email(email) is False


def test_track_license_acceptance_sends_plain_email(monkeypatch: pytest.MonkeyPatch) -> None:
    recorded: dict[str, dict[str, str]] = {}

    def fake_post(url: str, json: Mapping[str, str], timeout: int) -> None:
        recorded["payload"] = dict(json)

    monkeypatch.setattr(entrypoint.requests, "post", fake_post)
    monkeypatch.setattr(entrypoint, "validate_email", lambda *_args, **_kwargs: None)

    email = "User+tag@example.com"
    entrypoint._track_license_acceptance(email)

    payload = recorded.get("payload")
    assert payload is not None
    assert payload["email"] == "User+tag@example.com"
    assert payload["event"] == "license_accepted"


def test_track_license_acceptance_skips_invalid_email(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[dict[str, str]] = []

    def fake_post(url: str, json: Mapping[str, str], timeout: int) -> None:
        calls.append(dict(json))

    monkeypatch.setattr(entrypoint.requests, "post", fake_post)

    def always_invalid(*_args: object, **_kwargs: object) -> None:
        raise entrypoint.EmailNotValidError("bad")

    monkeypatch.setattr(entrypoint, "validate_email", always_invalid)

    entrypoint._track_license_acceptance("invalid-email")

    assert calls == []


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


def test_load_environment_without_file_respects_runtime_env(tmp_path: Path) -> None:
    custom_env = {"OPENROUTER_API_KEY": "from-runtime"}

    values = entrypoint.load_environment(app_home=tmp_path, env=custom_env)

    assert values == {}
    assert custom_env["OPENROUTER_API_KEY"] == "from-runtime"


def test_load_environment_uses_values_from_env_file(tmp_path: Path) -> None:
    env_path = tmp_path / entrypoint.ENV_FILENAME
    env_path.write_text("OPENROUTER_API_KEY=from-file\n", encoding="utf-8")
    env: dict[str, str] = {}

    entrypoint.load_environment(app_home=tmp_path, env=env)

    assert env["OPENROUTER_API_KEY"] == "from-file"


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
    assert motherduck_cfg["command"] == "mcp-server-motherduck"
    assert motherduck_cfg["args"] == [
        "--db-path",
        str(tmp_path / "adtech.duckdb"),
    ]
    assert "browserbase" not in data["mcp"]
    assert "gamma" not in data["mcp"]


def test_generate_crush_config_includes_gamma_when_configured(tmp_path: Path) -> None:
    env_values = {
        "OPENROUTER_API_KEY": "test-key",
        "VICTORIA_HOME": str(tmp_path),
        "GAMMA_API_KEY": "gamma-key",
    }

    template = entrypoint.resource_path(entrypoint.CRUSH_TEMPLATE)
    output = entrypoint.generate_crush_config(app_home=tmp_path, env=env_values, template_path=template)

    data = json.loads(output.read_text(encoding="utf-8"))

    gamma_config = data["mcp"]["gamma"]
    gamma_script = entrypoint.resource_path(Path("gamma_mcp.py"))

    assert gamma_config["command"] == "python3"
    assert gamma_config["args"] == [str(gamma_script)]
    assert gamma_config["cwd"] == str(gamma_script.parent)

    env_block = gamma_config["env"]
    assert env_block["GAMMA_API_KEY"] == "gamma-key"
    assert env_block["PYTHONPATH"] == str(gamma_script.parent)


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


def test_generate_crush_config_missing_template_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        entrypoint.generate_crush_config(app_home=tmp_path, template_path=tmp_path / "missing.json")


def test_parse_args_ignores_double_dash_separator() -> None:
    args = entrypoint.parse_args(["--", "--accept-license"])

    assert args.accept_license is True


def test_parse_args_rejects_app_home_override(tmp_path: Path) -> None:
    with pytest.raises(SystemExit) as exc_info:
        entrypoint.parse_args(["--app-home", str(tmp_path)])

    assert exc_info.value.code == 2


def test_parse_args_sets_accept_license_flag() -> None:
    args = entrypoint.parse_args(["--accept-license"])

    assert args.accept_license is True


def test_parse_args_supports_task_flag() -> None:
    args = entrypoint.parse_args(["--task", " Summarize mission "])

    assert args.task == " Summarize mission "


def test_launch_crush_appends_yolo_in_interactive_mode(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    recorded: dict[str, list[str]] = {}

    def fake_execvp(cmd: str, argv: list[str]) -> None:
        recorded["cmd"] = argv
        raise SystemExit(0)

    monkeypatch.setattr(entrypoint.os, "execvp", fake_execvp)

    with pytest.raises(SystemExit):
        entrypoint.launch_crush(app_home=tmp_path)

    assert recorded["cmd"][-1] == "--yolo"


def test_launch_crush_includes_yolo_in_task_mode(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    recorded: dict[str, list[str]] = {}

    def fake_execvp(cmd: str, argv: list[str]) -> None:
        recorded["cmd"] = argv
        raise SystemExit(0)

    monkeypatch.setattr(entrypoint.os, "execvp", fake_execvp)

    with pytest.raises(SystemExit):
        entrypoint.launch_crush(app_home=tmp_path, task_prompt="Chart conversions")

    assert "--yolo" in recorded["cmd"]
    assert "-q" in recorded["cmd"]
    prompt_index = recorded["cmd"].index("-q") + 1
    assert recorded["cmd"][prompt_index] == "Chart conversions"
