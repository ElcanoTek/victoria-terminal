@echo off
setlocal

rem Path to the version file
set VERSION_FILE=%~dp0..\VERSION

rem Read current version
set /p CURR_VERSION=<%VERSION_FILE%

for /f "tokens=1,2 delims=." %%a in ("%CURR_VERSION%") do (
  set MAJOR=%%a
  set MINOR=%%b
)

set /a MINOR+=1
if %MINOR% GEQ 10 (
  set /a MAJOR+=1
  set MINOR=0
)

set NEW_VERSION=%MAJOR%.%MINOR%
echo %NEW_VERSION% > %VERSION_FILE%

echo Building Victoria version %NEW_VERSION%

rem Update installer script with the new version
powershell -NoProfile -Command "(Get-Content '%~dp0installer_win.iss') -replace 'MyAppVersion ^"[0-9\.]*^"', 'MyAppVersion ^"%NEW_VERSION%^"' ^| Set-Content '%~dp0installer_win.iss'"

rem Create a matching git tag for this release
git tag v%NEW_VERSION%

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
