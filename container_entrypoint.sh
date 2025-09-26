#!/usr/bin/env bash
set -euo pipefail

DEFAULT_CMD=("python3" "/workspace/victoria_terminal.py")

configure_runtime_environment() {
    local chosen_home

    if [[ -n "${VICTORIA_HOME:-}" ]]; then
        chosen_home="${VICTORIA_HOME}"
    else
        chosen_home="${HOME:-/root}"
    fi

    mkdir -p "${chosen_home}"
    export HOME="${chosen_home}"

    mkdir -p "${HOME}/.local/share/crush"
    if [[ ! -f "${HOME}/.local/share/crush/crush.json" ]]; then
        cp /workspace/configs/crush/crush.local.json "${HOME}/.local/share/crush/crush.json"
    fi

    case ":${PATH}:" in
        *:"${HOME}/.local/bin":*) ;;
        *) export PATH="${HOME}/.local/bin:${PATH}" ;;
    esac
}

configure_runtime_environment

if [[ $# -eq 0 ]]; then
    exec "${DEFAULT_CMD[@]}"
fi

if [[ "$1" == "--" ]]; then
    shift
fi

if [[ $# -eq 0 ]]; then
    exec "${DEFAULT_CMD[@]}"
fi

if [[ "$1" == -* ]]; then
    exec "${DEFAULT_CMD[@]}" "$@"
fi

if command -v "$1" >/dev/null 2>&1; then
    exec "$@"
fi

exec "${DEFAULT_CMD[@]}" "$@"
