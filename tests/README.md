# Victoria Testing

The Victoria terminal has been simplified to rely on a single entry point. The
current test suite focuses on the essential behaviours that keep that workflow
reliable.

## Running the Tests

Execute the test suite from the project root:

```bash
pytest
```

## Covered Scenarios

- Validating `.env` parsing and serialization helpers.
- Ensuring shared configuration folders are synchronised correctly.
- Verifying Crush configuration generation performs environment substitution.
- Confirming the entry point refuses to proceed when configuration is missing in
  non-interactive mode.
