# Victoria Script Testing

This repository includes comprehensive tests for the `victoria.py` starter script to ensure it works correctly across different platforms and terminal environments.

## Test Coverage

### Automated Testing (GitHub Actions)

The GitHub Actions workflow (`.github/workflows/test-victoria.yml`) automatically tests the script on:

- **Operating Systems**: Ubuntu (Linux), Windows, macOS
- **Python Version**: Latest stable Python (3.x)
- **Terminal Environments**: Various TERM settings, PowerShell (Windows), Bash (Unix)
- **Locale Settings**: UTF-8, C locale, and others

### Test Categories

1. **Import Tests**: Verifies all required Python modules are available
2. **Syntax Tests**: Ensures the script has valid Python syntax
3. **Terminal Capability Detection**: Tests cross-platform terminal feature detection
4. **Cross-Platform Compatibility**: Validates file operations and platform detection
5. **Environment Variable Handling**: Tests environment variable access and manipulation
6. **Script Execution**: Verifies the script runs without hanging in different environments
7. **Unicode Handling**: Tests emoji and Unicode character support
8. **JSON Operations**: Validates JSON parsing and file I/O operations

### Running Tests Locally

All test scripts now reside in the `tests/` directory. To run the full test suite:

```bash
pytest tests/test_victoria.py tests/test_non_interactive.py
```

Or run the scripts directly:

```bash
python tests/test_victoria.py
python tests/test_non_interactive.py
```

### Test Script Features

- **Cross-Platform**: Works on Windows, macOS, and Linux
- **No Dependencies**: Uses only Python standard library modules
- **Comprehensive Coverage**: Tests all major functionality without requiring external services
- **Graceful Degradation**: Tests that the script handles different terminal capabilities appropriately
- **Non-Destructive**: All tests clean up after themselves

### GitHub Actions Matrix

The CI pipeline tests multiple combinations:

- **Linux**: All Python versions (3.8-3.12)
- **Windows**: Python 3.10, 3.11, 3.12 (reduced matrix for efficiency)
- **macOS**: Python 3.10, 3.11, 3.12 (reduced matrix for efficiency)

### Terminal Environment Testing

The workflow specifically tests:

- No TERM variable set
- TERM=dumb (basic terminal)
- TERM=xterm-256color (full-featured terminal)
- Different shells (bash, PowerShell, CMD on Windows)
- Various locale settings (UTF-8, C locale)
- Debug mode enabled

### Expected Behavior

The `victoria.py` script is designed to:

- Display a fancy banner with Unicode characters and emojis when supported
- Gracefully degrade to ASCII alternatives on basic terminals
- Handle user interruption (Ctrl+C) gracefully
- Prompt for user input and handle different response scenarios
- Work without requiring external dependencies or network access for basic functionality

### Continuous Integration

Tests run automatically on:

- Every push to `main` or `develop` branches
- Every pull request to `main` or `develop` branches
- Manual workflow dispatch

All tests must pass before code can be merged, ensuring the script remains compatible across all supported platforms and environments.