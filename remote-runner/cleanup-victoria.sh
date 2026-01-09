#!/bin/bash
#
# Victoria Folder Cleanup Script
# Removes old files while preserving protected configuration and caches
#
# Usage: ./cleanup-victoria.sh [--dry-run] [--victoria-home /path/to/victoria]
#

set -e

DRY_RUN=false
VICTORIA_HOME="${VICTORIA_HOME:-$HOME/victoria}"
DAYS_TO_KEEP=7  # Keep files from last 7 days

# Protected paths that should NEVER be cleaned
PROTECTED_PATHS=(
    "protocols"
    "forecasting_data"
    ".env"
    "VICTORIA.md"
    "email_last_checked.txt"
    ".crush"
    ".cache"
)

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --victoria-home)
            VICTORIA_HOME="$2"
            shift 2
            ;;
        --days)
            DAYS_TO_KEEP="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--dry-run] [--victoria-home /path] [--days N]"
            exit 1
            ;;
    esac
done

if [ "$DRY_RUN" = true ]; then
    echo "DRY RUN MODE - No changes will be made"
    echo "========================================"
fi

echo "Starting Victoria cleanup at $(date)"
echo "Victoria Home: $VICTORIA_HOME"
echo "Keeping files from last $DAYS_TO_KEEP days"
echo ""
echo "Protected paths (never cleaned):"
for path in "${PROTECTED_PATHS[@]}"; do
    echo "  - $path"
done
echo ""

# Check if Victoria home exists
if [ ! -d "$VICTORIA_HOME" ]; then
    echo "Warning: Victoria home directory not found: $VICTORIA_HOME"
    echo "Skipping cleanup"
    exit 0
fi

# Build find exclusion arguments
EXCLUDE_ARGS=()
for path in "${PROTECTED_PATHS[@]}"; do
    EXCLUDE_ARGS+=("!" "-path" "$VICTORIA_HOME/$path" "!" "-path" "$VICTORIA_HOME/$path/*")
done

echo "==> Finding old files (older than $DAYS_TO_KEEP days)"

# Find all files older than N days, excluding protected paths
if [ "$DRY_RUN" = true ]; then
    OLD_FILES=$(find "$VICTORIA_HOME" -type f -mtime +$DAYS_TO_KEEP "${EXCLUDE_ARGS[@]}" 2>/dev/null || true)
    FILE_COUNT=$(echo "$OLD_FILES" | grep -c . || echo "0")
    
    if [ "$FILE_COUNT" -gt 0 ]; then
        echo "  Found $FILE_COUNT old file(s) to remove"
        echo ""
        echo "Sample files (first 10):"
        echo "$OLD_FILES" | head -10
        if [ "$FILE_COUNT" -gt 10 ]; then
            echo "  ... and $((FILE_COUNT - 10)) more"
        fi
    else
        echo "  No old files found"
    fi
else
    # Actually delete the files using -print0 and xargs -0 for safety
    FILE_COUNT=$(find "$VICTORIA_HOME" -type f -mtime +$DAYS_TO_KEEP "${EXCLUDE_ARGS[@]}" -print0 2>/dev/null | xargs -0 rm -f | wc -l || echo "0")
    
    if [ "$FILE_COUNT" -gt 0 ]; then
        echo "  Removed $FILE_COUNT old file(s)"
    else
        echo "  No old files found"
    fi
fi

echo ""

# Clean empty directories (but preserve protected paths and root-level structure)
echo "==> Removing empty directories"

# Build exclusion for empty directory cleanup
EMPTY_EXCLUDE_ARGS=()
for path in "${PROTECTED_PATHS[@]}"; do
    EMPTY_EXCLUDE_ARGS+=("!" "-path" "$VICTORIA_HOME/$path/*")
done

if [ "$DRY_RUN" = true ]; then
    EMPTY_DIRS=$(find "$VICTORIA_HOME" -mindepth 2 -type d -empty "${EMPTY_EXCLUDE_ARGS[@]}" 2>/dev/null || true)
    if [ -n "$EMPTY_DIRS" ]; then
        EMPTY_COUNT=$(echo "$EMPTY_DIRS" | wc -l)
        echo "  Would remove $EMPTY_COUNT empty director(ies)"
        echo "$EMPTY_DIRS" | head -5
        if [ "$EMPTY_COUNT" -gt 5 ]; then
            echo "  ... and $((EMPTY_COUNT - 5)) more"
        fi
    else
        echo "  No empty directories found"
    fi
else
    find "$VICTORIA_HOME" -mindepth 2 -type d -empty "${EMPTY_EXCLUDE_ARGS[@]}" -delete 2>/dev/null || true
    echo "  Removed empty directories"
fi

echo ""
echo "Victoria cleanup completed at $(date)"
echo ""

# Display disk usage summary
if [ -d "$VICTORIA_HOME" ]; then
    echo "==> Current Victoria disk usage:"
    du -sh "$VICTORIA_HOME"
    echo ""
    echo "Breakdown by directory:"
    du -sh "$VICTORIA_HOME"/* 2>/dev/null | sort -hr | head -10 || true
fi
