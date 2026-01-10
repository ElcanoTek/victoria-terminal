# MCP Server Guidelines

Victoria relies on MCP servers to expose structured tools to Crush and the terminal experience.

## Expectations

- Implement servers as standalone Python scripts that run over stdio using FastMCP.
- Document each server and list required environment variables in `example.env`.
- Store secrets in the shared `.env` file mounted at `~/Victoria/.env`.
- Return structured errors and log diagnostics to `stderr`.

## Example MCP Server

```python
#!/usr/bin/env python3
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("server_name")

@mcp.tool()
async def tool_function(param: str) -> dict:
    """Tool description."""
    return {"result": param}

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

## Crush Configuration Snippet

```json
{
  "your_service": {
    "type": "stdio",
    "command": "python3",
    "args": ["${YOUR_SERVICE_MCP_SCRIPT}"],
    "cwd": "${YOUR_SERVICE_MCP_DIR}",
    "env": {
      "YOUR_SERVICE_API_KEY": "${YOUR_SERVICE_API_KEY}",
      "PYTHONPATH": "${YOUR_SERVICE_MCP_DIR}"
    }
  }
}
```

`configurator.config.generate_crush_config` resolves path variables like `${YOUR_SERVICE_MCP_SCRIPT}` and `${YOUR_SERVICE_MCP_DIR}` at runtime. You only need to provide the API key in your environment.
