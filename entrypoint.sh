#!/usr/bin/env bash
set -euo pipefail

# Ensure the user home directory exists (may be a mounted volume)
mkdir -p "${HOME}"

# Add user's local bin to PATH if not already present
case ":${PATH}:" in
    *:"${HOME}/.local/bin":*) ;;
    *) export PATH="${HOME}/.local/bin:${PATH}" ;;
esac

# Default command when none provided
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
