# Victoria Testing

The Victoria terminal has been simplified to rely on a single entry point. The
current test suite focuses on the essential behaviours that keep that workflow
reliable without relying on extensive mocking.

## Running the Tests

Run tests inside the container for parity with CI:

```bash
podman run --rm -v ~/Victoria:/workspace/Victoria victoria-terminal -- pytest
```

Or use `nox` which installs the minimal test dependencies automatically:

```bash
podman run --rm -v ~/Victoria:/workspace/Victoria victoria-terminal -- nox -s tests
```

## Covered Scenarios

- Validating `.env` parsing helpers.
- Verifying configuration files are created from bundled templates when
  variables are substituted.
- Exercising basic command-line parsing behaviour.
- Deferring complex lifecycle checks to integration tests.
