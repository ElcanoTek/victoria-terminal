@echo off
setlocal

echo Building Victoria version %VERSION%

if not defined VERSION (
    echo "VERSION environment variable is not set."
    exit /b 1
)

rem Clean previous builds
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
del /q *.spec

rem --- Build Victoria Configurator ---
echo "--- Building Victoria Configurator ---"
set REQ_FILE=%~dp0..\requirements.txt
uvx --with-requirements "%REQ_FILE%" pyinstaller --noconfirm --hidden-import colorama --hidden-import rich --onefile --name VictoriaConfigurator ^
  --icon assets\VictoriaTerminal.ico ^
  --add-data "dependencies\install_prerequisites_windows.ps1;dependencies" ^
  --add-data "dependencies\set_env_windows.ps1;dependencies" ^
  VictoriaConfigurator.py

rem --- Build Victoria Terminal ---
echo "--- Building Victoria Terminal ---"
uvx --with-requirements "%REQ_FILE%" pyinstaller --noconfirm --hidden-import colorama --hidden-import rich --onefile --name VictoriaTerminal ^
  --icon assets\VictoriaTerminal.ico ^
  --add-data "configs;configs" ^
  --add-data "VICTORIA.md;." ^
  VictoriaTerminal.py

rem --- Build Victoria Browser ---
echo "--- Building Victoria Browser ---"
uvx --with-requirements "%REQ_FILE%" pyinstaller --noconfirm --onefile --name VictoriaBrowser ^
  --icon assets\VictoriaBrowser.ico ^
  VictoriaBrowser.py

rem Update installer script with the version
powershell -NoProfile -Command "(Get-Content '%~dp0installer_win.iss') -replace 'MyAppVersion \"[0-9\.]*\"', 'MyAppVersion \"%VERSION%\"' | Set-Content '%~dp0installer_win.iss'"

REM Build installer with Inno Setup (iscc must be on PATH)
iscc %~dp0installer_win.iss

echo "--- Build complete ---"
