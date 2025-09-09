# Victoria

<img src="assets/icon.png" alt="Victoria Icon" width="200" />

Victoria is Elcano's AI agent that connects to programmatic advertising reports via MCP. Traders can ask powerful questions of CSVs, Excel files, and SQL-queryable datasets — making it easier to surface insights, spot trends, and optimize campaigns.

---

## ⚙️ Installation & Setup

This section covers how to run Victoria from source. For information on the packaged releases, see the project's [GitHub Releases](https://github.com/elcanotek/victoria/releases) page.

### Prerequisites

Before you begin, you will need the following tools installed and available on your system's `PATH`:

*   **Python 3.8+**
*   **uv**: A fast Python package installer. ([Installation guide](https://docs.astral.sh/uv/getting-started/installation/))
*   **crush**: The AI coding agent used by Victoria. ([Installation guide](https://github.com/charmbracelet/crush))

You can verify your installations by running:
```bash
python3 --version
uv --version
crush --version
```
> **Note:** If `crush` is not installed, the application will attempt to install it for you on the first run.

### Development Setup

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/elcanotek/victoria.git
    cd victoria
    ```

2.  **Create a Virtual Environment:**
    It is highly recommended to use a virtual environment to manage dependencies.
    ```bash
    uv venv
    source .venv/bin/activate
    ```

3.  **Install Dependencies:**
    Install all application and development dependencies using `uv`.
    ```bash
    uv pip install -r requirements-dev.txt
    ```

### Environment Variables & Secrets

Victoria uses environment variables for configuration, particularly for secrets like API keys. The recommended way to manage these during development is with a `.env` file.

1.  Create a file named `.env` inside the `~/Victoria` directory (the script will create this directory on first run if it doesn't exist).
    ```bash
    mkdir -p ~/Victoria
    touch ~/Victoria/.env
    ```

2.  Add your secrets to this file in `KEY="VALUE"` format. For example:
    ```
    # ~/Victoria/.env

    OPENROUTER_API_KEY="sk-or-v1-..."
    SNOWFLAKE_ACCOUNT="your_account"
    SNOWFLAKE_USER="your_user"
    SNOWFLAKE_PASSWORD="your_password"
    # ... etc.
    ```
The application will automatically load variables from this file at startup.

---

## 🚀 Launching Victoria

Victoria can be launched in interactive or non-interactive mode.

### Interactive Mode

To launch in interactive mode, open your terminal, change into the `victoria-app` folder, and run:

```bash
source .venv/bin/activate
python3 victoria.py
```

This will present you with menus to select the tool, model, and data source.

### Non-Interactive Mode (for scripting)

Victoria can also be launched non-interactively using command-line arguments. This is useful for scripting and automation.

```bash
python3 victoria.py [OPTIONS]
```

**Options:**

*   `--tool TEXT`: The name of the tool to use (e.g., `crush`).
*   `--course INTEGER`: The course to select (1 for Snowflake, 2 for local files).
*   `--local-model`: Use a local model.
*   `--quiet`: Suppress informational messages.
*   `--version`: Show the version and exit.
*   `--help`: Show the help message and exit.

**Example:**

```bash
python3 victoria.py --tool crush --course 2 --local-model
```

This will launch Victoria with the `crush` tool, using local files and a local model.

### Platform Notes

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

The Victoria app is essentially an installer that configures and runs a tool that is able to connect via MCP to our data sources and use VICTORIA.md as instructions. By default, it uses `crush`, but you can swap in another tool by following the steps below.

### Integrating a New Tool

Adding a new tool with its own configuration logic requires a few modifications to `victoria.py`:

1.  **Create a Configuration Directory**: Under the [`configs/`](configs) directory, add a new folder named after your tool (e.g., `configs/your_tool`).

2.  **Add Template Files**: Place any necessary JSON configuration templates inside your tool's directory. The system can substitute environment variables using the `${VAR_NAME}` syntax.

3.  **Implement Tool-Specific Functions**: In [`victoria.py`](victoria.py), create the following functions for your tool:
    *   `build_<tool_name>_config`: Contains the logic to load your templates, merge data, and produce the final configuration dictionary.
    *   `preflight_<tool_name>`: Checks if the tool's dependencies are met before launch.
    *   `launch_<tool_name>`: Contains the logic to start the tool. This is especially important for tools that are not simple command-line executables.

4.  **Register the Tool**: Add a new `Tool` object to the `TOOLS` dictionary in `victoria.py`. This object will link your new functions and configuration files to the main application.

    ```python
    # In victoria.py
    TOOLS: Dict[str, Tool] = {
        "crush": Tool(
            name="Crush",
            command="crush",
            output_config="crush.json",
            config_builder=build_crush_config,
            preflight=preflight_crush,
            launcher=launch_crush,
        ),
        "your_tool": Tool(
            name="Your Tool",
            command="your_tool_command", # Or an identifier for non-CLI tools
            output_config="your_tool.json",
            config_builder=build_your_tool_config,
            preflight=preflight_your_tool,
            launcher=launch_your_tool,
        ),
    }
    ```

If you add multiple tools, you will need to implement a tool selection menu in the `main` function to allow users to choose which tool to run.

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
