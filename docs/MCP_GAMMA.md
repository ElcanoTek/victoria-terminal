# Gamma MCP

The Gamma MCP integrates Victoria with Gamma to generate presentations and decks directly from an agent workflow.

## What It Does

- Creates slide decks or presentation drafts based on structured prompts.
- Enables hands-free reporting workflows (e.g., campaign recaps or monthly QBR decks).

## Configuration

The MCP is wired in `configs/crush/crush.template.json` and expects these environment variables:

- `GAMMA_API_KEY`: Your Gamma API key.
- `GAMMA_MCP_DIR`: Directory containing the Gamma MCP server code.
- `GAMMA_MCP_SCRIPT`: Entry point script for the MCP server.

Add the values to `~/Victoria/.env` before launching Victoria.
