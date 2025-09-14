@echo off
setlocal

echo Building Victoria version %VERSION%

if not defined VERSION (
    echo "VERSION environment variable is not set."
    exit /b 1
)

rem Code signing configuration
set SIGNTOOL="C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64\signtool.exe"
set CERT_PATH="certificate.pfx"
set CERT_PASS=%WINDOWS_CERTIFICATE_PASSWORD%
set TIMESTAMP_SERVER="http://timestamp.sectigo.com"

rem Clean previous builds
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
del /q *.spec

rem Check for ImageMagick
where /q convert
if %errorlevel% neq 0 (
    echo ImageMagick not found. Please install it and add to PATH.
    exit /b 1
)


rem --- Create Installer Icon ---
set INSTALLER_ICON=assets\VictoriaFleet.ico
if not exist %INSTALLER_ICON% (
    echo "--- Creating ICO for Installer ---"
    convert assets\VictoriaFleet.png -define icon:auto-resize=256,128,64,48,32,16 %INSTALLER_ICON%
)

rem --- Build Victoria Configurator ---
echo "--- Building Victoria Configurator ---"
set REQ_FILE=%~dp0..\requirements.txt
set CONFIGURATOR_ICON=assets\VictoriaConfigurator.ico
if not exist %CONFIGURATOR_ICON% (
    echo "--- Creating ICO for Configurator ---"
    convert assets\VictoriaConfigurator.png -define icon:auto-resize=256,128,64,48,32,16 %CONFIGURATOR_ICON%
)
uvx --with-requirements "%REQ_FILE%" pyinstaller --noconfirm --hidden-import colorama --hidden-import rich --onefile --name VictoriaConfigurator ^
  --icon %CONFIGURATOR_ICON% ^
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

rem --- Code Signing Executables ---
echo "--- Signing Windows Executables ---"

if exist %CERT_PATH% (
    if not exist %SIGNTOOL% (
        echo SignTool not found at %SIGNTOOL%. Skipping code signing.
        echo Please install the Windows SDK to enable signing.
    ) else (
        for %%f in (dist\*.exe) do (
            echo Signing %%f
            %SIGNTOOL% sign /f %CERT_PATH% /p "%CERT_PASS%" /tr %TIMESTAMP_SERVER% /td sha256 /fd sha256 /v "%%f"
            if %errorlevel% neq 0 (
                echo WARNING: Failed to sign %%f. The executable will be unsigned.
            )
        )
    )
) else (
    echo Certificate file not found at %CERT_PATH%. Skipping code signing.
    echo To enable code signing, ensure the certificate is available at the specified path.
)

rem Update installer script with the version
powershell -NoProfile -Command "(Get-Content '%~dp0installer_win.iss') -replace 'MyAppVersion \"[0-9\.]*\"', 'MyAppVersion \"%VERSION%\"' | Set-Content '%~dp0installer_win.iss'"

REM Build installer with Inno Setup (iscc must be on PATH)
iscc %~dp0installer_win.iss

rem --- Sign the Installer ---
if exist %CERT_PATH% (
    if exist %SIGNTOOL% (
        echo "--- Signing the installer ---"
        %SIGNTOOL% sign /f %CERT_PATH% /p "%CERT_PASS%" /tr %TIMESTAMP_SERVER% /td sha256 /fd sha256 /v "dist\VictoriaSetup.exe"
        if %errorlevel% neq 0 (
            echo WARNING: Failed to sign the installer. The installer will be unsigned.
        )
    )
) else (
    echo Certificate file not found. Installer not signed.
)

echo "--- Build complete ---"

