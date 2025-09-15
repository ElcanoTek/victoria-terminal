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

# Wrapper for Victoria Browser
    $SUDO_CMD tee "$BIN_DIR/victoria-browser" > /dev/null <<EOF
#!/usr/bin/env bash
exec "$VENV_DIR/bin/python" "$INSTALL_DIR/VictoriaBrowser.py" "\$@"
EOF
    $SUDO_CMD chmod +x "$BIN_DIR/victoria-browser"

    print_success "Victoria has been installed successfully!"
    print_info "You can now run the following commands from your terminal:"
    echo "  - victoria-configurator"
    echo "  - victoria-terminal"
    echo "  - victoria-browser"

    if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
        print_warning "The directory $BIN_DIR is not in your PATH. You may need to add it."
        print_info "You can do this by adding the following line to your shell profile (e.g., ~/.bashrc, ~/.zshrc):"
        echo "  export PATH=\"\$PATH:$BIN_DIR\""
    fi
}

# --- Script Entry Point ---
# Pass all script arguments to the main function
main "$@"
