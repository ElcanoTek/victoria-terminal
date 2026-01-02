#!/usr/bin/env bash
set -euo pipefail

# Ensure Victoria directory exists (may be a mounted volume)
mkdir -p "${VICTORIA_HOME}"

DEFAULT_CMD=("python3" "-m" "configurator")

# No arguments: run default command
if [[ $# -eq 0 ]]; then
    exec "${DEFAULT_CMD[@]}"
fi

# Strip leading "--" separator if present
if [[ "$1" == "--" ]]; then
    shift
fi

# After stripping "--", if no args remain: run default command
if [[ $# -eq 0 ]]; then
    exec "${DEFAULT_CMD[@]}"
fi

# If first arg looks like a flag, pass all args to default command
if [[ "$1" == -* ]]; then
    exec "${DEFAULT_CMD[@]}" "$@"
fi

# If first arg is an executable command, run it directly
if command -v "$1" >/dev/null 2>&1; then
    exec "$@"
fi

# Otherwise, pass all args to default command
exec "${DEFAULT_CMD[@]}" "$@"
