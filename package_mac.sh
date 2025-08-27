#!/usr/bin/env bash
set -e
uvx pyinstaller --noconfirm --console --name Victoria \
  --icon assets/icon.icns \
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
  osascript <<END
tell application "Terminal"
  if not (exists window 1) then
    do script "$BIN"
  else
    do script "$BIN" in window 1
    activate
  end if
end tell
END
fi
EOF
chmod +x "$MACOS/Victoria"
