# Victoria Terminal

[![CI](https://github.com/ElcanoTek/victoria-terminal/actions/workflows/ci.yml/badge.svg)](https://github.com/ElcanoTek/victoria-terminal/actions/workflows/ci.yml)
[![Container Image](https://github.com/ElcanoTek/victoria-terminal/actions/workflows/container-image.yml/badge.svg)](https://github.com/ElcanoTek/victoria-terminal/actions/workflows/container-image.yml)
[![License: BUSL-1.1](https://img.shields.io/badge/license-BUSL--1.1-blue.svg)](LICENSE)
[![Contact](https://img.shields.io/badge/contact-brad%40elcanotek.com-informational.svg)](mailto:brad@elcanotek.com)

<img src="assets/victoria.gif" alt="Victoria Terminal Demo" width="650">

Victoria is Elcano's AI agent for navigating programmatic advertising datasets. Ask natural-language questions of CSVs, Excel workbooks, and SQL-queryable sources to surface insights without leaving the terminal.

---

## 🔐 Security and licensing overview

- **Container-first distribution.** Victoria ships as a Podman image that packages Python, the `crush` CLI, and required dependencies. The container isolates the agent from the host OS while still allowing controlled file sharing via `~/Victoria`.
- **Secrets stay in your workspace.** Credentials are read from `~/Victoria/.env`, mounted into the container at runtime. Provide a fully populated file with the API keys your team needs and Victoria consumes them without persisting new secrets.
- **Transparent builds.** GitHub Actions builds and publishes the container to `ghcr.io/elcanotek/victoria-terminal`, ensuring every release is reproducible and verified in CI.
- **Source-available license.** Usage is governed by the Victoria Terminal Business Source License (BUSL-1.1). See [LICENSE](LICENSE) for details.
- **Contributor license agreement.** Submitting a patch, issue, or other material constitutes acceptance of the [ElcanoTek Contributor License Agreement](CLA.md).

## 🛠️ Requirements

### Terminal support

Victoria renders a richly styled terminal experience. Use a modern, standards-compliant emulator that supports OSC-52 and 24-bit color.

- **macOS:** [Ghostty](https://ghostty.org) provides the best results. The built-in macOS Terminal has known limitations such as unreliable copy and paste.
- **Linux:** [Ghostty](https://ghostty.org) offers broad standards support.
- **Windows:** Use [Windows Terminal](https://aka.ms/terminal).

### Podman

Podman is required for every installation option. Install it first, then verify the setup with `podman --version`.

1. **macOS and Windows:** Install Podman Desktop from [podman.io](https://podman.io).
2. **Linux:** Install Podman with your distribution's package manager.

---

## 🚀 Installation options

Victoria supports three installation flows. Use the summary below to pick the path that matches your workflow, then jump to the detailed instructions.

| Stream | Best for | What you get |
| --- | --- | --- |
| [Stream 1 – Guided helper script](#stream-1--guided-helper-script) | Analysts and traders who want the quickest setup | Installs Podman prerequisites, provisions the shared workspace, pulls the right image, and adds a `victoria` command to your shell profile. |
| [Stream 2 – Manual Podman commands](#stream-2--manual-podman-commands) | Operators who prefer to copy/paste each command | Step-by-step Podman instructions for creating the workspace, pulling images, running the container, and passing options. |
| [Stream 3 – Build from source](#stream-3--build-from-source) | Contributors and teams customizing Victoria | Clone the repository, create a Python environment, and build/test the container locally. |

### Stream 1 – Guided helper script

Let Victoria wire up the remaining pieces for you. The helper scripts validate Podman, ensure your `~/Victoria` workspace exists, detect the host architecture, pull the matching container image tag, and add a reusable `victoria` command to your shell profile.

* **macOS / Linux**
  ```bash
  curl -fsSL https://raw.githubusercontent.com/ElcanoTek/victoria-terminal/main/install_victoria.sh | bash
  ```
* **Windows (PowerShell)**
  ```powershell
  & ([scriptblock]::Create((irm 'https://raw.githubusercontent.com/ElcanoTek/victoria-terminal/main/install_victoria.ps1')))
  ```

After the helper finishes, open a new terminal session (or reload your profile with `source ~/.bashrc`, `source ~/.zshrc`, or `. $PROFILE`) and start Victoria with a single command:

```bash
victoria
```

Re-run the script any time you want to refresh the alias. It will not reinstall Podman, but it will remind you to start `podman machine` on macOS and Windows if needed.

### Stream 2 – Manual Podman commands

Prefer to copy and paste the commands yourself? Follow the steps below to mirror what the helper script does behind the scenes.

#### Create the shared workspace folder

Victoria stores configuration and credentials in a folder that is mounted into the container. Create it once and reuse it for every upgrade:

* **macOS / Linux**
  ```bash
  mkdir -p ~/Victoria
  ```
* **Windows (PowerShell)**
  ```powershell
  New-Item -ItemType Directory -Path "$HOME/Victoria" -Force
  ```
* **Windows (Command Prompt)**
  ```cmd
  mkdir %USERPROFILE%\Victoria
  ```

#### Pull the right image for your architecture

Victoria publishes multi-architecture tags. If you're unsure which CPU architecture your Podman host is using, check it with:

```bash
podman info --format '{{.Host.Arch}}'
```

Use the table below to pull (or update) the matching image and run it. Re-running the `podman pull` command keeps you on the latest release.

| Platform | CPU architecture | Pull / update | Run |
| --- | --- | --- | --- |
| macOS or Linux (Intel/AMD) | `x86_64` | `podman pull ghcr.io/elcanotek/victoria-terminal:latest` | `podman run --rm -it --userns=keep-id --security-opt=no-new-privileges --cap-drop=all -e VICTORIA_HOME=/workspace/Victoria -v ~/Victoria:/workspace/Victoria:z ghcr.io/elcanotek/victoria-terminal:latest` |
| macOS or Linux (Arm64) | `arm64` | `podman pull ghcr.io/elcanotek/victoria-terminal:latest-arm64` | `podman run --rm -it --userns=keep-id --security-opt=no-new-privileges --cap-drop=all -e VICTORIA_HOME=/workspace/Victoria -v ~/Victoria:/workspace/Victoria:z ghcr.io/elcanotek/victoria-terminal:latest-arm64` |
| Windows PowerShell (Intel/AMD) | `x86_64` | `podman pull ghcr.io/elcanotek/victoria-terminal:latest` | `podman run --rm -it -e VICTORIA_HOME=/workspace/Victoria -v "$env:USERPROFILE/Victoria:/workspace/Victoria" ghcr.io/elcanotek/victoria-terminal:latest` |
| Windows PowerShell (Arm64) | `arm64` | `podman pull ghcr.io/elcanotek/victoria-terminal:latest-arm64` | `podman run --rm -it -e VICTORIA_HOME=/workspace/Victoria -v "$env:USERPROFILE/Victoria:/workspace/Victoria" ghcr.io/elcanotek/victoria-terminal:latest-arm64` |

> **Tip:** The run commands are shown on a single line for PowerShell compatibility. On macOS and Linux you can add `\` line continuations for readability.

When you need to pass arguments through to Victoria, include `--` after the image name so Podman stops parsing options. For example:

```bash
podman run --rm -it --userns=keep-id --security-opt=no-new-privileges --cap-drop=all -e VICTORIA_HOME=/workspace/Victoria -v ~/Victoria:/workspace/Victoria ghcr.io/elcanotek/victoria-terminal:latest -- --skip-launch
```

The same command on Windows stays on a single line and uses `$env:USERPROFILE/Victoria` for the shared folder path.

> **Important:** Non-interactive runs that skip the launch banner must also pass `--accept-license` (for example, together with `--no-banner`). Using this flag automatically accepts the Victoria Terminal Business Source License described in [LICENSE](LICENSE).

#### Configure on first run

The container's default command (`victoria_terminal.py`) assumes you provide a ready-to-use `.env` file inside `~/Victoria`.

- If `~/Victoria/.env` exists, Victoria loads the environment variables and launches immediately.
- If the file is missing—or lacks a required key—it logs a warning that calls out which integrations will be unavailable until the `.env` file is updated.

Victoria validates your `.env` file on every launch. Pass `--skip-launch` if you only want to perform the configuration checks without starting the UI:

```bash
podman run --rm -it \
  --userns=keep-id \
  --security-opt=no-new-privileges \
  --cap-drop=all \
  -e VICTORIA_HOME=/workspace/Victoria \
  -v ~/Victoria:/workspace/Victoria \
  ghcr.io/elcanotek/victoria-terminal:latest -- --skip-launch
```

You can also point the default command at an alternate shared location with `--shared-home /path/to/shared/Victoria`.

> **Tip:** Ship a preconfigured `.env` file with every deployment so users can copy it into `~/Victoria` before launching.

##### Managing the `.env` file

Victoria reads every environment variable defined in `~/Victoria/.env` and exposes it to the terminal session. Provide two artifacts to your users:

1. A commented template that documents each key (use `example.env` as a starting point).
2. A deployment-ready file with live credentials so new users can copy it into place without editing.

```dotenv
# victoria/.env (sample deployment bundle)
OPENROUTER_API_KEY="sk-or-your-api-key-here"
GAMMA_API_KEY="sk-gamma-your-api-key-here"
```

- Keep comments in the template to describe why a key is needed or where to request it.
- Distribute sensitive values through secure channels—Victoria simply reads them at runtime.
- To rotate a credential, update the `.env` file on the host and restart the container; no interactive wizard is required.

Swap in the image tag that matches your architecture (from the table above) and adjust the host path syntax for your platform. Windows PowerShell users should run the command on a single line with `$env:USERPROFILE/Victoria`.

#### Using Local LLM Providers

Victoria is configured to work with local LLM providers like LM Studio. To connect to LM Studio from within the Victoria container, you must enable network access.

In LM Studio, navigate to the server settings and ensure that **"Serve on local network"** is turned on. This allows the container to reach the server at `http://host.containers.internal:1234`.

### Stream 3 – Build from source

Follow this path if you plan to modify Victoria, integrate it into a custom workflow, or contribute changes upstream. The end-to-end development workflow—including rebuilding the container, updating shared templates, and verifying changes—is documented in detail in [CONTRIBUTING.md](CONTRIBUTING.md).

## 🤝 Contributing

We welcome contributions to Victoria! Review our [Contributing Guidelines](CONTRIBUTING.md) for the full development workflow, workspace anatomy, and pull-request expectations.
