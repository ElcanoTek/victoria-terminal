# Remote Runner (Host Shim)

The Remote Runner is a host-side component that manages Victoria Terminal container execution in coordination with the [All-Time Quarterback](https://github.com/ElcanoTek/all-time-quarterback) orchestrator.

## Overview

The Remote Runner runs **outside** the container on the host OS (bare metal or VM) and handles:

- Polling the orchestrator for pending task assignments
- Launching Victoria Terminal containers with appropriate configuration
- Managing container lifecycle
- Reporting status back to the orchestrator

All communication uses **outbound HTTPS connections only**. Runners require no inbound ports, simplifying firewall configuration and improving security.

## Quick Start

```bash
python -m runner \
    --orchestrator-url https://quarterback.example.com \
    --registration-token your-registration-token \
    --name "prod-runner-01" \
    --poll-interval 30
```

## Installation

### Prerequisites

- Python 3.10 or later
- Podman or Docker
- Network access to the All-Time Quarterback orchestrator (outbound HTTPS)

### Install Dependencies

```bash
pip install httpx
```

### Running as a Service

#### Linux (systemd)

Create `/etc/systemd/system/victoria-runner.service`:

```ini
[Unit]
Description=Victoria Terminal Remote Runner
After=network.target

[Service]
Type=simple
User=victoria
WorkingDirectory=/home/victoria/victoria-terminal/remote-runner
ExecStart=/usr/bin/python3 -m runner \
    --orchestrator-url https://quarterback.example.com \
    --registration-token your-registration-token \
    --name "prod-runner-01"
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable victoria-runner
sudo systemctl start victoria-runner
```

## Configuration

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--name` | Unique name for task targeting (supports wildcards) | System hostname |
| `--orchestrator-url` | URL of the quarterback orchestrator | Required |
| `--registration-token` | Token for registering with the orchestrator | Required |
| `--poll-interval` | Polling interval in seconds | `30` |
| `--container-image` | Victoria Terminal container image | `ghcr.io/elcanotek/victoria-terminal:latest` |
| `--victoria-home` | Path to Victoria home directory | `~/Victoria` |
| `--env-file` | Path to .env file for container | None |
| `--container-runtime` | Container runtime (podman/docker/auto) | `auto` |

## Environment Variables

The runner passes these environment variables to the container:

| Variable | Description |
|----------|-------------|
| `ORCHESTRATOR_URL` | URL for MCP status reporting |
| `NODE_API_KEY` | API key for authenticating with the orchestrator |

Additional variables can be passed via the `--env-file` option.

## Security

### Authentication Flow

1. **Registration**: When the runner starts, it registers with the orchestrator using the `--registration-token`
2. **API Key Assignment**: The orchestrator validates the token and returns a unique Node API Key
3. **Subsequent Requests**: The runner uses this API key for all subsequent communication

### Security Considerations

1. **Registration Token Protection**: Keep your registration token secure. It allows new nodes to register with the orchestrator.

2. **Node API Key**: Automatically assigned during registration. Used for polling tasks and sending status updates.

3. **Outbound-Only Connections**: Runners only make outbound HTTPS requests to the orchestrator. No inbound ports need to be opened.

4. **Container Isolation**: The runner uses standard container isolation. Ensure your container runtime is properly configured.

## Troubleshooting

### Container Runtime Not Found

```
RuntimeError: No container runtime found. Install podman or docker.
```

Install Podman (recommended) or Docker:

```bash
# Fedora
sudo dnf install podman

# Debian/Ubuntu
sudo apt install podman
```

### Registration Failed

```
Registration failed - invalid registration token
```

Verify your `--registration-token` matches the `REGISTRATION_TOKEN` configured on the orchestrator.

```
Registration failed - orchestrator has registration disabled
```

The orchestrator doesn't have `REGISTRATION_TOKEN` set. Contact the orchestrator administrator.

### Connection Refused


```
Error polling for tasks: Connection refused
```

Check that:
1. The orchestrator URL is correct
2. The orchestrator is running
3. Network/firewall allows outbound HTTPS connections


## Node Naming and Task Targeting

The `--name` option assigns a unique identifier to your runner that the orchestrator uses for task targeting.

### Naming Convention

We recommend using a consistent naming convention:

```
{client}-{environment}-{role}-{number}
```

**Examples:**
- `client-acme-prod-1` - Acme's first production runner
- `client-acme-dev-1` - Acme's development runner
- `internal-gpu-1` - Internal GPU-enabled runner

### How Targeting Works

When a task is created with `target_node_name`, the orchestrator uses wildcard pattern matching:

| Task Target | Runner Name | Match? |
|-------------|-------------|--------|
| `client-acme-*` | `client-acme-prod-1` | ✅ Yes |
| `client-acme-*` | `client-acme-dev-2` | ✅ Yes |
| `client-acme-*` | `client-beta-prod-1` | ❌ No |
| `*-gpu-*` | `client-acme-gpu-1` | ✅ Yes |
| `prod-*` | `prod-server-1` | ✅ Yes |

### Client Isolation Example

To ensure a client's tasks only run on their dedicated runners:

1. **Start runners with client-specific names:**
   ```bash
   # On Client Acme's servers
   python -m runner --name "client-acme-runner-1" ...
   python -m runner --name "client-acme-runner-2" ...
   ```

2. **Create tasks targeting that client:**
   ```bash
   curl -X POST https://quarterback.example.com/tasks \
     -H "X-API-Key: $ADMIN_API_KEY" \
     -d '{"prompt": "Analyze data", "target_node_name": "client-acme-*"}'
   ```

3. **Only runners matching `client-acme-*` will pick up the task.**
