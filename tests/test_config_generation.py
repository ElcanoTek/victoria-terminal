import sys
from pathlib import Path
import pytest
import json

# Add project root to path to allow importing victoria
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from victoria import build_crush_config, APP_HOME, substitute_env


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
        },
    )


def test_config_snapshot_local_only(snapshot):
    """Test config generation for local files only."""
    config = build_crush_config(include_snowflake=False, strict_env=False, local_model=False)
    snapshot.assert_match(json.dumps(config, indent=2), "local_only_config.json")


def test_config_snapshot_with_snowflake(snapshot):
    """Test config generation with Snowflake included."""
    config = build_crush_config(include_snowflake=True, strict_env=True, local_model=False)
    snapshot.assert_match(json.dumps(config, indent=2), "with_snowflake_config.json")


def test_config_snapshot_with_local_model(snapshot):
    """Test config generation with a local model."""
    config = build_crush_config(include_snowflake=False, strict_env=False, local_model=True)
    snapshot.assert_match(json.dumps(config, indent=2), "with_local_model_config.json")


def test_config_snapshot_with_snowflake_and_local_model(snapshot):
    """Test config generation with Snowflake and a local model."""
    config = build_crush_config(include_snowflake=True, strict_env=True, local_model=True)
    snapshot.assert_match(
        json.dumps(config, indent=2), "with_snowflake_and_local_model_config.json"
    )


import victoria

def test_load_tool_config_not_found(mocker):
    """Test that FileNotFoundError is raised for a missing config file."""
    mocker.patch("pathlib.Path.exists", return_value=False)
    with pytest.raises(FileNotFoundError):
        victoria.load_tool_config("crush", "non_existent.json")
