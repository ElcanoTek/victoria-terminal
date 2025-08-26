# Victoria for Windows

This is the Windows PowerShell version of the Victoria script, providing a first-class experience for Windows users to access AdTech data analytics through the Crush CLI tool.

## Windows-Specific Files

- **`victoria.ps1`** - Comprehensive PowerShell script with dependency installation, environment setup, and main Victoria functionality
- **`victoria.bat`** - Batch file wrapper for easy double-click execution
- **`README-Windows.md`** - This file (Windows-specific documentation)

## Requirements

### Essential Dependencies
- **PowerShell 5.1+** (included with Windows 10/11) or **PowerShell Core 7+**
- **Git for Windows** - [Download here](https://git-scm.com/download/win)
- **crush** - [Installation guide](https://github.com/charmbracelet/crush)
- **uv** - [Installation guide](https://docs.astral.sh/uv/getting-started/installation/)

### Optional but Recommended
- **Windows Terminal** - [Microsoft Store](https://aka.ms/terminal) or [GitHub](https://github.com/microsoft/terminal)
- **Ghostty** - [ghostty.org](https://ghostty.org/) (when available for Windows)

### API Keys
- **`OPENROUTER_API_KEY`** - Required environment variable for Crush
  - GEMINI and OPENAI are also supported
  - Email [brad@elcanotek.com](mailto:brad@elcanotek.com) for a company key

## Installation

### 1. Install Dependencies

#### Install Git for Windows
Download and install from [git-scm.com](https://git-scm.com/download/win)

#### Install uv (Python package manager)
```powershell
# Using PowerShell (recommended)
irm https://astral.sh/uv/install.ps1 | iex

# Or using pip
pip install uv
```

#### Install crush
```powershell
# Using Go (if you have Go installed)
go install github.com/charmbracelet/crush@latest

# Or download binary from GitHub releases
# https://github.com/charmbracelet/crush/releases
```

### 2. Set Environment Variables

#### Set API Key (Required)
```powershell
# Temporary (current session only)
$env:OPENROUTER_API_KEY = "your_api_key_here"

# Permanent (all sessions)
[Environment]::SetEnvironmentVariable("OPENROUTER_API_KEY", "your_api_key_here", "User")
```

#### Set Snowflake Variables (Optional - for Full Ocean Expedition)
```powershell
# Temporary
$env:SNOWFLAKE_ACCOUNT = "your_account_identifier"
$env:SNOWFLAKE_USER = "your_username@domain.com"
$env:SNOWFLAKE_PASSWORD = "your_password"
$env:SNOWFLAKE_WAREHOUSE = "your_warehouse"
$env:SNOWFLAKE_ROLE = "your_read_only_role"

# Permanent
[Environment]::SetEnvironmentVariable("SNOWFLAKE_ACCOUNT", "your_account", "User")
[Environment]::SetEnvironmentVariable("SNOWFLAKE_USER", "your_user", "User")
[Environment]::SetEnvironmentVariable("SNOWFLAKE_PASSWORD", "your_password", "User")
[Environment]::SetEnvironmentVariable("SNOWFLAKE_WAREHOUSE", "your_warehouse", "User")
[Environment]::SetEnvironmentVariable("SNOWFLAKE_ROLE", "your_role", "User")
```

## Usage

### Method 1: Double-Click (Easiest)
1. Double-click `victoria.bat` in File Explorer
2. Follow the interactive prompts

### Method 2: PowerShell Direct
1. Open PowerShell or Windows Terminal
2. Navigate to the project folder:
   ```powershell
   cd path\to\victoria-crush
   ```
3. Run the script:
   ```powershell
   # Main Victoria interface
   .\victoria.ps1
   
   # Install dependencies only
   .\victoria.ps1 -InstallDeps
   
   # Setup environment variables only
   .\victoria.ps1 -Setup
   
   # Skip dependency check (if you know they're installed)
   .\victoria.ps1 -SkipDependencyCheck
   ```

### Method 3: Command Prompt
1. Open Command Prompt
2. Navigate to the project folder:
   ```cmd
   cd path\to\victoria-crush
   ```
3. Run via batch file:
   ```cmd
   victoria.bat
   ```

## Features

### 🌊 Full Ocean Expedition
- **Snowflake Integration**: Connect to enterprise Snowflake databases
- **Local Data Access**: Query CSV/Excel files via MotherDuck
- **Complete Analytics**: Full programmatic advertising data analysis
- **Requirements**: All Snowflake environment variables must be set

### 🏝️ Coastal Navigation
- **Local Data Only**: Query CSV/Excel files via MotherDuck
- **Fast Startup**: No external database dependencies
- **Perfect for**: Local data analysis and testing
- **Requirements**: Only basic dependencies needed

## Data Files

Add your CSV or Excel files to the `.\data` folder in this repository and they will be automatically available for analysis through Victoria.

## Troubleshooting

### PowerShell Execution Policy
If you get an execution policy error:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Missing Dependencies
The consolidated script now automatically checks for missing dependencies and offers to install them. Simply run `.\victoria.ps1` and follow the prompts, or use `.\victoria.ps1 -InstallDeps` to focus on dependency installation.

### SSH Key Configuration
For VICTORIA.md downloads, ensure your SSH key is configured:
```powershell
ssh -T git@github.com
```

### Environment Variables Not Persisting
Use the permanent method shown above, or add them to your PowerShell profile:
```powershell
# Edit your profile
notepad $PROFILE

# Add environment variables to the profile file
$env:OPENROUTER_API_KEY = "your_key_here"
```

## Windows-Specific Enhancements

- **All-in-One Script**: Dependency installation, environment setup, and Victoria launcher in one script
- **Native PowerShell Colors**: Full color support in Windows Terminal and PowerShell
- **Windows Path Handling**: Proper handling of Windows file paths and directories
- **Batch File Wrapper**: Easy execution without opening PowerShell manually
- **Error Handling**: Windows-specific error messages and troubleshooting
- **Automatic Dependency Management**: Checks and installs missing dependencies
- **Interactive Environment Setup**: Guided configuration of API keys and Snowflake credentials

## Model Recommendations

Same as the main README - see the model comparison table for pricing and performance guidance.

### Quick Picks for Windows Users
- **🎯 Start Here**: DeepSeek V3 ($0.27/$1.10) - Best overall value
- **💰 Budget**: GLM 4.5 ($0.20/$0.20) - Cheapest balanced option  
- **🆓 Free**: gpt-oss-20b (free) ($0/$0) - Completely free
- **🏆 Best**: GPT-5 ($1.25/$10) - Top performance
- **⚡ Fast**: GPT-5 Nano ($0.05/$0.40) - Ultra-fast responses

## Support

For Windows-specific issues:
1. Check this README first
2. Verify all dependencies are installed correctly
3. Ensure environment variables are set properly
4. Try running in Windows Terminal for better compatibility

For general Victoria questions, see the main README.md file.