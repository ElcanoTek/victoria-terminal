import json
import os
import sys
from pathlib import Path

import pytest

# Add project root to path to allow importing victoria
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import APP_HOME
from VictoriaTerminal import build_crush_config, load_tool_config, substitute_env


@pytest.fixture(autouse=True)
def mock_env(mocker):
    """Mock environment variables for consistent test runs."""
    mocker.patch.dict(
        "os.environ",
        {
            "SNOWFLAKE_ACCOUNT": "test_account",
            "SNOWFLAKE_USER": "test_user",
            "SNOWFLAKE_PASSWORD": "test_password",
            "SNOWFLAKE_WAREHOUSE": "test_warehouse",
            "SNOWFLAKE_ROLE": "test_role",
            "OPENROUTER_API_KEY": "test_api_key",
            "VICTORIA_HOME": str(APP_HOME),
        },
    )


def normalize_config_for_snapshot(config: dict) -> str:
    """Normalize dynamic paths in config for consistent snapshot testing."""
    config_str = json.dumps(config, indent=2)
    # The APP_HOME in victoria.py is defined at module load time, so we
    # can't easily mock it without reloading modules. Instead, we just
    # replace the generated path with a placeholder for snapshot consistency.
    home_dir = os.path.expanduser("~")
    app_home_path = str(Path(home_dir) / "Victoria")
    # In Windows, json.dumps will escape backslashes, so we need to do the same
    # for our replacement string.
    app_home_path_json = app_home_path.replace("\\", "\\\\")
    return config_str.replace(app_home_path_json, "/home/victoria/app")


def test_config_snapshot_local_only(snapshot):
    """Test config generation for local files only."""
    config = build_crush_config(
        include_snowflake=False, strict_env=False, local_model=False
    )
    snapshot.assert_match(
        normalize_config_for_snapshot(config), "local_only_config.json"
    )


def test_config_snapshot_with_snowflake(snapshot):
    """Test config generation with Snowflake included."""
    config = build_crush_config(
        include_snowflake=True, strict_env=True, local_model=False
    )
    snapshot.assert_match(
        normalize_config_for_snapshot(config), "with_snowflake_config.json"
    )


def test_config_snapshot_with_local_model(snapshot):
    """Test config generation with a local model."""
    config = build_crush_config(
        include_snowflake=False, strict_env=False, local_model=True
    )
    snapshot.assert_match(
        normalize_config_for_snapshot(config), "with_local_model_config.json"
    )


def test_config_snapshot_with_snowflake_and_local_model(snapshot):
    """Test config generation with Snowflake and a local model."""
    config = build_crush_config(
        include_snowflake=True, strict_env=True, local_model=True
    )
    snapshot.assert_match(
        normalize_config_for_snapshot(config),
        "with_snowflake_and_local_model_config.json",
    )


def test_load_tool_config_not_found(mocker):
    """Test that FileNotFoundError is raised for a missing config file."""
    mocker.patch("pathlib.Path.exists", return_value=False)
    with pytest.raises(FileNotFoundError):
        load_tool_config("crush", "non_existent.json")


def test_load_tool_config_success(mocker, tmp_path):
    """Test successfully loading a config file."""
    # Create a dummy config file in a temporary directory
    tool_dir = tmp_path / "configs" / "crush"
    tool_dir.mkdir(parents=True)
    config_path = tool_dir / "my_config.json"
    expected_config = {"key": "value", "nested": {"works": True}}
    config_path.write_text(json.dumps(expected_config))

    # Mock APP_HOME to point to our temporary directory
    mocker.patch("VictoriaTerminal.APP_HOME", tmp_path)

    # Call the function and assert the result
    config = load_tool_config("crush", "my_config.json")
    assert config == expected_config
