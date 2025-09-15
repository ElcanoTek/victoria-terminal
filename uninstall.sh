#!/usr/bin/env bash
set -e

# --- Configuration ---
INSTALL_DIR="$HOME/.victoria"
CONFIG_DIR="$HOME/Victoria"
BIN_DIR="/usr/local/bin"
WRAPPERS=("victoria-configurator" "victoria-terminal" "victoria-browser")

# --- Helper Functions ---
print_info() {
    echo -e "\033[34m[INFO]\033[0m $1"
}

print_success() {
    echo -e "\033[32m[SUCCESS]\033[0m $1"
}

print_warning() {
    echo -e "\033[33m[WARNING]\033[0m $1"
}

# --- Main Uninstall Logic ---
print_info "Starting Victoria uninstallation..."

# 1. Remove wrapper scripts
print_info "Removing wrapper scripts from $BIN_DIR..."
if [ -w "$BIN_DIR" ]; then
    SUDO_CMD=""
else
    print_warning "Cannot write to $BIN_DIR. You may need to run this script with sudo."
    SUDO_CMD="sudo"
fi

for wrapper in "${WRAPPERS[@]}"; do
    if [ -f "$BIN_DIR/$wrapper" ]; then
        print_info "Removing $BIN_DIR/$wrapper..."
        $SUDO_CMD rm -f "$BIN_DIR/$wrapper"
    else
        print_info "$BIN_DIR/$wrapper does not exist, skipping."
    fi
done

# 2. Remove installation directory
if [ -d "$INSTALL_DIR" ]; then
    print_info "Removing installation directory at $INSTALL_DIR..."
    rm -rf "$INSTALL_DIR"
    print_success "Victoria installation directory removed."
else
    print_info "Installation directory $INSTALL_DIR does not exist, skipping."
fi

# 3. Remove configuration directory
if [ -d "$CONFIG_DIR" ]; then
    print_info "Removing configuration directory at $CONFIG_DIR..."
    rm -rf "$CONFIG_DIR"
    print_success "Victoria configuration directory removed."
else
    print_info "Configuration directory $CONFIG_DIR does not exist, skipping."
fi

print_success "Victoria has been uninstalled successfully!"
