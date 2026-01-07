#!/usr/bin/env python3
# Copyright (c) 2025 ElcanoTek
#
# This file is part of Victoria Terminal.
#
# This software is licensed under the Business Source License 1.1.
# You may not use this file except in compliance with the license.
# You may obtain a copy of the license at
#
#     https://github.com/ElcanoTek/victoria-terminal/blob/main/LICENSE
#
# Change Date: 2027-09-20
# Change License: GNU General Public License v3.0 or later

"""
Remote Runner (Host Shim) for Victoria Terminal.

This script runs on the host OS (outside the container) and manages
Victoria Terminal container execution via pull mode.

All runners use pull mode for simplified security - they only make outbound
HTTPS connections to the orchestrator, requiring no inbound ports to be opened.
"""

from __future__ import annotations

import argparse
import hashlib
import logging
import platform
import shutil
import signal
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
from urllib.parse import quote

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("remote-runner")

# Cache for GNU timeout check
_IS_GNU_TIMEOUT: Optional[bool] = None

# Try to import httpx
try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False
    logger.warning("httpx not installed - install with: pip install httpx")


# Registration retry configuration
REGISTRATION_MAX_RETRIES = 5
REGISTRATION_RETRY_DELAY = 10  # seconds


@dataclass
class Config:
    """Configuration for the remote runner."""

    orchestrator_url: str
    node_api_key: str
    registration_token: str  # Token for initial registration with orchestrator
    container_runtime: str  # "podman" or "docker"
    container_image: str
    victoria_home: Path
    node_name: Optional[str] = None  # Unique name for task targeting
    node_id: Optional[str] = None  # Assigned by orchestrator during registration
    poll_interval: int = 30  # seconds
    env_file: Optional[Path] = None


def detect_container_runtime() -> str:
    """Detect available container runtime (podman preferred)."""
    for runtime in ("podman", "docker"):
        if shutil.which(runtime):
            logger.info(f"Detected container runtime: {runtime}")
            return runtime
    raise RuntimeError("No container runtime found. Install podman or docker.")


def detect_os_type() -> str:
    """Detect the operating system type."""
    system = platform.system().lower()
    if system == "linux":
        # Try to detect distribution
        try:
            with open("/etc/os-release") as f:
                content = f.read().lower()
                if "fedora" in content:
                    return "fedora"
                elif "debian" in content or "ubuntu" in content:
                    return "debian"
        except FileNotFoundError:
            pass
        return "linux"
    elif system == "darwin":
        return "macos"
    return system


