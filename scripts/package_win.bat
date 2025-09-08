@echo off
setlocal
set "PFX_PATH=%TEMP%\win.pfx"

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
  --add-data "VICTORIA.md;." ^
  --add-data "dependencies\install_prerequisites_windows.ps1;dependencies" ^
  --add-data "dependencies\set_env_windows.ps1;dependencies" ^
  victoria.py

rem Include dependencies required for installer
mkdir dist\dependencies
copy dependencies\install_prerequisites_windows.ps1 dist\dependencies\ >nul
copy dependencies\set_env_windows.ps1 dist\dependencies\ >nul

if defined WIN_CERT_PFX if defined WIN_CERT_PASSWORD (
  echo Importing Windows signing certificate and signing executable
  powershell -NoProfile -Command "[IO.File]::WriteAllBytes('%PFX_PATH%',[Convert]::FromBase64String($env:WIN_CERT_PFX))"
  signtool sign /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 ^
      /f "%PFX_PATH%" /p "%WIN_CERT_PASSWORD%" dist\Victoria.exe
) else (
  echo Warning: Windows signing certificate not found; binaries will be unsigned.>&2
)
REM Build installer with Inno Setup (iscc must be on PATH)
iscc %~dp0installer_win.iss

if defined WIN_CERT_PFX if defined WIN_CERT_PASSWORD (
  signtool sign /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 ^
      /f "%PFX_PATH%" /p "%WIN_CERT_PASSWORD%" dist\VictoriaSetup.exe
  del "%PFX_PATH%"
)

rem Remove temporary dependencies directory
if exist dist\dependencies rmdir /s /q dist\dependencies
