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

## 🚀 Install with the helper script

The fastest way to get Victoria on your machine is the guided installer. It checks for Podman, ensures your `~/Victoria` workspace exists, detects the host architecture, pulls the matching container image tag, and adds a reusable `victoria` command to your shell profile.

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

> **Need manual commands, pre-built image instructions, or the full development workflow?**
> Head over to [CONTRIBUTING.md](CONTRIBUTING.md) for step-by-step guidance on running published container images and building Victoria from source.

## 🤝 Contributing

We welcome contributions to Victoria! Review our [Contributing Guidelines](CONTRIBUTING.md) for the full development workflow, workspace anatomy, and pull-request expectations.
