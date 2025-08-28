#!/usr/bin/env bash
set -e
# Build a macOS .app bundle; use --windowed so PyInstaller creates the
# application structure we expect. The wrapper below will launch the binary in
# Terminal, so we do not need the console flag here.
# Bundle identifier for the app
BUNDLE_ID=${BUNDLE_ID:-com.elcanotek.victoria}

# Ensure required Python packages are installed
uv pip install --system colorama rich >/dev/null

uvx pyinstaller --noconfirm --hidden-import colorama --hidden-import rich --windowed --name Victoria \
  --icon assets/icon.icns \
  --osx-bundle-identifier "$BUNDLE_ID" \
  --add-data "crush.template.json:." \
  --add-data "snowflake.mcp.json:." \
  --add-data ".crushignore:." \
  --add-data "CRUSH.md:." \
  --add-data "VICTORIA.md:." \
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
