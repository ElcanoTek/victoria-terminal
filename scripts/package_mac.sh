#!/usr/bin/env bash
set -e

# Common setup
REQ_FILE="$(dirname "$0")/../requirements.txt"
if [ -z "$VERSION" ]; then
  echo "VERSION environment variable not set; falling back to date"
  VERSION=$(date -u +%Y.%m.%d)
fi

# Clean previous builds
rm -rf dist build *.spec

# --- Build Victoria Configurator ---
echo "--- Building Victoria Configurator ---"
CONFIGURATOR_BUNDLE_ID=${CONFIGURATOR_BUNDLE_ID:-com.elcanotek.victoriaconfigurator}
uvx --with-requirements "$REQ_FILE" pyinstaller --noconfirm --windowed --name VictoriaConfigurator \
  --hidden-import colorama --hidden-import rich \
  --icon assets/VictoriaTerminal.icns \
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


# --- Create final consolidated archive ---
echo "--- Creating consolidated macOS archive ---"
(cd dist && zip -r "../Victoria-${VERSION}-macos.zip" .)
echo "--- macOS build complete ---"
