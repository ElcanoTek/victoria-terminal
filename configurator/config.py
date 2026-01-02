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

"""Configuration management for Victoria Terminal."""

from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path
from string import Template
from typing import Any, Mapping, MutableMapping

from dotenv import dotenv_values, load_dotenv

from .constants import (
    BROWSERBASE_ENV_KEYS,
    BROWSEROS_ENV_KEY,
    CRUSH_CONFIG_NAME,
    CRUSH_LOCAL,
    CRUSH_TEMPLATE,
    EMAIL_ENV_KEYS,
    ENV_FILENAME,
    GAMMA_ENV_KEY,
    PROTOCOLS_DIR,
    REQUIRED_ENV_KEYS,
    SENDGRID_ENV_KEY,
    SNOWFLAKE_ENV_KEYS,
    SUPPORT_FILES,
    VICTORIA_CONFIG_DIR,
    VICTORIA_FILE,
)


def resource_path(name: str | Path) -> Path:
    """Resolve path to a bundled resource file."""
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
    return base / name


def parse_env_file(path: Path) -> dict[str, str]:
    """Parse a ``.env`` style file into a dictionary."""
    if not path.exists():
        return {}
    values = dotenv_values(path)
    return {key: str(value) for key, value in values.items() if value is not None}


def load_environment(
    app_home: Path,
    env: MutableMapping[str, str] | None = None,
    *,
    ui: Any = None,
) -> dict[str, str]:
    """Load environment variables from ``.env`` without overriding existing values.

    Args:
        app_home: The Victoria home directory.
        env: Target environment mapping (defaults to os.environ).
        ui: Optional UI instance for displaying messages.

    Returns:
        Dictionary of values loaded from the env file.
    """
    env_path = app_home / ENV_FILENAME
    target_env: MutableMapping[str, str] = env if env is not None else os.environ

    if not env_path.exists():
        missing_keys = [key for key in REQUIRED_ENV_KEYS if not target_env.get(key)]
        if missing_keys and ui:
            ui.warn(
                "No configuration file found. Provide a .env file or set the "
                f"following variables via the container runtime: {', '.join(missing_keys)}"
            )
        elif ui:
            ui.info("No .env file found. Using runtime-provided environment variables for secrets.")
        return {}

    values = parse_env_file(env_path)
    if env is None:
        load_dotenv(env_path, override=False)

    for key, value in values.items():
        target_env.setdefault(key, value)

    if ui:
        ui.info(f"Loaded environment variables from {env_path}")
        missing_keys = [key for key in REQUIRED_ENV_KEYS if not target_env.get(key)]
        if missing_keys:
            ui.warn(
                "The following API keys are missing. Update your .env file to enable "
                f"these integrations: {', '.join(missing_keys)}"
            )
        else:
            ui.info(f"Using API keys from {env_path}.")

    return values


def substitute_env(obj: Any, env: Mapping[str, str] | None = None) -> Any:
    """Replace ``${VAR}`` tokens with values from ``env``."""
    env_map = env or os.environ
    if isinstance(obj, dict):
        return {key: substitute_env(value, env_map) for key, value in obj.items()}
    if isinstance(obj, list):
        return [substitute_env(value, env_map) for value in obj]
    if isinstance(obj, str):
        template = Template(obj)
        try:
            return template.safe_substitute(env_map)
        except ValueError:
            return obj
    return obj


