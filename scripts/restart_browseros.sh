#!/usr/bin/env bash
# =============================================================================
# restart_browseros.sh - BrowserOS MCP Server Reset Helper
# =============================================================================
#
# Kills BrowserOS processes and restarts with fixed MCP port (9100).
#
# INSTALL (one-liner):
#   curl -fsSL https://raw.githubusercontent.com/ElcanoTek/victoria-terminal/main/scripts/restart_browseros.sh | bash -s -- --install
#
# USAGE:
#   restart-browseros          # Kill BrowserOS and restart on port 9100
#   restart-browseros --help   # Show help
#
# WHY THIS EXISTS:
#   BrowserOS uses dynamic port allocation. If port 9100 is busy at startup,
#   it increments to 9101, 9102, etc. and saves the new port to preferences.
#   This causes the BROWSEROS_URL in your .env to become stale.
#   This script ensures BrowserOS always starts on the expected ports.
#
# =============================================================================
set -euo pipefail

# Configuration - default ports
MCP_PORT="${BROWSEROS_MCP_PORT:-9100}"
CDP_PORT="${BROWSEROS_CDP_PORT:-9000}"
AGENT_PORT="${BROWSEROS_AGENT_PORT:-9200}"
EXTENSION_PORT="${BROWSEROS_EXTENSION_PORT:-9300}"

# Default URL to navigate to after launch
DEFAULT_URL="${BROWSEROS_DEFAULT_URL:-https://www.elcanotek.com/}"

# macOS paths
BROWSEROS_APP="/Applications/BrowserOS.app"

log() {
  printf '[browseros-restart] %s\n' "$1"
}

warn() {
  printf '[browseros-restart] ⚠️  %s\n' "$1" >&2
}

error() {
  printf '[browseros-restart] ❌ %s\n' "$1" >&2
}

success() {
  printf '[browseros-restart] ✅ %s\n' "$1"
}

usage() {
  cat <<'USAGE'
Usage: restart-browseros [OPTIONS]

Kills BrowserOS and restarts it with fixed MCP ports.

Options:
  --install     Install this script as 'restart-browseros' command
  --kill-ports  Kill processes using target ports without prompting
  --no-start    Kill BrowserOS but don't restart it
  --url URL     URL to navigate to after launch (default: https://www.elcanotek.com/)
  -h, --help    Show this help message

Environment Variables:
  BROWSEROS_MCP_PORT        MCP port (default: 9100)
  BROWSEROS_CDP_PORT        CDP port (default: 9000)
  BROWSEROS_AGENT_PORT      Agent port (default: 9200)
  BROWSEROS_EXTENSION_PORT  Extension port (default: 9300)
  BROWSEROS_DEFAULT_URL     URL to navigate to (default: https://www.elcanotek.com/)

Examples:
  restart-browseros                    # Normal restart, opens elcanotek.com
  restart-browseros --kill-ports       # Kill port conflicts without asking
  restart-browseros --url https://example.com  # Navigate to custom URL
  BROWSEROS_MCP_PORT=9200 restart-browseros  # Use custom port
USAGE
}

install_command() {
  log "Installing restart-browseros command..."
  
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

  MARKER_BEGIN="# >>> browseros-restart helper >>>"
  MARKER_END="# <<< browseros-restart helper <<<"

  # Remove existing block if present
  TEMP_FILE=$(mktemp)
  awk -v begin="$MARKER_BEGIN" -v end="$MARKER_END" '
    $0 == begin {in_block=1; next}
    $0 == end {in_block=0; next}
    !in_block {print}
  ' "$PROFILE_FILE" >"$TEMP_FILE"
  mv "$TEMP_FILE" "$PROFILE_FILE"

  # Add new block
  cat <<'BLOCK' >>"$PROFILE_FILE"

# >>> browseros-restart helper >>>
restart-browseros() {
  curl -fsSL https://raw.githubusercontent.com/ElcanoTek/victoria-terminal/main/scripts/restart_browseros.sh | bash -s -- "$@"
}
# <<< browseros-restart helper <<<
BLOCK

  success "Installed 'restart-browseros' command to $PROFILE_FILE"
  log "Restart your shell or run: source $PROFILE_FILE"
  exit 0
}

check_port() {
  local port=$1
  local pid
  pid=$(lsof -ti :"$port" 2>/dev/null || true)
  
  if [ -n "$pid" ]; then
    local process_name
    process_name=$(ps -p "$pid" -o comm= 2>/dev/null || echo "unknown")
    echo "$pid:$process_name"
  fi
}

prompt_kill_port() {
  local port=$1
  local pid=$2
  local process_name=$3
  
  warn "Port $port is in use by: $process_name (PID: $pid)"
  
  if [ "${KILL_PORTS:-false}" = "true" ]; then
    log "Killing process $pid (--kill-ports specified)..."
    kill -9 "$pid" 2>/dev/null || true
    return 0
  fi
  
  printf '[browseros-restart] Kill this process? [y/N] '
  read -r response
  case "$response" in
    [yY]|[yY][eE][sS])
      log "Killing process $pid..."
      kill -9 "$pid" 2>/dev/null || true
      ;;
    *)
      warn "Port $port still in use - BrowserOS may use a different port"
      return 1
      ;;
  esac
}

