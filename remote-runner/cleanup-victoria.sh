#!/bin/bash
#
# Victoria Folder Cleanup Script
# Removes old task files, logs, and temporary data
#
# Usage: ./cleanup-victoria.sh [--dry-run] [--victoria-home /path/to/victoria]
#

set -e

DRY_RUN=false
VICTORIA_HOME="${VICTORIA_HOME:-$HOME/victoria}"
DAYS_TO_KEEP=7  # Keep files from last 7 days

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

# Check if Victoria home exists
if [ ! -d "$VICTORIA_HOME" ]; then
    echo "Warning: Victoria home directory not found: $VICTORIA_HOME"
    echo "Skipping cleanup"
    exit 0
fi

# Function to run command or simulate in dry-run mode
run_cmd() {
    if [ "$DRY_RUN" = true ]; then
        echo "[DRY RUN] Would execute: $*"
    else
        eval "$@"
    fi
}

# Function to safely remove old files
cleanup_old_files() {
    local dir=$1
    local pattern=$2
    local description=$3
    
    if [ ! -d "$dir" ]; then
        echo "  Directory not found: $dir (skipping)"
        return
    fi
    
    echo "==> Cleaning $description in $dir"
    
    # Find and count files older than N days
    FILE_COUNT=$(find "$dir" -name "$pattern" -type f -mtime +$DAYS_TO_KEEP 2>/dev/null | wc -l || echo "0")
    
    if [ "$FILE_COUNT" -gt 0 ]; then
        echo "  Found $FILE_COUNT old file(s) to remove"
        
        if [ "$DRY_RUN" = true ]; then
            # Show first 5 files for dry run
            find "$dir" -name "$pattern" -type f -mtime +$DAYS_TO_KEEP 2>/dev/null | head -5
            if [ "$FILE_COUNT" -gt 5 ]; then
                echo "  ... and $((FILE_COUNT - 5)) more"
            fi
        else
            # Use -print0 and xargs -0 to handle filenames with spaces/newlines
            find "$dir" -name "$pattern" -type f -mtime +$DAYS_TO_KEEP -print0 2>/dev/null | xargs -0 rm -f
            echo "  Removed $FILE_COUNT file(s)"
        fi
    else
        echo "  No old files found"
    fi
    echo ""
}

# 1. Clean old task files
cleanup_old_files "$VICTORIA_HOME/tasks" "*.json" "task files"
cleanup_old_files "$VICTORIA_HOME/tasks" "*.txt" "task metadata"

# 2. Clean old log files
cleanup_old_files "$VICTORIA_HOME/logs" "*.log" "log files"
cleanup_old_files "$VICTORIA_HOME/logs" "*.txt" "text logs"

# 3. Clean old temporary files
cleanup_old_files "$VICTORIA_HOME/tmp" "*" "temporary files"
cleanup_old_files "$VICTORIA_HOME/temp" "*" "temporary files"

# 4. Clean old downloaded files (if exists)
cleanup_old_files "$VICTORIA_HOME/downloads" "*" "downloaded files"

# 5. Clean old cache files
if [ -d "$VICTORIA_HOME/.cache" ]; then
    echo "==> Cleaning cache directory"
    CACHE_SIZE_BEFORE=$(du -sh "$VICTORIA_HOME/.cache" 2>/dev/null | awk '{print $1}' || echo "0")
    run_cmd "find $VICTORIA_HOME/.cache -type f -mtime +$DAYS_TO_KEEP -delete"
    CACHE_SIZE_AFTER=$(du -sh "$VICTORIA_HOME/.cache" 2>/dev/null | awk '{print $1}' || echo "0")
    echo "  Cache size: $CACHE_SIZE_BEFORE -> $CACHE_SIZE_AFTER"
    echo ""
fi

# 6. Clean empty directories
echo "==> Removing empty directories"
if [ "$DRY_RUN" = true ]; then
    EMPTY_DIRS=$(find "$VICTORIA_HOME" -type d -empty 2>/dev/null || true)
    if [ -n "$EMPTY_DIRS" ]; then
        echo "  Would remove $(echo "$EMPTY_DIRS" | wc -l) empty directories"
    else
        echo "  No empty directories found"
    fi
else
    find "$VICTORIA_HOME" -type d -empty -delete 2>/dev/null || true
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
