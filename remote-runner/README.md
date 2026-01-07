# Remote Runner (Host Shim)

The Remote Runner is a host-side component that manages Victoria Terminal container execution in coordination with any compatible orchestrator.

## Overview

The Remote Runner runs **outside** the container on the host OS (bare metal or VM) and handles:

- Polling the orchestrator for pending task assignments
- Launching Victoria Terminal containers with appropriate configuration
- Managing container lifecycle
- Reporting status back to the orchestrator

All communication uses **outbound HTTPS connections only**. Runners require no inbound ports, simplifying firewall configuration and improving security.

## Orchestrator Compatibility

The Remote Runner is designed to work with **any orchestrator that implements the Victoria Terminal Orchestrator API**. This pull-based hub-and-spoke architecture provides several benefits:

- **Security**: Agents only make outbound connections; no inbound ports required
- **Firewall-friendly**: Works behind NAT and restrictive firewalls
- **Flexibility**: Use any orchestrator implementation that follows the spec

### OpenAPI Specification

The complete API specification is available in [`orchestrator-openapi.yaml`](./orchestrator-openapi.yaml). Any orchestrator that implements this specification will be compatible with Victoria Terminal agents.

You can use this spec to:
- Build your own orchestrator in any language
- Generate client/server code using OpenAPI tools
- Validate your orchestrator implementation

### Licensing Note

Victoria Terminal is licensed under the [Business Source License 1.1](../LICENSE) (BSL 1.1), which converts to GPL v3 after two years from each release. For production use, please contact ElcanoTek for commercial licensing options.

### Reference Implementation

ElcanoTek maintains a private reference orchestrator. If you're interested in a managed orchestrator solution, contact us at [elcanotek.com](https://elcanotek.com).

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
- Network access to a compatible orchestrator (outbound HTTPS)

### Step 1: Provision and Prepare the Instance

Deploy a **Fedora** or **Ubuntu** instance (Vultr, DGX Spark, or any Linux host) and create a non-root user for running the service.

```sh
# As root, create a user and grant sudo access
useradd -m -G wheel victoria  # Use 'sudo' group on Ubuntu
passwd victoria
# Log in as the `victoria` user
```

### Step 2: Install Dependencies

Install Podman, Python, and other necessary tools.

```sh
# Fedora
sudo dnf install -y podman python3 python3-pip git

# Ubuntu
sudo apt install -y podman python3 python3-pip git
```

### Step 3: Install the Remote Runner

The remote runner is part of the `victoria-terminal` repository.

```sh
# Clone the repository
git clone https://github.com/ElcanoTek/victoria-terminal.git
cd victoria-terminal/remote-runner

# Install Python dependencies
pip install httpx
```

### Step 4: Configure and Run as a systemd Service

Running the remote runner as a `systemd` service ensures it starts on boot and restarts if it fails.

Create a service file:

```sh
sudo vi /etc/systemd/system/victoria-runner.service
```

Paste the following content into the file. **Replace the placeholder values** with your actual Orchestrator URL, Registration Token, and a unique name for this runner.

```ini
[Unit]
Description=Victoria Terminal Remote Runner
After=network.target

[Service]
Type=simple
User=victoria
WorkingDirectory=/home/victoria/victoria-terminal/remote-runner
ExecStart=/usr/bin/python3 -m runner \
    --orchestrator-url https://<your-orchestrator-domain> \
    --registration-token <your-registration-token> \
    --name "prod-runner-01" \
    --poll-interval 30
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```sh
sudo systemctl daemon-reload
sudo systemctl enable victoria-runner.service
sudo systemctl start victoria-runner.service
# Check the status to ensure it is running
sudo systemctl status victoria-runner.service
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
| `--victoria-home` | Path to Victoria home directory (prompted when omitted in an interactive shell) | `~/Victoria` |
| `--env-file` | Path to .env file for container | None |
| `--container-runtime` | Container runtime (podman/docker/auto) | `auto` |

### Environment Variables

The runner passes these environment variables to the container:

| Variable | Description |
|----------|-------------|
| `ORCHESTRATOR_URL` | URL for MCP status reporting |
| `JOB_ID` | Unique identifier for the current task |
| `NODE_API_KEY` | API key for authenticating with the orchestrator |
| `TASK_FILES_DIR` | Path to task-specific files (only set if files were uploaded with the task) |

Additional variables can be passed via the `--env-file` option.

### Task Files

If you start the runner in an interactive shell without specifying `--victoria-home`,
it will prompt you for the shared Victoria folder on the host so downloaded task files
land in the same location that the container mounts with `-v`.

When a task includes uploaded files, the runner automatically downloads them before launching the container. Files are stored in a task-specific directory:

- **Host path**: `~/Victoria/tasks/{task_id}/files/`
- **Container path**: `/workspace/Victoria/tasks/{task_id}/files/`

The `TASK_FILES_DIR` environment variable is set to the container path, allowing the agent to easily locate and access the files.

## API Reference

This section documents all API endpoints used by the Remote Runner and the Status Reporter MCP server when communicating with the All-Time Quarterback orchestrator.

### Orchestrator API Endpoints

The following endpoints are provided by the All-Time Quarterback orchestrator. The Remote Runner and Status Reporter MCP use these endpoints to communicate task status and logs.

#### Node Management