# Parse arguments
KILL_PORTS=false
NO_START=false
NAVIGATE_URL="$DEFAULT_URL"

while [ $# -gt 0 ]; do
  case "$1" in
    --install)
      install_command
      ;;
    --kill-ports)
      KILL_PORTS=true
      shift
      ;;
    --no-start)
      NO_START=true
      shift
      ;;
    --url)
      if [ -n "${2:-}" ]; then
        NAVIGATE_URL="$2"
        shift 2
      else
        error "--url requires a URL argument"
        exit 1
      fi
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      error "Unknown option: $1"
      usage
      exit 1
      ;;
  esac
done

# Main script
log "BrowserOS Restart Helper"
log "========================"
echo ""

# Step 1: Kill BrowserOS processes
log "Stopping BrowserOS..."
pkill -f "BrowserOS" 2>/dev/null || true
pkill -f "browseros-agent" 2>/dev/null || true

# Give processes time to exit gracefully
sleep 2

# Force kill if still running
pkill -9 -f "BrowserOS" 2>/dev/null || true
pkill -9 -f "browseros-agent" 2>/dev/null || true

success "BrowserOS processes stopped"
echo ""

# Step 2: Check target ports
log "Checking target ports..."
PORTS_OK=true

for port in $MCP_PORT $CDP_PORT $AGENT_PORT $EXTENSION_PORT; do
  port_info=$(check_port "$port")
  if [ -n "$port_info" ]; then
    pid="${port_info%%:*}"
    process_name="${port_info#*:}"
    
    if ! prompt_kill_port "$port" "$pid" "$process_name"; then
      PORTS_OK=false
    fi
  fi
done

if [ "$PORTS_OK" = "true" ]; then
  success "All target ports are free"
else
  warn "Some ports are still in use"
fi
echo ""

# Step 3: Start BrowserOS with fixed ports
if [ "$NO_START" = "true" ]; then
  log "Skipping BrowserOS start (--no-start specified)"
  exit 0
fi

log "Starting BrowserOS with fixed ports..."
log "  MCP:       $MCP_PORT"
log "  CDP:       $CDP_PORT"
log "  Agent:     $AGENT_PORT"
log "  Extension: $EXTENSION_PORT"
log "  URL:       $NAVIGATE_URL"

if [ -d "$BROWSEROS_APP" ]; then
  # Launch BrowserOS with port flags and navigate to URL
  open "$BROWSEROS_APP" --args \
    --browseros-mcp-port="$MCP_PORT" \
    --browseros-cdp-port="$CDP_PORT" \
    --browseros-agent-port="$AGENT_PORT" \
    --browseros-extension-port="$EXTENSION_PORT" \
    "$NAVIGATE_URL"
  
  success "BrowserOS launched with fixed ports"
  success "Navigating to: $NAVIGATE_URL"
else
  error "BrowserOS.app not found at $BROWSEROS_APP"
  log "Please install BrowserOS from https://browseros.com"
  exit 1
fi

echo ""
success "Done! BrowserOS MCP server should be at:"
log "  http://127.0.0.1:$MCP_PORT/mcp"
echo ""
log "For Victoria Terminal, use in your .env:"
log "  BROWSEROS_URL=\"http://host.containers.internal:$MCP_PORT/mcp\""
echo ""
