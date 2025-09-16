# Victoria Terminal

<img src="assets/VictoriaTerminal.png" alt="Victoria Icon" width="200" />

Victoria is Elcano's AI agent that connects to programmatic advertising reports via MCP, and helps navigate advertising datasets and platforms. Traders can ask powerful questions of CSVs, Excel files, and SQL-queryable datasets — making it easier to surface insights, spot trends, and optimize campaigns.

---

## ⚠️ Install Podman First!

Before you start, make sure you have Podman installed on your local machine. Podman enables containerized applications, like the Victoria Terminal, to run seamlessly on any operating system, see more at [podman.io](https://podman.io).

---

## 🚢 Containerized Workflow

Victoria now ships as a Podman container image that bundles Python, `uv`, the `crush` CLI, and all required Python dependencies. The container stores configuration files inside a shared `~/Victoria` directory so that traders can easily drop files into a shared folder, but the Victoria agent's environment is isolated from their operating system. 

### Build locally with Podman

Clone the repository and build the image from the provided `Containerfile`:

```bash
podman build -t victoria-terminal .
```

### Run using the published image

A GitHub Action automatically builds and publishes the image to the GitHub Container Registry. Pull and run the latest image with Podman:

Before running the container, make sure the shared directory exists on your host machine. Create it once with the command that
matches your operating system:

* **macOS / Linux**: `mkdir -p ~/Victoria`
* **Windows (PowerShell)**: `New-Item -ItemType Directory -Path "$HOME/Victoria" -Force`
* **Windows (Command Prompt)**: `mkdir %USERPROFILE%\Victoria`

```bash
podman run --rm -it \
  -v ~/Victoria:/root/Victoria \
  ghcr.io/elcanotek/victoria-terminal:latest
```

> [!TIP]
> On Arm64 hardware such as Apple silicon Macs, use the dedicated Arm build:
>
> ```bash
> podman run --rm -it \
>   -v ~/Victoria:/root/Victoria \
>   ghcr.io/elcanotek/victoria-terminal:latest-arm64
> ```
>
> The workflow also publishes a commit-specific tag that includes the suffix `-arm64` if you need to pin to an exact build.

Mounting `~/Victoria` ensures that the entry point can reuse your configuration and generated project files across container sessions.

To pass options directly to `VictoriaTerminal.py`, append them after `--`:

```bash
podman run --rm -it \
  -v ~/Victoria:/root/Victoria \
  ghcr.io/elcanotek/victoria-terminal:latest -- --course 2
```

### First-run experience

When the container runs for the first time it executes `victoria_entrypoint.py`, which either:

* Detects configuration files inside the mounted `~/Victoria` directory and reuses them, or
* Prompts you for required settings (OpenRouter API keys, optional Snowflake credentials) and writes them to `~/Victoria/.env`.

Configuration prompts can be revisited at any time by running:

```bash
podman run --rm -it \
  -v ~/Victoria:/root/Victoria \
  ghcr.io/elcanotek/victoria-terminal:latest -- --reconfigure --skip-launch
```

The `--skip-launch` flag stops after writing configuration so that credentials can be updated without launching the terminal UI. You can also point the entry point at an alternate shared location with `--shared-home /path/to/shared/Victoria`.

### Local development workflow

For code changes you can either work directly on the host with a Python virtual environment or inside the container:

```bash
# Inside the repository
uv venv
source .venv/bin/activate
uv pip install -r requirements-dev.txt
pytest
```

To execute tests inside the container build:

```bash
podman run --rm -it \
  -v "$(pwd)":/workspace \
  -w /workspace \
  victoria-terminal pytest
```

Both approaches use the same source tree and configuration files in `~/Victoria`.

---

## 🤖 Continuous Delivery

The repository includes a GitHub Actions workflow that builds the Podman image on pushes to `main` and publishes it to `ghcr.io/elcanotek/victoria-terminal`. The published image is what production users run, and the workflow ensures every build contains the latest dependencies and CLI tooling.

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
