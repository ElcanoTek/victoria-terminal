# Victoria Testing

This directory contains the automated tests for the Victoria project, ensuring its components are reliable and function correctly across different scenarios.

## Testing Framework

The test suite is built using the [pytest](https://docs.pytest.org/) framework.

## How to Run Tests

To run the full suite of tests, navigate to the project's root directory and execute the following command:

```bash
pytest
```

This command will automatically discover and run all the tests located in the `tests/` directory.

## Test Coverage

The tests are organized into several modules, each focusing on a specific part of the application's functionality:

### Configuration Generation (`test_config_generation.py`)

- **Snapshot Testing**: Verifies that the `crush.json` configuration file is generated correctly for different scenarios.
- **Scenarios Covered**:
  - Local file analysis only.
  - Integration with Snowflake.
  - Usage of a local language model (e.g., LM Studio).
  - A combination of Snowflake and a local model.
- **File Loading**: Ensures that the application correctly loads tool configurations.

### Environment Handling

- **`.env` File Management (`test_dotenv.py`)**: Tests the loading and parsing of `.env` files.
- **Environment Utilities (`test_env_utils.py`)**: Verifies helper functions that interact with environment variables.

### Non-Interactive Mode (`test_non_interactive.py`)

- Tests the application's ability to run non-interactively, using command-line arguments to bypass interactive prompts for course selection and model provider.

### Preflight Checks (`test_preflight.py`)

- Ensures that the system's preflight checks work as expected. This includes verifying the presence of required command-line tools (like `crush`) and API keys.

### System and User Interaction

- **System Interaction (`test_system_interaction.py`)**: Mocks and tests interactions with the operating system, such as opening file explorers.
- **User Interaction (`test_user_interaction.py`)**: Tests the interactive menus and prompts presented to the user.

## Continuous Integration

The tests are designed to be run in a CI/CD pipeline to ensure that any changes to the codebase do not introduce regressions. All tests must pass before code is merged.
