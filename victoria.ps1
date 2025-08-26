#Requires -Version 5.1

<#
.SYNOPSIS
    Victoria - AdTech Data Navigation Tool (Windows PowerShell Version)

.DESCRIPTION
    A comprehensive PowerShell script that handles dependency installation, environment
    setup, and provides an interactive interface for connecting to Snowflake databases
    and local data files for programmatic advertising analytics using the Crush CLI tool.

.PARAMETER Setup
    Run environment variable setup mode

.PARAMETER InstallDeps
    Run dependency installation mode

.PARAMETER SkipDependencyCheck
    Skip the dependency check and go straight to Victoria

.NOTES
    Author: ElcanoTek
    Version: 2.0
    Requires: PowerShell 5.1+
#>

param(
    [switch]$Setup,
    [switch]$InstallDeps,
    [switch]$SkipDependencyCheck
)

# Color definitions for enhanced visual appeal
$Colors = @{
    Red     = [System.ConsoleColor]::Red
    Green   = [System.ConsoleColor]::Green
    Yellow  = [System.ConsoleColor]::Yellow
    Blue    = [System.ConsoleColor]::Blue
    Magenta = [System.ConsoleColor]::Magenta
    Cyan    = [System.ConsoleColor]::Cyan
    White   = [System.ConsoleColor]::White
    Gray    = [System.ConsoleColor]::Gray
}

# VICTORIA.md download configuration
$VICTORIA_REPO = "git@github.com:ElcanoTek/victoria-main.git"
$VICTORIA_FILE = "VICTORIA.md"
$VICTORIA_BRANCH = "main"

# Function to write colored text
function Write-ColorText {
    param(
        [string]$Text,
        [System.ConsoleColor]$Color = [System.ConsoleColor]::White,
        [switch]$NoNewline
    )
    
    $originalColor = $Host.UI.RawUI.ForegroundColor
    $Host.UI.RawUI.ForegroundColor = $Color
    
    if ($NoNewline) {
        Write-Host $Text -NoNewline
    } else {
        Write-Host $Text
    }
    
    $Host.UI.RawUI.ForegroundColor = $originalColor
}

