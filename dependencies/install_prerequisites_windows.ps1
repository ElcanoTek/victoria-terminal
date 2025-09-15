# Prerequisites Installer for Windows
# This script installs the required dependencies for the project
# Run this script in PowerShell as Administrator for best results

param(
    [switch]$Upgrade
)

# Set execution policy for current session, but don't fail if it's already set by a more specific policy
try {
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force -ErrorAction Stop
}
catch {
    Write-Warning "Could not set execution policy. This is usually not a problem if the script continues to run."
    Write-Warning "Details: $($_.Exception.Message)"
}

# Colors for output
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Cyan"

function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor $Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor $Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor $Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor $Red
}

function Test-CommandExists {
    param([string]$Command)
    $null -ne (Get-Command $Command -ErrorAction SilentlyContinue)
}

function Install-WinGet {
    if (-not (Test-CommandExists "winget")) {
        Write-Status "Installing WinGet (Windows Package Manager)..."
        try {
            # Try to install from Microsoft Store
            $progressPreference = 'silentlyContinue'
            Invoke-WebRequest -Uri "https://aka.ms/getwinget" -OutFile "$env:TEMP\Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle"
            Add-AppxPackage "$env:TEMP\Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle"
            Remove-Item "$env:TEMP\Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle"
            Write-Success "WinGet installed successfully"
        }
        catch {
            Write-Warning "Could not install WinGet automatically. Please install it manually from Microsoft Store."
            Write-Status "Visit: https://aka.ms/getwinget"
            return $false
        }
    }
    else {
        Write-Success "WinGet is already installed"
    }
    return $true
}

function Install-Scoop {
    if (-not (Test-CommandExists "scoop")) {
        Write-Status "Installing Scoop package manager..."
        try {
            Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
            Invoke-RestMethod get.scoop.sh | Invoke-Expression
            Write-Success "Scoop installed successfully"
        }
        catch {
            Write-Warning "Could not install Scoop automatically"
            return $false
        }
    }
    else {
        Write-Success "Scoop is already installed"
    }
    return $true
}

