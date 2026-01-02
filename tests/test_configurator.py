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
# License Notes: 2026-01-02

"""Tests for the configurator module."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

if TYPE_CHECKING:
    from collections.abc import Callable


# =============================================================================
# ENV FILE PARSING
# =============================================================================


class TestParseEnvFile:
    """Tests for parse_env_file function."""

    def test_handles_comments_and_malformed_lines(
        self, victoria_home: Path, env_file: Callable[[str], Path], module: Any
    ) -> None:
        env_file("FOO=bar\n# comment\nMALFORMED\n" 'QUOTED="some value"\n')
        env_path = victoria_home / module.ENV_FILENAME

        values = module.parse_env_file(env_path)

        assert values == {"FOO": "bar", "QUOTED": "some value"}

    def test_returns_empty_when_missing(
        self, victoria_home: Path, module: Any
    ) -> None:
        env_path = victoria_home / module.ENV_FILENAME
        assert module.parse_env_file(env_path) == {}


# =============================================================================
# EMAIL VALIDATION
# =============================================================================


class TestEmailValidation:
    """Tests for email validation functions."""

    VALID_EMAILS = [
        "user@example.com",
        "USER+tag@sub.example.co",
        "first.last@domain.io",
        "mixed-case@Example.Org",
    ]

    INVALID_EMAILS = [
        "plainaddress",
        "missing-domain@",
        "missing-at.example.com",
        "user@",
        "@example.com",
        "",
    ]

    @pytest.mark.parametrize("email", VALID_EMAILS)
    def test_accepts_valid_emails(
        self, email: str, mock_email_valid: None, module: Any
    ) -> None:
        assert module._is_valid_email(email) is True

    @pytest.mark.parametrize("email", INVALID_EMAILS)
    def test_rejects_invalid_emails(
        self, email: str, mock_email_invalid: None, module: Any
    ) -> None:
        assert module._is_valid_email(email) is False


# =============================================================================
# LICENSE TRACKING
# =============================================================================


class TestLicenseTracking:
    """Tests for license acceptance tracking."""

    def test_sends_telemetry_for_valid_email(
        self,
        mock_requests_post: list[dict[str, Any]],
        mock_email_valid: None,
        module: Any,
    ) -> None:
        module._track_license_acceptance("User+tag@example.com")

        assert len(mock_requests_post) == 1
        payload = mock_requests_post[0]
        assert payload["email"] == "User+tag@example.com"
        assert payload["event"] == "license_accepted"

    def test_skips_telemetry_for_invalid_email(
        self,
        mock_requests_post: list[dict[str, Any]],
        mock_email_invalid: None,
        module: Any,
    ) -> None:
        module._track_license_acceptance("invalid-email")

        assert mock_requests_post == []


# =============================================================================
# ENVIRONMENT LOADING
# =============================================================================


class TestLoadEnvironment:
    """Tests for load_environment function."""

    def test_preserves_existing_values(
        self, victoria_home: Path, env_file: Callable[[str], Path], module: Any
    ) -> None:
        env_file("FOO=bar\nSHARED=value\n")
        custom_env = {"SHARED": "existing"}

        values = module.load_environment(app_home=victoria_home, env=custom_env)

        assert values == {"FOO": "bar", "SHARED": "value"}
        assert custom_env["FOO"] == "bar"
        assert custom_env["SHARED"] == "existing"

    def test_returns_empty_when_file_absent(
        self, victoria_home: Path, module: Any
    ) -> None:
        assert module.load_environment(app_home=victoria_home, env={}) == {}

    def test_respects_runtime_env_without_file(
        self, victoria_home: Path, module: Any
    ) -> None:
        custom_env = {"OPENROUTER_API_KEY": "from-runtime"}

        values = module.load_environment(app_home=victoria_home, env=custom_env)

        assert values == {}
        assert custom_env["OPENROUTER_API_KEY"] == "from-runtime"

    def test_loads_values_from_file(
        self, victoria_home: Path, env_file: Callable[[str], Path], module: Any
    ) -> None:
        env_file("OPENROUTER_API_KEY=from-file\n")
        env: dict[str, str] = {}

        module.load_environment(app_home=victoria_home, env=env)

        assert env["OPENROUTER_API_KEY"] == "from-file"


# =============================================================================
# TEMPLATE SUBSTITUTION
# =============================================================================


class TestSubstituteEnv:
    """Tests for substitute_env function."""

    def test_handles_nested_structures(self, module: Any) -> None:
        payload = {
            "list": ["${FIRST}", {"second": "${SECOND}"}, "plain"],
            "missing": "${MISSING}",
        }
        env = {"FIRST": "one", "SECOND": "two"}

        result = module.substitute_env(payload, env)

        assert result["list"][0] == "one"
        assert result["list"][1]["second"] == "two"
        assert result["list"][2] == "plain"
        assert result["missing"] == "${MISSING}"

    def test_uses_process_environment(
        self, monkeypatch: pytest.MonkeyPatch, module: Any
    ) -> None:
        monkeypatch.setenv("TOKEN", "value")

        assert module.substitute_env("${TOKEN}") == "value"


# =============================================================================
# CRUSH CONFIG GENERATION
# =============================================================================


class TestGenerateCrushConfig:
    """Tests for generate_crush_config function."""

    def test_substitutes_env_and_includes_defaults(
        self, generated_config: Callable[[dict[str, str]], dict[str, Any]]
    ) -> None:
        data = generated_config({"OPENROUTER_API_KEY": "test-key"})

        assert data["providers"]["openrouter"]["api_key"] == "test-key"
        assert data["lsp"]["python"]["command"] == "python"
        assert data["lsp"]["python"]["args"] == ["-m", "pylsp"]
        assert "typescript" not in data["lsp"]
        assert data["mcp"]["motherduck"]["command"] == "mcp-server-motherduck"
        assert "browserbase" not in data["mcp"]
        assert "gamma" not in data["mcp"]

    def test_includes_gamma_when_configured(
        self,
        generated_config: Callable[[dict[str, str]], dict[str, Any]],
        module: Any,
    ) -> None:
        data = generated_config({
            "OPENROUTER_API_KEY": "test-key",
            "GAMMA_API_KEY": "gamma-key",
        })

        gamma_config = data["mcp"]["gamma"]
        gamma_script = module.resource_path(Path("mcp") / "gamma.py")

        assert gamma_config["command"] == "python3"
        assert gamma_config["args"] == [str(gamma_script)]
        assert gamma_config["cwd"] == str(gamma_script.parent)
        assert gamma_config["env"]["GAMMA_API_KEY"] == "gamma-key"

    def test_includes_browserbase_when_fully_configured(
        self, generated_config: Callable[[dict[str, str]], dict[str, Any]]
    ) -> None:
        data = generated_config({
            "OPENROUTER_API_KEY": "test-key",
            "BROWSERBASE_API_KEY": "bb-test-key",
            "BROWSERBASE_PROJECT_ID": "test-project-id",
            "GEMINI_API_KEY": "gemini-test-key",
        })

        browserbase_cfg = data["mcp"]["browserbase"]
        assert browserbase_cfg["command"] == "mcp-server-browserbase"
        assert browserbase_cfg["env"]["BROWSERBASE_API_KEY"] == "bb-test-key"
        assert browserbase_cfg["env"]["BROWSERBASE_PROJECT_ID"] == "test-project-id"
        assert browserbase_cfg["env"]["GEMINI_API_KEY"] == "gemini-test-key"

    @pytest.mark.parametrize(
        "invalid_env",
        [
            # Placeholder value
            {
                "BROWSERBASE_API_KEY": "<YOUR_BROWSERBASE_API_KEY>",
                "BROWSERBASE_PROJECT_ID": "test-project-id",
                "GEMINI_API_KEY": "gemini-test-key",
            },
            # Missing required keys
            {"BROWSERBASE_API_KEY": "bb-test-key"},
            # Blank key
            {
                "BROWSERBASE_API_KEY": "   ",
                "BROWSERBASE_PROJECT_ID": "test-project-id",
                "GEMINI_API_KEY": "gemini-test-key",
            },
        ],
        ids=["placeholder", "missing-keys", "blank-key"],
    )
    def test_excludes_browserbase_with_invalid_config(
        self,
        invalid_env: dict[str, str],
        generated_config: Callable[[dict[str, str]], dict[str, Any]],
    ) -> None:
        env = {"OPENROUTER_API_KEY": "test-key", **invalid_env}
        data = generated_config(env)

        assert "browserbase" not in data["mcp"]

    def test_raises_for_missing_template(
        self, victoria_home: Path, module: Any
    ) -> None:
        with pytest.raises(FileNotFoundError):
            module.generate_crush_config(
                app_home=victoria_home,
                template_path=victoria_home / "missing.json",
            )


# =============================================================================
# CLI ARGUMENT PARSING
# =============================================================================


class TestParseArgs:
    """Tests for parse_args function."""

    def test_strips_double_dash_separator(self, module: Any) -> None:
        args = module.parse_args(["--", "--accept-license"])
        assert args.accept_license is True

    def test_sets_accept_license_flag(self, module: Any) -> None:
        args = module.parse_args(["--accept-license"])
        assert args.accept_license is True

    def test_supports_task_flag(self, module: Any) -> None:
        args = module.parse_args(["--task", " Summarize mission "])
        assert args.task == " Summarize mission "


# =============================================================================
# CRUSH LAUNCH
# =============================================================================


class TestLaunchCrush:
    """Tests for launch_crush function."""

    def test_uses_yolo_in_interactive_mode(
        self, victoria_home: Path, mock_execvp: list[list[str]], module: Any
    ) -> None:
        with pytest.raises(SystemExit):
            module.launch_crush(app_home=victoria_home)

        cmd = mock_execvp[0]
        assert cmd[:2] == ["crush", "--yolo"]
        assert "-c" in cmd

    def test_uses_task_mode_with_prompt(
        self, victoria_home: Path, mock_execvp: list[list[str]], module: Any
    ) -> None:
        with pytest.raises(SystemExit):
            module.launch_crush(app_home=victoria_home, task_prompt="Chart conversions")

        cmd = mock_execvp[0]
        assert cmd[0] == "crush"
        assert "--yolo" not in cmd
        assert "-q" in cmd
        prompt_index = cmd.index("-q") + 1
        assert cmd[prompt_index] == "Chart conversions"
