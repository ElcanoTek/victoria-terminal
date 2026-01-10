# Security

Victoria Terminal is designed to keep agent workflows boxed in while preserving auditability and least-privilege access.

## Isolation & Execution

- **Containerized by default**: Victoria runs inside Podman to isolate the agent from the host.
- **Outbound-only orchestration**: Fleet nodes poll for work over HTTPS; no inbound ports are required.
- **Explicit MCP boundaries**: MCP servers define exactly which systems the agent can reach.

## Data Access Controls

- **Read-only by default**: We encourage read-only database credentials for analytics workflows, and many MCPs are configured for read-only access to production data.
- **Scoped secrets**: Credentials live in `~/Victoria/.env` or injected runtime variables, never hardcoded.
- **Attachment hygiene**: Task inputs and outputs stay within the mounted `~/Victoria` workspace for easy review and cleanup.

## Reporting & Disclosure

If you discover a security issue, please email brad@elcanotek.com with details so we can investigate promptly.
