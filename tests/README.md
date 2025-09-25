# Victoria Testing

The Victoria terminal has been simplified to rely on a single entry point. The
current test suite focuses on the essential behaviours that keep that workflow
reliable without relying on extensive mocking.

## Running the Tests

Use `nox` to create an isolated virtual environment and execute the suite:

```bash
nox -s tests
```

The session installs dependencies from `requirements.txt`. To iterate quickly
inside an existing environment you can still run:

```bash
pytest
```

## Covered Scenarios

- Validating `.env` parsing helpers.
- Verifying configuration files are created from bundled templates when
  variables are substituted.
- Exercising basic command-line parsing behaviour.
- Deferring complex lifecycle checks to integration tests.
