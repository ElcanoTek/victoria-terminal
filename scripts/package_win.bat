@echo off
uvx pyinstaller --noconfirm --onefile --name Victoria ^
  --icon assets\icon.ico ^
  --add-data "crush.template.json;." ^
  --add-data "snowflake.mcp.json;." ^
  --add-data ".crushignore;." ^
  --add-data "CRUSH.md;." ^
  --add-data "VICTORIA.md;." ^
  victoria.py
REM Build installer with Inno Setup (iscc must be on PATH)
iscc %~dp0installer_win.iss
