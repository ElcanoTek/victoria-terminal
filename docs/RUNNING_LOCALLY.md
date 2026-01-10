# Running Victoria (Pre-Built Images)

Use this guide when you want to run the published Victoria Terminal image without building locally.

## Create the Shared Workspace

Victoria stores configuration and outputs in a shared folder mounted into the container.

- **macOS / Linux**
  ```bash
  mkdir -p ~/Victoria
  ```
- **Windows (PowerShell)**
  ```powershell
  New-Item -ItemType Directory -Path "$env:USERPROFILE/Victoria" -Force
  ```
- **Windows (Command Prompt)**
  ```cmd
  mkdir %USERPROFILE%\Victoria
  ```

## Pull and Run the Image

Check your Podman host architecture:

```bash
podman info --format '{{.Host.Arch}}'
```

| Platform | CPU architecture | Pull / update | Run |
| --- | --- | --- | --- |
| macOS or Linux (Intel/AMD) | `x86_64` | `podman pull ghcr.io/elcanotek/victoria-terminal:latest` | `podman run --rm -it -v ~/Victoria:/workspace/Victoria:z ghcr.io/elcanotek/victoria-terminal:latest` |
| macOS or Linux (Arm64) | `arm64` | `podman pull ghcr.io/elcanotek/victoria-terminal:latest-arm64` | `podman run --rm -it -v ~/Victoria:/workspace/Victoria:z ghcr.io/elcanotek/victoria-terminal:latest-arm64` |
| Windows PowerShell (Intel/AMD) | `x86_64` | `podman pull ghcr.io/elcanotek/victoria-terminal:latest` | `podman run --rm -it -v "$env:USERPROFILE/Victoria:/workspace/Victoria" ghcr.io/elcanotek/victoria-terminal:latest` |
| Windows PowerShell (Arm64) | `arm64` | `podman pull ghcr.io/elcanotek/victoria-terminal:latest-arm64` | `podman run --rm -it -v "$env:USERPROFILE/Victoria:/workspace/Victoria" ghcr.io/elcanotek/victoria-terminal:latest-arm64` |

Pass arguments after `--` so Podman stops parsing options:

```bash
podman run --rm -it -v ~/Victoria:/workspace/Victoria ghcr.io/elcanotek/victoria-terminal:latest -- --accept-license
```

Non-interactive runs with `--task` must also pass `--accept-license`.

## Configure First Run

The container reads environment variables from `~/Victoria/.env` or from `podman run -e KEY=value` overrides.

- If `.env` exists, Victoria loads it and launches immediately.
- If runtime variables exist without `.env`, Victoria uses them for the current run.
- If required values are missing, Victoria reports which integrations are disabled.

### Managing the `.env` file

Provide two artifacts to your users:

1. A commented template (use `example.env` as a starting point).
2. A deployment-ready file with live credentials.

```dotenv
OPENROUTER_API_KEY="sk-or-v1-live-example-1234567890abcd"
# Add API keys for any MCP servers you configure
# YOUR_SERVICE_API_KEY="your-api-key-here"
```

### Passing ephemeral secrets

You can inject credentials at launch instead of distributing a shared `.env` file:

```bash
podman run --rm \
  --cap-drop all \
  -e OPENROUTER_API_KEY="sk-or-v1-live-example-1234567890abcd" \
  -e YOUR_SERVICE_API_KEY="your-api-key-here" \
  ghcr.io/elcanotek/victoria-terminal:latest \
  --accept-license \
  --task "Analyze this week's campaign performance and summarize key metrics"
```

> Dropping all capabilities prevents the container from writing to shared volumes. Omit `--cap-drop all` when you need to persist outputs back to `~/Victoria`.

## Workspace Layout

- `~/Victoria/.env` – API keys and other secrets read on startup.
- `~/Victoria/.config/victoria/crush.json` – Generated Crush configuration.
- `~/Victoria` – Input datasets, outputs, logs, and generated manifests.