function Install-Chocolatey {
    if (-not (Test-CommandExists "choco")) {
        Write-Status "Installing Chocolatey package manager..."
        try {
            Set-ExecutionPolicy Bypass -Scope Process -Force
            [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
            Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
            Write-Success "Chocolatey installed successfully"
        }
        catch {
            Write-Warning "Could not install Chocolatey automatically"
            return $false
        }
    }
    else {
        Write-Success "Chocolatey is already installed"
    }
    return $true
}

function Install-WindowsTerminal {
    if (-not (Get-AppxPackage -Name "Microsoft.WindowsTerminal" -ErrorAction SilentlyContinue)) {
        Write-Status "Installing Windows Terminal..."
        
        if (Test-CommandExists "winget") {
            try {
                winget install --id=Microsoft.WindowsTerminal -e --accept-source-agreements --accept-package-agreements
                Write-Success "Windows Terminal installed via WinGet"
                return
            }
            catch {
                Write-Warning "WinGet installation failed, trying alternative method"
            }
        }
        
        # Fallback to Microsoft Store
        Write-Status "Please install Windows Terminal from Microsoft Store:"
        Write-Status "https://aka.ms/terminal"
        Start-Process "ms-windows-store://pdp/?productid=9n0dx20hk701"
    }
    else {
        Write-Success "Windows Terminal is already installed"
    }
}

function Install-Python {
    if (-not (Test-CommandExists "python")) {
        Write-Status "Installing Python..."
        
        $installed = $false
        
        # Try WinGet first
        if (Test-CommandExists "winget") {
            try {
                winget install --id=Python.Python.3.12 -e --accept-source-agreements --accept-package-agreements
                $installed = $true
                Write-Success "Python installed via WinGet"
            }
            catch {
                Write-Warning "WinGet installation failed"
            }
        }
        
        # Try Chocolatey
        if (-not $installed -and (Test-CommandExists "choco")) {
            try {
                choco install python -y
                $installed = $true
                Write-Success "Python installed via Chocolatey"
            }
            catch {
                Write-Warning "Chocolatey installation failed"
            }
        }
        
        # Try Scoop
        if (-not $installed -and (Test-CommandExists "scoop")) {
            try {
                scoop install python
                $installed = $true
                Write-Success "Python installed via Scoop"
            }
            catch {
                Write-Warning "Scoop installation failed"
            }
        }
        
        # Manual fallback
        if (-not $installed) {
            Write-Status "Please download and install Python manually:"
            Write-Status "https://www.python.org/downloads/windows/"
            Start-Process "https://www.python.org/downloads/windows/"
            Read-Host "Press Enter after installing Python"
        }
        
        # Refresh PATH
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    }
    else {
        Write-Success "Python is already installed ($(python --version))"
    }
}

function Install-UV {
    if (($Upgrade.IsPresent -and (Test-CommandExists "uv")) -or (-not (Test-CommandExists "uv"))) {
        if ($Upgrade.IsPresent -and (Test-CommandExists "uv")) {
            Write-Status "Checking for uv upgrade..."
        } else {
            Write-Status "Installing uv (Python package manager)..."
        }
        
        $installed = $false
        
        # Try WinGet first
        if (Test-CommandExists "winget") {
            try {
                winget install --id=astral-sh.uv -e --accept-source-agreements --accept-package-agreements
                $installed = $true
                Write-Success "uv installed/upgraded via WinGet"
            }
            catch {
                Write-Warning "WinGet command failed"
            }
        }
        
        # Try Scoop
        if (-not $installed -and (Test-CommandExists "scoop")) {
            try {
                if ($Upgrade.IsPresent) {
                    scoop update main/uv
                } else {
                    scoop install main/uv
                }
                $installed = $true
                Write-Success "uv installed/upgraded via Scoop"
            }
            catch {
                Write-Warning "Scoop command failed"
            }
        }
        
        # Try standalone installer
        if (-not $installed) {
            try {
                Write-Status "Installing/upgrading uv via standalone installer..."
                $progressPreference = 'silentlyContinue'
                Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression
                $installed = $true
                Write-Success "uv installed/upgraded via standalone installer"
            }
            catch {
                Write-Error "Failed to install uv via standalone installer"
            }
        }
        
        # Refresh PATH
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    }
    else {
        Write-Success "uv is already installed ($(uv --version))"
    }
}

function Install-Crush {
    if (($Upgrade.IsPresent -and (Test-CommandExists "crush")) -or (-not (Test-CommandExists "crush"))) {
        if ($Upgrade.IsPresent -and (Test-CommandExists "crush")) {
            Write-Status "Checking for crush upgrade..."
        } else {
            Write-Status "Installing crush (AI coding agent)..."
        }
        
        $installed = $false
        
        # Try WinGet first
        if (Test-CommandExists "winget") {
            try {
                winget install --id=charmbracelet.crush -e --accept-source-agreements --accept-package-agreements
                $installed = $true
                Write-Success "crush installed/upgraded via WinGet"
            }
            catch {
                Write-Warning "WinGet command failed"
            }
        }
        
        # Try Scoop
        if (-not $installed -and (Test-CommandExists "scoop")) {
            try {
                # Add charm bucket if not already added
                if ((scoop bucket list) -notcontains "charm") {
                    scoop bucket add charm https://github.com/charmbracelet/scoop-bucket.git
                }
                if ($Upgrade.IsPresent) {
                    scoop update crush
                } else {
                    scoop install crush
                }
                $installed = $true
                Write-Success "crush installed/upgraded via Scoop"
            }
            catch {
                Write-Warning "Scoop command failed"
            }
        }
        
        # Try npm
        if (-not $installed -and (Test-CommandExists "npm")) {
            try {
                npm install -g @charmland/crush
                $installed = $true
                Write-Success "crush installed/upgraded via npm"
            }
            catch {
                Write-Warning "npm installation failed"
            }
        }
        
        # Manual fallback
        if (-not $installed -and -not $Upgrade.IsPresent) {
            Write-Status "Please download crush manually from:"
            Write-Status "https://github.com/charmbracelet/crush/releases"
            Start-Process "https://github.com/charmbracelet/crush/releases"
            Read-Host "Press Enter after installing crush"
        }
        
        # Refresh PATH
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    }
    else {
        Write-Success "crush is already installed"
    }
}

function Main {
    if ($Upgrade.IsPresent) {
        Write-Host "==================================================" -ForegroundColor Blue
        Write-Host "    Prerequisites Upgrader for Windows" -ForegroundColor Blue
        Write-Host "==================================================" -ForegroundColor Blue
        Write-Host ""
        Write-Status "Starting upgrade of prerequisites..."
    } else {
        Write-Host "==================================================" -ForegroundColor Blue
        Write-Host "    Prerequisites Installer for Windows" -ForegroundColor Blue
        Write-Host "==================================================" -ForegroundColor Blue
        Write-Host ""
        Write-Status "Starting installation of prerequisites..."
    }
    Write-Host ""
    
    # Check if running as administrator
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
    if (-not $isAdmin) {
        Write-Warning "Not running as Administrator. Some installations may fail."
        Write-Status "Consider running PowerShell as Administrator for best results."
        Write-Host ""
    }
    
    # Install package managers
    $wingetAvailable = Install-WinGet
    Write-Host ""
    
    if (-not $wingetAvailable) {
        Install-Scoop
        Write-Host ""
        Install-Chocolatey
        Write-Host ""
    }
    
    if ($Upgrade.IsPresent) {
        if (Test-CommandExists "winget") {
            Write-Status "Updating winget sources..."
            winget source update
        }
        if (Test-CommandExists "scoop") {
            Write-Status "Updating scoop..."
            scoop update
        }
        if (Test-CommandExists "choco") {
            Write-Status "Updating choco..."
            choco upgrade chocolatey -y
        }
    }

    # Install Windows Terminal
    Install-WindowsTerminal
    Write-Host ""
    
    # Install core dependencies
    Install-Python
    Write-Host ""
    
    Install-UV
    Write-Host ""
    
    Install-Crush
    Write-Host ""
    
    if ($Upgrade.IsPresent) {
        Write-Success "All prerequisites have been checked for upgrades!"
    } else {
        Write-Success "All prerequisites have been installed successfully!"
    }

    Write-Host ""
    Write-Status "You may need to restart your terminal or PowerShell session."
    Write-Host ""
    Write-Status "To verify installations, run:"
    Write-Status "python --version"
    Write-Status "uv --version"
    Write-Status "crush --version"
    Write-Host ""
    Write-Status "Installation complete!"
    if ([Environment]::UserInteractive) {
        Write-Status "Press any key to exit..."
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    }
}

# Run main function with global error handling
try {
    Main
}
catch {
    Write-Error "An unexpected error occurred during the installation."
    Write-Error "Details: $($_.Exception.Message)"
    Write-Host ""
    Write-Status "The script will now exit."
    if ([Environment]::UserInteractive) {
        Write-Status "Press any key to continue..."
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    }
    exit 1
}
