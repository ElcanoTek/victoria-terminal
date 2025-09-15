@echo on
setlocal enabledelayedexpansion

echo Building Victoria version %VERSION%

if not defined VERSION (
    echo "VERSION environment variable is not set."
    exit /b 1
)

rem --- Locate SignTool ---
set SIGNTOOL=
set SIGNTOOL_PATH=

call :find_signtool
goto :after_find_signtool

:find_signtool
rem Set local variables to avoid parentheses issues
set "PGMX86=%ProgramFiles(x86)%"
set "PGMFILES=%ProgramFiles%"

rem Search in Program Files (x86) first
if exist "%PGMX86%\Windows Kits\10\bin\" (
    for /r "%PGMX86%\Windows Kits\10\bin\" %%f in (signtool.exe) do (
        if exist "%%f" (
            set SIGNTOOL_PATH="%%f"
            exit /b
        )
    )
)

rem If not found, search in Program Files
if exist "%PGMFILES%\Windows Kits\10\bin\" (
    for /r "%PGMFILES%\Windows Kits\10\bin\" %%f in (signtool.exe) do (
        if exist "%%f" (
            set SIGNTOOL_PATH="%%f"
            exit /b
        )
    )
)
exit /b

:after_find_signtool
if not defined SIGNTOOL_PATH (
    echo "SignTool.exe not found. Signing will be skipped."
) else (
    echo "Found SignTool at %SIGNTOOL_PATH%"
)
set SIGNTOOL=%SIGNTOOL_PATH%

rem --- Code signing configuration ---
set CERT_PATH="certificate.pfx"
set CERT_PASS=%WINDOWS_CERTIFICATE_PASSWORD%
set TIMESTAMP_SERVER="http://timestamp.digicert.com"

rem --- Clean previous builds ---
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
del /q *.spec

rem --- Icon Generation ---
echo "--- Checking for required .ico files ---"
call :generate_ico_if_needed VictoriaConfigurator
call :generate_ico_if_needed VictoriaTerminal
call :generate_ico_if_needed VictoriaBrowser
call :generate_ico_if_needed VictoriaFleet
goto :build_executables

:generate_ico_if_needed
set APP_NAME=%1
set PNG_PATH=assets\%APP_NAME%.png
set ICO_PATH=assets\%APP_NAME%.ico
if not exist %ICO_PATH% (
    echo >>> Generating icon for %APP_NAME% from %PNG_PATH%...
    where /q magick
    if %errorlevel% neq 0 (
        echo ERROR: ImageMagick 'magick' command not found. Please install ImageMagick.
        exit /b 1
    )
    magick convert %PNG_PATH% -define icon:auto-resize=256,128,64,48,32,16 %ICO_PATH%
)
goto :eof

:build_executables
rem --- Build Victoria Configurator ---
echo "--- Building Victoria Configurator ---"
set REQ_FILE=%~dp0..\requirements.txt
uvx --with-requirements "%REQ_FILE%" pyinstaller --noconfirm --hidden-import colorama --hidden-import rich --onefile --name VictoriaConfigurator ^
  --icon "assets\VictoriaConfigurator.ico" ^
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

rem --- Code Signing ---
if exist %CERT_PATH% (
    if not defined SIGNTOOL_PATH (
        echo SignTool not found. Skipping code signing.
        echo Please install the Windows SDK and ensure SignTool.exe is available.
    ) else (
        echo "--- Signing Windows Executables ---"
        for %%f in (dist\*.exe) do (
            echo Signing %%f
            %SIGNTOOL% sign /f %CERT_PATH% /p "%CERT_PASS%" /tr %TIMESTAMP_SERVER% /td sha256 /fd sha256 /v "%%f"
            if !errorlevel! neq 0 (
                echo ERROR: Failed to sign %%f. Aborting build.
                exit /b 1
            )
        )

        echo "--- Signing the installer ---"
        %SIGNTOOL% sign /f %CERT_PATH% /p "%CERT_PASS%" /tr %TIMESTAMP_SERVER% /td sha256 /fd sha256 /v "dist\VictoriaSetup.exe"
        if !errorlevel! neq 0 (
            echo ERROR: Failed to sign the installer. Aborting build.
            exit /b 1
        )
    )
) else (
    echo Certificate file not found at %CERT_PATH%. Skipping code signing.
)

echo "--- Build complete ---"

