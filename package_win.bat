@echo off
pyinstaller --noconfirm --onefile --name Victoria ^
  --icon assets\icon.ico ^
  --add-data "crush.template.json;." ^
  --add-data "snowflake.mcp.json;." ^
  --add-data ".crushignore;." ^
  victoria.py
