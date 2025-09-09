"""
Tests for the main Victoria scripts: Configurator and Terminal.
"""

import os
import sys
import subprocess
import platform
import json
from pathlib import Path
import shutil

import pytest

# Add project root to path to allow importing scripts if needed, though not directly imported
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

@pytest.mark.parametrize("script_name", ["VictoriaConfigurator.py", "VictoriaTerminal.py", "common.py"])
def test_script_syntax(script_name):
    """Test that the main scripts have valid Python syntax."""
    try:
        with open(script_name, 'r', encoding='utf-8') as f:
            source = f.read()
        compile(source, script_name, 'exec')
    except (SyntaxError, Exception) as e:
        pytest.fail(f"Syntax error or other issue in {script_name}: {e}")


def test_cross_platform_compatibility(tmp_path):
    """Test cross-platform specific functionality."""
    # Test Path operations
    test_file = tmp_path / 'test.json'
    test_data = {"test": True, "platform": platform.system()}

    # Write and read JSON
    test_file.write_text(json.dumps(test_data), encoding='utf-8')
    read_data = json.loads(test_file.read_text(encoding='utf-8'))

    assert read_data == test_data

    # Test shutil.which (used in scripts)
    python_path = shutil.which('python') or shutil.which('python3')
    assert python_path is not None, "shutil.which should find python"


def test_environment_variables(monkeypatch):
    """Test environment variable handling."""
    test_key = 'VICTORIA_TEST_VAR'
    test_value = 'test_value_123'

    monkeypatch.setenv(test_key, test_value)
    retrieved_value = os.environ.get(test_key)

    assert retrieved_value == test_value


@pytest.mark.timeout(5)
@pytest.mark.parametrize("script_name", ["VictoriaConfigurator.py", "VictoriaTerminal.py"])
def test_script_execution_no_input(script_name):
    """Test that the scripts can be executed with no input without hanging."""
    try:
        # For the terminal, we need to create the sentinel file to avoid it exiting immediately
        if "Terminal" in script_name:
            sentinel = Path(os.path.expanduser("~")) / "Victoria" / ".first_run_complete"
            sentinel.parent.mkdir(exist_ok=True)
            sentinel.touch()

        result = subprocess.run(
            [sys.executable, script_name],
            input='n\n',  # Provide 'n' to any prompts to avoid hanging
            text=True,
            capture_output=True,
            timeout=3
        )
        assert result.returncode is not None

        if "Terminal" in script_name:
            sentinel.unlink()

    except subprocess.TimeoutExpired:
        pytest.fail(f"Script execution timed out for {script_name}")


def test_unicode_handling():
    """Test Unicode and emoji handling."""
    test_string = "🚢 VICTORIA 🌊 ADTECH"
    try:
        encoded = test_string.encode('utf-8')
        decoded = encoded.decode('utf-8')
        assert decoded == test_string
    except Exception as e:
        pytest.fail(f"Unicode handling failed: {e}")


def test_json_operations(tmp_path):
    """Test JSON operations used in the script."""
    test_data = {
        "snowflake": {
            "account": "${SNOWFLAKE_ACCOUNT}",
            "user": "${SNOWFLAKE_USER}"
        },
        "config": {
            "debug": True,
            "unicode_support": "🚢"
        }
    }

    # Test JSON serialization and parsing
    json_str = json.dumps(test_data, indent=2, ensure_ascii=False)
    parsed_data = json.loads(json_str)
    assert parsed_data == test_data

    # Test file I/O with JSON
    temp_file = tmp_path / 'test.json'
    temp_file.write_text(json_str, encoding='utf-8')
    read_json = json.loads(temp_file.read_text(encoding='utf-8'))
    assert read_json == test_data
