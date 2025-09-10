# Victoria Fleet

<img src="assets/VictoriaFleet.png" alt="Victoria Icon" width="200" />

Victoria is Elcano's AI agent that connects to programmatic advertising reports via MCP, her "fleet" are the apps that can use her smarts to navigate advertising datasets and platforms. Traders can ask powerful questions of CSVs, Excel files, and SQL-queryable datasets — making it easier to surface insights, spot trends, and optimize campaigns.

Victoria is not a single application, but a **fleet of apps** designed to work together. This approach allows for greater flexibility and modularity, enabling each component to be updated and deployed independently. For more details on the project's philosophy, see the [Victoria Roadmap](docs/ROADMAP.md).

---

## ⚙️ Installation & Setup

This section covers how to run Victoria from source. For information on the packaged releases, see the project's [GitHub Releases](https://github.com/ElcanoTek/victoria-fleet/releases) page.

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
    git clone git@github.com:ElcanoTek/victoria-fleet.git
    cd victoria-fleet
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

On Windows, PowerShell's security policy can sometimes prevent scripts from running. The `VictoriaConfigurator.py` script handles this for you, so **no manual steps are typically needed.**

### Model Notes

Victoria's supported models are defined in template JSON files. Check the [Crush template](configs/crush/crush.template.json) and the [Local Providers template](configs/crush/local.providers.json) to see the current models.

---
## 🤝 Contributing

We welcome contributions to Victoria! If you're interested in fixing bugs or adding new features, please see our [**Contributing Guidelines**](CONTRIBUTING.md) to get started.
