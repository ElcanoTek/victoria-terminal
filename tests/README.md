# Victoria Testing

The Victoria terminal has been simplified to rely on a single entry point. The
current test suite focuses on the essential behaviours that keep that workflow
reliable.

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

- Validating `.env` parsing and serialization helpers.
- Verifying configuration files are created from bundled templates when
  variables are substituted.
- Ensuring shared configuration folders synchronise bundled documentation.
- Confirming the entry point honours the `--skip-launch` flag without invoking
  external binaries.
