#!/bin/bash

# Prerequisites Installer for macOS
# This script installs the required dependencies for the project

set -e  # Exit on any error

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

# Function to install Homebrew if not present
install_homebrew() {
    if ! command_exists brew; then
        print_status "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        
        # Add Homebrew to PATH for this script's execution
        if [[ $(uname -m) == "arm64" ]]; then
            eval "$(/opt/homebrew/bin/brew shellenv)"
        else
            eval "$(/usr/local/bin/brew shellenv)"
        fi
        
        print_success "Homebrew installed successfully"
    else
        print_success "Homebrew is already installed"
    fi
}

# Function to install Python
install_python() {
    if ! command_exists python3; then
        print_status "Installing Python..."
        if command_exists brew; then
            brew install python
        else
            print_status "Please install Xcode Command Line Tools to get Python:"
            print_status "Run: xcode-select --install"
            print_status "Or download Python from: https://www.python.org/downloads/"
            read -p "Press Enter after installing Python..."
        fi
        print_success "Python installation completed"
    else
        print_success "Python is already installed ($(python3 --version))"
    fi
}

# Function to install uv
install_uv() {
    if ! command_exists uv; then
        print_status "Installing uv (Python package manager)..."
        if command_exists brew; then
            brew install uv
        else
            # Fallback to standalone installer
            curl -LsSf https://astral.sh/uv/install.sh | sh
            # Add to PATH for this script's execution
            export PATH="$HOME/.local/bin:$PATH"
        fi
        print_success "uv installed successfully"
    else
        print_success "uv is already installed ($(uv --version))"
    fi
}

# Function to install crush
install_crush() {
    if ! command_exists crush; then
        print_status "Installing crush (AI coding agent)..."
        if command_exists brew; then
            brew install charmbracelet/tap/crush
        else
            print_warning "Homebrew not available. Installing crush via Go..."
            if command_exists go; then
                go install github.com/charmbracelet/crush@latest
                # Add GOPATH/bin to PATH if not already there
                if [[ ":$PATH:" != *":$HOME/go/bin:"* ]]; then
                    export PATH="$HOME/go/bin:$PATH"
                fi
            else
                print_error "Go is not installed. Please install Go first or use Homebrew."
                print_status "You can download Go from: https://golang.org/dl/"
                return 1
            fi
        fi
        print_success "crush installed successfully"
    else
        print_success "crush is already installed"
    fi
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

# Main installation function
main() {
    echo "=================================================="
    echo "    Prerequisites Installer for macOS"
    echo "=================================================="
    echo
    
    print_status "Starting installation of prerequisites..."
    echo
    
    # Install Homebrew first (makes everything else easier)
    install_homebrew
    echo
    
    # Install core dependencies
    install_python
    echo
    
    install_uv
    echo
    
    install_crush
    echo

    # Save the path to the crush executable
    VICTORIA_HOME="$HOME/Victoria"
    mkdir -p "$VICTORIA_HOME"
    save_command_path "crush" "$VICTORIA_HOME/.crush_path"
    echo

    print_success "All prerequisites have been installed successfully!"
    echo
    print_status "To verify installations, you may run:"
    print_status "python3 --version"
    print_status "uv --version"
    print_status "crush --version"
}

# Run main function
main "$@"

