# AGENTS.md

This document provides instructions and guidelines for AI agents working on the Victoria Terminal project. Victoria Terminal is Elcano's container-first interface for analyzing programmatic advertising data with help from AI copilots.

## Project Overview

Victoria connects to advertising data sources (CSVs, Excel files, Snowflake) and allows users to ask powerful questions in natural language. The project is built with a modular architecture, with each component designed to be independent and flexible.

**Core Technologies:**
- Python 3.8+
- `crush` as the AI coding agent
- `rich` for terminal UI

## Core Philosophy

Victoria follows a "tires, not the car" philosophy. We build the specialized components that connect general-purpose AI agents to advertising data and workflows, while leveraging existing open-source projects for the foundational infrastructure.

- **Avoid Custom Model Lock-in**: We do not fine-tune custom models. We use the best available AI technologies as they emerge.
- **Humans in the Loop**: Victoria is an intelligent assistant, not a replacement for human expertise.
- **Rapid Evolution**: The architecture is designed for adaptability and quick iteration.

## Development Environment

To get started with Victoria development, you'll need to set up a Python environment and install the necessary dependencies.

### Local Development Setup (Recommended)

For local development, we strongly recommend using a virtual environment to isolate project dependencies. This prevents conflicts with other Python projects on your system and keeps Victoria's tooling self-contained.

#### Using `pip` and `venv`

1.  **Prerequisites**:
    - Python 3.8+

2.  **Setup**:
    ```bash
    # Clone the repository
    git clone https://github.com/ElcanoTek/victoria-terminal.git
    # Or use SSH
    git clone git@github.com:ElcanoTek/victoria-terminal.git
    cd victoria-terminal

    # Create and activate a virtual environment
    python -m venv .venv
    source .venv/bin/activate  # On Fedora Linux
    # .venv\Scripts\activate  # On Windows

    # Install development dependencies
    pip install -r requirements.txt
    ```

### Podman Containers

Victoria Terminal ships as a Podman container image that includes Python and the `crush` CLI. Developers can build it locally with `podman build -t victoria-terminal .` or run the published image from `ghcr.io/elcanotek/victoria-terminal:latest`. Mount `~/Victoria` into the container to reuse configuration created by the entry point.

```bash
podman run --rm -it -v ~/Victoria:/workspace/Victoria:z ghcr.io/elcanotek/victoria-terminal:latest
```

Windows PowerShell users should keep the command on a single line and substitute the host path syntax:

```powershell
podman run --rm -it -v "$env:USERPROFILE/Victoria:/workspace/Victoria" ghcr.io/elcanotek/victoria-terminal:latest
```

### Container Runtime Philosophy

The container setup for Victoria is intentionally designed to balance reliability with developer productivity and cross-platform compatibility. Agents working on this project should adhere to the following principles and avoid making changes that contradict them:

-   **Prefer the Default Podman Security Profile**: The streamlined `podman run` command above intentionally omits additional security flags that previously caused permission issues on macOS, Linux, and Windows hosts. Do not reintroduce `--userns=keep-id`, `--security-opt`, or `--cap-drop` defaults unless a regression is demonstrated and thoroughly tested across platforms.
-   **Root-Based Image**: The container image runs as root by default to guarantee mounted volumes remain writable regardless of host UID/GID mappings. Avoid adding a `USER` directive or runtime UID switching logic to the `Containerfile` or entrypoint.
-   **Two-Stage Build Layout**: The `Containerfile` now uses a dedicated builder stage to compile the `crush` binary with Go and a lean runtime stage that carries Python, Helix, and the application code. Keep this separation intact so the final image stays lightweight while still delivering the compiled tooling we depend on. Only adjust the stage boundaries if a regression or dependency change makes it unavoidable.
-   **"Always on Latest" Update Strategy**: The base image is intentionally set to `fedora:latest`. This ensures the container always benefits from the latest security patches. Builds are versioned and stored in the GitHub Container Registry, allowing for easy rollbacks if an update causes issues. Do not pin the base image to a specific version, as this would prevent automatic security updates.

### Dependencies Explained

- `requirements.txt`: Contains the dependencies required to run and develop the Victoria applications, including testing and formatting tools.

## Configuration & Secrets

- Environment variables are managed in a `.env` file located in `~/Victoria/`.
- The application automatically loads variables from this file at startup.
- **Example `.env` file**:
  ```
  OPENROUTER_API_KEY="sk-or-v1-..."
  SNOWFLAKE_ACCOUNT="your_account"
  SNOWFLAKE_USER="your_user"
  SNOWFLAKE_PASSWORD="your_password"
  ```

## Key Components

- **Victoria Entry Point (`victoria_terminal.py`)**: Container-aware bootstrapper that synchronizes configuration from `~/Victoria`, guides first-run setup when needed, and launches the terminal experience end-to-end.

## Testing Instructions

The test suite is located in the `tests/` directory and uses `pytest`.

To run the tests:

1.  **Set up your environment**: Ensure you have installed the development dependencies from `requirements.txt` as described in the "Development Environment" section. If you are using a virtual environment, make sure it is activated.

2.  **Run `pytest`**: From the root of the repository, run the following command:
    ```bash
    pytest
    ```
    This command will automatically discover and execute all tests in the `tests/` directory.

3.  **CI Parity**: GitHub Actions runs the same `pytest` suite through the `ci.yml` workflow. You can mimic the automated lint-and-test pipeline locally with `nox -s lint tests` if you prefer matching the CI environment.

## Code Style & Conventions

- Follow PEP 8 for Python code style.
- Use `black` for code formatting.
- Use `isort` for import sorting.
- Use type hints for all function signatures.
- Use `rich` for all terminal output.
- **License Notes (Python):** When editing any `.py` file that includes a `License Notes: YYYY-MM-DD` line in its header comment, update that date to match the day of your change (ISO `YYYY-MM-DD`).
- **Victoria manifest header:** Ensure `VICTORIA.md` begins with the standard license header comment block. Whenever you edit `VICTORIA.md`, refresh the `License Notes` line in that header to the current edit date (ISO `YYYY-MM-DD`).

## Data Analysis Principles

- **Prime Directive**: When computing ratio metrics (CPC, CTR, etc.), **aggregate numerators and denominators first**, then divide. **Never filter out rows where the denominator is zero**.
- **Safe Division**: Use `NULLIF` or `TRY_DIVIDE` to avoid division by zero errors.
- **Data Inspection**: Use `LIMIT 5` to inspect the structure of new data sources before performing a full analysis.

## Pull Request Guidelines

- **Title Format**: `[Component] Brief description of changes` (e.g., `[VictoriaTerminal] Add support for new data source`).
- **Description**: Provide a clear and concise description of the changes.
- **Testing**: Ensure all tests pass before submitting a pull request.
- **Linting**: Run `nox -s lint` and resolve any issues before creating a pull request.
- **Code Review**: All pull requests must be reviewed and approved by at least one other team member.


