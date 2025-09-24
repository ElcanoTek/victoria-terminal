# Gamma MCP Server Connection Fixes

This document outlines the fixes applied to resolve timeout and connection issues with the Gamma MCP server in Victoria Terminal.

## Issues Resolved

### 1. Test Organization and Structure ✅ FIXED
**Problem**: `test_gamma_mcp.py` was located in the root directory instead of following pytest conventions.

**Solution**: 
- Moved test file to `tests/test_gamma_mcp.py`
- Converted to proper pytest format with fixtures
- Added comprehensive test coverage for MCP protocol
- Included proper error handling and assertions

**Files Modified**:
- `tests/test_gamma_mcp.py` (new location)
- Removed `test_gamma_mcp.py` from root directory

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

## Model Configuration Notes

The Crush configuration files (`configs/crush/crush.template.json` and `configs/crush/crush.local.json`) contain model references that may need to be updated based on your API provider's supported models.

**Common supported models include**:
- `gpt-4.1-mini`
- `gpt-4.1-nano`
- `gemini-2.5-flash`

If you encounter "Unsupported model" errors, update your configuration files to use models supported by your API provider.

## Testing

### Test Gamma MCP Server
```bash
python3 -m pytest tests/test_gamma_mcp.py -v
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

## Troubleshooting

### Common Issues

1. **"Unsupported model" errors**
   - Update model IDs in configuration files to match your API provider's supported models
   - Check API key validity and permissions

2. **"Command not found: crush"**
   - Install Crush CLI using instructions above
   - Verify installation with `crush --version`

3. **MCP server timeout**
   - Check that `gamma-mcp.py` is executable
   - Verify `GAMMA_API_KEY` is set correctly
   - Test MCP server independently with `python3 -m pytest tests/test_gamma_mcp.py`

4. **Environment variable issues**
   - Ensure `.env` file exists and is properly formatted
   - Check that `VICTORIA_HOME` points to correct directory
   - Verify API keys are valid and have proper permissions

## Test Structure Improvements

The new test structure in `tests/test_gamma_mcp.py` includes:

- **Proper pytest fixtures** for environment setup
- **Comprehensive test coverage** for MCP protocol initialization
- **Tool discovery testing** to verify server exposes expected tools
- **Error handling tests** for missing API keys
- **Clean process management** to avoid hanging processes

## Future Improvements

1. **Container Integration**: Include Crush CLI in the Victoria Terminal container
2. **Configuration Validation**: Add startup checks for supported models
3. **Error Handling**: Improve error messages for missing dependencies
4. **Documentation**: Update main README with Crush installation requirements

## Related Files

- `gamma-mcp.py` - MCP server implementation
- `tests/test_gamma_mcp.py` - Comprehensive test suite for MCP server
- `configs/crush/` - Crush configuration files (user should update models as needed)
- `requirements.txt` - Python dependencies
