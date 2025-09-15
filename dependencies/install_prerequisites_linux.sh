#!/bin/bash

# Prerequisites Installer for Fedora Linux
# This script installs the required dependencies for the project

set -e  # Exit on any error

# Source common utility functions
source "$(dirname "$0")/common.sh"

# --- Global Variables ---
UPGRADE=false

# Function to update package manager
update_package_manager() {
    print_status "Updating package manager..."
    sudo dnf check-update || true # DNF exits with 100 if updates are available
}

# Function to install Python
install_python() {
    if ! command_exists python3; then
        print_status "Installing Python..."
        sudo dnf install -y python3 python3-pip
        print_success "Python installed successfully"
    else
        print_success "Python is already installed ($(python3 --version))"
    fi
}

# Function to install/upgrade uv
install_uv() {
    if [ "$UPGRADE" = true ]; then
        print_status "Upgrading uv (Python package manager)..."
    else
        print_status "Installing uv (Python package manager)..."
    fi

    # Fallback to standalone installer
    print_status "Installing/upgrading uv via standalone installer..."
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # Add to PATH for this script's execution
    export PATH="$HOME/.local/bin:$PATH"

    print_success "uv installation/upgrade complete."
}

# Function to install/upgrade crush
install_crush() {
    if [ "$UPGRADE" = true ]; then
        print_status "Upgrading crush (AI coding agent)..."
    else
        print_status "Installing crush (AI coding agent)..."
    fi

    print_status "Adding Charm repository and installing/upgrading crush..."
    echo '[charm]
name=Charm
baseurl=https://repo.charm.sh/yum/
enabled=1
gpgcheck=1
gpgkey=https://repo.charm.sh/yum/gpg.key' | sudo tee /etc/yum.repos.d/charm.repo
    sudo dnf install -y crush
    print_success "crush installed/upgraded via Charm repository"
    return 0
}

# Main installation function
main() {
    if [ "$1" == "--upgrade" ]; then
        UPGRADE=true
    fi

    if [ "$UPGRADE" = true ]; then
        echo "=================================================="
        echo "    Prerequisites Upgrader for Fedora Linux"
        echo "=================================================="
        echo
        print_status "Starting upgrade of prerequisites..."
    else
        echo "=================================================="
        echo "    Prerequisites Installer for Fedora Linux"
        echo "=================================================="
        echo
        print_status "Starting installation of prerequisites..."
    fi
    echo
    
    # Update package manager repositories
    update_package_manager
    echo
    
    # Install core dependencies. Python is not upgraded automatically.
    install_python
    echo

    # Install or upgrade uv and crush
    install_uv
    echo
    
    install_crush
    echo
    
    # Save the path to the crush executable
    if ! [ "$UPGRADE" = true ]; then
        VICTORIA_HOME="$HOME/Victoria"
        mkdir -p "$VICTORIA_HOME"
        save_command_path "crush" "$VICTORIA_HOME/.crush_path"
        echo
    fi

    if [ "$UPGRADE" = true ]; then
        print_success "All prerequisites have been checked for upgrades!"
    else
        print_success "All prerequisites have been installed successfully!"
    fi
    echo
    print_status "To verify installations, you may run:"
    print_status "python3 --version"
    print_status "uv --version"
    print_status "crush --version"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_error "Please do not run this script as root (use your regular user account)"
    print_status "The script will use sudo when needed"
    exit 1
fi

# Run main function
main "$@"
