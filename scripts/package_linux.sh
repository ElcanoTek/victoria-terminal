#!/usr/bin/env bash
set -e
# Build a Linux AppImage for Victoria.
# This script is designed to be run in a GitHub Actions environment on ubuntu-latest.

# 0. Install ImageMagick if not available (needed for icon resizing)
if ! command -v convert &> /dev/null; then
    echo ">>> Installing ImageMagick..."
    sudo apt-get update && sudo apt-get install -y imagemagick
fi

# 1. Run PyInstaller to create the executable
echo ">>> Running PyInstaller to create the executable..."
REQ_FILE="$(dirname "$0")/../requirements.txt"
# We create a single file executable.
uvx --with-requirements "$REQ_FILE" pyinstaller --noconfirm --onefile --hidden-import colorama --hidden-import rich --name Victoria \
  --add-data "configs:configs" \
  --add-data "VICTORIA.md:." \
  --add-data "dependencies/install_prerequisites_linux.sh:dependencies" \
  --add-data "dependencies/set_env_macos_linux.sh:dependencies" \
  victoria.py

# 2. Set up the AppDir structure
echo ">>> Setting up AppDir structure..."
APPDIR="Victoria.AppDir"
mkdir -p "$APPDIR/usr/bin"
mv dist/Victoria "$APPDIR/usr/bin/"

# 3. Create metadata files
echo ">>> Creating metadata files..."
# Desktop file - specifies this is a terminal application
cat > "$APPDIR/victoria.desktop" <<EOF
[Desktop Entry]
Name=Victoria
Exec=Victoria
Icon=victoria
Type=Application
Categories=Utility;
Terminal=true
EOF

# Copy and resize the icon to 512x512 (maximum supported by linuxdeploy)
# The original icon is 1024x1024, but linuxdeploy only supports up to 512x512
convert assets/icon.png -resize 512x512 "$APPDIR/victoria.png"

# AppRun - a simple launcher script
cat > "$APPDIR/AppRun" <<'EOF'
#!/bin/sh
HERE=$(dirname $(readlink -f "$0"))
"$HERE/usr/bin/Victoria" "$@"
EOF
chmod +x "$APPDIR/AppRun"

# 4. Download and run linuxdeploy
echo ">>> Detecting architecture..."
ARCH=$(uname -m)
case "$ARCH" in
  x86_64)
    LINUXDEPLOY_ARCH="x86_64"
    ;;
  aarch64)
    LINUXDEPLOY_ARCH="aarch64"
    ;;
  *)
    echo "Unsupported architecture: $ARCH"
    exit 1
    ;;
esac

echo ">>> Downloading linuxdeploy for $LINUXDEPLOY_ARCH..."
LINUXDEPLOY_APPIMAGE="linuxdeploy-$LINUXDEPLOY_ARCH.AppImage"
wget -c "https://github.com/linuxdeploy/linuxdeploy/releases/download/continuous/$LINUXDEPLOY_APPIMAGE"
chmod +x "$LINUXDEPLOY_APPIMAGE"

echo ">>> Bundling dependencies with linuxdeploy..."
# Let linuxdeploy find and bundle all necessary libraries.
# The output will be an AppImage file.
"./$LINUXDEPLOY_APPIMAGE" --appdir "$APPDIR" --output appimage -i "$APPDIR/victoria.png" -d "$APPDIR/victoria.desktop"

if [ -z "$VERSION" ]; then
  echo "VERSION environment variable not set; falling back to date"
  VERSION=$(date -u +%Y.%m.%d)
fi

echo ">>> Renaming and cleaning up..."
# The default output name is based on the application name and architecture.
SOURCE_APPIMAGE="Victoria-$LINUXDEPLOY_ARCH.AppImage"
DEST_APPIMAGE="Victoria-${VERSION}-$LINUXDEPLOY_ARCH.AppImage"
mv "$SOURCE_APPIMAGE" "$DEST_APPIMAGE"

echo ">>> AppImage created successfully: $DEST_APPIMAGE"