def ensure_app_home(app_home: Path, *, ui: Any = None) -> Path:
    """Ensure the Victoria home directory exists with bundled documentation."""
    app_home.mkdir(parents=True, exist_ok=True)
    for relative in SUPPORT_FILES:
        src = resource_path(relative)
        dest = app_home / relative.name
        if not src.exists():
            continue

        should_overwrite = relative.name == VICTORIA_FILE
        if should_overwrite or not dest.exists():
            shutil.copy2(src, dest)

    # Copy protocols directory
    protocols_src = resource_path(Path(PROTOCOLS_DIR))
    protocols_dest = app_home / PROTOCOLS_DIR
    if protocols_src.exists() and protocols_src.is_dir():
        protocols_dest.mkdir(parents=True, exist_ok=True)
        for src_file in protocols_src.iterdir():
            if src_file.is_file():
                dest_file = protocols_dest / src_file.name
                shutil.copy2(src_file, dest_file)

    return app_home


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def _has_valid_env_value(env_map: Mapping[str, str], key: str) -> bool:
    """Check if an environment variable has a valid (non-placeholder) value."""
    value = env_map.get(key)
    if value is None:
        return False
    trimmed = value.strip()
    if not trimmed:
        return False
    if trimmed.startswith("${") and trimmed.endswith("}"):
        return False
    if "<" in trimmed or ">" in trimmed:
        return False
    return True


# MCP feature detection functions
def _is_browserbase_enabled(env_map: Mapping[str, str]) -> bool:
    return all(_has_valid_env_value(env_map, key) for key in BROWSERBASE_ENV_KEYS)


def _is_gamma_enabled(env_map: Mapping[str, str]) -> bool:
    return _has_valid_env_value(env_map, GAMMA_ENV_KEY)


def _is_sendgrid_enabled(env_map: Mapping[str, str]) -> bool:
    return _has_valid_env_value(env_map, SENDGRID_ENV_KEY)


def _is_email_enabled(env_map: Mapping[str, str]) -> bool:
    return all(_has_valid_env_value(env_map, key) for key in EMAIL_ENV_KEYS)


def _is_snowflake_enabled(env_map: Mapping[str, str]) -> bool:
    return all(_has_valid_env_value(env_map, key) for key in SNOWFLAKE_ENV_KEYS)


def _is_browseros_enabled(env_map: Mapping[str, str]) -> bool:
    return _has_valid_env_value(env_map, BROWSEROS_ENV_KEY)


def generate_crush_config(
    *,
    app_home: Path,
    template_path: Path | None = None,
    env: Mapping[str, str] | None = None,
    ui: Any = None,
) -> Path:
    """Build the Crush configuration from the bundled template.

    Args:
        app_home: The Victoria home directory.
        template_path: Path to the config template (defaults to bundled).
        env: Environment mapping for substitution (defaults to os.environ).
        ui: Optional UI instance for displaying messages.

    Returns:
        Path to the config directory containing the generated config.
    """
    template = template_path or resource_path(CRUSH_TEMPLATE)
    if not template.exists():
        raise FileNotFoundError(f"Missing Crush template at {template}")

    config = _read_json(template)
    env_map = env or os.environ
    resolved_env: dict[str, str] = dict(env_map)

    mcp_config = config.get("mcp")
    if isinstance(mcp_config, dict):
        # Conditionally include MCP servers based on environment
        if not _is_browserbase_enabled(env_map):
            mcp_config.pop("browserbase", None)

        if not _is_browseros_enabled(env_map):
            mcp_config.pop("browseros", None)

        # Gamma MCP server
        gamma_config = mcp_config.get("gamma")
        if isinstance(gamma_config, dict):
            if not _is_gamma_enabled(env_map):
                mcp_config.pop("gamma", None)
            else:
                gamma_script = resource_path(Path("mcp") / "gamma.py")
                if not gamma_script.exists():
                    raise FileNotFoundError(
                        f"Gamma MCP server script is missing (expected at {gamma_script})."
                    )
                resolved_env["GAMMA_MCP_SCRIPT"] = str(gamma_script)
                resolved_env["GAMMA_MCP_DIR"] = str(gamma_script.parent)

        # SendGrid MCP server
        sendgrid_config = mcp_config.get("sendgrid")
        if isinstance(sendgrid_config, dict):
            if not _is_sendgrid_enabled(env_map):
                mcp_config.pop("sendgrid", None)
            else:
                sendgrid_script = resource_path(Path("mcp") / "sendgrid_server.py")
                if not sendgrid_script.exists():
                    raise FileNotFoundError(
                        f"SendGrid MCP server script is missing (expected at {sendgrid_script})."
                    )
                resolved_env["SENDGRID_MCP_SCRIPT"] = str(sendgrid_script)
                resolved_env["SENDGRID_MCP_DIR"] = str(sendgrid_script.parent)

        # Email MCP server
        email_config = mcp_config.get("email")
        if isinstance(email_config, dict):
            if not _is_email_enabled(env_map):
                mcp_config.pop("email", None)
            else:
                email_script = resource_path(Path("mcp") / "ses_s3_email.py")
                if not email_script.exists():
                    raise FileNotFoundError(
                        f"Email MCP server script is missing (expected at {email_script})."
                    )
                resolved_env["EMAIL_MCP_SCRIPT"] = str(email_script)
                resolved_env["EMAIL_MCP_DIR"] = str(email_script.parent)

        # Snowflake MCP server
        snowflake_config = mcp_config.get("snowflake")
        if isinstance(snowflake_config, dict) and not _is_snowflake_enabled(env_map):
            mcp_config.pop("snowflake", None)

    resolved = substitute_env(config, resolved_env)
    config_dir = app_home / VICTORIA_CONFIG_DIR
    output_path = config_dir / CRUSH_CONFIG_NAME
    _write_json(output_path, resolved)

    if ui:
        ui.good(f"Configuration written to {output_path}")

    return config_dir


