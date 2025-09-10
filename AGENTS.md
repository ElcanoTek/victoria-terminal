# AGENTS.md

This document provides instructions and guidelines for AI agents working on the Victoria project. Victoria is a fleet of AI-powered applications designed to help programmatic advertising traders analyze data and optimize campaigns.

## Project Overview

Victoria connects to advertising data sources (CSVs, Excel files, Snowflake) and allows users to ask powerful questions in natural language. The project is built with a modular architecture, with each component designed to be independent and flexible.

**Core Technologies:**
- Python 3.8+
- `uv` for package management
- `crush` as the AI coding agent
- `rich` for terminal UI
- `colorama` for cross-platform terminal colors

## Core Philosophy

Victoria follows a "tires, not the car" philosophy. We build the specialized components that connect general-purpose AI agents to advertising data and workflows, while leveraging existing open-source projects for the foundational infrastructure.

- **Avoid Custom Model Lock-in**: We do not fine-tune custom models. We use the best available AI technologies as they emerge.
- **Humans in the Loop**: Victoria is an intelligent assistant, not a replacement for human expertise.
- **Rapid Evolution**: The architecture is designed for adaptability and quick iteration.

## Development Environment Setup

To ensure a consistent development environment, please follow these steps carefully.

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/elcanotek/victoria.git
    cd victoria
    ```

2.  **Create a Virtual Environment**:
    We use `uv` for fast package management. Create a virtual environment by running:
    ```bash
    uv venv
    ```
    This will create a `.venv` directory in the project root.

3.  **Activate the Virtual Environment**:
    Before installing dependencies, you must activate the virtual environment. This ensures that `python`, `pip`, and other tools point to the versions inside the `.venv`.
    ```bash
    source .venv/bin/activate
    ```
    Your shell prompt should now be prefixed with `(.venv)`.

4.  **Install Dependencies**:
    Install all required development packages using:
    ```bash
    uv pip install -r requirements-dev.txt
    ```

## Testing and Code Style

The project includes a full test suite and code style checks to maintain quality.

### Running Tests

- The test suite is located in the `tests/` directory.
- With your virtual environment activated, run the tests using `pytest`:
  ```bash
  pytest
  ```
- A manual test workflow can also be triggered on GitHub Actions:
  ```bash
  gh workflow run manual-tests.yml
  ```

### Code Style & Conventions
- We use `black` for code formatting and `isort` for import sorting.
- The test suite automatically enforces these styles.
- To format your code locally before committing, run:
  ```bash
  black .
  isort .
  ```
- Use type hints for all function signatures.
- Use `rich` for all terminal output.

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

- **Victoria Configurator (`VictoriaConfigurator.py`)**: First-time setup tool that installs prerequisites and configures the environment.
- **Victoria Terminal (`VictoriaTerminal.py`)**: The main application for launching data analysis sessions with `crush`.
- **Victoria Browser (`VictoriaBrowser.py`)**: A utility to open the ElcanoTek website.

## Data Analysis Principles

- **Prime Directive**: When computing ratio metrics (CPC, CTR, etc.), **aggregate numerators and denominators first**, then divide. **Never filter out rows where the denominator is zero**.
- **Safe Division**: Use `NULLIF` or `TRY_DIVIDE` to avoid division by zero errors.
- **Data Inspection**: Use `LIMIT 5` to inspect the structure of new data sources before performing a full analysis.

## Pull Request Guidelines

- **Title Format**: `[Component] Brief description of changes` (e.g., `[VictoriaTerminal] Add support for new data source`).
- **Description**: Provide a clear and concise description of the changes.
- **Testing**: Ensure all tests pass before submitting a pull request.
- **Code Review**: All pull requests must be reviewed and approved by at least one other team member.


