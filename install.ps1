# Victoria Installer for Windows
#
# This script installs and configures Victoria on a Windows system.
# It should be run from a PowerShell terminal.

# --- Configuration ---
$RepoUrl = "https://github.com/elcanotek/victoria.git"
$InstallDir = "$env:USERPROFILE\.victoria"
$VenvDir = "$InstallDir\venv"
$BinDir = "$InstallDir\bin"

# --- Helper Functions ---
# Colors for output
$ColorRed = "Red"
$ColorGreen = "Green"
$ColorYellow = "Yellow"
$ColorBlue = "Cyan"

function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor $ColorBlue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor $ColorGreen
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor $ColorYellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor $ColorRed
    # Exit the script with a non-zero exit code
    exit 1
}

function Test-CommandExists {
    param([string]$Command)
    return $null -ne (Get-Command $Command -ErrorAction SilentlyContinue)
}

# --- Main Installation Logic ---
function Main {
    Write-Host "==============================================" -ForegroundColor $ColorBlue
    Write-Host "         Victoria Installer for Windows" -ForegroundColor $ColorBlue
    Write-Host "==============================================" -ForegroundColor $ColorBlue
    Write-Host ""

    Write-Status "Starting Victoria installation..."

    # 1. Check for prerequisites
    Write-Status "Checking for prerequisites..."
    if (-not (Test-CommandExists "python")) {
        Write-Error "Python is not installed. Please install Python 3 and ensure it's in your PATH."
    }
    if (-not (Test-CommandExists "git")) {
        Write-Error "Git is not installed. Please install Git and ensure it's in your PATH."
    }
    Write-Success "Prerequisites are satisfied."

    # 2. Create installation directory
    Write-Status "Creating installation directory at $InstallDir..."
    if (-not (Test-Path $InstallDir)) {
        New-Item -ItemType Directory -Path $InstallDir | Out-Null
    }

    # 3. Clone or update the repository
    if (Test-Path "$InstallDir\.git") {
        Write-Status "Victoria is already installed. Updating..."
        Set-Location $InstallDir
        try {
            git pull
        }
        catch {
            Write-Error "Failed to update the repository. Please check your internet connection or git configuration."
        }
    }
    else {
        Write-Status "Cloning Victoria repository..."
        try {
            git clone $RepoUrl $InstallDir
        }
        catch {
            Write-Error "Failed to clone the repository. Please check the URL and your internet connection."
        }
    }
    Set-Location $InstallDir

    # 4. Create a Python virtual environment
    Write-Status "Setting up Python virtual environment at $VenvDir..."
    if (-not (Test-Path $VenvDir)) {
        try {
            python -m venv $VenvDir
        }
        catch {
            Write-Error "Failed to create Python virtual environment."
        }
    }

    # 5. Install dependencies
    Write-Status "Installing dependencies from requirements.txt..."
    $PipExe = "$VenvDir\Scripts\pip.exe"
    if (-not (Test-Path $PipExe)) {
        Write-Error "pip.exe not found in the virtual environment. The venv setup may have failed."
    }
    try {
        & $PipExe install -r requirements.txt
    }
    catch {
        Write-Error "Failed to install dependencies. Please check requirements.txt and your internet connection."
    }

    # 6. Create wrapper scripts and update PATH
    Write-Status "Creating wrapper scripts in $BinDir..."
    if (-not (Test-Path $BinDir)) {
        New-Item -ItemType Directory -Path $BinDir | Out-Null
    }

    $PythonExe = "$VenvDir\Scripts\python.exe"

    # Wrapper for Victoria Configurator
    $WrapperConfigurator = @"
@echo off
"$PythonExe" "$InstallDir\VictoriaConfigurator.py" %*
"@
    $WrapperConfigurator | Set-Content -Path "$BinDir\victoria-configurator.bat" -Encoding Ascii

    # Wrapper for Victoria Terminal
    $WrapperTerminal = @"
@echo off
"$PythonExe" "$InstallDir\VictoriaTerminal.py" %*
"@
    $WrapperTerminal | Set-Content -Path "$BinDir\victoria-terminal.bat" -Encoding Ascii

    # Wrapper for Victoria Browser
    $WrapperBrowser = @"
@echo off
"$PythonExe" "$InstallDir\VictoriaBrowser.py" %*
"@
    $WrapperBrowser | Set-Content -Path "$BinDir\victoria-browser.bat" -Encoding Ascii

    Write-Success "Wrapper scripts created."

    # 7. Add bin directory to user's PATH
    Write-Status "Adding $BinDir to your PATH..."
    $UserPath = [System.Environment]::GetEnvironmentVariable("PATH", "User")
    if ($UserPath -notlike "*$BinDir*") {
        $NewPath = "$UserPath;$BinDir"
        [System.Environment]::SetEnvironmentVariable("PATH", $NewPath, "User")
        $env:PATH = "$env:PATH;$BinDir" # Update for current session
        Write-Success "$BinDir has been added to your PATH."
        Write-Warning "You may need to restart your terminal for the changes to take full effect."
    } else {
        Write-Status "$BinDir is already in your PATH."
    }

    Write-Host ""
    Write-Success "Victoria has been installed successfully!"
    Write-Host ""
    Write-Status "You can now run the following commands from a new terminal:"
    Write-Host "  - victoria-configurator" -ForegroundColor $ColorGreen
    Write-Host "  - victoria-terminal" -ForegroundColor $ColorGreen
    Write-Host "  - victoria-browser" -ForegroundColor $ColorGreen
    Write-Host ""
}

# --- Script Entry Point ---
# Use a try/catch block for global error handling
try {
    Main
}
catch {
    Write-Error "An unexpected error occurred during installation."
    Write-Error "Details: $($_.Exception.Message)"
    exit 1
}
