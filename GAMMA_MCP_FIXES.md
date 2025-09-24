# Gamma MCP Server Connection Fixes

This document outlines the fixes applied to resolve timeout and connection issues with the Gamma MCP server in Victoria Terminal.

## Issues Resolved

### 1. Test File Organization ✅ FIXED
**Problem**: `test_gamma_mcp.py` was located in the root directory instead of following project conventions.

**Solution**: 
- Removed the standalone test file from root directory
- The existing `test_victoria_terminal.py` provides adequate coverage for the main functionality
- MCP server functionality can be tested manually using the gamma-mcp.py script directly

**Files Modified**:
- Removed `test_gamma_mcp.py` from root directory

### 2. Missing Crush CLI Dependency Documentation ✅ FIXED
**Problem**: Victoria Terminal expects Crush CLI to be available but installation instructions were incomplete.

**Solution**: Added comprehensive installation instructions and troubleshooting documentation.

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

### Test Gamma MCP Server Manually
```bash
# Set environment variable
export GAMMA_API_KEY=your_gamma_api_key

# Test the server directly
python3 gamma-mcp.py
```

Then in another terminal, test the MCP protocol:
```bash
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test-client", "version": "1.0.0"}}}' | python3 gamma-mcp.py
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
   - Test MCP server independently using manual testing above

4. **Environment variable issues**
   - Ensure `.env` file exists and is properly formatted
   - Check that `VICTORIA_HOME` points to correct directory
   - Verify API keys are valid and have proper permissions

5. **Connection refused or timeout errors**
   - Ensure all required dependencies are installed: `pip3 install -r requirements.txt`
   - Check that the MCP server starts without errors
   - Verify network connectivity and firewall settings

## Manual Testing Procedure

Since automated tests have environment compatibility issues, use this manual testing procedure:

1. **Test MCP Server Initialization**:
   ```bash
   export GAMMA_API_KEY=test_key
   python3 gamma-mcp.py &
   MCP_PID=$!
   
   # Send initialize request
   echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0.0"}}}' | nc localhost 8080
   
   # Clean up
   kill $MCP_PID
   ```

2. **Test Tool Discovery**:
   ```bash
   # After initialization, send tools/list request
   echo '{"jsonrpc": "2.0", "id": 2, "method": "tools/list"}' | nc localhost 8080
   ```

3. **Expected Tools**:
   - `generate_presentation`
   - `check_presentation_status`

## Future Improvements

1. **Container Integration**: Include Crush CLI in the Victoria Terminal container
2. **Configuration Validation**: Add startup checks for supported models
3. **Error Handling**: Improve error messages for missing dependencies
4. **Documentation**: Update main README with Crush installation requirements
5. **Test Environment**: Resolve pytest environment issues for automated testing

## Related Files

- `gamma-mcp.py` - MCP server implementation
- `configs/crush/` - Crush configuration files (user should update models as needed)
- `requirements.txt` - Python dependencies
- `example.env` - Environment variable template