def run_container(
    config: Config,
    task_id: str,
    prompt: str,
    orchestrator_url: str,
    timeout_seconds: int = 3600,
    crush_server_url: Optional[str] = None,
    task_files_dir: Optional[Path] = None,
) -> subprocess.Popen:
    """
    Run a Victoria Terminal container with the given task.

    Args:
        config: Runner configuration
        task_id: Unique task identifier
        prompt: Task prompt to execute
        orchestrator_url: URL for status reporting
        timeout_seconds: Task timeout
        crush_server_url: Optional URL for Crush log server
        task_files_dir: Optional path to directory containing task-specific files

    Returns:
        The subprocess.Popen object for the container process
    """
    cmd = [
        config.container_runtime,
        "run",
        "--rm",
        "-it" if sys.stdin.isatty() else "-i",
        "--name", f"victoria-{task_id[:8]}",
        "-v", f"{config.victoria_home}:/workspace/Victoria:Z",
        "-e", f"ORCHESTRATOR_URL={orchestrator_url}",
        "-e", f"JOB_ID={task_id}",
        "-e", f"NODE_API_KEY={config.node_api_key}",
    ]

    # Add task files directory path if files were downloaded
    if task_files_dir:
        # Convert host path to container path
        # Host: ~/Victoria/tasks/{task_id}/files -> Container: /workspace/Victoria/tasks/{task_id}/files
        container_files_path = f"/workspace/Victoria/tasks/{task_id[:8]}/files"
        cmd.extend(["-e", f"TASK_FILES_DIR={container_files_path}"])
        logger.info(f"Task files available at: {container_files_path}")

    # Add Crush server URL if provided for log aggregation
    if crush_server_url:
        cmd.extend(["-e", f"CRUSH_SERVER_URL={crush_server_url}"])

    # Add environment file if specified
    if config.env_file and config.env_file.exists():
        cmd.extend(["--env-file", str(config.env_file)])

    # Add host networking for local services (like BrowserOS)
    # Use host.containers.internal for container-to-host communication
    if config.container_runtime == "podman":
        cmd.extend(["--add-host", "host.containers.internal:host-gateway"])

    # Add the image and command
    cmd.extend([
        config.container_image,
        "--accept-license",
        "--task", prompt,
    ])

    # Wrap with timeout command if available to prevent zombie processes
    # and enforce orchestrator-specified TTL
    timeout_cmd = shutil.which("timeout")
    if timeout_cmd and timeout_seconds and int(timeout_seconds) > 0:
        # Check if timeout supports extended flags (GNU coreutils)
        # We cache this check to avoid running it for every task
        global _IS_GNU_TIMEOUT
        if _IS_GNU_TIMEOUT is None:
            try:
                _IS_GNU_TIMEOUT = "GNU coreutils" in subprocess.check_output(
                    [timeout_cmd, "--version"],
                    stderr=subprocess.STDOUT,
                    text=True,
                )
            except Exception:
                _IS_GNU_TIMEOUT = False

        if _IS_GNU_TIMEOUT:
            # --preserve-status: allow normal exit codes if task finishes in time
            # -k 5s: send SIGKILL if process refuses to die 5s after SIGTERM
            cmd = [timeout_cmd, "--preserve-status", "-k", "5s", str(timeout_seconds)] + cmd
        else:
            # Fallback for BusyBox or other timeout implementations
            cmd = [timeout_cmd, str(timeout_seconds)] + cmd

        logger.info(f"Enforcing timeout of {timeout_seconds}s (GNU: {_IS_GNU_TIMEOUT})")

    logger.info(f"Starting container for task {task_id}")
    logger.debug(f"Command: {' '.join(cmd)}")

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    return process


