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
