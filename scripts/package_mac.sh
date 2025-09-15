#!/usr/bin/env bash
set -e

# Common setup
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

# --- Helper function for icon generation ---
generate_icns_if_needed() {
    local app_name=$1
    local source_png="assets/${app_name}.png"
    local icns_path="assets/${app_name}.icns"

    if [ -f "$icns_path" ]; then
        return 0
    fi

    echo "--- Generating rounded icon for ${app_name} ---"

    # Check for dependencies
    for cmd in magick identify sips iconutil bc; do
        if ! command -v "$cmd" &> /dev/null; then
            echo "ERROR: Command '$cmd' not found. Please install it to proceed."
            echo "On macOS, 'magick' and 'identify' are part of ImageMagick ('brew install imagemagick')."
            echo "'bc' can be installed with 'brew install bc'."
            exit 1
        fi
    done

    local base_image_size
    base_image_size=$(identify -format '%w' "${source_png}")
    local rounded_png="assets/${app_name}_rounded.png"
    local iconset_dir="${app_name}.iconset"

    # 1. Create a rounded mask. The corner radius is ~22.2% of the image size.
    echo "Creating rounded mask..."
    local corner_radius
    corner_radius=$(echo "$base_image_size * 0.222" | bc)
    magick -size "${base_image_size}x${base_image_size}" xc:none -draw "roundrectangle 0,0,${base_image_size},${base_image_size},${corner_radius},${corner_radius}" mask.png

    # 2. Apply the mask to the source image
    echo "Applying mask to ${source_png}..."
    magick "${source_png}" -alpha on -compose copyopacity mask.png "${rounded_png}"

    # 3. Create the iconset directory
    echo "Creating iconset directory: ${iconset_dir}"
    mkdir -p "${iconset_dir}"

    # 4. Generate different sizes for the iconset
    echo "Generating image sizes..."
    sips -z 16 16   "${rounded_png}" --out "${iconset_dir}/icon_16x16.png"
    sips -z 32 32   "${rounded_png}" --out "${iconset_dir}/icon_16x16@2x.png"
    sips -z 32 32   "${rounded_png}" --out "${iconset_dir}/icon_32x32.png"
    sips -z 64 64   "${rounded_png}" --out "${iconset_dir}/icon_32x32@2x.png"
    sips -z 128 128 "${rounded_png}" --out "${iconset_dir}/icon_128x128.png"
    sips -z 256 256 "${rounded_png}" --out "${iconset_dir}/icon_128x128@2x.png"
    sips -z 256 256 "${rounded_png}" --out "${iconset_dir}/icon_256x256.png"
    sips -z 512 512 "${rounded_png}" --out "${iconset_dir}/icon_256x256@2x.png"
    sips -z 512 512 "${rounded_png}" --out "${iconset_dir}/icon_512x512.png"
    sips -z 1024 1024 "${rounded_png}" --out "${iconset_dir}/icon_512x512@2x.png"

    # 5. Create the .icns file
    echo "Creating .icns file: ${icns_path}"
    iconutil -c icns "${iconset_dir}" -o "${icns_path}"

    # 6. Clean up
    echo "Cleaning up temporary files..."
    rm -f mask.png "${rounded_png}"
    rm -rf "${iconset_dir}"

    echo "--- Finished ${app_name} icon ---"
}

# --- Build Victoria Configurator ---
echo "--- Building Victoria Configurator ---"
generate_icns_if_needed "VictoriaConfigurator"
CONFIGURATOR_BUNDLE_ID=${CONFIGURATOR_BUNDLE_ID:-com.elcanotek.victoriaconfigurator}
CONFIGURATOR_ICON="assets/VictoriaConfigurator.icns"
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
generate_icns_if_needed "VictoriaTerminal"
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
generate_icns_if_needed "VictoriaBrowser"
BROWSER_BUNDLE_ID=${BROWSER_BUNDLE_ID:-com.elcanotek.victoriabrowser}
uvx --with-requirements "$REQ_FILE" pyinstaller --noconfirm --windowed --name VictoriaBrowser \
  --icon assets/VictoriaBrowser.icns \
  --osx-bundle-identifier "$BROWSER_BUNDLE_ID" \
  VictoriaBrowser.py
echo "--- Finished Victoria Browser ---"

# Final cleanup
rm -rf build VictoriaBrowser.spec

# --- Code Signing and Notarization ---
if [[ -n "${MACOS_CERTIFICATE_NAME}" && "${MACOS_CERTIFICATE_NAME}" != "Developer ID Application: Your Name (TEAM_ID)" ]]; then
    echo "--- Signing and Notarizing macOS Apps ---"

    # Create entitlements file
    ENTITLEMENTS="entitlements.plist"
    cat > "$ENTITLEMENTS" <<EOF
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

    for app in dist/*.app; do
        echo "--- Processing $app ---"
        APP_NAME=$(basename "$app")
        APP_ZIP="${APP_NAME%.app}.zip"

        # 1. Codesign the app
        echo "Signing $app with Hardened Runtime and timestamp..."
        codesign --force --deep --options runtime --timestamp \
            --entitlements "$ENTITLEMENTS" \
            --sign "$DEVELOPER_ID_CERT" "$app"

        # 2. Create a zip for submission
        echo "Creating archive $APP_ZIP for notarization..."
        ditto -c -k --keepParent "$app" "$APP_ZIP"

        # 3. Notarize the app
        echo "Submitting $APP_ZIP for notarization..."
        if [[ -n "${APPLE_ID}" && -n "${APP_SPECIFIC_PASSWORD}" && -n "${TEAM_ID}" ]]; then
            xcrun notarytool submit "$APP_ZIP" \
                --apple-id "$APPLE_ID" \
                --password "$APP_SPECIFIC_PASSWORD" \
                --team-id "$TEAM_ID" \
                --wait
        elif [[ -n "${KEYCHAIN_PROFILE}" ]]; then
            xcrun notarytool submit "$APP_ZIP" \
                --keychain-profile "$KEYCHAIN_PROFILE" \
                --wait
        else
            echo "Error: Notarization credentials not found."
            echo "Set APPLE_ID, APP_SPECIFIC_PASSWORD, and TEAM_ID, or set KEYCHAIN_PROFILE."
            exit 1
        fi

        # 4. Staple the ticket to the app
        echo "Stapling notarization ticket to $app..."
        xcrun stapler staple "$app"

        # 5. Verify the app's signature and notarization
        echo "Verifying signature and notarization for $app..."
        codesign --verify --deep --strict --verbose=2 "$app"
        spctl -a -vvv --type exec "$app"

        # 6. Clean up the temporary zip
        rm "$APP_ZIP"
        echo "--- Finished processing $app ---"
    done

    # Create the final distributable archive
    ARCHIVE_NAME="Victoria-${VERSION}-macos.zip"
    echo "Creating final distributable archive: $ARCHIVE_NAME"
    (cd dist && zip -r "../$ARCHIVE_NAME" ./*.app)

    # Clean up entitlements file
    rm "$ENTITLEMENTS"

    echo "--- macOS build complete (Signed and Notarized) ---"
else
    echo "--- Skipping Code Signing and Notarization ---"
    echo "MACOS_CERTIFICATE_NAME not set or is default. Creating unsigned apps."
    (cd dist && zip -r "../Victoria-${VERSION}-macos.zip" ./*.app)
    echo "--- macOS build complete (Unsigned) ---"
fi

