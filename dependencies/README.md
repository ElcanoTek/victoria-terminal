# Setup Scripts

Scripts in this directory help install prerequisites and configure environment variables for Victoria.

## Prerequisite Installers

Install the required tools:

- **Python 3**
- **uv** – fast Python package and project manager
- **crush** – AI coding agent

Run the script that matches your platform:

- `install_prerequisites_macos.sh`
- `install_prerequisites_linux.sh`
- `install_prerequisites_windows.ps1` (wrapper `install_prerequisites_windows.bat`)

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

## Developer Python Packages

The bundled application includes its own Python libraries. When running
`victoria.py` directly, install the UI helpers manually:

```bash
uv pip install colorama rich
```

Verify the installation:

```bash
python3 -c "import colorama, rich; print(colorama.__version__, rich.__version__)"
```

## Environment Variable Setup

Scripts that prompt for required environment variables and append them to your shell profile (or user environment on Windows):

- `set_env_macos_linux.sh`
- `set_env_windows.ps1` (wrapper `set_env_windows.bat`)

Run the script for your platform:

```bash
# macOS or Linux
./set_env_macos_linux.sh

# Windows (PowerShell)
powershell -ExecutionPolicy RemoteSigned -File set_env_windows.ps1
```

These scripts configure `OPENROUTER_API_KEY` and optional Snowflake variables. Restart your terminal after running.

You can re-run the scripts safely if needed.