def download_task_files(
    config: Config,
    task_id: str,
    files: List[str],
    orchestrator_url: str,
    file_checksums: Optional[List[str]] = None,
) -> Path:
    """
    Download task-specific files from the orchestrator.

    Files are downloaded to a task-specific directory within Victoria home,
    making them available to the agent container via the shared volume mount.

    Args:
        config: Runner configuration
        task_id: Unique task identifier
        files: List of filenames to download from the orchestrator
        orchestrator_url: Base URL of the orchestrator
        file_checksums: Optional list of SHA-256 checksums corresponding to files
                        (as provided in TaskAssignment.file_checksums per OpenAPI spec)

    Returns:
        Path to the directory containing downloaded files
    """
    # Create task-specific files directory
    # Use first 8 chars of task_id for brevity in path
    files_dir = config.victoria_home / "tasks" / task_id[:8] / "files"
    files_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Downloading {len(files)} file(s) for task {task_id[:8]}")

    # Build a mapping of normalized filename to expected checksum if checksums are provided
    # The file_checksums list corresponds positionally to the files list per OpenAPI spec
    checksum_map: dict[str, str] = {}
    if file_checksums and len(file_checksums) == len(files):
        for filename, checksum in zip(files, file_checksums):
            normalized_name = Path(filename).name
            if normalized_name in checksum_map:
                logger.error(
                    "Filename collision detected after normalization: "
                    f"{normalized_name} (from {filename})"
                )
                raise ValueError(
                    "Filename collision detected in task files. "
                    "Ensure filenames are unique after normalization."
                )
            checksum_map[normalized_name] = checksum
    elif file_checksums:
        logger.warning(
            f"file_checksums length ({len(file_checksums)}) does not match "
            f"files length ({len(files)}), skipping checksum verification"
        )

    with httpx.Client(timeout=60.0) as client:
        for filename in files:
            # Sanitize filename to prevent path traversal attacks
            # Extract only the base filename, stripping any directory components
            safe_filename = Path(filename).name
            if not safe_filename or safe_filename in (".", ".."):
                logger.warning(f"Skipping invalid filename: {filename}")
                continue

            dest_path = files_dir / safe_filename

            # Double-check that resolved path is within files_dir
            try:
                dest_path.resolve().relative_to(files_dir.resolve())
            except ValueError:
                logger.error(f"Path traversal attempt detected, skipping: {filename}")
                continue

            # URL-encode the filename as required by the OpenAPI spec
            # This handles spaces, special characters, and non-ASCII characters
            encoded_filename = quote(safe_filename, safe="")
            download_url = f"{orchestrator_url}/files/{encoded_filename}"

            try:
                logger.info(f"Downloading: {filename} -> {safe_filename}")
                response = client.get(
                    download_url,
                    headers={"X-API-Key": config.node_api_key},
                )
                response.raise_for_status()

                # Write file content
                with open(dest_path, "wb") as f:
                    f.write(response.content)

                # Verify checksum if provided in TaskAssignment.file_checksums
                # (aligned with OpenAPI spec which defines checksums in the task assignment)
                expected_checksum = checksum_map.get(safe_filename)
                if expected_checksum:
                    actual_checksum = hashlib.sha256(response.content).hexdigest()
                    if actual_checksum.lower() != expected_checksum.lower():
                        logger.error(
                            f"Checksum mismatch for {filename}: "
                            f"expected {expected_checksum}, got {actual_checksum}"
                        )
                        raise ValueError(f"Checksum verification failed for {filename}")
                    logger.info(f"Checksum verified for {safe_filename}")

                logger.info(f"Downloaded: {safe_filename} ({len(response.content)} bytes)")

            except httpx.HTTPStatusError as e:
                logger.error(f"Failed to download {filename}: HTTP {e.response.status_code}")
                raise
            except Exception as e:
                logger.error(f"Failed to download {filename}: {e}")
                raise

    logger.info(f"All files downloaded to {files_dir}")
    return files_dir


