# Prerequisite Installer Scripts

Scripts in this directory install the tools needed for the project:

- **Python 3**
- **uv** – fast Python package and project manager
- **crush** – AI coding agent

## Scripts

- `install_prerequisites_macos.sh`
- `install_prerequisites_linux.sh`
- `install_prerequisites_windows.ps1` (with wrapper `install_prerequisites_windows.bat`)

Run the script that matches your platform:

```bash
# macOS
./install_prerequisites_macos.sh

# Linux
./install_prerequisites_linux.sh

# Windows (PowerShell)
powershell -ExecutionPolicy RemoteSigned -File install_prerequisites_windows.ps1
```

After running, verify the installations:

```bash
python3 --version  # or python --version on Windows
uv --version
crush --version
```

You can re-run the scripts safely if needed.
