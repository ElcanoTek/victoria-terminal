#!/usr/bin/env bash
set -e
# Build a macOS .app bundle; use --windowed so PyInstaller creates the
# application structure we expect. The wrapper below will launch the binary in
# Terminal, so we do not need the console flag here.
# Bundle identifier for the app
BUNDLE_ID=${BUNDLE_ID:-com.elcanotek.victoria}

# Install dependencies from requirements.txt and run PyInstaller
REQ_FILE="$(dirname "$0")/../requirements.txt"
uvx --with-requirements "$REQ_FILE" pyinstaller --noconfirm --hidden-import colorama --hidden-import rich --windowed --name Victoria \
  --icon assets/icon.icns \
  --osx-bundle-identifier "$BUNDLE_ID" \
  --add-data "configs:configs" \
  --add-data "VICTORIA.md:." \
  --add-data "dependencies/install_prerequisites_macos.sh:dependencies" \
  --add-data "dependencies/set_env_macos_linux.sh:dependencies" \
  victoria.py

APP="dist/Victoria.app"
MACOS="$APP/Contents/MacOS"

# Rename the compiled binary so we can wrap it with a launcher
mv "$MACOS/Victoria" "$MACOS/victoria-bin"

# Wrapper executable that Finder launches. It opens Terminal and runs the binary.
cat > "$MACOS/Victoria" <<'EOF'
#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
BIN="$DIR/victoria-bin"
DEPS="$DIR/../Resources/dependencies"
if [ -n "$TERM_PROGRAM" ]; then
  exec "$BIN"
else
  BIN_ESCAPED=$(printf '%q' "$BIN")
  osascript <<END
tell application "Terminal"
  if not (exists window 1) then
    do script "$BIN_ESCAPED"
  else
    do script "$BIN_ESCAPED" in window 1
    activate
  end if
end tell
END

fi
EOF
chmod +x "$MACOS/Victoria"

# Zip the app for distribution
(cd dist && zip -r ../Victoria.app.zip Victoria.app)
