# Contributing to Victoria

This guide summarizes what you need to contribute code or documentation to Victoria.

## Contributor License Agreement

By submitting a contribution you agree to the [ElcanoTek Contributor License Agreement](CLA.md). The CLA allows ElcanoTek to use, modify, and relicense your work worldwide. If you cannot agree to those terms, please do not submit changes.

## Required Tooling

- **Git** for version control.
- **Podman** for running the development container. Install Podman Desktop on macOS or Windows from [podman.io](https://podman.io) or use your Linux distribution packages. Confirm your installation with `podman --version`.

> **Windows line endings**
> Podman runs shell scripts from this repository. Configure Git with `git config --global core.autocrlf false` before cloning so scripts keep Unix line endings. If you already cloned the repository, run `git reset --hard` after changing the setting or use Windows Subsystem for Linux (WSL).

## Prepare Your Workspace

1. **Clone the repository** and switch into the project directory.
2. **Create the shared host workspace**. Victoria reads configuration and writes analysis artifacts to `~/Victoria` (or `%USERPROFILE%\Victoria` on Windows):
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

## Running the Container

Run the image you just built and mount your shared workspace. Pass arguments after `--` to execute commands inside the container.

**Linux or macOS (Bash):**
```bash
podman run --rm -it \
  --userns=keep-id \
  --security-opt=no-new-privileges \
  --cap-drop=all \
  -e VICTORIA_HOME=/workspace/Victoria \
  -v ~/Victoria:/workspace/Victoria:z \
  victoria-terminal
```

**Windows (PowerShell):**
```powershell
podman run --rm -it `
  -e VICTORIA_HOME=/workspace/Victoria `
  -v "$env:USERPROFILE/Victoria:/workspace/Victoria" `
  victoria-terminal
```

The entrypoint provisions a writable home directory, synchronizes configuration from your mounted workspace, and then launches the terminal UI. Append flags such as `-- --skip-launch` to run configuration checks without starting the UI.

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
  --userns=keep-id \
  --security-opt=no-new-privileges \
  --cap-drop=all \
  -e VICTORIA_HOME=/workspace/Victoria \
  -v ~/Victoria:/workspace/Victoria \
  victoria-terminal -- nox -s lint
```

```powershell
podman run --rm -it -e VICTORIA_HOME=/workspace/Victoria -v "$env:USERPROFILE/Victoria:/workspace/Victoria" victoria-terminal -- nox -s lint
```

**Tests**
```bash
podman run --rm -it \
  --userns=keep-id \
  --security-opt=no-new-privileges \
  --cap-drop=all \
  -e VICTORIA_HOME=/workspace/Victoria \
  -v ~/Victoria:/workspace/Victoria \
  victoria-terminal -- nox -s tests
```

```powershell
podman run --rm -it -e VICTORIA_HOME=/workspace/Victoria -v "$env:USERPROFILE/Victoria:/workspace/Victoria" victoria-terminal -- nox -s tests
```

To target specific pytest paths or keywords, append them after `-- pytest`, for example:
```bash
podman run --rm -it \
  --userns=keep-id \
  --security-opt=no-new-privileges \
  --cap-drop=all \
  -e VICTORIA_HOME=/workspace/Victoria \
  -v ~/Victoria:/workspace/Victoria \
  victoria-terminal -- pytest tests/test_victoria_terminal.py -k "happy_path"
```

Local virtual environments are optional. If you experiment outside Podman, recreate the container to ensure your changes are reflected in future runs.

## Interactive Debugging

Open a shell inside the image when you need to inspect the runtime environment:
```bash
podman run --rm -it \
  --userns=keep-id \
  --security-opt=no-new-privileges \
  --cap-drop=all \
  -e VICTORIA_HOME=/workspace/Victoria \
  -v ~/Victoria:/workspace/Victoria \
  victoria-terminal bash
```
```powershell
podman run --rm -it -e VICTORIA_HOME=/workspace/Victoria -v "$env:USERPROFILE/Victoria:/workspace/Victoria" victoria-terminal bash
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
