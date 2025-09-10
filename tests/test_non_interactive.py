#!/usr/bin/env python3
"""
Non-interactive tests for Victoria scripts.
"""

import os
import platform
import signal
import subprocess
import sys
import time
from pathlib import Path

import pytest


def test_configurator_non_interactive():
    """Test VictoriaConfigurator.py with automated input."""
    print("🧪 Testing VictoriaConfigurator.py in non-interactive mode...")

    try:
        # Provide 'n' to both prompts (local model? and run setup?)
        input_data = "n\nn\n"
        python_cmd = sys.executable

        process = subprocess.run(
            [python_cmd, "VictoriaConfigurator.py"],
            input=input_data,
            text=True,
            capture_output=True,
            timeout=10,
            encoding="utf-8",
            errors="replace",
        )

        assert "First-time setup" in process.stdout
        # The script should exit gracefully
        assert process.returncode == 0

    except Exception as e:
        assert False, f"  ✗ Error testing script: {e}"


def test_terminal_non_interactive_no_setup():
    """Test VictoriaTerminal.py exits if setup has not been run."""
    print("🧪 Testing VictoriaTerminal.py without setup...")

    sentinel = Path(os.path.expanduser("~")) / "Victoria" / ".first_run_complete"
    if sentinel.exists():
        sentinel.unlink()

    python_cmd = sys.executable
    process = subprocess.run(
        [python_cmd, "VictoriaTerminal.py"],
        text=True,
        capture_output=True,
        timeout=10,
        encoding="utf-8",
        errors="replace",
    )

    assert "First-time setup has not been completed" in process.stdout
    assert process.returncode == 1


def test_terminal_non_interactive_with_setup(tmp_path):
    """Test VictoriaTerminal.py with automated input after setup."""
    print("🧪 Testing VictoriaTerminal.py with setup...")

    sentinel = Path(os.path.expanduser("~")) / "Victoria" / ".first_run_complete"
    sentinel.parent.mkdir(exist_ok=True)
    sentinel.touch()

    # Create a dummy crush executable to pass preflight checks
    dummy_crush_dir = tmp_path / "bin"
    dummy_crush_dir.mkdir()
    dummy_crush_path = dummy_crush_dir / "crush"
    dummy_crush_path.write_text("#!/bin/sh\necho 'Crush mock executed'\nexit 0")
    os.chmod(dummy_crush_path, 0o755)

    env = os.environ.copy()
    env["PATH"] = str(dummy_crush_dir) + os.pathsep + env.get("PATH", "")
    env["OPENROUTER_API_KEY"] = "test-key"

    try:
        input_data = "n\n2\n"  # No to local model, yes to local files
        python_cmd = sys.executable

        process = subprocess.run(
            [python_cmd, "VictoriaTerminal.py"],
            input=input_data,
            text=True,
            capture_output=True,
            timeout=10,
            env=env,
            encoding="utf-8",
            errors="replace",
        )

        assert "System preflight check" in process.stdout
        assert "Mission launch" in process.stdout

    finally:
        if sentinel.exists():
            sentinel.unlink()


def test_configurator_interrupt_handling():
    """Test that the configurator handles keyboard interrupt gracefully."""
    print(f"🧪 Testing VictoriaConfigurator.py keyboard interrupt handling...")

    try:
        python_cmd = sys.executable

        creationflags = 0
        if platform.system() == "Windows":
            creationflags = subprocess.CREATE_NEW_PROCESS_GROUP

        process = subprocess.Popen(
            [python_cmd, "VictoriaConfigurator.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=creationflags,
            encoding="utf-8",
            errors="replace",
        )

        time.sleep(1)

        if platform.system() == "Windows":
            process.send_signal(signal.CTRL_C_EVENT)
        else:
            process.send_signal(signal.SIGINT)

        stdout, stderr = process.communicate(timeout=5)

        assert process.returncode == 130

    except Exception as e:
        assert False, f"  ✗ Error testing interrupt for VictoriaConfigurator.py: {e}"


def test_terminal_interrupt_handling(tmp_path):
    """Test that the terminal handles keyboard interrupt gracefully."""
    print(f"🧪 Testing VictoriaTerminal.py keyboard interrupt handling...")

    sentinel = Path(os.path.expanduser("~")) / "Victoria" / ".first_run_complete"
    sentinel.parent.mkdir(exist_ok=True)
    sentinel.touch()

    dummy_crush_dir = tmp_path / "bin"
    dummy_crush_dir.mkdir()
    dummy_crush_path = dummy_crush_dir / "crush"
    dummy_crush_path.write_text("#!/bin/sh\nsleep 5\n")
    os.chmod(dummy_crush_path, 0o755)

    env = os.environ.copy()
    env["PATH"] = str(dummy_crush_dir) + os.pathsep + env.get("PATH", "")
    env["OPENROUTER_API_KEY"] = "test-key"

    try:
        python_cmd = sys.executable

        creationflags = 0
        if platform.system() == "Windows":
            creationflags = subprocess.CREATE_NEW_PROCESS_GROUP

        process = subprocess.Popen(
            [python_cmd, "VictoriaTerminal.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=creationflags,
            env=env,
            encoding="utf-8",
            errors="replace",
        )

        time.sleep(2)

        if platform.system() == "Windows":
            process.send_signal(signal.CTRL_C_EVENT)
        else:
            process.send_signal(signal.SIGINT)

        stdout, stderr = process.communicate(timeout=5)

        assert process.returncode == 130

    except Exception as e:
        assert False, f"  ✗ Error testing interrupt for VictoriaTerminal.py: {e}"
    finally:
        if sentinel.exists():
            sentinel.unlink()
