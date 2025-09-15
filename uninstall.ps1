# Victoria Uninstaller for Windows
#
# This script uninstalls Victoria from a Windows system.
# It should be run from a PowerShell terminal.

# --- Configuration ---
$InstallDir = "$env:USERPROFILE\.victoria"
$ConfigDir = "$env:USERPROFILE\Victoria"
$BinDir = "$InstallDir\bin"

# --- Helper Functions ---
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
}

# --- Main Uninstall Logic ---
function Main {
    Write-Host "==============================================" -ForegroundColor $ColorBlue
    Write-Host "       Victoria Uninstaller for Windows" -ForegroundColor $ColorBlue
    Write-Host "==============================================" -ForegroundColor $ColorBlue
    Write-Host ""

    Write-Status "Starting Victoria uninstallation..."

    # 1. Remove bin directory from user's PATH
    Write-Status "Removing $BinDir from your PATH..."
    try {
        $UserPath = [System.Environment]::GetEnvironmentVariable("PATH", "User")
        if ($UserPath -like "*$BinDir*") {
            $NewPath = ($UserPath.Split(';') | Where-Object { $_ -ne $BinDir }) -join ';'
            [System.Environment]::SetEnvironmentVariable("PATH", $NewPath, "User")
            Write-Success "$BinDir has been removed from your PATH."
            Write-Warning "You may need to restart your terminal for the changes to take full effect."
        } else {
            Write-Status "$BinDir was not found in your PATH."
        }
    }
    catch {
        Write-Warning "Could not modify PATH. You may need to remove '$BinDir' from your PATH manually."
    }


    # 2. Remove installation directory
    if (Test-Path $InstallDir) {
        Write-Status "Removing installation directory at $InstallDir..."
        try {
            Remove-Item -Recurse -Force -Path $InstallDir
            Write-Success "Victoria installation directory removed."
        }
        catch {
            Write-Warning "Could not remove '$InstallDir'. You may need to remove it manually."
        }
    } else {
        Write-Status "Installation directory $InstallDir does not exist, skipping."
    }

    # 3. Remove configuration directory
    if (Test-Path $ConfigDir) {
        Write-Warning "The directory $ConfigDir contains your Victoria configuration and secrets."
        $Choice = Read-Host "Do you want to permanently delete it? [y/N]"
        if ($Choice -eq 'y' -or $Choice -eq 'Y') {
            Write-Status "Removing configuration directory at $ConfigDir..."
            try {
                Remove-Item -Recurse -Force -Path $ConfigDir
                Write-Success "Victoria configuration directory removed."
            }
            catch {
                Write-Warning "Could not remove '$ConfigDir'. You may need to remove it manually."
            }
        } else {
            Write-Status "Skipping removal of configuration directory."
        }
    }

    Write-Host ""
    Write-Success "Victoria has been uninstalled successfully!"
    Write-Host ""
}

# --- Script Entry Point ---
try {
    Main
}
catch {
    Write-Error "An unexpected error occurred during uninstallation."
    Write-Error "Details: $($_.Exception.Message)"
    exit 1
}
