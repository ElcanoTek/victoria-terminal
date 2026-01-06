# Remote Runner (Host Shim)

The Remote Runner is a host-side component that manages Victoria Terminal container execution in coordination with the [All-Time Quarterback](https://github.com/ElcanoTek/all-time-quarterback) orchestrator.

## Overview

The Remote Runner runs **outside** the container on the host OS (bare metal or VM) and handles:

- Receiving task assignments from the orchestrator
- Launching Victoria Terminal containers with appropriate configuration
- Managing container lifecycle
- Reporting status back to the orchestrator

## Operating Modes

### Push Mode (Cloud/Static IP)

For servers with static IP addresses, the runner exposes an HTTP API that the orchestrator can call directly to trigger task execution.

```bash
python -m remote_runner push \
    --orchestrator-url http://quarterback.example.com:8000 \
    --api-key your-node-api-key \
    --port 8080
```

**Endpoints:**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/run` | POST | Start a new task |
| `/status` | GET | Get current status |

### Pull Mode (Local/Dynamic IP)

For workstations or edge devices with dynamic IPs, the runner polls the orchestrator for pending tasks.

```bash
python -m remote_runner pull \
    --orchestrator-url http://quarterback.example.com:8000 \
    --api-key your-node-api-key \
    --poll-interval 30
```

## Installation

### Prerequisites

- Python 3.10 or later
- Podman or Docker
- Network access to the All-Time Quarterback orchestrator

### Install Dependencies

```bash
# For push mode
pip install flask

# For pull mode
pip install httpx

# For both modes
pip install flask httpx
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
ExecStart=/usr/bin/python3 -m remote_runner pull \
    --orchestrator-url http://quarterback.example.com:8000 \
    --api-key your-node-api-key
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

#### OpenBSD (rc.d)

Create `/etc/rc.d/victoria_runner`:

```sh
#!/bin/ksh

daemon="/usr/local/bin/python3"
daemon_flags="-m remote_runner pull --orchestrator-url http://quarterback.example.com:8000 --api-key your-node-api-key"
daemon_user="victoria"

. /etc/rc.d/rc.subr

rc_bg=YES
rc_cmd $1
```

Then:

```bash
chmod +x /etc/rc.d/victoria_runner
rcctl enable victoria_runner
rcctl start victoria_runner
```

## Configuration

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--orchestrator-url` | URL of the quarterback orchestrator | Required |
| `--api-key` | Node API key for authentication | Required |
| `--container-image` | Victoria Terminal container image | `ghcr.io/elcanotek/victoria-terminal:latest` |
| `--victoria-home` | Path to Victoria home directory | `~/Victoria` |
| `--env-file` | Path to .env file for container | None |
| `--container-runtime` | Container runtime (podman/docker/auto) | `auto` |

### Push Mode Options

| Option | Description | Default |
|--------|-------------|---------|
| `--host` | Host to bind to | `0.0.0.0` |
| `--port` | Port to listen on | `8080` |

### Pull Mode Options

| Option | Description | Default |
|--------|-------------|---------|
| `--poll-interval` | Polling interval in seconds | `30` |

## Environment Variables

The runner passes these environment variables to the container:

| Variable | Description |
|----------|-------------|
| `ORCHESTRATOR_URL` | URL for MCP status reporting |
| `JOB_ID` | Unique task identifier |

Additional variables can be passed via the `--env-file` option.

## Security Considerations

1. **API Key Protection**: Keep your node API key secure. It authenticates your node with the orchestrator.

2. **Network Security**: In push mode, consider using a reverse proxy with TLS termination.

3. **Container Isolation**: The runner uses standard container isolation. Ensure your container runtime is properly configured.

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

### Authentication Failed

```
Authentication failed - check node API key
```

Verify your API key matches the one assigned during node registration with the orchestrator.

### Connection Refused

```
Error polling for tasks: Connection refused
```

Check that:
1. The orchestrator URL is correct
2. The orchestrator is running
3. Network/firewall allows the connection
