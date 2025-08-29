# Victoria

<img src="assets/icon.png" alt="Victoria Icon" width="200" />

Victoria is Elcano's AI agent that connects to programmatic advertising reports via MCP. Traders can ask powerful questions of CSVs, Excel files, and SQL-queryable datasets — making it easier to surface insights, spot trends, and optimize campaigns.

---

## ⚙️ Installation

### Dependencies

You may install prerequisites manually or run the platform script in the [dependencies](./dependencies) folder. Packaged releases
already include these scripts and, on both macOS and Windows, check for a system Python on launch, invoking the installer if it's
missing. These installations are managed separately and must be updated separately.

* `crush` – [GitHub](https://github.com/charmbracelet/crush)
* `uv` – [Docs](https://docs.astral.sh/uv/getting-started/installation/)
* `python` – download from [python.org](https://www.python.org) or use your platform's package manager.

Run `install_prerequisites_macos.sh`, `install_prerequisites_linux.sh`, or
`install_prerequisites_windows.ps1` from `dependencies/` to install these tools
automatically. After running, confirm everything is available:

```bash
python3 --version
uv --version
crush --version
```

### Python Packages (developers only)

The bundled application includes its own Python libraries. When running
`victoria.py` directly, install the UI helpers manually, on first run make sure you setup a venv:

```bash
uv venv
```

Next activate your venv ***IMPORTANT*** in future you'll want to activate your venv before running the victoria.py script

```
source .venv/bin/activate
```

Then install the requirements:

```bash
uv pip install -r requirements.txt
```

Verify the installation:

```bash
python3 -c "import colorama, importlib.metadata as im; print(colorama.__version__, im.version('rich'))"
```

### Environment Variables

Set your environment variables manually or use `set_env_macos_linux.sh` or
`set_env_windows.ps1` in the [dependencies](./dependencies) folder (triggered
automatically on first run) to append them to your shell profile. Restart your
terminal after running the script; you can safely rerun it if needed.

* `OPENROUTER_API_KEY` (required)
* `SNOWFLAKE_ACCOUNT` (optional)
* `SNOWFLAKE_USER` (optional)
* `SNOWFLAKE_PASSWORD` (optional)
* `SNOWFLAKE_WAREHOUSE` (optional)
* `SNOWFLAKE_ROLE` (optional)

---

## 🚀 Launching Victoria

Open your terminal, change into the `victoria-app` folder, and run:

```bash
cd /path/to/victoria-app
source .venv/bin/activate
python3 victoria.py
```

This gives you the most control and is the same across macOS, Linux, and Windows (PowerShell).
All modes store configuration and data in `~/Victoria` (or `%USERPROFILE%\Victoria` on Windows).
On Windows, PowerShell may block script execution. `victoria.py` runs setup scripts
with `-NoProfile` and a temporary `-ExecutionPolicy Bypass` and unblocks them so most
users won't need to tweak any settings. The bundled application unblocks the
scripts before invoking them so the "downloaded from the internet" mark is removed.
If you launch scripts manually and see policy errors, start a session with a bypass:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass
```

To permanently allow locally created scripts, run:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

### Customizing the launch tool

Victoria uses the `crush` CLI by default. Set the following environment variables to swap in a different tool or output file:

```bash
export VICTORIA_TOOL="your_cli"
export VICTORIA_OUTPUT="your_cli.json"
```

#### Adding a new tool configuration

1. Create a folder under [`configs/`](configs) named after your tool.
2. Place your template file inside that folder (e.g. `your_cli.template.json`).
3. Add a `build_<tool>_config` function and register it in `CONFIG_BUILDERS` within [`victoria.py`](victoria.py).
4. Run Victoria with `VICTORIA_TOOL="<tool>"` and optionally set `VICTORIA_OUTPUT`.

## 🔄 On-Demand GitHub Actions

Two workflows in [`.github/workflows`](.github/workflows) can be run manually from the **Actions** tab or via the GitHub CLI.

* **Manual Tests** ([`manual-tests.yml`](.github/workflows/manual-tests.yml)) — runs `tests/test_victoria.py` and `tests/test_non_interactive.py` on Linux, macOS, and Windows:

  ```bash
  gh workflow run manual-tests.yml
  ```

* **Build and Release** ([`build-release.yml`](.github/workflows/build-release.yml)) — executes the test suite and then calls [`scripts/package_mac.sh`](scripts/package_mac.sh) and [`scripts/package_win.bat`](scripts/package_win.bat) to produce `Victoria.app.zip` and `VictoriaSetup.exe`. The Windows packaging step creates a tiny launcher `Victoria.exe` that installs Python if required before delegating to the main `VictoriaApp.exe`. Both are bundled into the installer, and the packaging script removes the temporary copies so `dist/` contains only `VictoriaSetup.exe`:

  ```bash
  gh workflow run build-release.yml
  ```

These packaging scripts can also be run locally if you need to build outside of GitHub.

## 🔏 Certificates for Signed Builds

Signed packages require platform-specific code signing certificates:

- **macOS** – a *Developer ID Application* certificate (optionally *Developer ID
  Installer*) exported as a `.p12` file. Provide the Base64-encoded file via
  `APPLE_CERT_P12` and its password via `APPLE_CERT_PASSWORD`.
- **Windows** – an Authenticode code-signing certificate exported as a `.pfx`
  file and supplied through `WIN_CERT_PFX` and `WIN_CERT_PASSWORD`.

Convert certificate files to one-line Base64 strings for use in GitHub Actions
secrets.

## 🧠 Model Notes

| Model                     | Price (\$/1M tokens) | Category      | Best For              |
| ------------------------- | -------------------- | ------------- | --------------------- |
| **Google Gemini 2.5 Pro** | \$1.25 / \$10.00     | 🏆 Premium    | Best tested model     |
