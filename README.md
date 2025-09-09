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

The application is now split into two main components:

*   **Victoria Configurator**: A one-time setup tool that installs prerequisites (`crush`) and configures environment variables.
*   **Victoria Terminal**: The main application for launching data analysis sessions with `crush`.

### First-Time Setup

Before launching the terminal for the first time, you must run the configurator.

```bash
source .venv/bin/activate
python3 VictoriaConfigurator.py
```
This will guide you through the necessary setup steps.

### Running the Terminal

Once setup is complete, you can run the Victoria Terminal for your data analysis work.

#### Interactive Mode

To launch in interactive mode, run:
```bash
source .venv/bin/activate
python3 VictoriaTerminal.py
```
This will present you with menus to select the tool, model, and data source.

#### Non-Interactive Mode (for scripting)

The terminal can also be launched non-interactively using command-line arguments.

```bash
python3 VictoriaTerminal.py [OPTIONS]
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
python3 VictoriaTerminal.py --tool crush --course 2 --local-model
```

### Platform Notes

All modes store configuration and data in `~/Victoria` (or `%USERPROFILE%\Victoria` on Windows).

On Windows, PowerShell may block script execution. The `VictoriaConfigurator.py` script runs setup scripts with `-NoProfile` and a temporary `-ExecutionPolicy Bypass` and unblocks them so most users won't need to tweak any settings. If you launch scripts manually and see policy errors, start a session with a bypass:
```powershell
powershell -NoProfile -ExecutionPolicy Bypass
```

To permanently allow locally created scripts, run:
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

## 🔌 Extending Victoria with New Tools

The Victoria Terminal is designed to be extensible, allowing you to add new tools besides the default `crush` agent.

### Integrating a New Tool

Adding a new tool requires a few modifications to `VictoriaTerminal.py`:

1.  **Create a Configuration Directory**: Under the [`configs/`](configs) directory, add a new folder named after your tool (e.g., `configs/your_tool`).

2.  **Add Template Files**: Place any necessary JSON configuration templates inside your tool's directory. The system can substitute environment variables using the `${VAR_NAME}` syntax.

3.  **Implement Tool-Specific Functions**: In [`VictoriaTerminal.py`](VictoriaTerminal.py), create the following functions for your tool:
    *   `build_<tool_name>_config`: Contains the logic to load your templates, merge data, and produce the final configuration dictionary.
    *   `preflight_<tool_name>`: Checks if the tool's dependencies are met before launch.
    *   `launch_<tool_name>`: Contains the logic to start the tool.

4.  **Register the Tool**: Add a new `Tool` object to the `TOOLS` dictionary in `VictoriaTerminal.py`. This object will link your new functions and configuration files to the main application.

    ```python
    # In VictoriaTerminal.py
    TOOLS: Dict[str, Tool] = {
        "crush": Tool(...),
        "your_tool": Tool(
            name="Your Tool",
            command="your_tool_command",
            output_config="your_tool.json",
            config_builder=build_your_tool_config,
            preflight=preflight_your_tool,
            launcher=launch_your_tool,
        ),
    }
    ```

If you add multiple tools, the tool selection menu in the `main` function will automatically display them as choices.

## 🔄 On-Demand GitHub Actions

Two workflows in [`.github/workflows`](.github/workflows) can be run manually from the **Actions** tab or via the GitHub CLI.

* **Manual Tests** ([`manual-tests.yml`](.github/workflows/manual-tests.yml)) — runs the test suite, which has been updated to reflect the new application structure.

  ```bash
  gh workflow run manual-tests.yml
  ```

* **Build and Release** ([`build-release.yml`](.github/workflows/build-release.yml)) — executes the test suite and then calls the packaging scripts to produce application bundles for macOS, Windows, and Linux. For each platform, this workflow now produces two applications: **Victoria Configurator** and **Victoria Terminal**.

  ```bash
  gh workflow run build-release.yml
  ```

These packaging scripts can also be run locally if you need to build outside of GitHub.

## 🧠 Model Notes

Victoria's supported models are defined in template JSON files rather than listed here. Check the [Crush template](configs/crush/crush.template.json) and the [Local Providers template](configs/crush/local.providers.json) to see the current models. If you test additional models that work well, add them to these templates so everyone can benefit.
