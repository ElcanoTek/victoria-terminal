# Contributing to Victoria

This guide summarizes what you need to contribute code or documentation to Victoria.

## Contributor License Agreement

By submitting a contribution you agree to the [ElcanoTek Contributor License Agreement](CLA.md). The CLA allows ElcanoTek to use, modify, and relicense your work worldwide. If you cannot agree to those terms, please do not submit changes.

## Required Tooling

- **Git** for version control.
- **Podman** for running either the published containers or the development image. Install Podman Desktop on macOS or Windows from [podman.io](https://podman.io) or use your Linux distribution packages. Confirm your installation with `podman --version`.

> **Windows line endings**
> Podman runs shell scripts from this repository. Configure Git with `git config --global core.autocrlf false` before cloning so scripts keep Unix line endings. If you already cloned the repository, run `git reset --hard` after changing the setting or use Windows Subsystem for Linux (WSL).

## Run pre-built images

Use this path when you want to run the latest Victoria release without building the container yourself.

### 1. Create the shared workspace

Victoria stores configuration and credentials in a folder that is mounted into the container. Create it once and reuse it for every upgrade.

- **macOS / Linux**
  ```bash
  mkdir -p ~/Victoria
  ```
- **Windows (PowerShell)**
  ```powershell
  New-Item -ItemType Directory -Path "$env:USERPROFILE/Victoria" -Force
  ```
- **Windows (Command Prompt)**
  ```cmd
  mkdir %USERPROFILE%\Victoria
  ```

### 2. Pull the correct image for your architecture

Check your Podman host architecture so you can pull the matching multi-architecture image tag:

```bash
podman info --format '{{.Host.Arch}}'
```

Use the commands below to stay current with the published images. Re-running `podman pull` keeps you on the latest release.

| Platform | CPU architecture | Pull / update | Run |
| --- | --- | --- | --- |
| macOS or Linux (Intel/AMD) | `x86_64` | `podman pull ghcr.io/elcanotek/victoria-terminal:latest` | `podman run --rm -it -v ~/Victoria:/workspace/Victoria:z ghcr.io/elcanotek/victoria-terminal:latest` |
| macOS or Linux (Arm64) | `arm64` | `podman pull ghcr.io/elcanotek/victoria-terminal:latest-arm64` | `podman run --rm -it -v ~/Victoria:/workspace/Victoria:z ghcr.io/elcanotek/victoria-terminal:latest-arm64` |
| Windows PowerShell (Intel/AMD) | `x86_64` | `podman pull ghcr.io/elcanotek/victoria-terminal:latest` | `podman run --rm -it -v "$env:USERPROFILE/Victoria:/workspace/Victoria" ghcr.io/elcanotek/victoria-terminal:latest` |
| Windows PowerShell (Arm64) | `arm64` | `podman pull ghcr.io/elcanotek/victoria-terminal:latest-arm64` | `podman run --rm -it -v "$env:USERPROFILE/Victoria:/workspace/Victoria" ghcr.io/elcanotek/victoria-terminal:latest-arm64` |

> **Tip:** The run commands are shown on a single line for PowerShell compatibility. On macOS and Linux you can add `\` line continuations for readability.

The container image exports `VICTORIA_HOME=/workspace/Victoria` by default, so mounting your host directory at `/workspace/Victoria` is all that is required to persist configuration and logs between runs.

When you need to pass arguments through to Victoria, include `--` after the image name so Podman stops parsing options. For example:

```bash
podman run --rm -it -v ~/Victoria:/workspace/Victoria ghcr.io/elcanotek/victoria-terminal:latest -- --accept-license
```

The same command on Windows stays on a single line and uses `$env:USERPROFILE/Victoria` for the shared folder path.

> **Important:** Non-interactive runs triggered with `--task` must also pass `--accept-license`. Using this flag automatically accepts the Victoria Terminal Business Source License described in [LICENSE](LICENSE).

Automated tasks run the same agent that powers the interactive terminal, so craft prompts that describe the real-world workflow you want to verify. Our default integration run asks Victoria to produce a Gamma presentation and email it to `brad@elcanotek.com`:

```bash
victoria --accept-license --task "create a Gamma presentation on this week's optimizations and email it to brad@elcanotek.com"
```

Update the quoted instruction to match your integration test or CI scenario. When you need artifacts written to disk, tell Victoria exactly which filenames to create inside `/workspace/Victoria` so your automation can pick them up after the container exits.

### 3. Configure on first run

The container's default command (`victoria_terminal.py`) assumes you provide a ready-to-use `.env` file inside `~/Victoria`.

- If `~/Victoria/.env` exists, Victoria loads the environment variables and launches immediately.
- If the file is missing—or lacks a required key—it logs a warning that calls out which integrations will be unavailable until the `.env` file is updated.

Victoria validates your `.env` file on every launch.

You can also point the default command at an alternate shared location with `--shared-home /path/to/shared/Victoria`.

#### Managing the `.env` file

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

#### Using local LLM providers

Victoria is configured to work with local LLM providers like LM Studio. To connect to LM Studio from within the Victoria container, you must enable network access.

In LM Studio, navigate to the server settings and ensure that **"Serve on local network"** is turned on. This allows the container to reach the server at `http://host.containers.internal:1234`.

## Build from source

Follow this path if you plan to modify Victoria, integrate it into a custom workflow, or contribute changes upstream.

1. **Clone the repository** and switch into the project directory.
2. **Create the shared host workspace** if you have not already done so:
   ```bash
   mkdir -p ~/Victoria
   ```
   ```powershell
   New-Item -ItemType Directory -Path "$env:USERPROFILE/Victoria" -Force
   ```
3. **Build the development image**. The `Containerfile` captures all runtime dependencies and tooling:
   ```bash
   podman build -t victoria-terminal .
   ```
   Rebuild the image whenever you change dependencies or Python source files.

Run the image you just built and mount your shared workspace. Pass arguments after `--` to execute commands inside the container.

**Linux or macOS (Bash):**
```bash
podman run --rm -it \
  -v ~/Victoria:/workspace/Victoria:z \
  victoria-terminal
```

**Windows (PowerShell):**
```powershell
podman run --rm -it `
  -v "$env:USERPROFILE/Victoria:/workspace/Victoria" `
  victoria-terminal
```

The entrypoint provisions a writable home directory, synchronizes configuration from your mounted workspace, and then launches the terminal UI.

## Workspace Layout

The container image ships with the application code. The mounted host directory keeps your mutable data.

- `~/Victoria/.env` – API keys and other secrets read on startup.
- `~/Victoria` – Input datasets, analysis exports, logs, and generated manifests (including `VICTORIA.md` and `crush.template.json`). Treat these files as ephemeral outputs unless you copy them elsewhere.

Everything stored outside the mounted directory is removed when the container exits because we run with `--rm`.

## Automation and Tests

Victoria standardizes on Nox sessions for linting and tests. Run them through Podman for parity with CI.

**Linting**
```bash
podman run --rm -it \
  -v ~/Victoria:/workspace/Victoria \
  victoria-terminal -- nox -s lint
```

```powershell
podman run --rm -it -v "$env:USERPROFILE/Victoria:/workspace/Victoria" victoria-terminal -- nox -s lint
```

**Tests**
```bash
podman run --rm -it \
  -v ~/Victoria:/workspace/Victoria \
  victoria-terminal -- nox -s tests
```

```powershell
podman run --rm -it -v "$env:USERPROFILE/Victoria:/workspace/Victoria" victoria-terminal -- nox -s tests
```

To target specific pytest paths or keywords, append them after `-- pytest`, for example:
```bash
podman run --rm -it \
  -v ~/Victoria:/workspace/Victoria \
  victoria-terminal -- pytest tests/test_victoria_terminal.py -k "happy_path"
```

Local virtual environments are optional. If you experiment outside Podman, recreate the container to ensure your changes are reflected in future runs.

## Interactive Debugging

Open a shell inside the image when you need to inspect the runtime environment:
```bash
podman run --rm -it \
  -v ~/Victoria:/workspace/Victoria \
  victoria-terminal bash
```
```powershell
podman run --rm -it -v "$env:USERPROFILE/Victoria:/workspace/Victoria" victoria-terminal bash
```
Inside the shell you can run `env | sort`, inspect `/workspace/Victoria`, or execute `nox` and `pytest` directly. Files you create outside the mounted directory disappear when the container stops.

## GitHub Actions

Two workflows can be triggered manually from the **Actions** tab or via the GitHub CLI:

- `manual-tests.yml` – Runs the test suite.
  ```bash
  gh workflow run manual-tests.yml
  ```
- `container-image.yml` – Builds and publishes the Podman image.
  ```bash
  gh workflow run container-image.yml
  ```

## Pull Request Guidelines

- Title format: `[Component] Summary of change` (for example, `[VictoriaTerminal] Add Snowflake query helper`).
- Include a concise summary of what changed and why.
- Run linting and tests before requesting review.
- Every pull request requires approval from another team member.
