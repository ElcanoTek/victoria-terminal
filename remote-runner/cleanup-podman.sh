#!/bin/bash
#
# Podman Cleanup Script for Victoria Terminal Runners
# Removes stopped containers, dangling images, and unused volumes
#
# Usage: ./cleanup-podman.sh [--dry-run]
#

set -e

DRY_RUN=false
if [ "$1" = "--dry-run" ]; then
    DRY_RUN=true
    echo "DRY RUN MODE - No changes will be made"
    echo "========================================"
fi

echo "Starting Podman cleanup at $(date)"
echo ""

# Function to run command or simulate in dry-run mode
run_cmd() {
    if [ "$DRY_RUN" = true ]; then
        echo "[DRY RUN] Would execute: $*"
    else
        eval "$@"
    fi
}

# 1. Remove stopped containers older than 24 hours
echo "==> Removing stopped Victoria Terminal containers..."
STOPPED_CONTAINERS=$(podman ps -a --filter "name=victoria-" --filter "status=exited" --filter "status=created" --format "{{.ID}} {{.CreatedAt}}" 2>/dev/null || true)

if [ -n "$STOPPED_CONTAINERS" ]; then
    while IFS= read -r line; do
        CONTAINER_ID=$(echo "$line" | awk '{print $1}')
        CREATED_AT=$(echo "$line" | cut -d' ' -f2-)
        
        # Check if container is older than 24 hours
        if [ "$(uname)" = "Linux" ]; then
            CREATED_TIMESTAMP=$(date -d "$CREATED_AT" +%s 2>/dev/null || echo "0")
        else
            # macOS fallback
            CREATED_TIMESTAMP=$(date -j -f "%Y-%m-%d %H:%M:%S" "$CREATED_AT" +%s 2>/dev/null || echo "0")
        fi
        
        NOW=$(date +%s)
        AGE_HOURS=$(( (NOW - CREATED_TIMESTAMP) / 3600 ))
        
        if [ "$AGE_HOURS" -gt 24 ]; then
            echo "  Removing container $CONTAINER_ID (age: ${AGE_HOURS}h)"
            run_cmd "podman rm $CONTAINER_ID"
        fi
    done <<< "$STOPPED_CONTAINERS"
else
    echo "  No stopped containers found"
fi

echo ""

# 2. Remove dangling images (untagged intermediate images)
echo "==> Removing dangling images..."
DANGLING_IMAGES=$(podman images -f "dangling=true" -q 2>/dev/null || true)
if [ -n "$DANGLING_IMAGES" ]; then
    echo "  Found $(echo "$DANGLING_IMAGES" | wc -l) dangling image(s)"
    run_cmd "podman rmi $DANGLING_IMAGES"
else
    echo "  No dangling images found"
fi

echo ""

# 3. Remove unused volumes
echo "==> Pruning unused volumes..."
run_cmd "podman volume prune -f"

echo ""

# 4. Remove old Victoria Terminal images (keep latest 2 versions)
echo "==> Cleaning old Victoria Terminal images..."
VICTORIA_IMAGES=$(podman images --format "{{.Repository}}:{{.Tag}} {{.ID}} {{.CreatedAt}}" | grep "victoria-terminal" | sort -rk3 || true)

if [ -n "$VICTORIA_IMAGES" ]; then
    IMAGE_COUNT=$(echo "$VICTORIA_IMAGES" | wc -l)
    if [ "$IMAGE_COUNT" -gt 2 ]; then
        echo "  Found $IMAGE_COUNT Victoria Terminal images, keeping latest 2"
        echo "$VICTORIA_IMAGES" | tail -n +3 | while read -r line; do
            IMAGE_ID=$(echo "$line" | awk '{print $2}')
            IMAGE_NAME=$(echo "$line" | awk '{print $1}')
            echo "  Removing old image: $IMAGE_NAME ($IMAGE_ID)"
            run_cmd "podman rmi $IMAGE_ID"
        done
    else
        echo "  Only $IMAGE_COUNT image(s) found, keeping all"
    fi
else
    echo "  No Victoria Terminal images found"
fi

echo ""

# 5. System prune (removes all unused data)
echo "==> Running system prune..."
run_cmd "podman system prune -f --volumes"

echo ""
echo "Podman cleanup completed at $(date)"
echo ""

# Display current disk usage
echo "==> Current Podman disk usage:"
podman system df
