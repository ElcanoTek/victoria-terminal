# Contributing to Victoria

First off, thank you for considering contributing to Victoria! We welcome all contributions, from bug reports to new features.

This document provides guidelines for developers who want to contribute to the project.

## Development Environment

We recommend using a virtual environment to isolate project dependencies.

### Using `uv` (Recommended)

1.  **Prerequisites**:
    - Python 3.8+
    - `uv` installed (`pip install uv`)

2.  **Setup**:
    ```bash
    # Clone the repository
    git clone https://github.com/elcanotek/victoria.git
    cd victoria

    # Create and activate a virtual environment
    uv venv
    source .venv/bin/activate  # On macOS/Linux
    # .venv\Scripts\activate  # On Windows

    # Install development dependencies
    uv pip install -r requirements-dev.txt
    ```

### Using `pip` and `venv`

1.  **Prerequisites**:
    - Python 3.8+

2.  **Setup**:
    ```bash
    # Create and activate a virtual environment
    python -m venv .venv
    source .venv/bin/activate  # On macOS/Linux
    # .venv\Scripts\activate  # On Windows

    # Install development dependencies
    pip install -r requirements-dev.txt
    ```

## Code Quality & Linting

Victoria follows Python best practices with automated code formatting and linting. The project uses:

- **[Black](https://black.readthedocs.io/)**: Code formatter for consistent style
- **[isort](https://pycqa.github.io/isort/)**: Import statement organizer
- **[flake8](https://flake8.pycqa.org/)**: Linter for PEP8 compliance and code quality

### Running Linting Tools

After installing development dependencies, you can run the linting tools:

```bash
# Format code with Black (88 character line length)
black .

# Sort imports with isort
isort .

# Check for linting issues with flake8
flake8 .
```

### Pre-commit Workflow

For the best development experience, run all linting tools before committing:

```bash
# Format and lint all code
black . && isort . && flake8 .
```

## Testing

The test suite is located in the `tests/` directory and uses `pytest`.

To run the tests:

1.  **Set up your environment**: Ensure you have installed the development dependencies from `requirements-dev.txt`.
2.  **Run `pytest`**: From the root of the repository, run the following command:
    ```bash
    pytest
    ```

## On-Demand GitHub Actions

Two workflows in [`.github/workflows`](.github/workflows) can be run manually from the **Actions** tab or via the GitHub CLI.

* **Manual Tests** ([`manual-tests.yml`](.github/workflows/manual-tests.yml)) — runs the test suite.
  ```bash
  gh workflow run manual-tests.yml
  ```

* **Build and Release** ([`build-release.yml`](.github/workflows/build-release.yml)) — executes the test suite and then calls the packaging scripts to produce application bundles for macOS, Windows, and Linux.
  ```bash
  gh workflow run build-release.yml
  ```

## Pull Request Guidelines

- **Title Format**: `[Component] Brief description of changes` (e.g., `[VictoriaTerminal] Add support for new data source`).
- **Description**: Provide a clear and concise description of the changes.
- **Testing**: Ensure all tests pass before submitting a pull request.
- **Code Review**: All pull requests must be reviewed and approved by at least one other team member.
