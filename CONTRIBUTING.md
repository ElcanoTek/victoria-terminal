# Contributing to Victoria

First off, thank you for considering contributing to Victoria! We welcome all contributions, from bug reports to new features.

This document provides guidelines for developers who want to contribute to the project.

## Development Environment

We recommend using a virtual environment to isolate project dependencies.

### Setup with `venv`

1.  **Prerequisites**:
    - Python 3.8+

2.  **Setup**:
    ```bash
    # Clone the repository
    git clone https://github.com/elcanotek/victoria.git
    cd victoria

    # Create and activate a virtual environment
    python -m venv .venv
    source .venv/bin/activate  # On macOS/Linux
    # .venv\Scripts\activate  # On Windows

    # Install development dependencies
    pip install -r requirements.txt
    ```

## Code Quality & Linting

Victoria follows Python best practices with automated code formatting and linting. The project uses:

- **[Black](https://black.readthedocs.io/)**: Code formatter for consistent style
- **[isort](https://pycqa.github.io/isort/)**: Import statement organizer
- **[flake8](https://flake8.pycqa.org/)**: Linter for PEP8 compliance and code quality

### Running Linting Tools

The repository ships with a [Nox](https://nox.thea.codes/) configuration that
invokes Black, isort, and flake8 with the project's settings (100 character line
length, Black import ordering, and PEP 8 checks). After installing the
dependencies listed in `requirements.txt`, run:

```bash
nox -s lint
```

Nox manages its own virtual environments by default so you can execute the
command from a clean checkout without activating `.venv` first.

## Testing

The test suite is located in the `tests/` directory and uses `pytest`.

To run the tests:

1.  **Set up your environment**: Ensure you have installed the development dependencies from `requirements.txt`.
2.  **Run the suite**: Execute the tests through Nox, which installs
    dependencies and enables coverage measurement out of the box:
    ```bash
    nox -s tests
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