def copy_crush_local_config(
    *,
    app_home: Path,
    local_config_path: Path | None = None,
    ui: Any = None,
) -> Path:
    """Copy crush.local.json to the user's local crush config directory."""
    local_config = local_config_path or resource_path(CRUSH_LOCAL)
    if not local_config.exists():
        raise FileNotFoundError(f"Missing Crush local config at {local_config}")

    crush_config_dir = app_home / ".local" / "share" / "crush"
    crush_config_dir.mkdir(parents=True, exist_ok=True)

    dest_path = crush_config_dir / CRUSH_CONFIG_NAME
    if not dest_path.exists():
        shutil.copy2(local_config, dest_path)
        if ui:
            ui.good(f"Local Crush configuration copied to {dest_path}")
    elif ui:
        ui.info(f"Local Crush configuration already exists at {dest_path}")

    return dest_path


def remove_local_duckdb(app_home: Path, *, ui: Any = None) -> None:
    """Remove the cached DuckDB file so each run starts fresh."""
    db_path = app_home / "adtech.duckdb"
    try:
        if db_path.exists():
            db_path.unlink()
            if ui:
                ui.info(f"Removed local database: {db_path}")
    except Exception as exc:  # pragma: no cover
        if ui:
            ui.warn(f"Could not remove {db_path}: {exc}")


def remove_cache_folders(app_home: Path, *, ui: Any = None) -> None:
    """Remove .crush and .local cache folders so each run starts fresh."""
    cache_dirs = [".crush", ".local"]
    for dir_name in cache_dirs:
        dir_path = app_home / dir_name
        try:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                if ui:
                    ui.info(f"Removed cache folder: {dir_path}")
        except Exception as exc:  # pragma: no cover
            if ui:
                ui.warn(f"Could not remove {dir_path}: {exc}")


def initialize_crush_init(app_home: Path, *, ui: Any = None) -> Path:
    """Create the .crush/init marker so crush skips project initialization prompts.

    Args:
        app_home: The Victoria home directory.
        ui: Optional UI instance for displaying messages.

    Returns:
        Path to the created init file.
    """
    crush_dir = app_home / ".crush"
    crush_dir.mkdir(parents=True, exist_ok=True)
    init_file = crush_dir / "init"
    init_file.touch(exist_ok=True)
    if ui:
        ui.info(f"Initialized crush project marker at {init_file}")
    return init_file
