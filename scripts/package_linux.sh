#!/usr/bin/env bash
set -e
# Build Linux AppImages for Victoria tools.

# 0. Common setup
if ! command -v convert &> /dev/null; then
    echo ">>> Installing ImageMagick..."
    sudo apt-get update && sudo apt-get install -y imagemagick
fi
REQ_FILE="$(dirname "$0")/../requirements.txt"
if [ -z "$VERSION" ]; then
  echo "VERSION environment variable not set; falling back to date"
  VERSION=$(date -u +%Y.%m.%d)
fi
ARCH=$(uname -m)
case "$ARCH" in
  x86_64) LINUXDEPLOY_ARCH="x86_64" ;;
  aarch64) LINUXDEPLOY_ARCH="aarch64" ;;
  *) echo "Unsupported architecture: $ARCH"; exit 1 ;;
esac
LINUXDEPLOY_APPIMAGE="linuxdeploy-$LINUXDEPLOY_ARCH.AppImage"
wget -c "https://github.com/linuxdeploy/linuxdeploy/releases/download/continuous/$LINUXDEPLOY_APPIMAGE"
chmod +x "$LINUXDEPLOY_APPIMAGE"

# Clean previous builds
rm -rf dist build *.spec Victoria*.AppDir Victoria*.AppImage

# 1. Run PyInstaller for both executables
echo ">>> Running PyInstaller for both executables..."
uvx --with-requirements "$REQ_FILE" pyinstaller --noconfirm --onefile --hidden-import colorama --hidden-import rich --name VictoriaConfigurator \
  --add-data "dependencies/common.sh:dependencies" \
  --add-data "dependencies/install_prerequisites_linux.sh:dependencies" \
  --add-data "dependencies/set_env_macos_linux.sh:dependencies" \
  VictoriaConfigurator.py

uvx --with-requirements "$REQ_FILE" pyinstaller --noconfirm --onefile --hidden-import colorama --hidden-import rich --name VictoriaTerminal \
  --add-data "configs:configs" \
  --add-data "VICTORIA.md:." \
  VictoriaTerminal.py

uvx --with-requirements "$REQ_FILE" pyinstaller --noconfirm --onefile --name VictoriaBrowser \
  VictoriaBrowser.py


# --- Build Victoria Configurator AppImage ---
echo ">>> Building Victoria Configurator AppImage..."
APPDIR_CONFIG="VictoriaConfigurator.AppDir"
mkdir -p "$APPDIR_CONFIG/usr/bin"
mv dist/VictoriaConfigurator "$APPDIR_CONFIG/usr/bin/"

cat > "$APPDIR_CONFIG/victoriaconfigurator.desktop" <<EOF
[Desktop Entry]
Name=Victoria Configurator
Exec=VictoriaConfigurator
Icon=victoriaconfigurator
Type=Application
Categories=Utility;
Terminal=true
EOF

convert assets/VictoriaConfigurator.png -resize 512x512 "$APPDIR_CONFIG/victoriaconfigurator.png"

cat > "$APPDIR_CONFIG/AppRun" <<'EOF'
#!/bin/sh
HERE=$(dirname $(readlink -f "$0"))
"$HERE/usr/bin/VictoriaConfigurator" "$@"
EOF
chmod +x "$APPDIR_CONFIG/AppRun"

echo ">>> Bundling dependencies with linuxdeploy for Configurator..."
SOURCE_APPIMAGE_CONFIG="VictoriaConfigurator-$LINUXDEPLOY_ARCH.AppImage"
OUTPUT="$SOURCE_APPIMAGE_CONFIG" "./$LINUXDEPLOY_APPIMAGE" --appdir "$APPDIR_CONFIG" --output appimage -i "$APPDIR_CONFIG/victoriaconfigurator.png" -d "$APPDIR_CONFIG/victoriaconfigurator.desktop"
DEST_APPIMAGE_CONFIG="VictoriaConfigurator-${VERSION}-$LINUXDEPLOY_ARCH.AppImage"
mv "$SOURCE_APPIMAGE_CONFIG" "$DEST_APPIMAGE_CONFIG"
echo ">>> Configurator AppImage created: $DEST_APPIMAGE_CONFIG"


