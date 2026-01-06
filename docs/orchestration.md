# Victoria Terminal Orchestration

This document describes how Victoria Terminal integrates with the [All-Time Quarterback](https://github.com/ElcanoTek/all-time-quarterback) orchestrator for fleet management and remote task execution.

## Overview

The orchestration system enables centralized management of multiple Victoria Terminal instances across hybrid infrastructure:

- **Cloud Servers** (Static IP): Receive tasks via push (HTTP API)
- **Local/Edge Devices** (Dynamic IP): Poll for tasks via pull

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    All-Time Quarterback                         │
│                      (Orchestrator)                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │   Fleet     │  │    Task     │  │      Dashboard          │ │
│  │  Registry   │  │  Scheduler  │  │   (Web UI + API)        │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
         │                    │                    ▲
         │ Push (HTTP)        │ Pull (Polling)     │ Status (MCP)
         ▼                    ▼                    │
┌─────────────────┐  ┌─────────────────┐          │
│  Remote Runner  │  │  Remote Runner  │          │
│   (Push Mode)   │  │   (Pull Mode)   │          │
│                 │  │                 │          │
│  ┌───────────┐  │  │  ┌───────────┐  │          │
│  │ Victoria  │──┼──┼──│ Victoria  │──┼──────────┘
│  │ Container │  │  │  │ Container │  │
│  └───────────┘  │  │  └───────────┘  │
└─────────────────┘  └─────────────────┘
   Cloud Server         Local Device
```

## Components

### 1. Remote Runner (Host Shim)

The Remote Runner runs on the host OS (outside the container) and manages container lifecycle:

```bash
# Push mode (cloud server)
python -m remote_runner push \
    --orchestrator-url http://quarterback.example.com:8000 \
    --api-key your-node-api-key

# Pull mode (local workstation)
python -m remote_runner pull \
    --orchestrator-url http://quarterback.example.com:8000 \
    --api-key your-node-api-key
```

See [remote-runner/README.md](../remote-runner/README.md) for detailed documentation.

### 2. Status Reporter MCP Server

The Status Reporter is an MCP server that runs inside the Victoria container and reports task progress back to the orchestrator.

**Available Tools:**

| Tool | Description |
|------|-------------|
| `report_status` | Report current task status with optional message and progress |
| `report_started` | Convenience wrapper for reporting task start |
| `report_complete` | Report successful task completion |
| `report_error` | Report task failure with error message |
| `get_job_info` | Get current job ID and orchestrator URL |

**Example Usage (from within Victoria):**

```python
# The LLM agent can call these tools during task execution

# Report that analysis has started
report_status(status="analyzing", message="Analyzing sales data from Q4")

# Report progress on a long task
report_status(status="running", message="Processing files", progress=45.0)

# Report successful completion
report_complete(message="Analysis complete. Found 3 key insights.")

# Report an error
report_error(error_message="Failed to connect to database")
```

### 3. Crush Log Integration

Victoria Terminal streams logs to Crush for aggregation. The orchestrator can link to specific Crush sessions for historical log viewing.

## Configuration

### Environment Variables

The following environment variables are set by the Remote Runner when launching containers:

| Variable | Description |
|----------|-------------|
| `ORCHESTRATOR_URL` | URL of the quarterback orchestrator |
| `JOB_ID` | Unique identifier for the current task |
| `CRUSH_SERVER_URL` | (Optional) URL for Crush log server |

### .env Configuration

Add these to your `.env` file for manual testing:

```bash
# Orchestrator URL (set by remote-runner when launching containers)
ORCHESTRATOR_URL="http://quarterback.example.com:8000"

# Job ID (set by remote-runner when launching containers)
JOB_ID="your-job-id-here"
```

**Note:** In production, these variables are automatically set by the Remote Runner. You only need to configure them manually for testing.

## Workflow

### Push Strategy (Cloud Servers)

1. Orchestrator receives a task creation request
2. Orchestrator sends POST request to Cloud Node's Remote Runner
3. Remote Runner validates request and runs `podman run victoria-terminal`
4. Victoria starts and reports "Status: Started" via MCP
5. Victoria processes task and streams logs to Crush
6. Victoria reports "Status: Complete" via MCP

### Pull Strategy (Local Hardware)

1. Remote Runner (on local machine) polls Orchestrator: "Any jobs?"
2. Orchestrator replies with task details
3. Remote Runner runs `podman run victoria-terminal`
4. Victoria processes task and reports status via MCP
5. Victoria reports "Status: Complete" via MCP

## Security

### API Key Authentication

- Each node receives a unique API key upon registration
- All API calls require the `X-API-Key` header
- Admin operations require a separate admin API key

### Network Security

- Use TLS/HTTPS for all orchestrator communications
- Consider VPN or private networking for sensitive deployments
- Push-mode nodes should use firewall rules to restrict access

## Troubleshooting

### Status Reporter Not Working

1. Check that `ORCHESTRATOR_URL` and `JOB_ID` are set
2. Verify network connectivity to the orchestrator
3. Check container logs for MCP server startup errors

### Node Not Receiving Tasks

1. Verify node registration with the orchestrator
2. Check API key is correct
3. Ensure node status is "idle" (not "busy" or "offline")

### Logs Not Appearing in Dashboard

1. Verify Crush session ID is being reported
2. Check Crush server connectivity
3. Ensure logs are being written to stdout/stderr
