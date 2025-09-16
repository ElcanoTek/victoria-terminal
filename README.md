# Victoria Terminal

<img src="assets/VictoriaTerminal.png" alt="Victoria Icon" width="200" />

Victoria is Elcano's AI agent that connects to programmatic advertising reports via MCP, her "fleet" are the apps that can use her smarts to navigate advertising datasets and platforms. Traders can ask powerful questions of CSVs, Excel files, and SQL-queryable datasets — making it easier to surface insights, spot trends, and optimize campaigns.

Victoria is not a single application, but a **fleet of apps** designed to work together. This approach allows for greater flexibility and modularity, enabling each component to be updated and deployed independently. For more details on the project's philosophy, see the [Victoria Roadmap](docs/ROADMAP.md).

---

## ⚙️ Installation & Setup

Victoria can be installed on Fedora Linux.

### Fedora Linux

The recommended way to install Victoria on Fedora Linux is with the `install.sh` script. This will install the Victoria fleet as command-line tools on your system.

```bash
curl -sL https://raw.githubusercontent.com/ElcanoTek/victoria-fleet/main/install.sh | bash
```

This script will:
- Clone the repository to `~/.victoria`.
- Set up a Python virtual environment.
- Install all necessary dependencies.
- Create command-line wrappers in `/usr/local/bin`.

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

### Fedora Linux

Run the `uninstall.sh` script from the repository directory, or download and run it directly:

```bash
curl -sL https://raw.githubusercontent.com/ElcanoTek/victoria-fleet/main/uninstall.sh | bash
```

This script will:
- Remove the command-line wrappers from `/usr/local/bin`.
- Delete the Victoria installation directory at `~/.victoria`.

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

## Recommended Models for Testing Victoria

When testing **Victoria** in the terminal, we recommend and have tested the following models.  
These models have been vetted for **compatibility, reliability, and cost considerations**.  
We will keep this list updated as new models become approved, tested, and vetted.

| **Model Name**           | **How It Appears in Crush (under ✅ Configured)** |
|---------------------------|--------------------------------------------------|
| ChatGPT 5                | `OpenAI: GPT-5`                                   |
| ChatGPT 5 Mini           | `OpenAI: GPT-5 Mini`                              |
| xAI Grok Code Fast 1     | `xAI: Grok Code Fast 1`                           |
| Google Gemini 2.5 Pro    | `Google: Gemini 2.5 Pro`                          |
| Google Gemini 2.5 Flash  | `Google: Gemini 2.5 Flash`                        |

### How to Select a Model in Crush
1. Launch Victoria in your terminal.  
2. Press **`Ctrl+P`** to open the command menu.  
3. Choose **“Select Model.”**  
4. In the search bar, type part of the model name (e.g., `GPT-5` or `Gemini 2.5`) to narrow down the results.  
5. Under the **✅ Configured** heading, select one of the recommended models from the table above.  

<p align="left">
  <img src="assets/select_model.png" alt="Select Model in Crush" width="300"/>
</p>

### Important Notes
- These five models are the **only** ones approved for Victoria at this time.
- Selecting any model outside this list is unsupported and may produce unreliable results.  
- As additional models are vetted, this table will be updated to reflect the approved set.
- Victoria remembers the **last model you selected** and will load it automatically the next time you start.
- **Tip:** If you want to compare results across models, switch models, then **restart Victoria** before running your prompts. This gives each model a fresh context and makes results easier to compare.  

## 🤝 Contributing

We welcome contributions to Victoria! If you're interested in fixing bugs or adding new features, please see our [**Contributing Guidelines**](CONTRIBUTING.md) to get started.
