"""
Tests for the main victoria.py script, refactored from the original
test_victoria.py script to use pytest.
"""

import os
import sys
import subprocess
import platform
import json
from pathlib import Path
import shutil

import pytest

# Add project root to path to allow importing victoria
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import victoria


def test_imports():
    """Test that all required modules can be imported."""
    required_modules = [
        'json', 'os', 're', 'shutil', 'subprocess', 'sys',
        'pathlib', 'typing', 'platform'
    ]
    for module in required_modules:
        try:
            __import__(module)
        except ImportError as e:
            pytest.fail(f"Failed to import {module}: {e}")


def test_victoria_script_syntax():
    """Test that victoria.py has valid Python syntax."""
    try:
        with open('victoria.py', 'r', encoding='utf-8') as f:
            source = f.read()
        compile(source, 'victoria.py', 'exec')
    except (SyntaxError, Exception) as e:
        pytest.fail(f"Syntax error or other issue in victoria.py: {e}")


def test_cross_platform_compatibility(tmp_path):
    """Test cross-platform specific functionality."""
    # Test Path operations
    test_file = tmp_path / 'test.json'
    test_data = {"test": True, "platform": platform.system()}

    # Write and read JSON
    test_file.write_text(json.dumps(test_data), encoding='utf-8')
    read_data = json.loads(test_file.read_text(encoding='utf-8'))

    assert read_data == test_data

    # Test shutil.which (used in victoria.py)
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
def test_script_execution_no_input():
    """Test that the script can be executed with no input without hanging."""
    try:
        result = subprocess.run(
            [sys.executable, 'victoria.py'],
            input='',
            text=True,
            capture_output=True,
            timeout=3
        )
        # The script should exit with a non-zero code because it expects input,
        # or 0 if it exits gracefully. We just want to ensure it doesn't hang.
        assert result.returncode is not None
    except subprocess.TimeoutExpired:
        pytest.fail("Script execution timed out")


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