class Runner:
    """Pull-mode runner daemon for Victoria Terminal."""

    def __init__(self, config: Config):
        if not HAS_HTTPX:
            raise RuntimeError("httpx is required. Install with: pip install httpx")
        
        self.config = config
        self.running = True
        self.current_process: Optional[subprocess.Popen] = None
        self.current_task_id: Optional[str] = None

    def _register_node(self) -> Optional[tuple[str, str]]:
        """Register this node with the orchestrator.
        
        Returns a tuple of (api_key, node_id) on success, None on failure.
        """
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    f"{self.config.orchestrator_url}/register",
                    json={
                        "hostname": platform.node(),
                        "name": self.config.node_name,
                        "os_type": detect_os_type(),
                    },
                    headers={
                        "X-Registration-Token": self.config.registration_token,
                    },
                )
                response.raise_for_status()
                data = response.json()
                api_key = data.get("api_key")
                node_id = data.get("id")
                if not api_key or not node_id:
                    logger.error(
                        "Registration response missing required fields "
                        f"(id: {bool(node_id)}, api_key: {bool(api_key)}). "
                        f"Response keys: {sorted(data.keys())}"
                    )
                    return None
                logger.info(
                    "Registered with orchestrator as node "
                    f"{node_id} (name: {self.config.node_name})"
                )
                return (api_key, node_id)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                logger.error("Registration failed - invalid registration token")
            elif e.response.status_code == 503:
                logger.error("Registration failed - orchestrator has registration disabled")
            else:
                logger.error(f"Registration failed: HTTP {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Failed to register with orchestrator: {e}")
            return None

    def _register_with_retry(self) -> Optional[tuple[str, str]]:
        """Attempt to register with the orchestrator, with retries.
        
        Returns a tuple of (api_key, node_id) on success, None after all retries exhausted.
        """
        for attempt in range(1, REGISTRATION_MAX_RETRIES + 1):
            logger.info(f"Registration attempt {attempt}/{REGISTRATION_MAX_RETRIES}...")
            result = self._register_node()
            if result:
                return result
            
            if attempt < REGISTRATION_MAX_RETRIES:
                logger.info(f"Retrying in {REGISTRATION_RETRY_DELAY} seconds...")
                time.sleep(REGISTRATION_RETRY_DELAY)
        
        logger.error(f"Failed to register after {REGISTRATION_MAX_RETRIES} attempts")
        return None

    def _poll_for_tasks(self) -> Optional[dict]:
        """Poll the orchestrator for pending tasks."""
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(
                    f"{self.config.orchestrator_url}/tasks/pending",
                    headers={"X-API-Key": self.config.node_api_key},
                )
                response.raise_for_status()
                data = response.json()
                return data if data else None
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                logger.error("Authentication failed - check node API key")
            else:
                logger.error(f"HTTP error polling for tasks: {e}")
            return None
        except Exception as e:
            logger.error(f"Error polling for tasks: {e}")
            return None

    def _send_heartbeat(self):
        """Send a heartbeat to the orchestrator."""
        if not self.config.node_id:
            logger.debug("Skipping heartbeat - node_id not set")
            return
        
        try:
            status = "idle"
            if self.current_process and self.current_process.poll() is None:
                status = "busy"
            
            with httpx.Client(timeout=10.0) as client:
                response = client.post(
                    f"{self.config.orchestrator_url}/nodes/heartbeat",
                    json={
                        "node_id": self.config.node_id,
                        "status": status,
                        "current_task_id": self.current_task_id,
                    },
                    headers={"X-API-Key": self.config.node_api_key},
                )
                response.raise_for_status()
        except httpx.HTTPStatusError as e:
            logger.warning(
                "Heartbeat rejected by orchestrator: "
                f"HTTP {e.response.status_code} - {e.response.text}"
            )
        except Exception as e:
            logger.warning(f"Failed to send heartbeat: {e}")

    def run(self):
        """Start the runner daemon."""
        logger.info("Starting remote runner")
        logger.info(f"Polling orchestrator at {self.config.orchestrator_url}")
        logger.info(f"Poll interval: {self.config.poll_interval} seconds")

        # Register with orchestrator and get API key (with retries)
        logger.info("Registering with orchestrator...")
        registration_result = self._register_with_retry()
        if not registration_result:
            logger.error("Failed to register with orchestrator. Exiting.")
            sys.exit(1)
        
        # Update config with the assigned API key and node ID for subsequent requests
        assigned_api_key, assigned_node_id = registration_result
        self.config.node_api_key = assigned_api_key
        self.config.node_id = assigned_node_id
        logger.info("Registration successful - using assigned API key")

        # Set up signal handlers
        def handle_signal(signum, frame):
            logger.info("Received shutdown signal")
            self.running = False
            if self.current_process:
                self.current_process.terminate()

        signal.signal(signal.SIGINT, handle_signal)
        signal.signal(signal.SIGTERM, handle_signal)

        while self.running:
            # Check if current task is still running
            if self.current_process:
                poll_result = self.current_process.poll()
                if poll_result is not None:
                    logger.info(f"Task completed with exit code {poll_result}")
                    self.current_process = None
                    self.current_task_id = None

            # If idle, poll for new tasks
            if self.current_process is None:
                task = self._poll_for_tasks()
                if task:
                    logger.info(f"Received task: {task['task_id']}")
                    try:
                        # Download task files if any are specified
                        task_files_dir = None
                        task_files = task.get("files", [])
                        if task_files:
                            task_files_dir = download_task_files(
                                self.config,
                                task["task_id"],
                                task_files,
                                task["orchestrator_url"],
                                file_checksums=task.get("file_checksums"),
                            )

                        self.current_process = run_container(
                            self.config,
                            task["task_id"],
                            task["prompt"],
                            task["orchestrator_url"],
                            task.get("timeout_seconds", 3600),
                            task_files_dir=task_files_dir,
                        )
                        self.current_task_id = task["task_id"]
                    except Exception as e:
                        logger.error(f"Failed to start container: {e}")

            # Send heartbeat
            self._send_heartbeat()

            # Wait before next poll
            time.sleep(self.config.poll_interval)

        logger.info("Remote runner stopped")


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Remote Runner (Host Shim) for Victoria Terminal",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start the runner (polls orchestrator for tasks)
  %(prog)s --orchestrator-url https://quarterback.example.com \\
           --registration-token your-token --name "prod-server-1"

  # Named node for client-specific tasks (tasks targeting "client-acme-*" will match)
  %(prog)s --orchestrator-url https://quarterback.example.com \\
           --registration-token your-token --name "client-acme-gpu-runner"
        """,
    )

    parser.add_argument(
        "--orchestrator-url",
        required=True,
        help="URL of the All-Time Quarterback orchestrator (e.g., https://quarterback.example.com)",
    )

    parser.add_argument(
        "--registration-token",
        required=True,
        help="Registration token for authenticating with the orchestrator during registration",
    )

    parser.add_argument(
        "--name",
        dest="node_name",
        help=(
            "Unique name for this node, used for task targeting. "
            "Tasks can target nodes by name pattern (e.g., 'client-acme-*'). "
            "Defaults to the system hostname if not specified."
        ),
    )

    parser.add_argument(
        "--container-image",
        default="ghcr.io/elcanotek/victoria-terminal:latest",
        help="Container image to run (default: ghcr.io/elcanotek/victoria-terminal:latest)",
    )

    parser.add_argument(
        "--victoria-home",
        type=Path,
        default=Path.home() / "Victoria",
        help="Path to Victoria home directory (default: ~/Victoria)",
    )

    parser.add_argument(
        "--env-file",
        type=Path,
        help="Path to .env file for container environment variables",
    )

    parser.add_argument(
        "--poll-interval",
        type=int,
        default=30,
        help="Polling interval in seconds (default: 30)",
    )

    parser.add_argument(
        "--container-runtime",
        choices=["podman", "docker", "auto"],
        default="auto",
        help="Container runtime to use (default: auto-detect)",
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Detect container runtime
    if args.container_runtime == "auto":
        container_runtime = detect_container_runtime()
    else:
        container_runtime = args.container_runtime
        if not shutil.which(container_runtime):
            logger.error(f"Container runtime '{container_runtime}' not found")
            sys.exit(1)

    # Ensure Victoria home exists
    args.victoria_home.mkdir(parents=True, exist_ok=True)

    # Use provided name or default to hostname
    node_name = args.node_name or platform.node()

    config = Config(
        orchestrator_url=args.orchestrator_url.rstrip("/"),
        node_api_key="",  # Will be assigned during registration
        registration_token=args.registration_token,
        container_runtime=container_runtime,
        container_image=args.container_image,
        victoria_home=args.victoria_home,
        node_name=node_name,
        poll_interval=args.poll_interval,
        env_file=args.env_file,
    )

    logger.info("Remote Runner starting")
    logger.info(f"Node Name: {node_name}")
    logger.info(f"OS Type: {detect_os_type()}")
    logger.info(f"Container Runtime: {container_runtime}")
    logger.info(f"Victoria Home: {config.victoria_home}")

    runner = Runner(config)
    runner.run()


if __name__ == "__main__":
    main()
