import json
import sys
from pathlib import Path

import pytest

# Add project root to path to allow importing victoria
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common import APP_HOME
from VictoriaTerminal import build_crush_config, load_tool_config


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


def test_config_local_only():
    """Test config generation for local files only."""
    config = build_crush_config(
        include_snowflake=False, strict_env=False, local_model=False
    )
    assert "motherduck" in config["mcp"]
    assert "snowflake" not in config["mcp"]
    assert "lmstudio" not in config["providers"]
    assert config["providers"]["openrouter"]["api_key"] == "test_api_key"


def test_config_with_snowflake():
    """Test config generation with Snowflake included."""
    config = build_crush_config(
        include_snowflake=True, strict_env=True, local_model=False
    )
    assert "motherduck" in config["mcp"]
    assert "snowflake" in config["mcp"]
    assert "lmstudio" not in config["providers"]
    assert "test_account" in config["mcp"]["snowflake"]["args"]


def test_config_with_local_model():
    """Test config generation with a local model."""
    config = build_crush_config(
        include_snowflake=False, strict_env=False, local_model=True
    )
    assert "motherduck" in config["mcp"]
    assert "snowflake" not in config["mcp"]
    assert "lmstudio" in config["providers"]


def test_config_with_snowflake_and_local_model():
    """Test config generation with Snowflake and a local model."""
    config = build_crush_config(
        include_snowflake=True, strict_env=True, local_model=True
    )
    assert "motherduck" in config["mcp"]
    assert "snowflake" in config["mcp"]
    assert "lmstudio" in config["providers"]
    assert "test_account" in config["mcp"]["snowflake"]["args"]


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
