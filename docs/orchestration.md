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
         │ Push (HTTP)        │ Pull (Polling)     │ Status + Logs (MCP)
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

The Status Reporter is an MCP server that runs inside the Victoria container and reports task progress and logs back to the orchestrator.

**Available Tools:**

| Tool | Description |
|------|-------------|
| `report_status` | Report current task status with optional message and progress |
| `report_started` | Convenience wrapper for reporting task start |
| `report_complete` | Report successful task completion (auto-submits logs) |
| `report_error` | Report task failure with error message (auto-submits logs) |
| `submit_crush_logs` | Manually submit Crush session logs to the orchestrator |
| `get_job_info` | Get current job ID, orchestrator URL, and Crush database info |

**Example Usage (from within Victoria):**

```python
# The LLM agent can call these tools during task execution

# Report that analysis has started
report_status(status="analyzing", message="Analyzing sales data from Q4")

# Report progress on a long task
report_status(status="running", message="Processing files", progress=45.0)

# Report successful completion (automatically submits logs)
report_complete(message="Analysis complete. Found 3 key insights.")

# Report an error (automatically submits logs)
report_error(error_message="Failed to connect to database")

# Manually submit logs without changing status
submit_crush_logs()
```

### 3. Crush Log Integration

Victoria Terminal stores conversation logs in a local SQLite database (Crush). The Status Reporter MCP server reads this database and uploads the full conversation history to the orchestrator.

**How it works:**

1. Crush stores all agent conversations in `~/.crush/crush.db` (or `~/Victoria/.crush/crush.db`)
2. The database contains sessions (conversations) and messages (individual turns)
3. When `report_complete()` or `report_error()` is called, the Status Reporter:
   - Reads the most recent session from the Crush database
   - Extracts all messages with their roles, content, model info, and timestamps
   - POSTs the session data to the orchestrator's `/logs` endpoint
4. The orchestrator stores the logs and links them to the task for dashboard viewing

**Database Schema:**

```sql
-- Sessions table
sessions (
    id TEXT PRIMARY KEY,
    title TEXT,
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    cost REAL,
    created_at INTEGER,
    updated_at INTEGER
)

-- Messages table
messages (
    id TEXT PRIMARY KEY,
    session_id TEXT,
    role TEXT,           -- user, assistant, system, tool
    parts TEXT,          -- message content (JSON)
    model TEXT,
    provider TEXT,
    created_at INTEGER,
    finished_at INTEGER
)
```

## Configuration

### Environment Variables

The following environment variables are set by the Remote Runner when launching containers:

| Variable | Description |
|----------|-------------|
| `ORCHESTRATOR_URL` | URL of the quarterback orchestrator |
| `JOB_ID` | Unique identifier for the current task |
| `VICTORIA_HOME` | Path to Victoria home directory (for finding Crush DB) |

### .env Configuration

Add these to your `.env` file for manual testing:

```bash
# Orchestrator URL (set by remote-runner when launching containers)
ORCHESTRATOR_URL="http://quarterback.example.com:8000"

# Job ID (set by remote-runner when launching containers)
JOB_ID="your-job-id-here"

# Victoria home directory (optional, defaults to ~/Victoria)
VICTORIA_HOME="/home/user/Victoria"
```

**Note:** In production, these variables are automatically set by the Remote Runner. You only need to configure them manually for testing.

## Workflow

### Push Strategy (Cloud Servers)

1. Orchestrator receives a task creation request
2. Orchestrator sends POST request to Cloud Node's Remote Runner
3. Remote Runner validates request and runs `podman run victoria-terminal`
4. Victoria starts and reports "Status: Started" via MCP
5. Victoria processes task (Crush logs conversation to local DB)
6. Victoria reports "Status: Complete" via MCP and submits logs

### Pull Strategy (Local Hardware)

1. Remote Runner (on local machine) polls Orchestrator: "Any jobs?"
2. Orchestrator replies with task details
3. Remote Runner runs `podman run victoria-terminal`
4. Victoria processes task (Crush logs conversation to local DB)
5. Victoria reports "Status: Complete" via MCP and submits logs

### Log Submission Flow

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Victoria Agent │     │   Crush DB      │     │  Orchestrator   │
│                 │     │ ~/.crush/       │     │                 │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                       │
         │ Conversation happens  │                       │
         │──────────────────────>│                       │
         │                       │ (stored locally)      │
         │                       │                       │
         │ report_complete()     │                       │
         │───────────────────────┼──────────────────────>│
         │                       │                       │
         │ Read session data     │                       │
         │<──────────────────────│                       │
         │                       │                       │
         │ POST /logs            │                       │
         │──────────────────────────────────────────────>│
         │                       │                       │ (stored for dashboard)
         │                       │                       │
```

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

1. Verify the Crush database exists at `~/.crush/crush.db` or `~/Victoria/.crush/crush.db`
2. Check that `submit_crush_logs()` was called (or `report_complete()`/`report_error()`)
3. Verify network connectivity to the orchestrator
4. Check orchestrator logs for any errors receiving the log submission
5. Use `get_job_info()` to verify the Crush database path is detected