# Function to check if a command exists
function Test-Command {
    param([string]$Command)
    
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

# Function to check if running as administrator
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Function to securely read password
function Read-SecureInput {
    param([string]$Prompt)
    
    Write-ColorText $Prompt -Color $Colors.White -NoNewline
    $secureString = Read-Host -AsSecureString
    $ptr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureString)
    $plainText = [System.Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
    [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
    return $plainText
}

# Function to set environment variable
function Set-EnvironmentVariable {
    param(
        [string]$Name,
        [string]$Value,
        [switch]$Permanent
    )
    
    if ($Permanent) {
        [Environment]::SetEnvironmentVariable($Name, $Value, "User")
        Write-ColorText "✓ Set $Name permanently (will persist after restart)" -Color $Colors.Green
    } else {
        Set-Item "env:$Name" $Value
        Write-ColorText "✓ Set $Name for current session only" -Color $Colors.Yellow
    }
}

# Function to install dependencies
function Install-Dependencies {
    Clear-Host
    
    Write-ColorText @"
🔧 VICTORIA DEPENDENCY INSTALLER 🔧

This will help you install the required dependencies
for Victoria on Windows.

"@ -Color $Colors.Cyan

    # Check current dependencies
    Write-ColorText "📋 Checking current dependencies..." -Color $Colors.Blue
    Write-Host ""

    $dependencies = @{
        "git" = @{
            "name" = "Git for Windows"
            "check" = "git"
            "install" = "Download from https://git-scm.com/download/win"
            "required" = $true
        }
        "uv" = @{
            "name" = "uv (Python package manager)"
            "check" = "uv"
            "install" = "PowerShell: irm https://astral.sh/uv/install.ps1 | iex"
            "required" = $true
        }
        "crush" = @{
            "name" = "Crush CLI"
            "check" = "crush"
            "install" = "Download from https://github.com/charmbracelet/crush/releases"
            "required" = $true
        }
        "python" = @{
            "name" = "Python"
            "check" = "python"
            "install" = "Download from https://python.org or use Microsoft Store"
            "required" = $false
        }
    }

    $missing = @()
    $available = @()

    foreach ($dep in $dependencies.Keys) {
        $info = $dependencies[$dep]
        if (Test-Command $info.check) {
            Write-ColorText "✓ $($info.name) is available" -Color $Colors.Green
            $available += $dep
        } else {
            $status = if ($info.required) { "MISSING (required)" } else { "missing (optional)" }
            $color = if ($info.required) { $Colors.Red } else { $Colors.Yellow }
            Write-ColorText "✗ $($info.name) is $status" -Color $color
            $missing += $dep
        }
    }

    Write-Host ""

    if ($missing.Count -eq 0) {
        Write-ColorText "🎉 All dependencies are already installed!" -Color $Colors.Green
        Write-ColorText "You can now run Victoria using .\victoria.ps1" -Color $Colors.Cyan
        Write-Host ""
        Write-ColorText "Press any key to continue to Victoria..." -Color $Colors.Gray
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        return $true
    }

    Write-ColorText "🔧 INSTALLATION GUIDE" -Color $Colors.Yellow
    Write-Host ""

    # Install uv if missing
    if ("uv" -in $missing) {
        Write-ColorText "Installing uv (Python package manager)..." -Color $Colors.Cyan
        Write-ColorText "This will download and install uv automatically." -Color $Colors.Gray
        Write-Host ""
        
        Write-ColorText "Install uv now? [Y/n]: " -Color $Colors.White -NoNewline
        $installUv = Read-Host
        
        if ($installUv -notmatch '^[Nn]([Oo])?$') {
            try {
                Write-ColorText "Downloading and installing uv..." -Color $Colors.Blue
                Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression
                
                # Refresh PATH
                $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
                
                if (Test-Command "uv") {
                    Write-ColorText "✓ uv installed successfully!" -Color $Colors.Green
                    $missing = $missing | Where-Object { $_ -ne "uv" }
                } else {
                    Write-ColorText "⚠️  uv installation completed, but command not found." -Color $Colors.Yellow
                    Write-ColorText "You may need to restart your terminal or add uv to your PATH." -Color $Colors.Gray
                }
            }
            catch {
                Write-ColorText "❌ Failed to install uv: $($_.Exception.Message)" -Color $Colors.Red
            }
        }
        Write-Host ""
    }

    # Provide manual installation instructions for remaining dependencies
    if ($missing.Count -gt 0) {
        Write-ColorText "📋 MANUAL INSTALLATION REQUIRED" -Color $Colors.Yellow
        Write-ColorText "Please install the following dependencies manually:" -Color $Colors.Gray
        Write-Host ""
        
        foreach ($dep in $missing) {
            $info = $dependencies[$dep]
            Write-ColorText "🔸 $($info.name)" -Color $Colors.Cyan
            Write-ColorText "   Installation: $($info.install)" -Color $Colors.White
            Write-Host ""
        }
        
        Write-ColorText "After installing the dependencies:" -Color $Colors.Blue
        Write-ColorText "1. Restart your terminal/PowerShell" -Color $Colors.White
        Write-ColorText "2. Run .\victoria.ps1 -InstallDeps to verify installation" -Color $Colors.White
        Write-ColorText "3. Run .\victoria.ps1 -Setup to configure environment variables" -Color $Colors.White
        Write-ColorText "4. Run .\victoria.ps1 to start Victoria" -Color $Colors.White
        
        Write-Host ""
        Write-ColorText "Press any key to exit..." -Color $Colors.Gray
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        return $false
    }

    return $true
}

# Function to setup environment variables
function Setup-Environment {
    Clear-Host

    Write-ColorText @"
🔧 VICTORIA ENVIRONMENT SETUP 🔧

This will help you configure the environment variables
needed to run Victoria on Windows.

"@ -Color $Colors.Cyan

    # Check current environment
    Write-ColorText "📋 Checking current environment..." -Color $Colors.Blue
    Write-Host ""

    $requiredVars = @("OPENROUTER_API_KEY")
    $optionalVars = @("SNOWFLAKE_ACCOUNT", "SNOWFLAKE_USER", "SNOWFLAKE_PASSWORD", "SNOWFLAKE_WAREHOUSE", "SNOWFLAKE_ROLE")

    # Check required variables
    $missingRequired = @()
    foreach ($var in $requiredVars) {
        $value = [Environment]::GetEnvironmentVariable($var, "User")
        if (-not $value) {
            $value = [Environment]::GetEnvironmentVariable($var, "Process")
        }
        
        if ($value) {
            Write-ColorText "✓ $var is set" -Color $Colors.Green
        } else {
            Write-ColorText "✗ $var is missing" -Color $Colors.Red
            $missingRequired += $var
        }
    }

    # Check optional variables
    $missingOptional = @()
    foreach ($var in $optionalVars) {
        $value = [Environment]::GetEnvironmentVariable($var, "User")
        if (-not $value) {
            $value = [Environment]::GetEnvironmentVariable($var, "Process")
        }
        
        if ($value) {
            Write-ColorText "✓ $var is set" -Color $Colors.Green
        } else {
            Write-ColorText "○ $var is not set (optional for Snowflake)" -Color $Colors.Gray
            $missingOptional += $var
        }
    }

    Write-Host ""

    # Handle required variables
    if ($missingRequired.Count -gt 0) {
        Write-ColorText "🔑 REQUIRED API KEY SETUP" -Color $Colors.Yellow
        Write-Host ""
        
        foreach ($var in $missingRequired) {
            switch ($var) {
                "OPENROUTER_API_KEY" {
                    Write-ColorText "OpenRouter API Key is required for Victoria to work." -Color $Colors.Cyan
                    Write-ColorText "You can get a key from: https://openrouter.ai/" -Color $Colors.Gray
                    Write-ColorText "Or email brad@elcanotek.com for a company key." -Color $Colors.Gray
                    Write-Host ""
                    
                    $apiKey = Read-Host "Enter your OpenRouter API Key"
                    if ($apiKey) {
                        Write-ColorText "Make this permanent? [Y/n]: " -Color $Colors.White -NoNewline
                        $permanent = Read-Host
                        $isPermanent = $permanent -notmatch '^[Nn]([Oo])?$'
                        
                        Set-EnvironmentVariable -Name $var -Value $apiKey -Permanent:$isPermanent
                    }
                }
            }
            Write-Host ""
        }
    }

    # Handle optional Snowflake variables
    if ($missingOptional.Count -gt 0) {
        Write-ColorText "❄️  OPTIONAL SNOWFLAKE SETUP" -Color $Colors.Blue
        Write-ColorText "Snowflake integration enables the 'Full Ocean Expedition' mode." -Color $Colors.Gray
        Write-Host ""
        
        Write-ColorText "Would you like to configure Snowflake integration? [y/N]: " -Color $Colors.White -NoNewline
        $configureSnowflake = Read-Host
        
        if ($configureSnowflake -match '^[Yy]([Ee][Ss])?$') {
            Write-Host ""
            Write-ColorText "Please provide your Snowflake connection details:" -Color $Colors.Cyan
            Write-Host ""
            
            $snowflakeVars = @{
                "SNOWFLAKE_ACCOUNT" = "Account identifier (e.g., abc12345.us-east-1)"
                "SNOWFLAKE_USER" = "Username (e.g., user@company.com)"
                "SNOWFLAKE_PASSWORD" = "Password (will be hidden)"
                "SNOWFLAKE_WAREHOUSE" = "Warehouse name"
                "SNOWFLAKE_ROLE" = "Role name (should have read-only permissions)"
            }
            
            Write-ColorText "Make Snowflake settings permanent? [Y/n]: " -Color $Colors.White -NoNewline
            $permanentChoice = Read-Host
            $isPermanent = $permanentChoice -notmatch '^[Nn]([Oo])?$'
            Write-Host ""
            
            foreach ($var in $missingOptional) {
                if ($snowflakeVars.ContainsKey($var)) {
                    $description = $snowflakeVars[$var]
                    
                    if ($var -eq "SNOWFLAKE_PASSWORD") {
                        $value = Read-SecureInput "$description: "
                    } else {
                        $value = Read-Host "$description"
                    }
                    
                    if ($value) {
                        Set-EnvironmentVariable -Name $var -Value $value -Permanent:$isPermanent
                    }
                }
            }
        }
    }

    Write-Host ""
    Write-ColorText "🎉 SETUP COMPLETE!" -Color $Colors.Green
    Write-Host ""

    # Final status check
    Write-ColorText "📋 Final Environment Status:" -Color $Colors.Blue
    $allVars = $requiredVars + $optionalVars
    foreach ($var in $allVars) {
        $value = [Environment]::GetEnvironmentVariable($var, "User")
        if (-not $value) {
            $value = [Environment]::GetEnvironmentVariable($var, "Process")
        }
        
        if ($value) {
            $displayValue = if ($var -eq "SNOWFLAKE_PASSWORD") { "***hidden***" } else { $value.Substring(0, [Math]::Min(20, $value.Length)) + "..." }
            Write-ColorText "✓ $var = $displayValue" -Color $Colors.Green
        } else {
            $status = if ($var -in $requiredVars) { "MISSING (required)" } else { "not set (optional)" }
            $color = if ($var -in $requiredVars) { $Colors.Red } else { $Colors.Gray }
            Write-ColorText "○ $var = $status" -Color $color
        }
    }

    Write-Host ""
    Write-ColorText "You can now run Victoria using: .\victoria.ps1" -Color $Colors.Cyan
    Write-Host ""

    if ($isPermanent) {
        Write-ColorText "Note: You may need to restart your terminal/PowerShell for permanent" -Color $Colors.Yellow
        Write-ColorText "environment variables to take effect in new sessions." -Color $Colors.Yellow
    }

    Write-Host ""
    Write-ColorText "Press any key to continue to Victoria..." -Color $Colors.Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

# Function to download VICTORIA.md using SSH clone method
function Download-Victoria {
    Write-ColorText "📋 Downloading VICTORIA.md from ElcanoTek/victoria-main..." -Color $Colors.Cyan
    
    $tempDir = Join-Path $env:TEMP "victoria_clone_$(Get-Random)"
    $success = $false
    
    try {
        # Clone the repository temporarily
        $cloneResult = & git clone --depth 1 --branch $VICTORIA_BRANCH $VICTORIA_REPO $tempDir 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            $victoriaPath = Join-Path $tempDir $VICTORIA_FILE
            
            if (Test-Path $victoriaPath) {
                # Copy the file to current directory
                Copy-Item $victoriaPath "./$VICTORIA_FILE" -Force
                $success = $true
                
                # Show file info
                $fileInfo = Get-Item $VICTORIA_FILE
                Write-ColorText "✅ VICTORIA.md downloaded successfully!" -Color $Colors.Green
                Write-ColorText "   📄 Size: $($fileInfo.Length) bytes" -Color $Colors.Cyan
                Write-ColorText "   📍 Location: ./$VICTORIA_FILE" -Color $Colors.Cyan
                
                # Show first few lines as preview
                Write-ColorText "   📝 Preview (first 3 lines):" -Color $Colors.Magenta
                $preview = Get-Content $VICTORIA_FILE -TotalCount 3
                foreach ($line in $preview) {
                    Write-ColorText "      $line" -Color $Colors.Gray
                }
            } else {
                Write-ColorText "❌ VICTORIA.md not found in repository" -Color $Colors.Red
            }
        } else {
            Write-ColorText "❌ Failed to clone repository" -Color $Colors.Red
            Write-ColorText "💡 Make sure your SSH key is configured: ssh -T git@github.com" -Color $Colors.Yellow
        }
    }
    catch {
        Write-ColorText "❌ Error during clone operation: $($_.Exception.Message)" -Color $Colors.Red
    }
    finally {
        # Clean up temporary directory
        if (Test-Path $tempDir) {
            Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
    
    return $success
}

# Function to generate crush configuration (equivalent to generate_config.sh)
function Generate-CrushConfig {
    param(
        [bool]$IncludeSnowflake,
        [string]$OutputFile
    )
    
    try {
        # Read the template
        if (-not (Test-Path "crush.template.json")) {
            Write-ColorText "Error: crush.template.json not found!" -Color $Colors.Red
            return $false
        }
        
        $templateContent = Get-Content "crush.template.json" -Raw
        
        if ($IncludeSnowflake) {
            # Check if snowflake.mcp.json exists
            if (-not (Test-Path "snowflake.mcp.json")) {
                Write-ColorText "Error: snowflake.mcp.json not found!" -Color $Colors.Red
                return $false
            }
            
            # Read Snowflake MCP configuration from separate file
            $snowflakeConfig = Get-Content "snowflake.mcp.json" -Raw
            
            # Extract just the snowflake MCP part (remove outer braces and add proper indentation)
            $lines = $snowflakeConfig -split "`n"
            $snowflakeMcp = $lines[1..($lines.Length-2)] | ForEach-Object { "    $_" }
            $snowflakeMcp = ",`n" + ($snowflakeMcp -join "`n")
            
            # Replace the placeholder with Snowflake configuration
            $finalContent = $templateContent -replace '\{\{SNOWFLAKE_MCP\}\}', $snowflakeMcp
        } else {
            # Remove the placeholder (no Snowflake configuration)
            $finalContent = $templateContent -replace '\{\{SNOWFLAKE_MCP\}\}', ''
        }
        
        # Write the final configuration
        $finalContent | Out-File -FilePath $OutputFile -Encoding UTF8
        return $true
    }
    catch {
        Write-ColorText "Error generating configuration: $($_.Exception.Message)" -Color $Colors.Red
        return $false
    }
}

# Function to validate Snowflake environment variables
function Test-SnowflakeEnvironment {
    $requiredVars = @("SNOWFLAKE_ACCOUNT", "SNOWFLAKE_USER", "SNOWFLAKE_PASSWORD", "SNOWFLAKE_WAREHOUSE", "SNOWFLAKE_ROLE")
    $missingVars = @()
    
    foreach ($var in $requiredVars) {
        if (-not (Get-Item "env:$var" -ErrorAction SilentlyContinue)) {
            $missingVars += $var
        }
    }
    
    return $missingVars
}

# Function to show animated loading effect
function Show-LoadingAnimation {
    Write-ColorText "Initializing navigation systems..." -Color $Colors.Cyan
    for ($i = 1; $i -le 3; $i++) {
        Write-ColorText "▓" -Color $Colors.Blue -NoNewline
        Start-Sleep -Milliseconds 300
    }
    Write-ColorText " ✓ Ready" -Color $Colors.Green
}

# Function to run the main Victoria interface
function Start-Victoria {
    # Check for required dependencies unless skipped
    if (-not $SkipDependencyCheck) {
        $missingDeps = @()
        $requiredCommands = @("crush", "git", "uv")

        foreach ($cmd in $requiredCommands) {
            if (-not (Test-Command $cmd)) {
                $missingDeps += $cmd
            }
        }

        if ($missingDeps.Count -gt 0) {
            Write-ColorText "❌ Missing required dependencies:" -Color $Colors.Red
            foreach ($dep in $missingDeps) {
                Write-ColorText "  ✗ $dep" -Color $Colors.Red
            }
            Write-Host ""
            Write-ColorText "Would you like to install dependencies now? [Y/n]: " -Color $Colors.White -NoNewline
            $installChoice = Read-Host
            
            if ($installChoice -notmatch '^[Nn]([Oo])?$') {
                if (Install-Dependencies) {
                    # Continue to Victoria after successful installation
                } else {
                    exit 1
                }
            } else {
                Write-ColorText "Please install the missing dependencies and try again." -Color $Colors.Yellow
                Write-ColorText "Run: .\victoria.ps1 -InstallDeps" -Color $Colors.Cyan
                exit 1
            }
        }
    }

    Clear-Host

    # Display impressive ASCII Art
    Write-ColorText @"
██╗   ██╗██╗ ██████╗████████╗ ██████╗ ██████╗ ██╗ █████╗
██║   ██║██║██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗██║██╔══██╗
██║   ██║██║██║        ██║   ██║   ██║██████╔╝██║███████║
╚██╗ ██╔╝██║██║        ██║   ██║   ██║██╔══██╗██║██╔══██║
 ╚████╔╝ ██║╚██████╗   ██║   ╚██████╔╝██║  ██║██║██║  ██║
  ╚═══╝  ╚═╝ ╚═════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝
"@ -Color $Colors.Cyan

    Write-ColorText @"
⚓ NAVIGATION READY ⚓

🚢 "Not all who wander are lost" 🚢

───────────────────────────────────────
Charting the Digital Seas of AdTech
───────────────────────────────────────
"@ -Color $Colors.White

    # Check for VICTORIA.md update at the beginning
    Write-ColorText "`n📋 VICTORIA.md Update Check" -Color $Colors.Yellow
    Write-Host ""

    if (Test-Path $VICTORIA_FILE) {
        Write-ColorText "VICTORIA.md already exists in current directory" -Color $Colors.Cyan
        Write-ColorText "Would you like to update it with the latest version? [y/N]: " -Color $Colors.White -NoNewline
        $updateChoice = Read-Host
        
        if ($updateChoice -match '^[Yy]([Ee][Ss])?$') {
            Download-Victoria | Out-Null
        } else {
            Write-ColorText "Using existing VICTORIA.md" -Color $Colors.Green
        }
    } else {
        Write-ColorText "VICTORIA.md not found in current directory" -Color $Colors.Cyan
        Write-ColorText "Would you like to download it? [Y/n]: " -Color $Colors.White -NoNewline
        $downloadChoice = Read-Host
        
        if ($downloadChoice -notmatch '^[Nn]([Oo])?$') {
            Download-Victoria | Out-Null
        } else {
            Write-ColorText "Skipping VICTORIA.md download" -Color $Colors.Yellow
        }
    }

    Write-Host ""
    Write-ColorText @"
⭐ ⭐ ⭐
🧭 COURSE SELECTION 🧭
⭐ ⭐ ⭐
"@ -Color $Colors.Yellow

    Write-Host ""

    # Animated loading effect
    Show-LoadingAnimation

    Write-Host ""
    Write-ColorText "Choose your data exploration voyage:" -Color $Colors.White
    Write-Host ""
    Write-ColorText "[1] " -Color $Colors.Green -NoNewline
    Write-ColorText "🌊 Full Ocean Expedition" -Color $Colors.Cyan -NoNewline
    Write-ColorText " - Connect to Snowflake + Local Data"
    Write-ColorText "    ├─ Access enterprise Snowflake databases" -Color $Colors.Magenta
    Write-ColorText "    ├─ Query local CSV/Excel files via MotherDuck" -Color $Colors.Magenta
    Write-ColorText "    └─ Complete programmatic advertising analytics" -Color $Colors.Magenta
    Write-Host ""
    Write-ColorText "[2] " -Color $Colors.Yellow -NoNewline
    Write-ColorText "🏝️  Coastal Navigation" -Color $Colors.Cyan -NoNewline
    Write-ColorText " - Local Data Only"
    Write-ColorText "    ├─ Query local CSV/Excel files via MotherDuck" -Color $Colors.Magenta
    Write-ColorText "    ├─ Fast startup, no external dependencies" -Color $Colors.Magenta
    Write-ColorText "    └─ Perfect for local data analysis" -Color $Colors.Magenta
    Write-Host ""

    # Interactive prompt with validation
    while ($true) {
        Write-ColorText "⚓ Select your course [1-2]: " -Color $Colors.White -NoNewline
        $choice = Read-Host

        switch ($choice) {
            "1" {
                Write-Host ""
                Write-ColorText "🌊 FULL OCEAN EXPEDITION SELECTED 🌊" -Color $Colors.Green
                Write-ColorText "Preparing to set sail with Snowflake integration..." -Color $Colors.Cyan

                # Check for Snowflake environment variables
                $missingVars = Test-SnowflakeEnvironment

                if ($missingVars.Count -gt 0) {
                    Write-Host ""
                    Write-ColorText "⚠️  NAVIGATION WARNING ⚠️" -Color $Colors.Red
                    Write-ColorText "Missing Snowflake environment variables:" -Color $Colors.Yellow
                    foreach ($var in $missingVars) {
                        Write-ColorText "  ✗ $var" -Color $Colors.Red
                    }
                    Write-Host ""
                    Write-ColorText "Would you like to set up Snowflake environment variables now? [Y/n]: " -Color $Colors.White -NoNewline
                    $setupChoice = Read-Host
                    
                    if ($setupChoice -notmatch '^[Nn]([Oo])?$') {
                        Setup-Environment
                        # Re-check after setup
                        $missingVars = Test-SnowflakeEnvironment
                        if ($missingVars.Count -gt 0) {
                            Write-ColorText "Still missing required variables. Please run .\victoria.ps1 -Setup" -Color $Colors.Red
                            exit 1
                        }
                    } else {
                        Write-ColorText "Please set these variables before continuing:" -Color $Colors.Cyan
                        Write-ColorText "`$env:SNOWFLAKE_ACCOUNT = `"your_account`"" -Color $Colors.White
                        Write-ColorText "`$env:SNOWFLAKE_USER = `"your_user`"" -Color $Colors.White
                        Write-ColorText "`$env:SNOWFLAKE_PASSWORD = `"your_password`"" -Color $Colors.White
                        Write-ColorText "`$env:SNOWFLAKE_WAREHOUSE = `"your_warehouse`"" -Color $Colors.White
                        Write-ColorText "`$env:SNOWFLAKE_ROLE = `"your_role`"" -Color $Colors.White
                        Write-Host ""
                        Write-ColorText "Or run: .\victoria.ps1 -Setup" -Color $Colors.Cyan
                        exit 1
                    }
                }

                Write-ColorText "✓ Snowflake credentials detected" -Color $Colors.Green
                Write-ColorText "🚢 Generating configuration with Snowflake integration..." -Color $Colors.Cyan
                
                # Generate configuration with Snowflake
                if (Generate-CrushConfig -IncludeSnowflake $true -OutputFile "crush.json") {
                    Write-ColorText "🚢 Launching Victoria with full data access..." -Color $Colors.Cyan
                    Write-Host ""

                    # Launch crush with generated configuration
                    if (Test-Path "crush.json") {
                        & crush
                    } else {
                        Write-ColorText "Error: Failed to generate configuration!" -Color $Colors.Red
                        exit 1
                    }
                } else {
                    Write-ColorText "Error: Failed to generate configuration!" -Color $Colors.Red
                    exit 1
                }
                return
            }
            "2" {
                Write-Host ""
                Write-ColorText "🏝️  COASTAL NAVIGATION SELECTED 🏝️" -Color $Colors.Yellow
                Write-ColorText "Preparing for local data exploration..." -Color $Colors.Cyan
                Write-ColorText "✓ Local data access ready" -Color $Colors.Green
                Write-ColorText "🚢 Generating configuration for local data access..." -Color $Colors.Cyan
                
                # Generate configuration without Snowflake
                if (Generate-CrushConfig -IncludeSnowflake $false -OutputFile "crush.json") {
                    Write-ColorText "🚢 Launching Victoria with local data access..." -Color $Colors.Cyan
                    Write-Host ""

                    # Launch crush with generated configuration
                    if (Test-Path "crush.json") {
                        & crush
                    } else {
                        Write-ColorText "Error: Failed to generate configuration!" -Color $Colors.Red
                        exit 1
                    }
                } else {
                    Write-ColorText "Error: Failed to generate configuration!" -Color $Colors.Red
                    exit 1
                }
                return
            }
            default {
                Write-ColorText "Invalid selection. Please choose 1 or 2." -Color $Colors.Red
            }
        }
    }
}

# Main script execution
if ($InstallDeps) {
    Install-Dependencies
} elseif ($Setup) {
    Setup-Environment
} else {
    Start-Victoria
}