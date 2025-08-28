@echo off
setlocal

rem Determine version string from the current date in YYYY.MM.DD format.
for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyy.MM.dd"') do set VERSION=%%i

echo Building Victoria version %VERSION%

rem Update installer script with the version
powershell -NoProfile -Command "(Get-Content '%~dp0installer_win.iss') -replace 'MyAppVersion ^"[0-9\.]*^"', 'MyAppVersion ^"%VERSION%^"' ^| Set-Content '%~dp0installer_win.iss'"
rem Install dependencies from requirements.txt and run PyInstaller
set REQ_FILE=%~dp0..\requirements.txt
uvx --with-requirements "%REQ_FILE%" pyinstaller --noconfirm --hidden-import colorama --hidden-import rich --onefile --name Victoria ^
  --icon assets\icon.ico ^
  --add-data "configs;configs" ^
  --add-data ".crushignore;." ^
  --add-data "CRUSH.md;." ^
  --add-data "VICTORIA.md;." ^
  victoria.py
REM Build installer with Inno Setup (iscc must be on PATH)
iscc %~dp0installer_win.iss
