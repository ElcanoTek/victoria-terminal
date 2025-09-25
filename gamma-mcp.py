#!/usr/bin/env python3
"""
Gamma MCP Server

A simple MCP server for Gamma AI presentation generation.
Runs within the Victoria Terminal container environment.
"""

import logging
import os
import sys
from typing import Any, Dict, Optional

import httpx
from mcp.server.fastmcp import FastMCP

# Configure logging to stderr (not stdout for STDIO transport)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("gamma")

# Constants
GAMMA_API_BASE = "https://public-api.gamma.app/v0.2"
USER_AGENT = "victoria-terminal/1.0"
DEFAULT_TIMEOUT = 60.0  # Increased timeout for presentation generation


async def make_gamma_request(method: str, url: str, json: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Make a request to the Gamma API with proper error handling."""
    api_key = os.environ.get("GAMMA_API_KEY")
    if not api_key:
        error_msg = "GAMMA_API_KEY environment variable not set"
        logger.error(error_msg)
        return {"error": error_msg}

    headers = {
        "User-Agent": USER_AGENT,
        "Content-Type": "application/json",
        "X-API-KEY": api_key,
        "accept": "application/json",
    }

    logger.info(f"Making {method} request to {url}")
    
    try:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            if method.upper() == "POST":
                response = await client.post(url, headers=headers, json=json)
            else:
                response = await client.get(url, headers=headers)
            
            logger.info(f"Response status: {response.status_code}")
            response.raise_for_status()
            result = response.json()
            logger.info("Request completed successfully")
            return result
            
    except httpx.TimeoutException as e:
        error_msg = f"Request timeout after {DEFAULT_TIMEOUT}s: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg}
    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP error: {e.response.status_code} - {e.response.text}"
        logger.error(error_msg)
        return {"error": error_msg}
    except httpx.RequestError as e:
        error_msg = f"Request error: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg}
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg}

DEFAULT_THEME = "Elcano"
AVAILABLE_THEMES = {"Elcano", "Elcano_Light"}


def _resolve_theme_name(theme_name: str) -> str:
    """Normalize a requested theme to one of the supported Gamma themes."""

    requested = theme_name.strip()
    if requested in AVAILABLE_THEMES:
        return requested

    normalized = requested.replace("-", "_").replace(" ", "_").casefold()
    for theme in AVAILABLE_THEMES:
        if normalized == theme.casefold():
            return theme

    logger.warning(
        "Unsupported theme '%s' requested. Falling back to default theme '%s'.",
        theme_name,
        DEFAULT_THEME,
    )
    return DEFAULT_THEME

@mcp.tool()
async def generate_presentation(
    input_text: str,
    theme_name: str = DEFAULT_THEME,
    additional_instructions: str = (
        "Use a modern and clean design. Ensure all charts are easy to read "
        "and properly labeled."
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
    resolved_theme = _resolve_theme_name(theme_name)
    logger.info(
        "Generating presentation with theme: %s (requested: %s), format: %s",
        resolved_theme,
        theme_name,
        export_as,
    )
    url = f"{GAMMA_API_BASE}/generations"
    payload = {
        "inputText": input_text,
        "format": "presentation",
        "themeName": resolved_theme,
        "additionalInstructions": additional_instructions,
        "imageOptions": {
            "source": "aiGenerated",
            "model": "imagen-4-pro",
            "style": "photorealistic",
        },
        "exportAs": export_as,
    }
    
    result = await make_gamma_request("POST", url, json=payload)
    
    if "error" not in result:
        logger.info(f"Presentation generation started successfully")
    
    return result


@mcp.tool()
async def check_presentation_status(generation_id: str) -> Dict[str, Any]:
    """
    Check the status of a presentation generation.

    Args:
        generation_id: The ID of the generation to check

    Returns:
        Dictionary containing the generation status or error information
    """
    logger.info(f"Checking status for generation ID: {generation_id}")
    
    url = f"{GAMMA_API_BASE}/generations/{generation_id}"
    result = await make_gamma_request("GET", url)
    
    if "error" not in result:
        status = result.get("status", "unknown")
        logger.info(f"Generation status: {status}")
    
    return result


if __name__ == "__main__":
    logger.info("Starting Gamma MCP Server")
    
    # Check if API key is available
    if not os.environ.get("GAMMA_API_KEY"):
        logger.error("GAMMA_API_KEY environment variable is not set")
        sys.exit(1)
    
    try:
        # Use stdio transport (default for FastMCP)
        mcp.run(transport="stdio")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)