# --- Build Victoria Terminal AppImage ---
echo ">>> Building Victoria Terminal AppImage..."
APPDIR_TERM="VictoriaTerminal.AppDir"
mkdir -p "$APPDIR_TERM/usr/bin"
mv dist/VictoriaTerminal "$APPDIR_TERM/usr/bin/"

cat > "$APPDIR_TERM/victoriaterminal.desktop" <<EOF
[Desktop Entry]
Name=Victoria Terminal
Exec=VictoriaTerminal
Icon=victoriaterminal
Type=Application
Categories=Utility;
Terminal=true
EOF

convert assets/VictoriaTerminal.png -resize 512x512 "$APPDIR_TERM/victoriaterminal.png"

cat > "$APPDIR_TERM/AppRun" <<'EOF'
#!/bin/sh
HERE=$(dirname $(readlink -f "$0"))
"$HERE/usr/bin/VictoriaTerminal" "$@"
EOF
chmod +x "$APPDIR_TERM/AppRun"

echo ">>> Bundling dependencies with linuxdeploy for Terminal..."
SOURCE_APPIMAGE_TERM="VictoriaTerminal-$LINUXDEPLOY_ARCH.AppImage"
OUTPUT="$SOURCE_APPIMAGE_TERM" "./$LINUXDEPLOY_APPIMAGE" --appdir "$APPDIR_TERM" --output appimage -i "$APPDIR_TERM/victoriaterminal.png" -d "$APPDIR_TERM/victoriaterminal.desktop"
DEST_APPIMAGE_TERM="VictoriaTerminal-${VERSION}-$LINUXDEPLOY_ARCH.AppImage"
mv "$SOURCE_APPIMAGE_TERM" "$DEST_APPIMAGE_TERM"
echo ">>> Terminal AppImage created: $DEST_APPIMAGE_TERM"


# --- Build Victoria Browser AppImage ---
echo ">>> Building Victoria Browser AppImage..."
APPDIR_BROWSER="VictoriaBrowser.AppDir"
mkdir -p "$APPDIR_BROWSER/usr/bin"
mv dist/VictoriaBrowser "$APPDIR_BROWSER/usr/bin/"

cat > "$APPDIR_BROWSER/victoriabrowser.desktop" <<EOF
[Desktop Entry]
Name=Victoria Browser
Exec=VictoriaBrowser
Icon=victoriabrowser
Type=Application
Categories=Utility;
Terminal=false
EOF

convert assets/VictoriaBrowser.png -resize 512x512 "$APPDIR_BROWSER/victoriabrowser.png"

cat > "$APPDIR_BROWSER/AppRun" <<'EOF'
#!/bin/sh
HERE=$(dirname $(readlink -f "$0"))
"$HERE/usr/bin/VictoriaBrowser" "$@"
EOF
chmod +x "$APPDIR_BROWSER/AppRun"

echo ">>> Bundling dependencies with linuxdeploy for Browser..."
SOURCE_APPIMAGE_BROWSER="VictoriaBrowser-$LINUXDEPLOY_ARCH.AppImage"
OUTPUT="$SOURCE_APPIMAGE_BROWSER" "./$LINUXDEPLOY_APPIMAGE" --appdir "$APPDIR_BROWSER" --output appimage -i "$APPDIR_BROWSER/victoriabrowser.png" -d "$APPDIR_BROWSER/victoriabrowser.desktop"
DEST_APPIMAGE_BROWSER="VictoriaBrowser-${VERSION}-$LINUXDEPLOY_ARCH.AppImage"
mv "$SOURCE_APPIMAGE_BROWSER" "$DEST_APPIMAGE_BROWSER"
echo ">>> Browser AppImage created: $DEST_APPIMAGE_BROWSER"


echo ">>> All AppImages created successfully."

# --- Create final consolidated archive ---
echo "--- Creating consolidated Linux archive ---"
ARCHIVE_NAME="Victoria-${VERSION}-linux-${ARCH}.tar.gz"
tar -czf "$ARCHIVE_NAME" Victoria*-*-$ARCH.AppImage
rm Victoria*-*-$ARCH.AppImage
echo "--- Linux build complete: $ARCHIVE_NAME created ---"
