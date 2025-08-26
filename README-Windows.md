# Victoria for Windows

This is the Windows PowerShell version of the Victoria script, providing a first-class experience for Windows users to access AdTech data analytics through the Crush CLI tool.

## Windows-Specific Files

- **`victoria.ps1`** - Comprehensive PowerShell script with dependency installation, environment setup, and main Victoria functionality
- **`victoria.bat`** - Batch file wrapper for easy double-click execution
- **`README-Windows.md`** - This file (Windows-specific documentation)

## Requirements

### Essential Dependencies
- **Windows Terminal** - [Microsoft Store](https://aka.ms/terminal) or [GitHub](https://github.com/microsoft/terminal)
- **Git for Windows** - [Download here](https://git-scm.com/download/win)
- **crush** - [Installation guide](https://github.com/charmbracelet/crush)
- **uv** - [Installation guide](https://docs.astral.sh/uv/getting-started/installation/)

### API Keys
- **`OPENROUTER_API_KEY`** - Required environment variable for Crush
  - GEMINI and OPENAI are also supported
  - Email [brad@elcanotek.com](mailto:brad@elcanotek.com) for a company key
 
```powershell
# Permanent (all sessions)
[Environment]::SetEnvironmentVariable("OPENROUTER_API_KEY", "your_api_key_here", "User")
```

#### Set Snowflake Variables (Optional - for Full Ocean Expedition)
```powershell
# Permanent
[Environment]::SetEnvironmentVariable("SNOWFLAKE_ACCOUNT", "your_account", "User")
[Environment]::SetEnvironmentVariable("SNOWFLAKE_USER", "your_user", "User")
[Environment]::SetEnvironmentVariable("SNOWFLAKE_PASSWORD", "your_password", "User")
[Environment]::SetEnvironmentVariable("SNOWFLAKE_WAREHOUSE", "your_warehouse", "User")
[Environment]::SetEnvironmentVariable("SNOWFLAKE_ROLE", "your_role", "User")
```

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
