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

# Script that actually executes the binary inside a Terminal session
cat > "$MACOS/launch.command" <<'EOF'
#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
"$DIR/victoria-bin"
EOF
chmod +x "$MACOS/launch.command"

# Wrapper executable that Finder launches. It opens Terminal and runs the command script.
cat > "$MACOS/Victoria" <<'EOF'
#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -n "$TERM_PROGRAM" ]; then
  "$DIR/launch.command"
else
  open -a Terminal "$DIR/launch.command"
fi
EOF
chmod +x "$MACOS/Victoria"
