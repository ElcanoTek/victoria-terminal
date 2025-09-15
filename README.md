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
curl -sL https://raw.githubusercontent.com/ElcanoTek/victoria-fleet/main/install.sh | bash
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
    iwr https://raw.githubusercontent.com/ElcanoTek/victoria-fleet/main/install.ps1 -useb | iex
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

## 🧹 Uninstalling Victoria

If you wish to remove Victoria from your system, you can use the provided uninstaller scripts.

### macOS and Linux

Run the `uninstall.sh` script from the repository directory, or download and run it directly:

```bash
curl -sL https://raw.githubusercontent.com/ElcanoTek/victoria-fleet/main/uninstall.sh | bash
```

This script will:
- Remove the command-line wrappers from `/usr/local/bin`.
- Delete the Victoria installation directory at `~/.victoria`.

### Windows

Run the `uninstall.ps1` script from the repository directory, or download and run it directly in PowerShell:

```powershell
iwr https://raw.githubusercontent.com/ElcanoTek/victoria-fleet/main/uninstall.ps1 -useb | iex
```

This script will:
- Remove the Victoria installation directory from `%USERPROFILE%\.victoria`.
- Remove the `bin` directory from your user `PATH` environment variable.

---

## 🚀 For Developers

If you want to contribute to Victoria, you can set up a development environment by following these steps.

### Prerequisites

*   **Python 3.8+**
*   **uv**: A fast Python package installer. ([Installation guide](https://docs.astral.sh/uv/getting-started/installation/))

### Development Setup

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/ElcanoTek/victoria-fleet.git
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

4.  **Running the tools:**
    You can run the tools directly from the command line:
    ```bash
    python3 VictoriaConfigurator.py
    python3 VictoriaTerminal.py
    python3 VictoriaBrowser.py
    ```

---

## Approved Models for Victoria (Terminal Testing Guide)

When testing **Victoria** in the terminal, only the following models are approved for use.  
These models have been vetted for **compatibility, reliability, and cost considerations**.  
We will keep this list updated as new models become approved, tested, and vetted.  

Even though Crush will display many additional models from Catwalk, you should ignore those.  
Use only the models listed here.

| **Approved Model Name** | **How It Appears in Crush (Catwalk)** |
|--------------------------|----------------------------------------|
| ChatGPT 5               | `openai/chatgpt-5`                     |
| ChatGPT 5 Mini          | `openai/chatgpt-5-mini`                |
| xAI Grok Codefast 1     | `xai/grok-code-fast-1`                  |
| Google Gemini 2.5 Pro   | `google/gemini-2.5-pro`                 |
| Google Gemini 2.5 Flash | `google/gemini-2.5-flash`               |

### Important Notes
- These five models are the **only** ones approved for Victoria at this time.  
- If you see other providers/models in the Crush UI, they are coming from Catwalk and are **not approved**.  
- Selecting any model outside this list is unsupported and may produce unreliable results.  
- As additional models are vetted, this table will be updated to reflect the approved set.

## 🤝 Contributing

We welcome contributions to Victoria! If you're interested in fixing bugs or adding new features, please see our [**Contributing Guidelines**](CONTRIBUTING.md) to get started.
