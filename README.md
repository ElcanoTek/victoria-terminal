# Victoria Terminal

[![CI](https://github.com/ElcanoTek/victoria-terminal/actions/workflows/ci.yml/badge.svg)](https://github.com/ElcanoTek/victoria-terminal/actions/workflows/ci.yml)
[![Container Image](https://github.com/ElcanoTek/victoria-terminal/actions/workflows/container-image.yml/badge.svg)](https://github.com/ElcanoTek/victoria-terminal/actions/workflows/container-image.yml)
[![License: BUSL-1.1](https://img.shields.io/badge/license-BUSL--1.1-blue.svg)](LICENSE)
[![Contact](https://img.shields.io/badge/contact-brad%40elcanotek.com-informational.svg)](mailto:brad@elcanotek.com)

Victoria is Elcano's container-first AI agent for programmatic advertising. It connects to your data sources through MCP servers you control, and it runs inside a locked-down Podman container so you can analyze sensitive data with confidence.

---

## Motivation

Modern ad ops teams spend too much time wiring spreadsheets and dashboards together. Victoria exists to:

- Ask questions in plain English and get reproducible answers.
- Keep data access explicit, auditable, and isolated.
- Run the same workflows locally, in CI, or across a managed fleet.

---

## Quickstart

**Requirements:** a modern terminal (OSC-52 + 24-bit color) and [Podman](https://podman.io).

**macOS / Linux**
```bash
curl -fsSL https://raw.githubusercontent.com/ElcanoTek/victoria-terminal/main/scripts/install_victoria.sh | bash
```

**Windows (PowerShell)**
```powershell
& ([scriptblock]::Create((irm 'https://raw.githubusercontent.com/ElcanoTek/victoria-terminal/main/scripts/install_victoria.ps1')))
```

Launch Victoria:

```bash
victoria
```

Run a headless task:

```bash
victoria --task "analyze this week's campaign performance and email the report to brad@elcanotek.com"
```

Need manual commands or the full dev workflow? See [CONTRIBUTING.md](CONTRIBUTING.md). Use [example.env](example.env) as a starter template for your `~/Victoria/.env`.

---

## Core Functionality

- **MCP-first connectivity** for databases, SaaS APIs, and file systems you own.
- **Containerized execution** with reproducible images and explicit configuration.

---

## Protocols

Protocols are markdown playbooks that tell Victoria how to execute repeatable workflows. Store your team’s protocols in `~/Victoria/protocols/` so the agent can follow them during each run. See the built-in examples in [`protocols/`](protocols/).

---

## Why Crush

We use [Crush](https://charm.land/crush) because it is a production-ready, terminal-native agent runtime with first-class MCP support. It gives Victoria a consistent operator experience, fast iteration on prompts and protocols, and a reliable way to store session context.

---

## Why Podman

We run Victoria inside [Podman](https://podman.io) to keep the agent boxed in. Podman gives us rootless-friendly containers, simple volume mounts for `~/Victoria`, and a security posture that fits regulated data environments without extra infrastructure.

---

## MCP Catalog

MCP servers define what Victoria can reach. The default configuration lives in [`configs/crush/crush.template.json`](configs/crush/crush.template.json). MCP server are automatically configured if you fill out the required variables in your ```~/Victoria/.env``` file. See [example.env](example.env) for the full list of required variables for each MCP server.


**External MCPs we integrate with:**
- [Snowflake MCP](https://github.com/Snowflake-Labs/mcp) (setup guide: [SNOWFLAKE_SETUP.md](docs/SNOWFLAKE_SETUP.md))
- [BrowserOS](https://browseros.com)
- [Browserbase MCP](https://www.browserbase.com/mcp)
- [MotherDuck MCP](https://github.com/motherduckdb/mcp-server-motherduck)

**Homespun MCPs (Victoria-specific):**
- [Gamma MCP](docs/MCP_GAMMA.md)
- [SendGrid MCP](docs/MCP_SENDGRID.md)
- [Email (SES) MCP](docs/MCP_EMAIL.md) (setup guide: [SES_EMAIL_SETUP.md](docs/SES_EMAIL_SETUP.md))

---

## Orchestration

Victoria integrates with **All-Time-Quarterback**, our proprietary fleet orchestrator for running agents across on-prem and cloud nodes. It focuses on pull-based scheduling, reliable task execution, and centralized log collection while keeping nodes behind outbound-only HTTPS.

See [docs/ORCHESTRATION.md](docs/ORCHESTRATION.md) for a concise overview.

---

## LLM Providers

Crush supports nearly every provider under the sun. We lean on [OpenRouter](https://openrouter.ai/) to access the latest frontier models across our fleet, and we also run local models 24×7 on-prem ([NVIDIA DGX Spark](https://www.nvidia.com/en-us/products/workstations/dgx-spark/) clusters) for background jobs. Victoria works well with local LLMs on [Mac Studio](https://www.apple.com/mac-studio/) rigs too, and we use [Ollama](https://ollama.com/) to run models locally on both. See the [Crush docs](https://charm.land/crush) for the latest provider setup guidance.

---

## Security & Licensing

- Containerization isolates Victoria from the host.
- MCP servers constrain exactly what the agent can access.
- Secrets live in `~/Victoria/.env` or runtime environment variables.
- See [SECURITY.md](SECURITY.md) for more detail.
- Licensed under [BUSL-1.1](LICENSE).

---

## Learn More

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Elcano Dev Blog](https://elcanotek.substack.com)
- [Elcano Website](https://www.elcanotek.com/)
