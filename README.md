# Victoria Terminal

[![CI](https://github.com/ElcanoTek/victoria-terminal/actions/workflows/ci.yml/badge.svg)](https://github.com/ElcanoTek/victoria-terminal/actions/workflows/ci.yml)
[![Container Image](https://github.com/ElcanoTek/victoria-terminal/actions/workflows/container-image.yml/badge.svg)](https://github.com/ElcanoTek/victoria-terminal/actions/workflows/container-image.yml)
[![License: BUSL-1.1](https://img.shields.io/badge/license-BUSL--1.1-blue.svg)](LICENSE)
[![Contact](https://img.shields.io/badge/contact-brad%40elcanotek.com-informational.svg)](mailto:brad@elcanotek.com)

<img src="assets/victoria.gif" alt="Victoria Terminal Demo" width="650">

Victoria is Elcano's AI agent for programmatic advertising—a container-first intelligence layer that connects to any data source, API, or service through the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/). Speak to Victoria in plain English. She handles the tedium—data wrangling, report generation, campaign analysis—so your traders can focus on the decisions that actually matter.

---

## 💡 Philosophy

Victoria embodies a distinct approach to AI agent design:

**Eliminate tedium, keep humans in the loop.** An LLM can process more data in a minute than a trader could read in a week. But that doesn't make traders obsolete—it gives them superpowers. Victoria handles the repetitive work so humans can focus on judgment, context, and the pattern recognition that comes from years of experience.

**Don't trust the agent, control the access.** You can't bank on alignment. The only thing you can actually control is what the agent can reach. Victoria runs in isolated containers with scoped MCP connections—she only accesses what you explicitly permit. If something goes wrong, the blast radius is limited.

**Unix philosophy: do one thing well.** We don't use sprawling frameworks with tens of thousands of lines nobody can maintain. Victoria is a configuration layer on top of battle-tested tools, chained together to solve hard problems. Simple, composable, auditable.

**Protocols over frameworks.** Instead of fighting complex agent architectures, we write protocols in English that guide Victoria through specific workflows. Markdown files that humans can read, agents can follow, and anyone can extend.

---

## 🔌 MCP: Connect to Anything

The [Model Context Protocol](https://modelcontextprotocol.io/) is how Victoria interfaces with the outside world—databases, APIs, SSPs, DSPs, analytics platforms, and any service your workflow requires.

MCP servers define exactly what Victoria can access. Want read-only database queries? Write an MCP server that only exposes SELECT operations. Need campaign data from multiple platforms? Each connection is scoped and controlled. This is the practical implementation of our security model: freedom to act within boundaries, with no way to escape them.

Victoria ships ready to connect. Bring your own MCP servers for proprietary systems, or leverage the growing ecosystem of community and vendor-supported implementations.

---

## 🔐 Security Model

- **Container-first distribution.** Victoria ships as a Podman image that packages Python, the `crush` CLI, and all dependencies. The container isolates the agent from the host OS while allowing controlled file sharing via `~/Victoria` when you opt to mount it.
- **Sandboxed execution.** Tasks can run entirely inside the container without mounting a host workspace, eliminating exposure of local files during read-only operations.
- **Secrets stay in your control.** Provide API keys as environment variables at launch or store them in `~/Victoria/.env`. Victoria consumes credentials at runtime without persisting new secrets to disk.
- **Transparent, reproducible builds.** GitHub Actions builds and publishes every release to `ghcr.io/elcanotek/victoria-terminal`. Every image is verified in CI.
- **Source-available license.** Usage is governed by the Victoria Terminal Business Source License (BUSL-1.1). You can inspect exactly how Victoria works. See [LICENSE](LICENSE) for details.
- **Contributor license agreement.** Submitting a patch, issue, or other material constitutes acceptance of the [ElcanoTek Contributor License Agreement](CLA.md).

---

## 🛠️ Requirements

### Terminal support

Victoria renders a richly styled terminal experience. Use a modern, standards-compliant emulator that supports OSC-52 and 24-bit color:

- [Ghostty](https://ghostty.org) (Linux and macOS) — **recommended** for deep feature support.
- [Windows Terminal](https://aka.ms/terminal) (Windows) — solid OSC-52 and 24-bit color out of the box.

### Podman

Podman is required for every installation option. Install it first, then verify with `podman --version`.

1. **macOS and Windows:** Install Podman Desktop from [podman.io](https://podman.io).
2. **Linux:** Install via your distribution's package manager.

---

## 🚀 Install

The guided installer checks for Podman, ensures your `~/Victoria` workspace exists, detects the host architecture, pulls the matching container image, and adds a reusable `victoria` command to your shell profile.

**macOS / Linux**
```bash
curl -fsSL https://raw.githubusercontent.com/ElcanoTek/victoria-terminal/main/scripts/install_victoria.sh | bash
```

**Windows (PowerShell)**
```powershell
& ([scriptblock]::Create((irm 'https://raw.githubusercontent.com/ElcanoTek/victoria-terminal/main/scripts/install_victoria.ps1')))
```

After the installer finishes, open a new terminal session (or reload your profile) and start Victoria:

```bash
victoria
```

Re-run the script anytime to refresh the alias. It will remind you to start `podman machine` on macOS and Windows if needed.

### Automate with `--task`

Victoria can execute non-interactive tasks headlessly:

```bash
victoria --task "analyze this week's campaign performance and email the report to brad@elcanotek.com"
```

Use clear, production-ready instructions—automation jobs frequently power integration tests and CI workflows. When tasks require filesystem output, specify both filename and directory inside your mounted `~/Victoria` workspace so downstream jobs can inspect results.

> **Need manual commands, pre-built image instructions, or the full development workflow?**
> See [CONTRIBUTING.md](CONTRIBUTING.md) for step-by-step guidance.

---

## 📋 Protocols

Victoria uses **protocols**—modular markdown files that guide the agent through specialized workflows. Protocols are how you encode institutional knowledge, standard operating procedures, and repeatable analysis patterns into something an AI can follow.

Several built-in protocols ship with Victoria. Add your own by placing markdown files in `~/Victoria/protocols/`:

```
~/Victoria/
├── protocols/
│   └── my-custom-workflow.md
├── data/
└── .env
```

Victoria automatically loads all `.md` files from the `protocols/` directory, merging your custom protocols with built-ins.

### Protocol Structure

Each protocol should include:

1. **Clear title and purpose** — What task does this protocol address?
2. **Step-by-step workflow** — The systematic approach to follow
3. **Output format** — How to deliver results (email, presentation, file)
4. **Examples** — Sample queries, code snippets, or templates

```markdown
# Campaign Performance Review

When to use: Weekly analysis of active campaigns.

## Workflow

### Step 1: Data Collection
Pull performance metrics from connected platforms...

### Step 2: Analysis
Calculate key ratios, identify anomalies...

### Step 3: Delivery
Format findings as HTML email to stakeholders...

## Examples

Sample SQL queries, metric definitions, output templates...
```

When a user requests a task matching a protocol, Victoria reads the file and follows its guidance.

---

## 🔄 Provider Agnostic

The AI landscape moves fast. Victoria doesn't lock you into any single model provider. Through OpenRouter and modular tooling, you can switch between GPT, Claude, Gemini, or local models as benchmarks shift and your needs evolve. You sit downstream from a trillion-dollar investment boom in AI capabilities—benefit from it without betting everything on one vendor.

---

## 🤝 Contributing

We welcome contributions! Review our [Contributing Guidelines](CONTRIBUTING.md) for the full development workflow, workspace anatomy, and pull-request expectations.

---

## 📚 Learn More

- [Model Context Protocol](https://modelcontextprotocol.io/) — The standard for connecting AI agents to tools and data
- [Elcano Website](https://www.elcanotek.com/) — More about our approach to AI in programmatic advertising
