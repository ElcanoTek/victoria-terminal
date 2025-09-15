#!/usr/bin/env python3
"""
Non-interactive tests for Victoria scripts.
"""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.skipif(sys.platform == "win32", reason="Integration test hangs on Windows in CI due to PowerShell script execution")
def test_configurator_non_interactive():
    """Test VictoriaConfigurator.py with automated input."""
    print("🧪 Testing VictoriaConfigurator.py in non-interactive mode...")

    victoria_home = Path.home() / "Victoria"

    # Ensure a clean slate by removing the entire Victoria home directory
    shutil.rmtree(victoria_home, ignore_errors=True)

    try:
        # Provide 'n' to the local model prompt, a dummy API key,
        # and 'n' to the snowflake prompt.
        input_data = "n\nTEST_API_KEY\nn\n"
        python_cmd = sys.executable

        process = subprocess.run(
            [python_cmd, "VictoriaConfigurator.py"],
            input=input_data,
            text=True,
            capture_output=True,
            timeout=60,  # Reduced timeout since we need to catch hangs faster
            encoding="utf-8",
            errors="replace",
            # On Windows, prevent new console windows from appearing
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )

        # The script should exit gracefully
        assert process.returncode == 0
        assert "System Prerequisite Installation" in process.stdout

    finally:
        # Clean up the directory after the test
        shutil.rmtree(victoria_home, ignore_errors=True)
