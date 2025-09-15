# Victoria Fleet

<img src="assets/VictoriaFleet.png" alt="Victoria Icon" width="200" />

Victoria is Elcano's AI agent that connects to programmatic advertising reports via MCP, her "fleet" are the apps that can use her smarts to navigate advertising datasets and platforms. Traders can ask powerful questions of CSVs, Excel files, and SQL-queryable datasets — making it easier to surface insights, spot trends, and optimize campaigns.

Victoria is not a single application, but a **fleet of apps** designed to work together. This approach allows for greater flexibility and modularity, enabling each component to be updated and deployed independently. For more details on the project's philosophy, see the [Victoria Roadmap](docs/ROADMAP.md).

---

## ⚙️ Installation & Setup

Victoria can be installed on macOS, Linux, and Windows.

### macOS and Linux

The recommended way to install Victoria on macOS and Linux is with the `install.sh` script. This will install the Victoria fleet as command-line tools on your system.

```bash
curl -sL https://raw.githubusercontent.com/elcanotek/victoria/main/install.sh | bash
```

This script will:
- Clone the repository to `~/.victoria`.
- Set up a Python virtual environment.
- Install all necessary dependencies.
- Create command-line wrappers in `/usr/local/bin`.

### Windows

On Windows, you can install Victoria using the `install.ps1` PowerShell script.

1.  **Open PowerShell:** Open a PowerShell terminal. You may need to run it as an administrator for the script to correctly modify the `PATH`.

2.  **Set Execution Policy (if needed):** You might need to allow script execution. You can do this for the current session by running:
    ```powershell
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
    ```

3.  **Download and Run the Installer:** Run the following command to download and execute the installation script.
    ```powershell
    iwr https://raw.githubusercontent.com/elcanotek/victoria/main/install.ps1 -useb | iex
    ```

This script will:
- Clone the repository to `%USERPROFILE%\.victoria`.
- Set up a Python virtual environment.
- Install all necessary dependencies.
- Create command-line wrappers (`.bat` files) in `%USERPROFILE%\.victoria\bin`.
- Add the wrapper directory to your user `PATH`.

After installation, you will have access to the following commands:
- `victoria-configurator`
- `victoria-terminal`
- `victoria-browser`

### First-Time Setup

After installation, you must run the configurator to set up your environment.

```bash
victoria-configurator
```
This will guide you through the necessary setup steps, including creating a `.env` file for your API keys and other secrets in `~/Victoria/.env`.

### Running the Terminal

Once setup is complete, you can run the Victoria Terminal for your data analysis work.

```bash
victoria-terminal
```

---

## 🚀 For Developers

If you want to contribute to Victoria, you can set up a development environment by following these steps.

### Prerequisites

*   **Python 3.8+**
*   **uv**: A fast Python package installer. ([Installation guide](https://docs.astral.sh/uv/getting-started/installation/))

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

4.  **Running the tools:**
    You can run the tools directly from the command line:
    ```bash
    python3 VictoriaConfigurator.py
    python3 VictoriaTerminal.py
    python3 VictoriaBrowser.py
    ```

---
## 🤝 Contributing

We welcome contributions to Victoria! If you're interested in fixing bugs or adding new features, please see our [**Contributing Guidelines**](CONTRIBUTING.md) to get started.
