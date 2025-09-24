#!/usr/bin/env python3
"""
Test script for the Gamma MCP server
"""

import asyncio
import json
import subprocess
import sys
import os

async def test_mcp_server():
    """Test the MCP server by sending a simple tools/list request"""
    
    # Set environment variable
    env = os.environ.copy()
    env['GAMMA_API_KEY'] = 'test_key'
    
    # Start the MCP server process
    process = subprocess.Popen(
        [sys.executable, 'gamma-mcp.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env
    )
    
    try:
        # Send initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        print("Sending initialize request...")
        process.stdin.write(json.dumps(init_request) + '\n')
        process.stdin.flush()
        
        # Read response
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            print(f"Initialize response: {response}")
            
            if response.get('result'):
                print("✅ Server initialized successfully")
                
                # Send initialized notification (required by MCP protocol)
                initialized_notification = {
                    "jsonrpc": "2.0",
                    "method": "notifications/initialized",
                    "params": {}
                }
                
                print("Sending initialized notification...")
                process.stdin.write(json.dumps(initialized_notification) + '\n')
                process.stdin.flush()
                
                # Send tools/list request
                tools_request = {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/list"
                }
                
                print("Sending tools/list request...")
                process.stdin.write(json.dumps(tools_request) + '\n')
                process.stdin.flush()
                
                # Read tools response
                tools_response_line = process.stdout.readline()
                if tools_response_line:
                    tools_response = json.loads(tools_response_line.strip())
                    print(f"Tools response: {tools_response}")
                    
                    if 'result' in tools_response and 'tools' in tools_response['result']:
                        tools = tools_response['result']['tools']
                        print(f"✅ Found {len(tools)} tools:")
                        for tool in tools:
                            print(f"  - {tool['name']}: {tool.get('description', 'No description')}")
                        return True
                    else:
                        print("❌ No tools found in response")
                        return False
                else:
                    print("❌ No response to tools/list request")
                    return False
            else:
                print(f"❌ Initialize failed: {response}")
                return False
        else:
            print("❌ No response to initialize request")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        # Print stderr for debugging
        stderr_output = process.stderr.read()
        if stderr_output:
            print(f"Server stderr: {stderr_output}")
        return False
    finally:
        # Clean up
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()

if __name__ == "__main__":
    print("Testing Gamma MCP Server...")
    success = asyncio.run(test_mcp_server())
    sys.exit(0 if success else 1)
