# Prerequisites Installer Scripts

This repository contains three installer scripts that automatically install the required dependencies for your project across different operating systems.

## Overview

The installer scripts will install the following dependencies:

### Required Dependencies
- **Git** - Version control system
- **Python 3** - Programming language and runtime
- **uv** - Fast Python package manager and project manager
- **crush** - AI coding agent for terminal

### Optional Dependencies
- **ghostty** - Modern, fast terminal emulator (recommended but optional)

## Platform-Specific Scripts

### 1. macOS Installer (`install_prerequisites_macos.sh`)

**Requirements:**
- macOS 10.15 or later
- Internet connection
- Terminal access

**Installation Methods Used:**
- **Homebrew** (primary method) - Automatically installs if not present
- **Xcode Command Line Tools** (fallback for Git and Python)
- **Standalone installers** (fallback for uv)
- **Go installation** (fallback for crush)

**Usage:**
```bash
# Download and run the script
curl -O https://raw.githubusercontent.com/your-repo/install_prerequisites_macos.sh
chmod +x install_prerequisites_macos.sh
./install_prerequisites_macos.sh
```

**What it does:**
1. Installs Homebrew if not present
2. Installs Git via Homebrew or Xcode Command Line Tools
3. Installs Python via Homebrew or Xcode Command Line Tools
4. Installs uv via Homebrew or standalone installer
5. Installs crush via Homebrew or Go
6. Optionally installs ghostty via Homebrew or manual download

### 2. Linux Installer (`install_prerequisites_linux.sh`)

**Requirements:**
- Linux distribution (Ubuntu, Debian, Fedora, RHEL, CentOS, Arch, openSUSE, Alpine)
- Internet connection
- sudo privileges
- Terminal access

**Supported Distributions:**
- **Ubuntu/Debian** - Uses apt package manager
- **Fedora/RHEL/CentOS** - Uses dnf/yum package manager
- **Arch Linux/Manjaro** - Uses pacman and AUR
- **openSUSE/SLES** - Uses zypper package manager
- **Alpine Linux** - Uses apk package manager

**Usage:**
```bash
# Download and run the script
curl -O https://raw.githubusercontent.com/your-repo/install_prerequisites_linux.sh
chmod +x install_prerequisites_linux.sh
./install_prerequisites_linux.sh
```

**What it does:**
1. Detects your Linux distribution automatically
2. Updates package manager repositories
3. Installs Git via distribution package manager
4. Installs Python via distribution package manager
5. Installs uv via distribution packages or standalone installer
6. Installs crush via distribution repositories or Go
7. Optionally installs ghostty via distribution packages or community packages

### 3. Windows Installer (`install_prerequisites_windows.ps1`)

**Requirements:**
- Windows 10 or later
- PowerShell 5.1 or later
- Internet connection
- Administrator privileges (recommended)

**Installation Methods Used:**
- **WinGet** (Windows Package Manager) - Primary method
- **Scoop** - Alternative package manager
- **Chocolatey** - Alternative package manager
- **npm** - For crush installation
- **Manual downloads** - Fallback method

**Usage:**
```powershell
# Download and run the script in PowerShell (Run as Administrator recommended)
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/your-repo/install_prerequisites_windows.ps1" -OutFile "install_prerequisites_windows.ps1"
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\install_prerequisites_windows.ps1
```

**What it does:**
1. Installs WinGet if not present
2. Installs Windows Terminal
3. Installs Git via WinGet, Chocolatey, or Scoop
4. Installs Python via WinGet, Chocolatey, or Scoop
5. Installs uv via WinGet, Scoop, or standalone installer
6. Installs crush via WinGet, Scoop, or npm
7. Optionally installs ghostty via manual download

## Features

### Smart Detection
- All scripts detect if dependencies are already installed
- Skip installation if a dependency is already present
- Provide version information for installed dependencies

### Multiple Installation Methods
- Each script tries multiple installation methods
- Falls back to alternative methods if primary method fails
- Provides manual installation instructions as last resort

### User-Friendly Output
- Color-coded status messages
- Clear success/warning/error indicators
- Progress information throughout installation

### Safety Features
- Linux script prevents running as root
- Windows script handles execution policy
- All scripts use error handling to prevent partial installations

## Troubleshooting

### Common Issues

**macOS:**
- If Homebrew installation fails, install Xcode Command Line Tools manually: `xcode-select --install`
- If you get permission errors, ensure your user account has admin privileges

**Linux:**
- If package manager updates fail, check your internet connection
- For distribution-specific issues, ensure your system is up to date
- Some distributions may require enabling additional repositories

**Windows:**
- If PowerShell execution is blocked, run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- If WinGet is not available, the script will install alternative package managers
- Run PowerShell as Administrator for best results

### Manual Installation

If the automated scripts fail, you can install dependencies manually:

1. **Git**: Visit [git-scm.com](https://git-scm.com/downloads)
2. **Python**: Visit [python.org](https://www.python.org/downloads/)
3. **uv**: Visit [docs.astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/)
4. **crush**: Visit [github.com/charmbracelet/crush](https://github.com/charmbracelet/crush)
5. **ghostty**: Visit [ghostty.org](https://ghostty.org/docs/install/binary)

## Verification

After running any installer script, verify the installations by running:

```bash
# Check versions of installed tools
git --version
python3 --version  # or python --version on Windows
uv --version
crush --version
ghostty --version  # if installed
```

## Support

If you encounter issues with these installer scripts:

1. Check the troubleshooting section above
2. Ensure your system meets the requirements
3. Try running the script again (it's safe to re-run)
4. For persistent issues, install dependencies manually using the links provided

## License

These installer scripts are provided as-is for convenience. Please refer to the individual software licenses for each dependency being installed.