| Method | Path | Description | Auth | Used By |
|--------|------|-------------|------|---------|
| `POST` | `/register` | Register a new node with the orchestrator | Registration Token | Remote Runner |
| `POST` | `/nodes/heartbeat` | Send node heartbeat with status | Node Key | Remote Runner |
| `GET` | `/nodes` | List all registered nodes | Admin | Dashboard |
| `GET` | `/nodes/{id}` | Get details for a specific node | Admin | Dashboard |
| `DELETE` | `/nodes/{id}` | Unregister a node | Admin | Dashboard |

#### Task Management

| Method | Path | Description | Auth | Used By |
|--------|------|-------------|------|---------|
| `GET` | `/tasks/pending` | Get the next pending task for this node | Node Key | Remote Runner |
| `POST` | `/tasks` | Create a new task | Admin or Scoped Key | External Systems |
| `GET` | `/tasks` | List all tasks | Admin | Dashboard |
| `GET` | `/tasks/{id}` | Get details for a specific task | Admin | Dashboard |
| `DELETE` | `/tasks/{id}` | Cancel a task | Admin | Dashboard |
| `POST` | `/tasks/cleanup` | Delete old task history | Admin | Maintenance |

#### Status and Logging

| Method | Path | Description | Auth | Used By |
|--------|------|-------------|------|---------|
| `POST` | `/status` | Report task status update | Node Key | Status Reporter MCP |
| `POST` | `/logs` | Submit Crush session logs | Node Key | Status Reporter MCP |
| `GET` | `/logs/{task_id}` | Retrieve logs for a task | Admin | Dashboard |

#### API Key Management

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| `POST` | `/keys` | Create a new API key | Admin |
| `GET` | `/keys` | List all API keys | Admin |
| `GET` | `/keys/{id}` | Get API key details | Admin |
| `POST` | `/keys/{id}/rotate` | Rotate an API key | Admin |
| `POST` | `/keys/{id}/revoke` | Revoke an API key | Admin |
| `DELETE` | `/keys/{id}` | Delete an API key | Admin |
| `GET` | `/keys/audit` | Get API key audit log | Admin |

#### System

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| `GET` | `/health` | Health check endpoint | None |
| `GET` | `/dashboard` | Dashboard web UI | None |
| `GET` | `/dashboard/stats` | Dashboard statistics | Admin |

### Status Reporter MCP Tools

The Status Reporter MCP server runs inside the Victoria container and provides tools for the LLM agent to report task progress. These tools communicate with the orchestrator via the `/status` and `/logs` endpoints.

| Tool | Description | Parameters |
|------|-------------|------------|
| `report_status` | Report current task status | `status` (running/analyzing/success/error), `message` (optional), `progress` (0-100, optional) |
| `report_started` | Convenience wrapper for task start | `message` (optional) |
| `report_complete` | Report successful completion (auto-submits logs) | `message` (optional), `submit_logs` (default: true) |
| `report_error` | Report task failure (auto-submits logs) | `error_message` (required), `submit_logs` (default: true) |
| `submit_crush_logs` | Manually submit Crush session logs | `session_id` (optional, defaults to latest) |
| `get_job_info` | Get current job configuration | None |

### Request/Response Examples

#### Node Registration

```bash
# Request
curl -X POST https://quarterback.example.com/register \
  -H "X-Registration-Token: your-registration-token" \
  -H "Content-Type: application/json" \
  -d '{
    "hostname": "server-01.example.com",
    "name": "prod-runner-01",
    "os_type": "fedora",
    "capabilities": [],
    "tags": {}
  }'

# Response
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "api_key": "assigned-node-api-key"
}
```

#### Poll for Tasks

```bash
# Request
curl -X GET https://quarterback.example.com/tasks/pending \
  -H "X-API-Key: your-node-api-key"

# Response (when task available)
{
  "task_id": "task-uuid-here",
  "prompt": "Analyze the sales data and generate a report",
  "orchestrator_url": "https://quarterback.example.com",
  "timeout_seconds": 3600
}
```

#### Report Status

```bash
# Request
curl -X POST https://quarterback.example.com/status \
  -H "X-API-Key: your-node-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "task-uuid-here",
    "status": "running",
    "message": "Processing data files",
    "progress": 45.0
  }'
```

#### Submit Logs

```bash
# Request
curl -X POST https://quarterback.example.com/logs \
  -H "X-API-Key: your-node-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "task-uuid-here",
    "session": {
      "id": "session-uuid",
      "title": "Task Session",
      "messages": [
        {"role": "user", "content": "...", "created_at": 1234567890},
        {"role": "assistant", "content": "...", "created_at": 1234567891}
      ]
    }
  }'
```

#### Create Task (Admin)

```bash
# Request
curl -X POST https://quarterback.example.com/tasks \
  -H "X-API-Key: your-admin-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Run security scan",
    "target_node_name": "client-acme-prod-*",
    "target_tags": {"env": "production"},
    "priority": 10
  }'
```

### Task Targeting

Tasks can be targeted to specific nodes using:

- **`target_node_id`**: Exact UUID match
- **`target_node_name`**: Wildcard pattern (e.g., `client-acme-*`)
- **`target_tags`**: Key-value tag matching

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

### Tasks Not Being Picked Up

Verify that the `target_node_name` in your task creation request matches the `--name` of your intended runner. Wildcards (`*`) are supported.
