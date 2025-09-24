#!/usr/bin/env bash
set -euo pipefail

log() {
  printf '[victoria-install] %s\n' "$1"
}

error() {
  printf '[victoria-install] ERROR: %s\n' "$1" >&2
}

usage() {
  cat <<'USAGE'
Usage: install_victoria.sh

This helper validates Podman, prepares the shared Victoria workspace, and
installs a reusable `victoria` command in your default shell profile.
USAGE
}

if [ "$#" -gt 0 ]; then
  case "$1" in
    -h|--help)
      usage
      exit 0
      ;;
    *)
      error "This script does not accept arguments."
      usage
      exit 1
      ;;
  esac
fi

if ! command -v podman >/dev/null 2>&1; then
  error "Podman is not installed or not on PATH. Install Podman from https://podman.io and rerun this script."
  exit 1
fi

log "Podman detected: $(podman --version 2>/dev/null | head -n1)"

if ! podman info >/dev/null 2>&1; then
  log "Podman is installed but not ready. If you're on macOS or Windows, run 'podman machine init' (first time only) and 'podman machine start' before launching Victoria."
fi

WORKSPACE_DIR="$HOME/Victoria"
mkdir -p "$WORKSPACE_DIR"
log "Ensured shared workspace exists at $WORKSPACE_DIR"

ARCH=""
if ARCH=$(podman info --format '{{.Host.Arch}}' 2>/dev/null); then
  log "Detected Podman host architecture via podman info: $ARCH"
else
  ARCH=$(uname -m)
  log "Using uname fallback for architecture detection: $ARCH"
fi

case "$ARCH" in
  arm64|aarch64)
    IMAGE_TAG="latest-arm64"
    ;;
  x86_64|amd64)
    IMAGE_TAG="latest"
    ;;
  *)
    IMAGE_TAG="latest"
    log "Unknown architecture '$ARCH'; defaulting to multi-arch 'latest' tag."
    ;;
esac
IMAGE="ghcr.io/elcanotek/victoria-terminal:${IMAGE_TAG}"
log "Using container image $IMAGE"

SHELL_NAME="${SHELL##*/}"
case "$SHELL_NAME" in
  zsh)
    PROFILE_FILE="${ZDOTDIR:-$HOME}/.zshrc"
    ;;
  bash)
    PROFILE_FILE="$HOME/.bashrc"
    ;;
  *)
    if [ -f "$HOME/.bashrc" ]; then
      PROFILE_FILE="$HOME/.bashrc"
    else
      PROFILE_FILE="$HOME/.profile"
    fi
    ;;
esac

touch "$PROFILE_FILE"
log "Updating shell profile at $PROFILE_FILE"

MARKER_BEGIN="# >>> victoria-terminal helper >>>"
MARKER_END="# <<< victoria-terminal helper <<<"

TEMP_FILE=$(mktemp)
awk -v begin="$MARKER_BEGIN" -v end="$MARKER_END" '
  $0 == begin {in_block=1; next}
  $0 == end {in_block=0; next}
  !in_block {print}
' "$PROFILE_FILE" >"$TEMP_FILE"

mv "$TEMP_FILE" "$PROFILE_FILE"

cat <<'BLOCK' >>"$PROFILE_FILE"

# >>> victoria-terminal helper >>>
victoria() {
  local image="IMAGE_PLACEHOLDER"
  if ! podman pull "$image"; then
    printf 'Victoria setup: unable to pull %s. Make sure Podman is running (start `podman machine` if applicable).\n' "$image" >&2
    return $?
  fi
  podman run --rm -it \
    -v "$HOME/Victoria:/root/Victoria" \
    "$image" "$@"
}
# <<< victoria-terminal helper <<<
BLOCK

# Replace placeholder with actual image in the profile block.
sed -i "" -e "s|IMAGE_PLACEHOLDER|$IMAGE|" "$PROFILE_FILE" 2>/dev/null || \
  sed -i -e "s|IMAGE_PLACEHOLDER|$IMAGE|" "$PROFILE_FILE"

log "Added 'victoria' function to $PROFILE_FILE"

log "Pulling the latest container image (this may take a moment)..."
if ! podman pull "$IMAGE"; then
  log "Pull failed. Start Podman (or 'podman machine start' on macOS/Windows) and run 'victoria' later to finish the download."
fi

log "All set! Restart your shell or run 'source $PROFILE_FILE', then launch Victoria with: victoria"
