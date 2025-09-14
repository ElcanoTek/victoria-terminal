#!/usr/bin/env bash
set -e

# Common setup
if ! command -v convert &> /dev/null; then
    echo ">>> Installing ImageMagick..."
    brew install imagemagick
fi
REQ_FILE="$(dirname "$0")/../requirements.txt"
if [ -z "$VERSION" ]; then
  echo "VERSION environment variable not set; falling back to date"
  VERSION=$(date -u +%Y.%m.%d)
fi

# Code signing configuration
DEVELOPER_ID_CERT="${MACOS_CERTIFICATE_NAME:-Developer ID Application: Your Name (TEAM_ID)}"
KEYCHAIN_PROFILE="${KEYCHAIN_PROFILE:-notarization-profile}"

# Clean previous builds
rm -rf dist build *.spec

# --- Build Victoria Configurator ---
echo "--- Building Victoria Configurator ---"
CONFIGURATOR_BUNDLE_ID=${CONFIGURATOR_BUNDLE_ID:-com.elcanotek.victoriaconfigurator}
CONFIGURATOR_ICON="assets/VictoriaConfigurator.icns"
if [ ! -f "$CONFIGURATOR_ICON" ]; then
  echo ">>> Creating ICNS for Configurator..."
  convert "assets/VictoriaConfigurator.png" -define icon:auto-resize=256,128,64,48,32,16 "$CONFIGURATOR_ICON"
fi
uvx --with-requirements "$REQ_FILE" pyinstaller --noconfirm --windowed --name VictoriaConfigurator \
  --hidden-import colorama --hidden-import rich \
  --icon "$CONFIGURATOR_ICON" \
  --osx-bundle-identifier "$CONFIGURATOR_BUNDLE_ID" \
  --add-data "dependencies/common.sh:dependencies" \
  --add-data "dependencies/install_prerequisites_macos.sh:dependencies" \
  --add-data "dependencies/set_env_macos_linux.sh:dependencies" \
  VictoriaConfigurator.py

CONFIGURATOR_APP="dist/VictoriaConfigurator.app"
CONFIGURATOR_MACOS="$CONFIGURATOR_APP/Contents/MacOS"

# Rename the compiled binary so we can wrap it
mv "$CONFIGURATOR_MACOS/VictoriaConfigurator" "$CONFIGURATOR_MACOS/victoriaconfigurator-bin"

# Wrapper executable
cat > "$CONFIGURATOR_MACOS/VictoriaConfigurator" <<'EOF'
#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
BIN="$DIR/victoriaconfigurator-bin"
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
chmod +x "$CONFIGURATOR_MACOS/VictoriaConfigurator"

echo "--- Finished Victoria Configurator ---"

# Clean up build artifacts before the next run
rm -rf build VictoriaConfigurator.spec

# --- Build Victoria Terminal ---
echo "--- Building Victoria Terminal ---"
TERMINAL_BUNDLE_ID=${TERMINAL_BUNDLE_ID:-com.elcanotek.victoriaterminal}
uvx --with-requirements "$REQ_FILE" pyinstaller --noconfirm --windowed --name VictoriaTerminal \
  --hidden-import colorama --hidden-import rich \
  --icon assets/VictoriaTerminal.icns \
  --osx-bundle-identifier "$TERMINAL_BUNDLE_ID" \
  --add-data "configs:configs" \
  --add-data "VICTORIA.md:." \
  VictoriaTerminal.py

TERMINAL_APP="dist/VictoriaTerminal.app"
TERMINAL_MACOS="$TERMINAL_APP/Contents/MacOS"

# Rename the compiled binary so we can wrap it
mv "$TERMINAL_MACOS/VictoriaTerminal" "$TERMINAL_MACOS/victoriaterminal-bin"

# Wrapper executable
cat > "$TERMINAL_MACOS/VictoriaTerminal" <<'EOF'
#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
BIN="$DIR/victoriaterminal-bin"
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
chmod +x "$TERMINAL_MACOS/VictoriaTerminal"
echo "--- Finished Victoria Terminal ---"

# Final cleanup
rm -rf build VictoriaTerminal.spec

# --- Build Victoria Browser ---
echo "--- Building Victoria Browser ---"
BROWSER_BUNDLE_ID=${BROWSER_BUNDLE_ID:-com.elcanotek.victoriabrowser}
uvx --with-requirements "$REQ_FILE" pyinstaller --noconfirm --windowed --name VictoriaBrowser \
  --icon assets/VictoriaBrowser.icns \
  --osx-bundle-identifier "$BROWSER_BUNDLE_ID" \
  VictoriaBrowser.py
echo "--- Finished Victoria Browser ---"

# Final cleanup
rm -rf build VictoriaBrowser.spec

# --- Code Signing and Notarization ---
echo "--- Signing and Notarizing macOS Apps ---"

# Create entitlements file
cat > entitlements.plist <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>com.apple.security.cs.allow-jit</key>
    <true/>
    <key>com.apple.security.cs.allow-unsigned-executable-memory</key>
    <true/>
    <key>com.apple.security.cs.allow-dyld-environment-variables</key>
    <true/>
</dict>
</plist>
EOF

# Sign all executables and frameworks within each app bundle
for app in dist/*.app; do
    echo "Signing all binaries in $app"
    
    # Sign all frameworks and dylibs first
    find "$app" -name "*.framework" -o -name "*.dylib" -o -name "*.so" | while read -r file; do
        echo "  Signing $file"
        codesign --force --verify --verbose --timestamp --options=runtime --sign "$DEVELOPER_ID_CERT" "$file" || true
    done
    
    # Sign all executables
    find "$app" -type f -perm -111 | while read -r file; do
        if file "$file" | grep -q "Mach-O"; then
            echo "  Signing executable $file"
            codesign --force --verify --verbose --timestamp --options=runtime --entitlements entitlements.plist --sign "$DEVELOPER_ID_CERT" "$file"
        fi
    done
    
    # Finally, sign the app bundle itself
    echo "Signing app bundle $app"
    codesign --force --verify --verbose --timestamp --options=runtime --entitlements entitlements.plist --sign "$DEVELOPER_ID_CERT" "$app"
    
    # Verify the signature
    echo "Verifying signature for $app"
    codesign --verify --deep --strict --verbose=2 "$app"
    spctl --assess --type exec --verbose "$app"
done

# Create a zip archive for notarization
echo "Creating archive for notarization..."
(cd dist && zip -r "../Victoria-${VERSION}-macos.zip" .)

# Notarize the application
echo "Notarizing the application..."
xcrun notarytool submit "Victoria-${VERSION}-macos.zip" --keychain-profile "$KEYCHAIN_PROFILE" --wait

# Extract and staple each app
echo "Stapling notarization tickets..."
rm -rf temp_extract
mkdir temp_extract
(cd temp_extract && unzip "../Victoria-${VERSION}-macos.zip")

for app in temp_extract/*.app; do
    echo "Stapling $app"
    xcrun stapler staple "$app"
done

# Recreate the final archive with stapled apps
rm "Victoria-${VERSION}-macos.zip"
(cd temp_extract && zip -r "../Victoria-${VERSION}-macos.zip" .)
rm -rf temp_extract

echo "--- macOS build complete ---"

