# Victoria

<img src="assets/Victoria.png" alt="Victoria Icon" width="200" />

Victoria is Elcano's AI agent that connects to programmatic advertising reports via MCP. Traders can ask powerful questions of CSVs, Excel files, and SQL-queryable datasets — making it easier to surface insights, spot trends, and optimize campaigns.

Victoria is not a single application, but a **fleet of apps** designed to work together. This approach allows for greater flexibility and modularity, enabling each component to be updated and deployed independently. For more details on the project's philosophy, see the [Victoria Roadmap](docs/ROADMAP.md).

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

### Code Quality & Linting

Victoria follows Python best practices with automated code formatting and linting. The project uses:

- **[Black](https://black.readthedocs.io/)**: Code formatter for consistent style
- **[isort](https://pycqa.github.io/isort/)**: Import statement organizer
- **[flake8](https://flake8.pycqa.org/)**: Linter for PEP8 compliance and code quality

#### Running Linting Tools

After installing development dependencies, you can run the linting tools:

```bash
# Format code with Black (88 character line length)
black .

# Sort imports with isort
isort .

# Check for linting issues with flake8
flake8 .
```

#### Pre-commit Workflow

For the best development experience, run all linting tools before committing:

```bash
# Format and lint all code
black . && isort . && flake8 .
```

#### Configuration

- **Black**: Uses 88 character line length (default)
- **isort**: Configured to work with Black's formatting
- **flake8**: Configured in `.flake8` with 88 character line length and ignores E402 in test files

All linting tools are included in `requirements-dev.txt` and will be installed automatically during development setup.

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

## 🚀 The Victoria Fleet

The Victoria project is a **fleet of applications**, each with a specific purpose. The initial fleet consists of three main components:

*   **Victoria Configurator**: The starting point for all new users. This is a one-time setup tool that installs prerequisites (`crush`) and configures your environment variables.
*   **Victoria Terminal**: The flagship application for launching data analysis sessions with the `crush` AI agent.
*   **Victoria Browser**: A simple utility that opens your default web browser to the ElcanoTek website.

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
This will present you with menus to select the model and data source.

#### Non-Interactive Mode (for scripting)

The terminal can also be launched non-interactively using command-line arguments.

```bash
python3 VictoriaTerminal.py [OPTIONS]
```

**Options:**

*   `--course INTEGER`: The course to select (1 for Snowflake, 2 for local files).
*   `--local-model`: Use a local model.
*   `--quiet`: Suppress informational messages.
*   `--version`: Show the version and exit.
*   `--help`: Show the help message and exit.

**Example:**

```bash
python3 VictoriaTerminal.py --course 2 --local-model
```

### Platform Notes

All modes store configuration and data in `~/Victoria` (or `%USERPROFILE%\Victoria` on Windows).

On Windows, PowerShell's security policy can prevent scripts from running. We've designed the `VictoriaConfigurator.py` to handle this automatically, so for most users, **no manual configuration is necessary.** The configurator uses a temporary bypass and unblocks the necessary scripts for you.

If you choose to run the setup scripts from the `dependencies` folder manually and encounter an error, you have two options:

1.  **Start a bypassed PowerShell session:**
    Open a new terminal and run the following command. This will start a new PowerShell session that allows scripts to run.
    ```powershell
    powershell -NoProfile -ExecutionPolicy Bypass
    ```
    From this new session, you can then run the `.ps1` scripts directly.

2.  **Set a permanent policy:**
    To allow all locally-created scripts to run on your system, you can run this command once in any PowerShell terminal. This is a common configuration for developers.
    ```powershell
    Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
    ```


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
