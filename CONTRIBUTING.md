# Contributing to Victoria

First off, thank you for considering contributing to Victoria! We welcome all contributions, from bug reports to new features.

This document provides guidelines for developers who want to contribute to the project.

## Contributor License Agreement

By submitting a Contribution you agree to the terms of the [ElcanoTek Contributor License Agreement](CLA.md). The CLA grants ElcanoTek a perpetual, worldwide right to use, modify, commercialize, and relicense your Contribution in any manner. If you do not agree to those terms, do not submit Contributions.

## Development Environment

Victoria is distributed as a container image and contributors are encouraged to
develop, lint, and test inside that environment. Podman is the only hard
requirement.

### 1. Install and validate Podman

1. Install Podman (or Podman Desktop) for your platform. The quickest path for
   macOS and Windows is [podman.io](https://podman.io); Linux users should rely
   on their distribution packages.
2. Confirm Podman is working:

   ```bash
   podman --version
   ```

### 2. Provision the shared workspace

Victoria mounts `~/Victoria` from the host into the container to share
configuration, credentials, and cached data. Create it once and reuse it for
every run:

```bash
mkdir -p ~/Victoria
```

On Windows PowerShell use:

```powershell
New-Item -ItemType Directory -Path "$env:USERPROFILE/Victoria" -Force
```

### 3. Build the development container

Contributors are expected to build the Podman image locally. From the
repository root run:

```bash
podman build -t victoria-terminal .
```

Rebuild any time you change dependencies or modify the `Containerfile`.

> [!TIP]
> If you need a quicker bootstrap while investigating an issue, you can still
> pull the published image via `podman pull
> ghcr.io/elcanotek/victoria-terminal:latest`. Replace the tag with
> `latest-arm64` on Apple Silicon.

### 4. Run the development container

Use the locally built image for day-to-day development. Mount the shared
workspace and optionally pass arguments after `--` to reach the entrypoint:

```bash
podman run --rm -it \
  -v ~/Victoria:/root/Victoria \
  victoria-terminal

# Run the automated formatting and lint checks
podman run --rm -it \
  -v ~/Victoria:/root/Victoria \
  victoria-terminal -- nox -s lint

# Run the pytest suite
podman run --rm -it \
  -v ~/Victoria:/root/Victoria \
  victoria-terminal -- nox -s tests
```

> [!TIP]
> Append `-- --reconfigure --skip-launch` to trigger the configuration wizard
> without launching the terminal UI. Windows users should keep the command on a
> single line and use `$env:USERPROFILE/Victoria` for the volume mount.

Both commands reuse the mounted workspace so cached configuration and shared
credentials remain available.

### 5. Optional: iterate outside the container

If you need to experiment with dependencies before baking them into the image,
work from a local virtual environment and rebuild as needed:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# make local changes, then rebuild the container
podman build -t victoria-terminal .
```

## Code Quality & Linting

Victoria follows Python best practices with automated code formatting and linting. The project uses:

- **[Black](https://black.readthedocs.io/)**: Code formatter for consistent style
- **[isort](https://pycqa.github.io/isort/)**: Import statement organizer
- **[flake8](https://flake8.pycqa.org/)**: Linter for PEP8 compliance and code quality

### Running Linting Tools

The repository ships with a [Nox](https://nox.thea.codes/) configuration that
invokes Black, isort, and flake8 with the project's settings (100 character line
length, Black import ordering, and PEP 8 checks). When using the container the
tools are already available. If you are iterating in a local virtual
environment, install the dependencies from `requirements.txt` first.

```bash
podman run --rm -it \
  -v ~/Victoria:/root/Victoria \
  victoria-terminal -- nox -s lint
```

Nox manages its own virtual environments by default, so these commands can be
executed from a clean checkout without activating `.venv` first.

## Testing

The test suite is located in the `tests/` directory and uses `pytest`.

To run the tests:

1.  **Set up your environment**: Either work inside the Podman container (recommended) or install the development dependencies from `requirements.txt` in your local virtual environment.
2.  **Run the suite**: Execute the tests through Nox, which installs
    dependencies and enables coverage measurement out of the box:
    ```bash
    podman run --rm -it \
      -v ~/Victoria:/root/Victoria \
      victoria-terminal -- nox -s tests
    ```

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
