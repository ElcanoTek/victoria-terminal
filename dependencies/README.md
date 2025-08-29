# Setup Scripts

Scripts in this directory help install prerequisites and configure environment variables for Victoria.
They are executed automatically the first time you run `victoria.py`, but they can also be run manually.

## Prerequisite Installers

Install the required tools:

- **Python 3**
- **uv** – fast Python package and project manager
- **crush** – AI coding agent

Run the script that matches your platform:

- `install_prerequisites_macos.sh`
- `install_prerequisites_linux.sh`
- `install_prerequisites_windows.ps1`

```bash
# macOS
./install_prerequisites_macos.sh

# Linux
./install_prerequisites_linux.sh

# Windows (PowerShell)
powershell -NoProfile -ExecutionPolicy Bypass -File install_prerequisites_windows.ps1
```

After running, verify the installations:

```bash
python3 --version  # or python --version on Windows
uv --version
crush --version
```

## Environment Variable Setup

Scripts that prompt for required environment variables and append them to your shell profile (or user environment on Windows):

- `set_env_macos_linux.sh`
- `set_env_windows.ps1`

Run the script for your platform:

```bash
# macOS or Linux
./set_env_macos_linux.sh

# Windows (PowerShell)
powershell -NoProfile -ExecutionPolicy Bypass -File set_env_windows.ps1
```

These scripts configure `OPENROUTER_API_KEY` and optional Snowflake variables. Restart your terminal after running.

You can re-run the scripts safely if needed.

### Windows PowerShell execution policy

`victoria.py` automatically unblocks these scripts and runs them with a temporary
`-ExecutionPolicy Bypass`, removing any "downloaded from the internet" mark.
When running them manually, start a session with a policy bypass to avoid errors:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass
```

To permanently allow locally created scripts without signing:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```
