#!/usr/bin/env bash
set -euo pipefail

DEFAULT_CMD=("python3" "-m" "configurator")

configure_runtime_environment() {
    if [[ -z "${VICTORIA_HOME:-}" ]]; then
        echo "VICTORIA_HOME must be set." >&2
        exit 1
    fi

    export HOME="${VICTORIA_HOME}"
    mkdir -p "${HOME}"

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
