@echo off
REM Prerequisites Installer for Windows (Batch Wrapper)
REM This batch file runs the PowerShell installer script

echo ================================================
echo    Prerequisites Installer for Windows
echo ================================================
echo.

REM Check if PowerShell is available
powershell -Command "Write-Host 'PowerShell is available'" >nul 2>&1
if errorlevel 1 (
    echo ERROR: PowerShell is not available or not in PATH
    echo Please install PowerShell and try again
    pause
    exit /b 1
)

echo Starting PowerShell installer script...
echo.

REM Run the PowerShell script
powershell -ExecutionPolicy RemoteSigned -File "%~dp0install_prerequisites_windows.ps1"

echo.
echo Installation completed. Press any key to exit...
pause >nul

