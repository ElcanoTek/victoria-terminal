# Victoria Terminal MCP Servers

This directory contains Model Context Protocol (MCP) servers that extend Victoria's capabilities by providing secure, structured access to external APIs and services.

## Overview

MCP servers enable Victoria to interact with external services through a standardized protocol, replacing direct API calls and curl commands with secure, type-safe tool interfaces. Each server runs within the existing Victoria Terminal container environment.

## Available Servers

### Gamma AI Server (`gamma_server.py`)

The Gamma MCP server provides secure access to Gamma's presentation generation API, replacing the previous curl-based implementation with a structured tool interface.

**Features:**
- Generate presentations from markdown content
- Check presentation generation status
- Secure API key handling through environment variables
- Runs within the existing container environment

**Tools:**
- `generate_presentation`: Create a new presentation with customizable themes and options
- `check_presentation_status`: Monitor the status of presentation generation

**Configuration:**
The server is configured in the Crush template as:
```json
{
  "gamma": {
    "type": "stdio",
    "command": "python3",
    "args": ["mcp/gamma_server.py"]
  }
}
```

**Environment Variables:**
- `GAMMA_API_KEY`: Your Gamma API key (required)

## Usage

The Gamma server provides two main tools accessible through Victoria:

### Generate Presentation
```python
# Call the generate_presentation tool
result = gamma.generate_presentation(
    input_text="# My Presentation\n## Slide 1\nContent here...",
    theme_name="Professional"
)
```

### Check Status
```python
# Check presentation generation status
status = gamma.check_presentation_status(generation_id="gen_123456")
```

## Adding New MCP Servers

When adding new MCP servers:

1. **Create a new Python file** in this directory (e.g., `service_server.py`)
2. **Use the FastMCP framework** for implementation
3. **Add configuration** to the Crush template
4. **Update this README** with documentation
5. **Use existing container dependencies** where possible

## Development Guidelines

### Server Implementation Pattern

```python
#!/usr/bin/env python3
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("server_name")

@mcp.tool()
async def tool_function(param: str) -> dict:
    """Tool description."""
    # Implementation
    return result

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

### Best Practices

- Use existing container dependencies (no separate requirements)
- Handle errors gracefully with structured responses
- Use environment variables for sensitive configuration
- Log to stderr (not stdout for stdio transport)
- Include comprehensive docstrings for tools

## Testing

Test the server independently:
```bash
python3 mcp/gamma_server.py
```

Or use MCP Inspector:
```bash
npx @modelcontextprotocol/inspector python3 mcp/gamma_server.py
```

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure required packages are available in the container
2. **API authentication**: Verify environment variables are set correctly
3. **Server not found**: Check file paths in Crush configuration
4. **Permission errors**: Ensure server files are executable

### Environment Setup

The servers run within the Victoria Terminal container which includes:
- Python 3.11+
- Standard HTTP libraries
- MCP framework (when available)

For more information about MCP development, see the [official documentation](https://modelcontextprotocol.io/).
