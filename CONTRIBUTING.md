# Contributing to Victoria

First off, thank you for considering contributing to Victoria! We welcome all contributions, from bug reports to new features.

This document provides guidelines for developers who want to contribute to the project.

## Contributor License Agreement

By submitting a Contribution you agree to the terms of the [ElcanoTek Contributor License Agreement](CLA.md). The CLA grants ElcanoTek a perpetual, worldwide right to use, modify, commercialize, and relicense your Contribution in any manner. If you do not agree to those terms, do not submit Contributions.

## Development Workflow

Victoria is distributed as a container image and contributors are expected to
build and run that image locally during development. Podman is the only hard
requirement.

1. **Install and validate Podman.** macOS and Windows users can install Podman
   Desktop from [podman.io](https://podman.io); Linux users should use their
   distribution packages. Confirm the installation with `podman --version`.
2. **Clone the repository** and change into it. All build commands run from the
   repository root.
3. **Build the development image.** The Containerfile is the source of truth for
   dependencies and tooling:

   ```bash
   podman build -t victoria-terminal .
   ```

   Rebuild whenever you update Python dependencies, adjust the `Containerfile`,
   or need the container to pick up local source code changes.

4. **Run the development image.** Mount your shared workspace and pass optional
   arguments after `--` to forward them to the entrypoint:

   ```bash
   podman run --rm -it \
     -v ~/Victoria:/root/Victoria \
     victoria-terminal

   # Run automated linting
   podman run --rm -it \
     -v ~/Victoria:/root/Victoria \
     victoria-terminal -- nox -s lint
   ```

   Windows users should keep the command on a single line and replace
   `~/Victoria` with `$env:USERPROFILE/Victoria`.

5. **Optional virtual environment.** If you must experiment outside Podman,
   create a local virtual environment with `python -m venv .venv`, install
   `requirements.txt`, and rebuild the container once you are satisfied with the
   changes. Treat this as a temporary escape hatch; the container remains the
   source of truth.

> [!TIP]
> Append `-- --reconfigure --skip-launch` to trigger the configuration wizard
> without launching the terminal UI. This is useful when validating environment
> variables or first-run flows.

## Workspace Anatomy

Victoria splits responsibilities between the host and the Podman container. A
clear understanding of the shared files prevents accidental data loss.

### Host: `~/Victoria`

* **`.env`** — Stores all secrets (API keys, Snowflake credentials). Victoria
  reads from this file on startup and never bakes secrets into the container.
* **Working assets** — Drop CSVs or other source files here so Victoria can load
  them. The agent writes analysis outputs, transformed files, and exports back
  into the same folder.
* **`VICTORIA.md`** — Regenerated on every run. Treat this as ephemeral output
  summarizing the capabilities of the current build. Any manual edits will be
  overwritten.
* **`crush.template.json`** — Configuration for the Crush agent template. The runtime
  rewrites it when the crush configuration changes.

Create the workspace once and reuse it for every run:

```bash
mkdir -p ~/Victoria
```

On Windows PowerShell:

```powershell
New-Item -ItemType Directory -Path "$env:USERPROFILE/Victoria" -Force
```

Because this directory is mounted into the container, edits from either side are
visible immediately. Keep a backup of anything that should not be replaced by
Victoria's automated writers.

### Podman Container: source tree and runtime

* **Application code** lives inside the container filesystem. Editing Python
  modules or templates requires a container rebuild (`podman build -t
  victoria-terminal .`) before the changes take effect.
* **Templates and manifests** (including the Crush template and `VICTORIA.md`)
  ship in the image. Use the rebuild cycle to propagate any updates into the
  runtime environment.
* **Nox, pytest, and development tooling** are preinstalled via the
  `Containerfile`. Running them through `podman run ... -- nox -s <session>`
  ensures consistency with CI.

## Extending Victoria's Functionality

Adding new capabilities typically touches both configuration and documentation:

1. **Update the Crush template** in `configs/crush/` (or the relevant template
   directory) so the agent understands the new commands or behaviors.
2. **Revise `VICTORIA.md`** to explain the new skills. Remember that `VICTORIA.md`
   is regenerated on every run, so build automation should own these updates.
3. **Rebuild the container** so the Podman runtime picks up code and template
   changes.
4. **Document user-facing changes** if the host workflow needs new files or
   environment variables.

Commit related updates together so reviewers can reason about the full feature
addition.

## Tooling & Linting

Victoria follows Python best practices with automated formatting and linting:

* **[Black](https://black.readthedocs.io/)** — Code formatter for consistent style.
* **[isort](https://pycqa.github.io/isort/)** — Import organizer aligned with Black.
* **[flake8](https://flake8.pycqa.org/)** — Enforces PEP 8 compliance and highlights
  common mistakes.

These tools run through [Nox](https://nox.thea.codes/) sessions defined in
`noxfile.py`. Because the container ships with the tooling installed, invoke them
directly via Podman:

```bash
podman run --rm -it \
  -v ~/Victoria:/root/Victoria \
  victoria-terminal -- nox -s lint
```

Nox manages its own virtual environments, so you can run the command from a
fresh checkout without pre-creating `.venv`.

## Testing (Optional Locally)

End-to-end verification happens automatically in GitHub Actions. Local test runs
are optional but useful when iterating on complex changes:

```bash
podman run --rm -it \
  -v ~/Victoria:/root/Victoria \
  victoria-terminal -- nox -s tests
```

Use local pytest invocations only if you understand the impact; otherwise rely on
the Nox session above for parity with CI.

## On-Demand GitHub Actions

Two workflows in [`.github/workflows`](.github/workflows) can be run manually from the **Actions** tab or via the GitHub CLI.

* **Manual Tests** ([`manual-tests.yml`](.github/workflows/manual-tests.yml)) — runs the test suite.
  ```bash
  gh workflow run manual-tests.yml
  ```

* **Container Image** ([`container-image.yml`](.github/workflows/container-image.yml)) — builds and publishes the Podman image used by contributors and production operators.
  ```bash
  gh workflow run container-image.yml
  ```

## Pull Request Guidelines

- **Title Format**: `[Component] Brief description of changes` (e.g., `[VictoriaTerminal] Add support for new data source`).
- **Description**: Provide a clear and concise description of the changes.
- **Testing**: Ensure all tests pass before submitting a pull request.
- **Code Review**: All pull requests must be reviewed and approved by at least one other team member.
