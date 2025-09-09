# Victoria

<img src="assets/icon.png" alt="Victoria Icon" width="200" />

Victoria is Elcano's AI agent that connects to programmatic advertising reports via MCP. Traders can ask powerful questions of CSVs, Excel files, and SQL-queryable datasets — making it easier to surface insights, spot trends, and optimize campaigns.

---

## ⚙️ Installation

### Dependencies

You may install prerequisites manually or run the platform script in the [dependencies](./dependencies) folder. For packaged releases,
the application will automatically run these scripts on first launch if it
detects that prerequisites are missing. After installation, you will be
prompted to restart the application.

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

* `OPENROUTER_API_KEY` (optional; required for OpenRouter models)
* `SNOWFLAKE_ACCOUNT` (optional)
* `SNOWFLAKE_USER` (optional)
* `SNOWFLAKE_PASSWORD` (optional)
* `SNOWFLAKE_WAREHOUSE` (optional)
* `SNOWFLAKE_ROLE` (optional)

---

## 🚀 Launching Victoria

Open your terminal, change into the `victoria-app` folder, and run:

```bash
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

## 🔌 Extending Victoria with New Tools

Victoria is designed to be extensible, allowing you to integrate different command-line tools for data analysis. By default, it uses `crush`, but you can swap in another tool by following the steps below.

### Using a Different Tool

To switch the active tool, set the following environment variables before launching the application:

- `VICTORIA_TOOL`: The name of the command-line executable (e.g., `your_cli`).
- `VICTORIA_OUTPUT`: The name of the configuration file Victoria should generate (e.g., `your_cli.json`).

Example:
```bash
export VICTORIA_TOOL="your_cli"
export VICTORIA_OUTPUT="your_cli_config.json"
python3 victoria.py
```

### Integrating a New Tool

Adding a new tool with its own configuration logic requires a few modifications:

1.  **Create a Configuration Directory**: Under the [`configs/`](configs) directory, add a new folder named after your tool (e.g., `configs/your_cli`).

2.  **Add Template Files**: Place any necessary JSON configuration templates inside your tool's directory. The system can substitute environment variables using the `${VAR_NAME}` syntax.

3.  **Implement a Config Builder**: In [`victoria.py`](victoria.py), create a `build_<tool>_config` function. This function will contain the logic to load your templates, merge data, and produce the final configuration dictionary.

4.  **Register the Builder**: Add your new function to the `CONFIG_BUILDERS` dictionary in `victoria.py` to make it accessible to the application.

    ```python
    # In victoria.py
    CONFIG_BUILDERS: Dict[str, Callable[[bool, bool, bool], Dict[str, Any]]] = {
        "crush": build_crush_config,
        "your_cli": build_your_cli_config,  # Add your new tool here
    }
    ```

With these changes, you can run Victoria with `VICTORIA_TOOL` set to your tool's name, and it will use your custom configuration logic.

## 🔄 On-Demand GitHub Actions

Two workflows in [`.github/workflows`](.github/workflows) can be run manually from the **Actions** tab or via the GitHub CLI.

* **Manual Tests** ([`manual-tests.yml`](.github/workflows/manual-tests.yml)) — runs `tests/test_victoria.py` and `tests/test_non_interactive.py` on Linux, macOS, and Windows:

  ```bash
  gh workflow run manual-tests.yml
  ```

* **Build and Release** ([`build-release.yml`](.github/workflows/build-release.yml)) — executes the test suite and then calls [`scripts/package_mac.sh`](scripts/package_mac.sh) and [`scripts/package_win.bat`](scripts/package_win.bat) to produce `Victoria.app.zip` and `VictoriaSetup.exe`. The packaged applications produced by this workflow are self-contained and will handle the installation of dependencies on first run.

  ```bash
  gh workflow run build-release.yml
  ```

These packaging scripts can also be run locally if you need to build outside of GitHub.

## 🧠 Model Notes

Victoria's supported models are defined in template JSON files rather than listed here. Check the [Crush template](configs/crush/crush.template.json) and the [Local Providers template](configs/crush/local.providers.json) to see the current models. If you test additional models that work well, add them to these templates so everyone can benefit.
