# AGENTS.md

This document provides instructions and guidelines for AI agents working on the Victoria project. Victoria is a fleet of AI-powered applications designed to help programmatic advertising traders analyze data and optimize campaigns.

## Project Overview

Victoria connects to advertising data sources (CSVs, Excel files, Snowflake) and allows users to ask powerful questions in natural language. The project is built with a modular architecture, with each component designed to be independent and flexible.

**Core Technologies:**
- Python 3.8+
- `crush` as the AI coding agent
- `rich` for terminal UI
- `colorama` for cross-platform terminal colors

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

Victoria now provides a Podman container image that ships with Python and the `crush` CLI pre-installed. Developers can build it locally with `podman build -t victoria-terminal .` or run the published image from `ghcr.io/elcanotek/victoria-terminal:latest`. Mount `~/Victoria` into the container to reuse configuration created by the entry point.

```bash
podman run --rm -it \
  --user 0 \
  --userns=keep-id \
  -e VICTORIA_HOME=/workspace/Victoria \
  -v ~/Victoria:/workspace/Victoria \
  ghcr.io/elcanotek/victoria-terminal:latest
```

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

## The Victoria Fleet

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

3.  **Manual Workflow**: A manual test workflow can also be triggered on GitHub Actions for additional verification:
    ```bash
    gh workflow run manual-tests.yml
    ```

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
- **Code Review**: All pull requests must be reviewed and approved by at least one other team member.


