#!/bin/bash

# Prerequisites Installer for Linux
# This script installs the required dependencies for the project
# Supports: Ubuntu/Debian, Fedora/RHEL/CentOS, Arch Linux, openSUSE, Alpine

set -e  # Exit on any error

# Source common utility functions
source "$(dirname "$0")/common.sh"

# --- Global Variables ---
UPGRADE=false

# Function to detect Linux distribution
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID
        VERSION=$VERSION_ID
    elif [ -f /etc/redhat-release ]; then
        DISTRO="rhel"
    elif [ -f /etc/debian_version ]; then
        DISTRO="debian"
    else
        DISTRO="unknown"
    fi
    
    print_status "Detected distribution: $DISTRO"
}

# Function to update package manager
update_package_manager() {
    print_status "Updating package manager..."
    case $DISTRO in
        ubuntu|debian)
            sudo apt update
            ;;
        fedora)
            sudo dnf check-update || true # DNF exits with 100 if updates are available
            ;;
        rhel|centos|rocky|almalinux)
            if command_exists dnf; then
                sudo dnf check-update || true
            else
                sudo yum check-update || true
            fi
            ;;
        arch|manjaro)
            sudo pacman -Sy
            ;;
        opensuse*|sles)
            sudo zypper refresh
            ;;
        alpine)
            sudo apk update
            ;;
        *)
            print_warning "Unknown distribution, skipping package manager update"
            ;;
    esac
}

# Function to install Python
install_python() {
    if ! command_exists python3; then
        print_status "Installing Python..."
        case $DISTRO in
            ubuntu|debian)
                sudo apt install -y python3 python3-pip python3-venv
                ;;
            fedora)
                sudo dnf install -y python3 python3-pip
                ;;
            rhel|centos|rocky|almalinux)
                if command_exists dnf; then
                    sudo dnf install -y python3 python3-pip
                else
                    sudo yum install -y python3 python3-pip
                fi
                ;;
            arch|manjaro)
                sudo pacman -S --noconfirm python python-pip
                ;;
            opensuse*|sles)
                sudo zypper install -y python3 python3-pip
                ;;
            alpine)
                sudo apk add python3 py3-pip
                ;;
            *)
                print_error "Unsupported distribution for automatic Python installation"
                print_status "Please install Python manually using your package manager"
                return 1
                ;;
        esac
        print_success "Python installed successfully"
    else
        print_success "Python is already installed ($(python3 --version))"
    fi
}

# Function to install/upgrade uv
install_uv() {
    if ! command_exists uv || [ "$UPGRADE" = true ]; then
        if [ "$UPGRADE" = true ] && command_exists uv; then
            print_status "Checking for uv upgrade..."
        else
            print_status "Installing uv (Python package manager)..."
        fi
        
        # Try distribution-specific packages first
        case $DISTRO in
            arch|manjaro)
                if command_exists yay; then
                    yay -S --noconfirm uv
                    print_success "uv installed/upgraded via AUR"
                    return 0
                fi
                ;;
        esac
        
        # Fallback to standalone installer
        print_status "Installing/upgrading uv via standalone installer..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        
        # Add to PATH for this script's execution
        export PATH="$HOME/.local/bin:$PATH"
        
        print_success "uv installation/upgrade complete."
    else
        print_success "uv is already installed ($(uv --version))"
    fi
}

# Function to install/upgrade crush
install_crush() {
    if ! command_exists crush || [ "$UPGRADE" = true ]; then
        if [ "$UPGRADE" = true ] && command_exists crush; then
            print_status "Checking for crush upgrade..."
        else
            print_status "Installing crush (AI coding agent)..."
        fi
        
        # Try distribution-specific packages first
        case $DISTRO in
            ubuntu|debian)
                print_status "Adding Charm repository and installing/upgrading crush..."
                sudo mkdir -p /etc/apt/keyrings
                curl -fsSL https://repo.charm.sh/apt/gpg.key | sudo gpg --dearmor -o /etc/apt/keyrings/charm.gpg
                echo "deb [signed-by=/etc/apt/keyrings/charm.gpg] https://repo.charm.sh/apt/ * *" | sudo tee /etc/apt/sources.list.d/charm.list
                sudo apt update
                sudo apt install -y crush
                print_success "crush installed/upgraded via Charm repository"
                return 0
                ;;
            fedora|rhel|centos|rocky|almalinux)
                print_status "Adding Charm repository and installing/upgrading crush..."
                echo '[charm]
name=Charm
baseurl=https://repo.charm.sh/yum/
enabled=1
gpgcheck=1
gpgkey=https://repo.charm.sh/yum/gpg.key' | sudo tee /etc/yum.repos.d/charm.repo
                if command_exists dnf; then
                    sudo dnf install -y crush
                else
                    sudo yum install -y crush
                fi
                print_success "crush installed/upgraded via Charm repository"
                return 0
                ;;
            arch|manjaro)
                if command_exists yay; then
                    yay -S --noconfirm crush-bin
                    print_success "crush installed/upgraded via AUR"
                    return 0
                fi
                ;;
        esac
        
        # Fallback to Go installation
        print_warning "Distribution-specific package not available. Trying Go installation..."
        if command_exists go; then
            go install github.com/charmbracelet/crush@latest
            
            # Add GOPATH/bin to PATH for this script's execution
            GOPATH=$(go env GOPATH)
            export PATH="$GOPATH/bin:$PATH"
            
            print_success "crush installed/upgraded via Go"
        else
            print_error "Go is not installed and no distribution package available."
            print_status "Please install Go first or install crush manually."
            print_status "Go can be installed from: https://golang.org/dl/"
            return 1
        fi
    else
        print_success "crush is already installed"
    fi
}

# Function to install Go (if needed for crush)
install_go() {
    # Only install Go if crush isn't installed and we're not upgrading via package manager
    if ! command_exists go && ! command_exists crush; then
        print_status "Go is needed to install crush. Installing Go..."
        case $DISTRO in
            ubuntu|debian)
                # Use snap for latest version
                if command_exists snap; then
                    sudo snap install go --classic
                else
                    sudo apt install -y golang-go
                fi
                ;;
            fedora)
                sudo dnf install -y golang
                ;;
            rhel|centos|rocky|almalinux)
                if command_exists dnf; then
                    sudo dnf install -y golang
                else
                    sudo yum install -y golang
                fi
                ;;
            arch|manjaro)
                sudo pacman -S --noconfirm go
                ;;
            opensuse*|sles)
                sudo zypper install -y go
                ;;
            alpine)
                sudo apk add go
                ;;
            *)
                print_warning "Please install Go manually from: https://golang.org/dl/"
                return 1
                ;;
        esac
        print_success "Go installed successfully"
    fi
}


# Main installation function
main() {
    if [ "$1" == "--upgrade" ]; then
        UPGRADE=true
    fi

    if [ "$UPGRADE" = true ]; then
        echo "=================================================="
        echo "    Prerequisites Upgrader for Linux"
        echo "=================================================="
        echo
        print_status "Starting upgrade of prerequisites..."
    else
        echo "=================================================="
        echo "    Prerequisites Installer for Linux"
        echo "=================================================="
        echo
        print_status "Starting installation of prerequisites..."
    fi
    echo
    
    # Detect distribution
    detect_distro
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
    
    # Install Go if needed for crush (only on first install)
    install_go
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
