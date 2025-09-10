import sys
from pathlib import Path

import pytest

# Add project root to path to allow importing victoria
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# We import the function directly to test it in isolation
from common import load_dotenv


@pytest.fixture
def temp_app_home(tmp_path):
    """Create a temporary app home directory for testing."""
    # This structure mimics the real app's use of a subdirectory in the temp path
    app_home = tmp_path / "Victoria"
    app_home.mkdir()
    return app_home


def test_load_dotenv_loads_variables(temp_app_home):
    """Test that load_dotenv loads variables from a .env file."""
    # 1. Arrange
    env_file = temp_app_home / ".env"
    env_file.write_text(
        'OPENROUTER_API_KEY="test_key_from_dotenv"\n'
        'SNOWFLAKE_USER = "test_user_from_dotenv"\n'
        "# This is a comment\n"
        "MALFORMED_LINE\n"
        "EMPTY_VALUE=\n"
        'QUOTED_VALUE="some value with spaces"\n'
    )

    mock_environ = {}

    # 2. Act
    load_dotenv(_APP_HOME=temp_app_home, _os_environ=mock_environ)

    # 3. Assert
    assert mock_environ.get("OPENROUTER_API_KEY") == "test_key_from_dotenv"
    assert mock_environ.get("SNOWFLAKE_USER") == "test_user_from_dotenv"
    assert "MALFORMED_LINE" not in mock_environ
    assert "EMPTY_VALUE" in mock_environ
    assert mock_environ.get("EMPTY_VALUE") == ""
    assert mock_environ.get("QUOTED_VALUE") == "some value with spaces"
    assert "# This is a comment" not in mock_environ


def test_load_dotenv_does_not_overwrite_existing_vars(temp_app_home):
    """Test that load_dotenv does not overwrite existing environment variables."""
    # 1. Arrange
    env_file = temp_app_home / ".env"
    env_file.write_text('EXISTING_VAR="new_value"\n')

    mock_environ = {"EXISTING_VAR": "original_value"}

    # 2. Act
    load_dotenv(_APP_HOME=temp_app_home, _os_environ=mock_environ)

    # 3. Assert
    assert mock_environ.get("EXISTING_VAR") == "original_value"


def test_load_dotenv_handles_nonexistent_file(temp_app_home):
    """Test that load_dotenv runs without error if the .env file does not exist."""
    # 1. Arrange
    # .env file is not created
    mock_environ = {}

    # 2. Act & 3. Assert
    try:
        load_dotenv(_APP_HOME=temp_app_home, _os_environ=mock_environ)
    except Exception as e:
        pytest.fail(f"load_dotenv raised an exception unexpectedly: {e}")

    assert not mock_environ  # Ensure no variables were added
