# Copyright (c) 2025 ElcanoTek
#
# This file is part of Victoria Terminal.
#
# This software is licensed under the Business Source License 1.1.
# You may not use this file except in compliance with the license.
# You may obtain a copy of the license at
#
#     https://github.com/ElcanoTek/victoria-terminal/blob/main/LICENSE
#
# Change Date: 2027-09-20
# Change License: GNU General Public License v3.0 or later

"""Tests for the Gamma MCP server."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture
def gamma_mcp_path():
    """Return the path to the gamma-mcp.py script."""
    return Path(__file__).parent.parent / "gamma-mcp.py"


@pytest.fixture
def test_env(monkeypatch):
    """Set up test environment variables."""
    monkeypatch.setenv("GAMMA_API_KEY", "test_key")


class TestGammaMCPServer:
    """Test suite for the Gamma MCP server."""

    def test_server_initialization(self, gamma_mcp_path, test_env):
        """Test that the MCP server initializes correctly."""
        process = subprocess.Popen(
            [sys.executable, str(gamma_mcp_path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
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

            process.stdin.write(json.dumps(init_request) + '\n')
            process.stdin.flush()

            # Read response
            response_line = process.stdout.readline()
            assert response_line, "No response received from server"
            
            response = json.loads(response_line.strip())
            
            # Verify response structure
            assert response["jsonrpc"] == "2.0"
            assert response["id"] == 1
            assert "result" in response
            
            result = response["result"]
            assert result["protocolVersion"] == "2024-11-05"
            assert "capabilities" in result
            assert "serverInfo" in result
            assert result["serverInfo"]["name"] == "gamma"

        finally:
            process.terminate()
            process.wait(timeout=5)

    def test_tools_list(self, gamma_mcp_path, test_env):
        """Test that the server exposes the expected tools."""
        process = subprocess.Popen(
            [sys.executable, str(gamma_mcp_path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        try:
            # Initialize server
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test-client", "version": "1.0.0"}
                }
            }
            process.stdin.write(json.dumps(init_request) + '\n')
            process.stdin.flush()
            
            # Read init response
            init_response = process.stdout.readline()
            assert init_response
            
            # Send initialized notification
            initialized_notification = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
                "params": {}
            }
            process.stdin.write(json.dumps(initialized_notification) + '\n')
            process.stdin.flush()

            # Request tools list
            tools_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list"
            }
            process.stdin.write(json.dumps(tools_request) + '\n')
            process.stdin.flush()

            # Read tools response
            tools_response_line = process.stdout.readline()
            assert tools_response_line, "No tools response received"
            
            tools_response = json.loads(tools_response_line.strip())
            
            # Verify tools response
            assert tools_response["jsonrpc"] == "2.0"
            assert tools_response["id"] == 2
            assert "result" in tools_response
            
            tools = tools_response["result"]["tools"]
            assert len(tools) == 2
            
            tool_names = {tool["name"] for tool in tools}
            expected_tools = {"generate_presentation", "check_presentation_status"}
            assert tool_names == expected_tools
            
            # Verify tool schemas
            for tool in tools:
                assert "name" in tool
                assert "description" in tool
                assert "inputSchema" in tool
                assert "outputSchema" in tool

        finally:
            process.terminate()
            process.wait(timeout=5)

    def test_server_requires_api_key(self, gamma_mcp_path, monkeypatch):
        """Test that the server fails gracefully without API key."""
        # Remove the API key
        monkeypatch.delenv("GAMMA_API_KEY", raising=False)
        
        process = subprocess.Popen(
            [sys.executable, str(gamma_mcp_path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        try:
            # Server should exit with error code 1
            return_code = process.wait(timeout=5)
            assert return_code == 1
            
            # Check stderr for error message
            stderr_output = process.stderr.read()
            assert "GAMMA_API_KEY environment variable is not set" in stderr_output

        except subprocess.TimeoutExpired:
            process.kill()
            pytest.fail("Server did not exit when API key was missing")
