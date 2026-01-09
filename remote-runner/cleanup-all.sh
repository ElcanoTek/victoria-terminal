#!/bin/bash
#
# Combined Cleanup Script for Victoria Terminal Runners
# Runs both podman and Victoria folder cleanup
#
# Usage: ./cleanup-all.sh [--dry-run]
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "========================================"
echo "Victoria Terminal Cleanup"
echo "========================================"
echo "Started at: $(date)"
echo ""

# Run podman cleanup
echo "### PODMAN CLEANUP ###"
echo ""
"$SCRIPT_DIR/cleanup-podman.sh" "$@"

echo ""
echo "========================================"
echo ""

# Run Victoria folder cleanup
echo "### VICTORIA FOLDER CLEANUP ###"
echo ""
"$SCRIPT_DIR/cleanup-victoria.sh" "$@"

echo ""
echo "========================================"
echo "All cleanup tasks completed at: $(date)"
echo "========================================"
