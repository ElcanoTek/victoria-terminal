#!/usr/bin/env bash
set -e

# --- Configuration ---
INSTALL_DIR="$HOME/.victoria"
VENV_DIR="$INSTALL_DIR/venv"
BIN_DIR="/usr/local/bin"
REPO_URL="https://github.com/ElcanoTek/victoria-fleet.git"
DEFAULT_BRANCH="main" # 'stable' version

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

print_error() {
    echo -e "\033[31m[ERROR]\033[0m $1" >&2
    exit 1
}

# --- Main Installation Logic ---
main() {
    # Determine version to install
    local version="$1"
    local branch_to_checkout="$DEFAULT_BRANCH"

    if [ -z "$version" ] || [ "$version" == "stable" ]; then
        print_info "Installing stable version of Victoria."
        branch_to_checkout="$DEFAULT_BRANCH"
    elif [ "$version" == "latest" ]; then
        print_info "Installing latest version (from 'dev' branch) of Victoria."
        branch_to_checkout="dev"
    else
        print_info "Installing specific version: $version"
        branch_to_checkout="$version"
    fi

    print_info "Starting Victoria installation..."

    # 1. Check for prerequisites
    if ! command -v python3 &>/dev/null; then
        print_error "Python 3 is not installed. Please install it to continue."
    fi
    if ! command -v git &>/dev/null; then
        print_error "Git is not installed. Please install it to continue."
    fi

    # 2. Create installation directory
    print_info "Creating installation directory at $INSTALL_DIR..."
    mkdir -p "$INSTALL_DIR"

    # 3. Clone or update the repository
    if [ -d "$INSTALL_DIR/.git" ]; then
        print_info "Victoria is already installed. Updating to version '$branch_to_checkout'..."
        cd "$INSTALL_DIR"
        git fetch --all --prune
        if ! git checkout "$branch_to_checkout"; then
            print_error "Failed to checkout version '$branch_to_checkout'. Does it exist?"
        fi
        git pull origin "$branch_to_checkout"
    else
        print_info "Cloning Victoria repository (version: $branch_to_checkout)..."
        git clone --branch "$branch_to_checkout" "$REPO_URL" "$INSTALL_DIR"
    fi
    cd "$INSTALL_DIR"

    # 4. Create and activate a virtual environment
    print_info "Setting up Python virtual environment..."
    if [ ! -d "$VENV_DIR" ]; then
        python3 -m venv "$VENV_DIR"
    fi
    source "$VENV_DIR/bin/activate"

    # 5. Install dependencies
    print_info "Installing dependencies..."
    pip install -r requirements.txt

    # 6. Create wrapper scripts
    print_info "Creating wrapper scripts in $BIN_DIR..."
    if [ ! -w "$BIN_DIR" ]; then
        print_warning "Cannot write to $BIN_DIR. You may need to run this script with sudo, or create the wrappers manually."
        SUDO_CMD="sudo"
    else
        SUDO_CMD=""
    fi

    # Wrapper for Victoria Configurator
    $SUDO_CMD tee "$BIN_DIR/victoria-configurator" > /dev/null <<EOF
#!/usr/bin/env bash
exec "$VENV_DIR/bin/python" "$INSTALL_DIR/VictoriaConfigurator.py" "\$@"
EOF
    $SUDO_CMD chmod +x "$BIN_DIR/victoria-configurator"

    # Wrapper for Victoria Terminal
    $SUDO_CMD tee "$BIN_DIR/victoria-terminal" > /dev/null <<EOF
#!/usr/bin/env bash
exec "$VENV_DIR/bin/python" "$INSTALL_DIR/VictoriaTerminal.py" "\$@"
EOF
    $SUDO_CMD chmod +x "$BIN_DIR/victoria-terminal"

    print_success "Victoria has been installed successfully!"
    print_info "You can now run the following commands from your terminal:"
    echo "  - victoria-configurator"
    echo "  - victoria-terminal"

    # 7. Update shell configuration
    update_shell_config
}

# --- Shell Configuration Logic ---
update_shell_config() {
    print_info "Checking if $BIN_DIR is in your PATH..."

    if [[ ":$PATH:" == *":$BIN_DIR:"* ]]; then
        print_info "$BIN_DIR is already in your PATH. No changes needed."
        return
    fi

    read -p "The directory $BIN_DIR is not in your PATH. Add it now? [Y/n] " -r answer
    # Default to 'yes' if no answer is given
    if [[ -z "$answer" || "$answer" =~ ^[Yy]$ ]]; then
        local shell_config_file="$HOME/.bashrc"

        if [ ! -f "$shell_config_file" ]; then
            print_warning "Could not find ~/.bashrc. Creating it."
            touch "$shell_config_file"
        fi

        print_info "Adding $BIN_DIR to PATH in $shell_config_file..."
        # Use a comment to identify the line for future reference or uninstallation
        echo -e "\n# Added by Victoria installer" >> "$shell_config_file"
        echo "export PATH=\"\$PATH:$BIN_DIR\"" >> "$shell_config_file"

        print_success "$BIN_DIR has been added to your PATH."
        print_info "Attempting to apply changes to the current session..."

        # Try to source the file for the current session
        # This may not work depending on how the script is executed
        if [ -f "$shell_config_file" ]; then
            source "$shell_config_file"
            # Check if the PATH was updated in the current script's environment
            if [[ ":$PATH:" == *":$BIN_DIR:"* ]]; then
                print_success "PATH updated for the current session."
            else
                print_warning "Could not automatically update PATH for the current session."
                print_info "Please run the following command to apply changes:"
                echo "  source $shell_config_file"
            fi
        fi
    else
        print_warning "You chose not to update your PATH. You will need to add $BIN_DIR to your PATH manually to run Victoria commands."
    fi
}


# --- Script Entry Point ---
# Pass all script arguments to the main function
main "$@"
