@echo off
REM Victoria - AdTech Data Navigation Tool (Windows Batch Wrapper)
REM This batch file launches the PowerShell version of Victoria

REM Check if PowerShell is available
where powershell >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: PowerShell is not available on this system.
    echo Please install PowerShell or use PowerShell Core.
    pause
    exit /b 1
)

REM Get the directory where this batch file is located
set "SCRIPT_DIR=%~dp0"

REM Launch the PowerShell script
powershell -ExecutionPolicy Bypass -File "%SCRIPT_DIR%victoria.ps1"

REM Pause if there was an error
if %errorlevel% neq 0 (
    echo.
    echo Script execution failed. Press any key to exit...
    pause >nul
)