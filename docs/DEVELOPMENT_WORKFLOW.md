# Development Workflow

Use this guide when you need to modify Victoria or run the development image locally.

## Build from Source

1. Clone the repository.
2. Create the shared host workspace if you have not already done so:
   ```bash
   mkdir -p ~/Victoria
   ```
   ```powershell
   New-Item -ItemType Directory -Path "$env:USERPROFILE/Victoria" -Force
   ```
3. Build the development image:
   ```bash
   podman build -t victoria-terminal .
   ```

## Run the Development Image

**Linux or macOS (Bash):**
```bash
podman run --rm -it \
  -v ~/Victoria:/workspace/Victoria:z \
  victoria-terminal
```

**Windows (PowerShell):**
```powershell
podman run --rm -it `
  -v "$env:USERPROFILE/Victoria:/workspace/Victoria" `
  victoria-terminal
```

The entrypoint provisions a writable home directory, syncs configuration from your mounted workspace, and launches the terminal UI.

## Automation and Tests

Victoria standardizes on Nox sessions for linting and tests. Run them through Podman for parity with CI.

**Linting**
```bash
podman run --rm -it \
  -v ~/Victoria:/workspace/Victoria \
  victoria-terminal -- nox -s lint
```

```powershell
podman run --rm -it -v "$env:USERPROFILE/Victoria:/workspace/Victoria" victoria-terminal -- nox -s lint
```

**Tests**
```bash
podman run --rm -it \
  -v ~/Victoria:/workspace/Victoria \
  victoria-terminal -- nox -s tests
```

```powershell
podman run --rm -it -v "$env:USERPROFILE/Victoria:/workspace/Victoria" victoria-terminal -- nox -s tests
```

To target specific pytest paths or keywords, append them after `-- pytest`, for example:
```bash
podman run --rm -it \
  -v ~/Victoria:/workspace/Victoria \
  victoria-terminal -- pytest tests/test_configurator.py -k "happy_path"
```

## Interactive Debugging

Open a shell inside the image when you need to inspect the runtime environment:
```bash
podman run --rm -it \
  -v ~/Victoria:/workspace/Victoria \
  victoria-terminal bash
```
```powershell
podman run --rm -it -v "$env:USERPROFILE/Victoria:/workspace/Victoria" victoria-terminal bash
```

Inside the shell you can run `env | sort`, inspect `/workspace/Victoria`, or execute `nox` and `pytest` directly.

## GitHub Actions

Two workflows can be triggered manually from the **Actions** tab or via the GitHub CLI:

- `manual-tests.yml` – Runs the test suite.
  ```bash
  gh workflow run manual-tests.yml
  ```
- `container-image.yml` – Builds and publishes the Podman image.
  ```bash
  gh workflow run container-image.yml
  ```
