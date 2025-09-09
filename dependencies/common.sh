#!/bin/bash

# Common utility functions and variables for Victoria installation scripts

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to find and save the path of a command
save_command_path() {
    local cmd="$1"
    local output_file="$2"

    if command_exists "$cmd"; then
        local cmd_path
        cmd_path=$(command -v "$cmd")
        echo "$cmd_path" > "$output_file"
        print_status "Saved path for '$cmd' to $output_file"
    else
        print_warning "'$cmd' command not found after installation."
    fi
}
