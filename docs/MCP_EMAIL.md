# Email (SES) MCP

The Email MCP connects Victoria to an AWS SES-backed inbox for ingesting inbound requests and sending outbound replies.

## What It Does

- Reads emails from an SES-backed mailbox.
- Saves attachments into the Victoria workspace for analysis.
- Sends outbound replies with reports or generated artifacts.

## Configuration

The MCP is configured in `configs/crush/crush.template.json` and expects the following environment variables:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`
- `EMAIL_S3_BUCKET`
- `EMAIL_S3_PREFIX`
- `EMAIL_ATTACHMENT_DIR`
- `EMAIL_LAST_CHECK_FILE`
- `EMAIL_MCP_DIR`
- `EMAIL_MCP_SCRIPT`

See [SES_EMAIL_SETUP.md](SES_EMAIL_SETUP.md) for step-by-step setup details.
