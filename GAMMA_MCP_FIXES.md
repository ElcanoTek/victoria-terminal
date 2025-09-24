# Gamma MCP Server Connection Fixes

This document outlines the fixes applied to resolve timeout and connection issues with the Gamma MCP server in Victoria Terminal.

## Issues Resolved

### 1. Unsupported Model Configuration
**Problem**: Configuration files referenced unsupported models that caused API errors.

**Models Updated**:
- `openai/chatgpt-5` → `gpt-4.1-mini`
- `openai/chatgpt-5-mini` → `gpt-4.1-nano`
- `xai/grok-code-fast-1` → Removed (unsupported)

**Files Modified**:
- `configs/crush/crush.template.json`
- `configs/crush/crush.local.json`

### 2. Missing Crush CLI Dependency
**Problem**: Victoria Terminal expects Crush CLI to be available but installation instructions were incomplete.

**Solution**: Added installation instructions and updated documentation.

## Installation Requirements

### Prerequisites
1. **Install Crush CLI** (required for MCP integration):
   ```bash
   # Linux x86_64
   curl -L https://github.com/charmbracelet/crush/releases/download/v0.9.3/crush_0.9.3_Linux_x86_64.tar.gz | tar xz
   sudo mv crush_0.9.3_Linux_x86_64/crush /usr/local/bin/
   
   # Or use package manager (see Crush documentation)
   brew install charmbracelet/tap/crush  # macOS
   ```

2. **Install Python Dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```

### Environment Variables
Ensure these are set in your `.env` file:
```bash
OPENROUTER_API_KEY=your_openrouter_api_key
GAMMA_API_KEY=your_gamma_api_key
VICTORIA_HOME=/path/to/victoria-terminal
```

## Supported Models

The following models are confirmed to work with the current API:
- `gpt-4.1-mini`
- `gpt-4.1-nano`
- `gemini-2.5-flash`

## Testing

### Test Gamma MCP Server
```bash
python3 test_gamma_mcp.py
```

Expected output:
```
✅ Server initialized successfully
✅ Found 2 tools:
  - generate_presentation
  - check_presentation_status
```

### Test Crush Integration
```bash
export OPENROUTER_API_KEY=your_key
export GAMMA_API_KEY=your_key
export VICTORIA_HOME=$(pwd)
crush run "what tools are available?"
```

## Configuration Changes

### configs/crush/crush.template.json
- Updated model IDs to supported versions
- Maintained all MCP server configurations
- Preserved provider structure

### configs/crush/crush.local.json
- Updated default model references
- Ensured compatibility with template configuration

## Troubleshooting

### Common Issues

1. **"Unsupported model" errors**
   - Ensure model IDs match supported list above
   - Check API key validity

2. **"Command not found: crush"**
   - Install Crush CLI using instructions above
   - Verify installation with `crush --version`

3. **MCP server timeout**
   - Check that `gamma-mcp.py` is executable
   - Verify `GAMMA_API_KEY` is set correctly
   - Test MCP server independently with `python3 test_gamma_mcp.py`

4. **Environment variable issues**
   - Ensure `.env` file exists and is properly formatted
   - Check that `VICTORIA_HOME` points to correct directory
   - Verify API keys are valid and have proper permissions

## Future Improvements

1. **Container Integration**: Include Crush CLI in the Victoria Terminal container
2. **Configuration Validation**: Add startup checks for supported models
3. **Error Handling**: Improve error messages for missing dependencies
4. **Documentation**: Update main README with Crush installation requirements

## Related Files

- `gamma-mcp.py` - MCP server implementation
- `test_gamma_mcp.py` - Test suite for MCP server
- `configs/crush/` - Crush configuration files
- `requirements.txt` - Python dependencies
