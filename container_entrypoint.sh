#!/usr/bin/env bash
set -euo pipefail

DEFAULT_CMD=("python3" "/app/victoria_terminal.py")

# If no arguments were provided, launch Victoria.
if [[ $# -eq 0 ]]; then
    exec "${DEFAULT_CMD[@]}"
fi

# Handle a bare `--` separator used to distinguish container options from application arguments.
# This follows standard Unix conventions where `--` signals the end of options processing.
# Using `--` is the recommended way to pass arguments to Victoria to avoid confusion
# between Podman container options and Victoria application flags.
if [[ "$1" == "--" ]]; then
    shift
fi

# If nothing remains after stripping `--`, fall back to Victoria.
if [[ $# -eq 0 ]]; then
    exec "${DEFAULT_CMD[@]}"
fi

# Treat leading flags as arguments for Victoria.
if [[ "$1" == -* ]]; then
    exec "${DEFAULT_CMD[@]}" "$@"
fi

# If the first argument is an executable on PATH, run it directly. This allows
# commands such as `podman run … bash` to spawn an interactive shell.
if command -v "$1" >/dev/null 2>&1; then
    exec "$@"
fi

# Fallback: run Victoria with the provided arguments.
exec "${DEFAULT_CMD[@]}" "$@"
