# Victoria Terminal

[![CI](https://github.com/ElcanoTek/victoria-terminal/actions/workflows/ci.yml/badge.svg)](https://github.com/ElcanoTek/victoria-terminal/actions/workflows/ci.yml)
[![Container Image](https://github.com/ElcanoTek/victoria-terminal/actions/workflows/container-image.yml/badge.svg)](https://github.com/ElcanoTek/victoria-terminal/actions/workflows/container-image.yml)
[![License: BUSL-1.1](https://img.shields.io/badge/license-BUSL--1.1-blue.svg)](LICENSE)
[![Contact](https://img.shields.io/badge/contact-brad%40elcanotek.com-informational.svg)](mailto:brad@elcanotek.com)

<img src="assets/victoria.gif" alt="Victoria Terminal Demo" width="650">

Victoria is Elcano's AI agent for navigating programmatic advertising datasets. Ask natural-language questions of CSVs, Excel workbooks, and SQL-queryable sources to surface insights without leaving the terminal.

---

## 🔐 Security and licensing overview

- **Container-first distribution.** Victoria ships as a Podman image that packages Python, the `crush` CLI, and required dependencies. The container isolates the agent from the host OS while still allowing controlled file sharing via `~/Victoria` when you opt to mount it.
- **Task isolation without sharing directories.** Automated runs launched with `victoria --task` can execute entirely inside the container without mounting a host workspace, eliminating the need to expose local files during read-only operations.
- **Secrets stay in your control.** Provide API keys as environment variables when you launch the container or store them in `~/Victoria/.env` if you choose to mount that directory. Victoria consumes credentials at runtime without persisting new secrets to disk.
- **Transparent builds.** GitHub Actions builds and publishes the container to `ghcr.io/elcanotek/victoria-terminal`, ensuring every release is reproducible and verified in CI.
- **Source-available license.** Usage is governed by the Victoria Terminal Business Source License (BUSL-1.1). See [LICENSE](LICENSE) for details.
- **Contributor license agreement.** Submitting a patch, issue, or other material constitutes acceptance of the [ElcanoTek Contributor License Agreement](CLA.md).

## 🛠️ Requirements

### Terminal support

Victoria renders a richly styled terminal experience. Use a modern, standards-compliant emulator that supports OSC-52 and 24-bit color. To get the best results, pick a contemporary terminal such as:

- [Ghostty](https://ghostty.org) (Linux and macOS) — **recommended** for its deep feature support.
- [Windows Terminal](https://aka.ms/terminal) (Windows only) which offers solid OSC-52 and 24-bit color support out of the box.

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

### Automate Victoria with `--task`

Victoria can execute non-interactive tasks when launched with the `--task` flag:

```bash
victoria --task "create a Gamma presentation on this week's optimizations and email it to brad@elcanotek.com"
```

Use clear, production-ready instructions in the quoted task string—automation jobs frequently power integration tests and CI workflows. The example above mirrors the internal integration scenario we maintain; adapt the prompt to match the workflow you need to validate. When automations require filesystem output, specify both the filename and the directory inside your mounted `~/Victoria` workspace so downstream jobs can inspect the results.

> **Need manual commands, pre-built image instructions, or the full development workflow?**
> Head over to [CONTRIBUTING.md](CONTRIBUTING.md) for step-by-step guidance on running published container images and building Victoria from source.

## 📋 Protocols

Victoria uses **protocols**—modular markdown files that guide the AI through specialized workflows. Several built-in protocols ship with Victoria, and you can add your own.

### Adding Your Own Protocols

Extend Victoria with custom protocols tailored to your team's workflows. Place markdown files in the `protocols/` folder within your `~/Victoria` workspace:

```bash
~/Victoria/
├── protocols/
│   └── my-custom-workflow.md  # Your custom protocol
├── data/
└── .env
```

Victoria automatically loads all `.md` files from the `protocols/` directory, merging your custom protocols with the built-in ones.

### Protocol File Structure

Each protocol file should include:

1. **Clear title and purpose** — What task does this protocol address?
2. **Step-by-step workflow** — The systematic approach to follow
3. **Output format** — How to deliver the results (email, presentation, conversation)
4. **Examples** — Sample queries, code snippets, or templates

**Example protocol structure:**

```markdown
# My Custom Protocol

Brief description of when to use this protocol.

## Overview

What this protocol accomplishes and why it's useful.

## Workflow

### Step 1: Data Collection
Instructions for gathering data...

### Step 2: Analysis
How to analyze the data...

### Step 3: Delivery
How to present findings...

## Examples

Sample queries, code snippets, or templates...
```

When a user requests a task matching your protocol (e.g., "run my custom workflow"), Victoria reads the protocol file and follows its guidance.

## 🤝 Contributing

We welcome contributions to Victoria! Review our [Contributing Guidelines](CONTRIBUTING.md) for the full development workflow, workspace anatomy, and pull-request expectations.
