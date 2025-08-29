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
if ! command -v python3 >/dev/null 2>&1; then
  "$DEPS/install_prerequisites_macos.sh"
fi
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

# Sign the app if a certificate is provided via environment variables
if [[ -n "$APPLE_CERT_P12" && -n "$APPLE_CERT_PASSWORD" ]]; then
  echo "Importing macOS signing certificate and signing app"
  CERT_PATH=$(mktemp)
  echo "$APPLE_CERT_P12" | base64 --decode > "$CERT_PATH"
  security import "$CERT_PATH" -P "$APPLE_CERT_PASSWORD" -T /usr/bin/codesign >/dev/null 2>&1 || true
  SIGN_ID=$(security find-identity -v -p codesigning | awk 'NR==1{print $2}')
  if [[ -n "$SIGN_ID" ]]; then
    codesign --deep --force --options runtime --sign "$SIGN_ID" "$APP"
  else
    echo "Warning: no signing identity found; app will be unsigned." >&2
  fi
  rm -f "$CERT_PATH"
else
  echo "Warning: macOS signing certificate not found; app will be unsigned." >&2
fi

# Zip the app for distribution
(cd dist && zip -r ../Victoria.app.zip Victoria.app)
