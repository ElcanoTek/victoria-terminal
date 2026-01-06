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
    --registration-token your-registration-token \
    --name "prod-server-1" \
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
    --registration-token your-registration-token \
    --name "client-acme-workstation-1" \
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
    --registration-token your-registration-token \
    --name "client-acme-runner-1"
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
daemon_flags="-m remote_runner pull --orchestrator-url http://quarterback.example.com:8000 --registration-token your-registration-token --name client-acme-runner-1"
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
| `--name` | Unique name for task targeting (supports wildcards) | System hostname |
| `--orchestrator-url` | URL of the quarterback orchestrator | Required |
| `--registration-token` | Token for registering with the orchestrator | Required |
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

3. **Network Security**: In push mode, consider using a reverse proxy with TLS termination.

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
3. Network/firewall allows the connection


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
   python -m remote_runner pull --name "client-acme-runner-1" ...
   python -m remote_runner pull --name "client-acme-runner-2" ...
   ```

2. **Create tasks targeting that client:**
   ```bash
   curl -X POST http://quarterback.example.com:8000/tasks \
     -H "X-API-Key: $ADMIN_API_KEY" \
     -d '{"prompt": "Analyze data", "target_node_name": "client-acme-*"}'
   ```

3. **Only runners matching `client-acme-*` will pick up the task.**
