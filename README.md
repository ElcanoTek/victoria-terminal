# Victoria Terminal

[![CI](https://github.com/ElcanoTek/victoria-terminal/actions/workflows/ci.yml/badge.svg)](https://github.com/ElcanoTek/victoria-terminal/actions/workflows/ci.yml)
[![Container Image](https://github.com/ElcanoTek/victoria-terminal/actions/workflows/container-image.yml/badge.svg)](https://github.com/ElcanoTek/victoria-terminal/actions/workflows/container-image.yml)
[![License: BUSL-1.1](https://img.shields.io/badge/license-BUSL--1.1-blue.svg)](LICENSE)
[![Contact](https://img.shields.io/badge/contact-brad%40elcanotek.com-informational.svg)](mailto:brad@elcanotek.com)

<img src="assets/victoria.gif" alt="Victoria Terminal Demo" width="650">

Victoria is Elcano's container-first AI agent for programmatic advertising. It runs in Podman, speaks [Model Context Protocol (MCP)](https://modelcontextprotocol.io/), and keeps your data sources isolated while you query them in plain English.

---

## What Victoria Does

- Connects to databases, APIs, SSPs, DSPs, and files through MCP servers you control.
- Automates campaign analysis, report generation, and data wrangling inside an isolated container.
- Runs reproducibly via published images at `ghcr.io/elcanotek/victoria-terminal`.

---

## Requirements

- Modern terminal with OSC-52 and 24-bit color (e.g., [Ghostty](https://ghostty.org) on macOS/Linux, [Windows Terminal](https://aka.ms/terminal) on Windows).
- [Podman](https://podman.io) installed and available on `PATH`.

---

## Quick Install

**macOS / Linux**
```bash
curl -fsSL https://raw.githubusercontent.com/ElcanoTek/victoria-terminal/main/scripts/install_victoria.sh | bash
```

**Windows (PowerShell)**
```powershell
& ([scriptblock]::Create((irm 'https://raw.githubusercontent.com/ElcanoTek/victoria-terminal/main/scripts/install_victoria.ps1')))
```

Then start Victoria:

```bash
victoria
```

Re-run the installer anytime to update the CLI alias. On macOS and Windows, start `podman machine` first if prompted.

### Headless runs

Execute a task without the interactive UI:

```bash
victoria --task "analyze this week's campaign performance and email the report to brad@elcanotek.com"
```

Place any outputs under your mounted `~/Victoria` workspace so downstream jobs can read them.

> Need manual commands or the full dev workflow? See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Protocols

Protocols are markdown files that define repeatable workflows. Drop custom files into `~/Victoria/protocols/` to extend built-ins:

```
~/Victoria/
├── protocols/
│   └── my-custom-workflow.md
├── data/
└── .env
```

Victoria loads every `.md` file in that directory so the agent can follow your steps.

---

## Security at a Glance

- Podman containerization isolates the agent from the host.
- MCP servers constrain exactly what Victoria can reach.
- Secrets stay in `~/Victoria/.env` or your runtime environment.
- BUSL-1.1 licensing and reproducible images keep the stack auditable.
- Contributing implies acceptance of the [ElcanoTek CLA](CLA.md).

---

## Contributing

Check [CONTRIBUTING.md](CONTRIBUTING.md) for coding standards, testing, and release steps.

---

## Learn More

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Elcano Dev Blog](https://elcanotek.substack.com)
- [Elcano Website](https://www.elcanotek.com/)
