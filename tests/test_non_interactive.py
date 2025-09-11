#!/usr/bin/env python3
"""
Non-interactive tests for Victoria scripts.
"""

import shutil
import subprocess
import sys
from pathlib import Path


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
            timeout=120,  # Increased timeout for prerequisite installation
            encoding="utf-8",
            errors="replace",
        )

        # The script should exit gracefully
        assert process.returncode == 0
        assert "System Prerequisite Installation" in process.stdout

    finally:
        # Clean up the directory after the test
        shutil.rmtree(victoria_home, ignore_errors=True)
