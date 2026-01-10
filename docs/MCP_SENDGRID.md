# SendGrid MCP

The SendGrid MCP lets Victoria send transactional email through SendGrid during automated workflows.

## What It Does

- Sends emails for reports, alerts, and scheduled summaries.
- Supports attaching outputs produced in `~/Victoria`.

## Configuration

The MCP is configured in `configs/crush/crush.template.json` and expects:

- `SENDGRID_API_KEY`: Your SendGrid API key.
- `SENDGRID_MCP_DIR`: Directory containing the SendGrid MCP server code.
- `SENDGRID_MCP_SCRIPT`: Entry point script for the MCP server.

Set these in `~/Victoria/.env` before running Victoria.
