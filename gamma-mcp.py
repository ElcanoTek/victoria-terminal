#!/usr/bin/env python3
"""
Gamma MCP Server

A simple MCP server for Gamma AI presentation generation.
Runs within the Victoria Terminal container environment.
"""

import os
from typing import Any, Dict, Optional

import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("gamma")

# Constants
GAMMA_API_BASE = "https://public-api.gamma.app/v0.2"
USER_AGENT = "victoria-terminal/1.0"


async def make_gamma_request(method: str, url: str, json: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Make a request to the Gamma API with proper error handling."""
    api_key = os.environ.get("GAMMA_API_KEY")
    if not api_key:
        return {"error": "GAMMA_API_KEY environment variable not set"}

    headers = {
        "User-Agent": USER_AGENT,
        "Content-Type": "application/json",
        "X-API-KEY": api_key,
        "accept": "application/json",
    }

    async with httpx.AsyncClient() as client:
        try:
            if method.upper() == "POST":
                response = await client.post(url, headers=headers, json=json, timeout=30.0)
            else:
                response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP error: {e.response.status_code} - {e.response.text}"}
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}


@mcp.tool()
async def generate_presentation(
    input_text: str,
    theme_name: str = "Professional",
    additional_instructions: str = (
        "Use a modern and clean design. Ensure all charts are easy to read " "and properly labeled."
    ),
    export_as: str = "pptx",
) -> Dict[str, Any]:
    """
    Generate a presentation using the Gamma API.

    Args:
        input_text: The markdown content for the presentation
        theme_name: The name of the theme to use (default: Professional)
        additional_instructions: Additional instructions for generation
        export_as: Export format (default: pptx)

    Returns:
        Dictionary containing the generation ID or error information
    """
    url = f"{GAMMA_API_BASE}/generations"
    payload = {
        "inputText": input_text,
        "format": "presentation",
        "themeName": theme_name,
        "additionalInstructions": additional_instructions,
        "imageOptions": {
            "source": "aiGenerated",
            "model": "imagen-4-pro",
            "style": "photorealistic",
        },
        "exportAs": export_as,
    }
    return await make_gamma_request("POST", url, json=payload)


@mcp.tool()
async def check_presentation_status(generation_id: str) -> Dict[str, Any]:
    """
    Check the status of a presentation generation.

    Args:
        generation_id: The ID of the generation to check

    Returns:
        Dictionary containing the generation status or error information
    """
    url = f"{GAMMA_API_BASE}/generations/{generation_id}"
    return await make_gamma_request("GET", url)


if __name__ == "__main__":
    mcp.run(transport="stdio")
