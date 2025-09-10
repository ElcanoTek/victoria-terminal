#!/usr/bin/env python3
"""
Non-interactive tests for Victoria scripts.
"""

import subprocess
import sys
import time
import platform
import signal
from pathlib import Path
import os
import pytest


def test_configurator_non_interactive():
    """Test VictoriaConfigurator.py with automated input."""
    print("🧪 Testing VictoriaConfigurator.py in non-interactive mode...")

    try:
        # Provide 'n' to both prompts (local model? and run setup?)
        input_data = "n\nn\n"
        python_cmd = sys.executable

        process = subprocess.run(
            [python_cmd, 'VictoriaConfigurator.py'],
            input=input_data,
            text=True,
            capture_output=True,
            timeout=10,
            encoding="utf-8",
            errors="replace"
        )

        assert "First-time setup" in process.stdout
        # The script should exit gracefully
        assert process.returncode == 0

    except Exception as e:
        assert False, f"  ✗ Error testing script: {e}"
