#!/usr/bin/env bash
set -e
pyinstaller --noconfirm --windowed --name Victoria \
  --icon assets/icon.icns \
  --add-data "crush.template.json:." \
  --add-data "snowflake.mcp.json:." \
  --add-data ".crushignore:." \
  victoria.py
