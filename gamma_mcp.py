#!/usr/bin/env python3
"""
Gamma MCP Server

A simple MCP server for Gamma AI presentation generation.
Runs within the Victoria Terminal container environment.
"""

import asyncio
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

# Polling configuration
POLLING_INTERVAL = 30  # seconds
MAX_POLLING_ATTEMPTS = 10  # Maximum number of polling attempts (5 minutes total)


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
    layout_format: str = "16x9",
    additional_instructions: str = (
    "Use the Elcano theme with standard title and thank you slides. "
    "For Campaign Wrap-Up Protocol presentations, follow this 10-slide structure: "
    "1) Title: Client name/logo left, Elcano logo right, campaign year bottom-center; full-width card with Elcano Gamma accent image. "
    "2) Executive Summary: Four metrics at top (Investment, Conversions, Rate, CPA); Highlights bottom-left; Recommendations bottom-right. "
    "3) Platform Analysis: Table of metrics top; donut chart conversions bottom-left; key insights bottom-right. "
    "4) Lifecycle Optimization: Line chart CPA left; optimization actions right. "
    "5) Conversion Spikes: Line chart left; event details right; Immediate Actions bottom. "
    "6) Winning Inventory: Bar chart conversions by theme left; Content Theme Analysis right; Recommendation bottom. "
    "7) Geographic Insights: Heat map top 3 DMAs left; DMA Analysis right; table of DMA, CTR, Spend Share. "
    "8) Day of Week: Bar chart conversions by day top; 4 highlights in cards below. "
    "9) Key Learnings & Next Steps: Two sections. "
    "10) Thank You: Simple message with Elcano logo. "
    "Charts & visuals: "
    "1) Use the right type (bar for comparisons, line for trends, pie/donut for proportions, maps for geo). "
    "2) Add clear titles and axis labels. "
    "3) Use Elcano brand colors. "
    "4) Sort data logically. "
    "5) Add labels if readability improves. "
    "6) Highlight only key insights. "
    "7) Keep formatting clean with spacing, headings, readable fonts. "
    "8) Use card styling (borders, shadows, padding) to group important insights, summaries, or recs; apply sparingly for emphasis."
),
    export_as: str = "pptx",
) -> Dict[str, Any]:
    """
    Generate a presentation using the Gamma API.

    Args:
        input_text: The markdown content for the presentation
        theme_name: The name of the theme to use (default: Elcano)
        layout_format: Layout format for the presentation. Options: "16x9" (Traditional), "4x3" (Tall), "fluid" (Default/Fluid). Default: "16x9"
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
    
    # Add standard Elcano title and thank you slides
    title_slide = "# Elcano\n## 2025"
    thank_you_slide = "---\n# Thank you\n## Elcano"
    
    # Combine title slide, user content, and thank you slide
    full_input_text = f"{title_slide}\n\n{input_text}\n\n{thank_you_slide}"
    
    url = f"{GAMMA_API_BASE}/generations"
    payload = {
        "inputText": full_input_text,
        "format": "presentation",
        "themeName": resolved_theme,
        "cardOptions": {
            "dimensions": layout_format
        },
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


@mcp.tool()
async def wait_for_presentation_completion(
    generation_id: str,
    polling_interval: int = POLLING_INTERVAL,
    max_attempts: int = MAX_POLLING_ATTEMPTS
) -> Dict[str, Any]:
    """
    Automatically poll the presentation status until completion or timeout.
    
    This function will check the presentation status every 30 seconds (by default)
    until the presentation is completed, failed, or the maximum number of attempts
    is reached.

    Args:
        generation_id: The ID of the generation to monitor
        polling_interval: Time in seconds between status checks (default: 30)
        max_attempts: Maximum number of polling attempts (default: 10)

    Returns:
        Dictionary containing the final generation status or error information
    """
    logger.info(f"Starting automatic polling for generation ID: {generation_id}")
    logger.info(f"Polling every {polling_interval} seconds, max attempts: {max_attempts}")
    
    attempt = 0
    
    while attempt < max_attempts:
        attempt += 1
        logger.info(f"Polling attempt {attempt}/{max_attempts}")
        
        # Check the current status
        result = await check_presentation_status(generation_id)
        
        # Handle errors
        if "error" in result:
            logger.error(f"Error checking status: {result['error']}")
            return result
        
        status = result.get("status", "unknown")
        logger.info(f"Current status: {status}")
        
        # Check if presentation is completed
        if status == "completed":
            logger.info("Presentation generation completed successfully!")
            return result
        
        # Check if presentation failed
        if status == "failed":
            logger.error("Presentation generation failed")
            return result
        
        # If still pending and not the last attempt, wait before next check
        if attempt < max_attempts:
            logger.info(f"Status is '{status}', waiting {polling_interval} seconds before next check...")
            await asyncio.sleep(polling_interval)
        else:
            logger.warning(f"Maximum polling attempts ({max_attempts}) reached")
            return {
                "error": f"Presentation generation timed out after {max_attempts} attempts",
                "generationId": generation_id,
                "status": status,
                "attempts": attempt
            }
    
    # This should not be reached, but included for completeness
    return {
        "error": "Unexpected end of polling loop",
        "generationId": generation_id,
        "attempts": attempt
    }


@mcp.tool()
async def generate_and_wait_for_presentation(
    input_text: str,
    theme_name: str = DEFAULT_THEME,
    layout_format: str = "16x9",
    additional_instructions: str = (
    "Use the Elcano theme with standard title and thank you slides. "
    "For Campaign Wrap-Up Protocol presentations, follow this 10-slide structure: "
    "1) Title: Client name/logo left, Elcano logo right, campaign year bottom-center; full-width card with Elcano Gamma accent image. "
    "2) Executive Summary: Four metrics at top (Investment, Conversions, Rate, CPA); Highlights bottom-left; Recommendations bottom-right. "
    "3) Platform Analysis: Table of metrics top; donut chart conversions bottom-left; key insights bottom-right. "
    "4) Lifecycle Optimization: Line chart CPA left; optimization actions right. "
    "5) Conversion Spikes: Line chart left; event details right; Immediate Actions bottom. "
    "6) Winning Inventory: Bar chart conversions by theme left; Content Theme Analysis right; Recommendation bottom. "
    "7) Geographic Insights: Heat map top 3 DMAs left; DMA Analysis right; table of DMA, CTR, Spend Share. "
    "8) Day of Week: Bar chart conversions by day top; 4 highlights in cards below. "
    "9) Key Learnings & Next Steps: Two sections. "
    "10) Thank You: Simple message with Elcano logo. "
    "Charts & visuals: "
    "1) Use the right type (bar for comparisons, line for trends, pie/donut for proportions, maps for geo). "
    "2) Add clear titles and axis labels. "
    "3) Use Elcano brand colors. "
    "4) Sort data logically. "
    "5) Add labels if readability improves. "
    "6) Highlight only key insights. "
    "7) Keep formatting clean with spacing, headings, readable fonts. "
    "8) Use card styling (borders, shadows, padding) to group important insights, summaries, or recs; apply sparingly for emphasis."
),
    export_as: str = "pptx",
    polling_interval: int = POLLING_INTERVAL,
    max_attempts: int = MAX_POLLING_ATTEMPTS
) -> Dict[str, Any]:
    """
    Generate a presentation and automatically wait for completion.
    
    This is a convenience function that combines generate_presentation and
    wait_for_presentation_completion into a single call. It will start the
    generation and then automatically poll every 30 seconds until the
    presentation is ready.

    Args:
        input_text: The markdown content for the presentation
        theme_name: The name of the theme to use (default: Elcano)
        layout_format: Layout format for the presentation. Options: "16x9" (Traditional), "4x3" (Tall), "fluid" (Default/Fluid). Default: "16x9"
        additional_instructions: Additional instructions for generation
        export_as: Export format (default: pptx)
        polling_interval: Time in seconds between status checks (default: 30)
        max_attempts: Maximum number of polling attempts (default: 10)

    Returns:
        Dictionary containing the final generation result or error information
    """
    logger.info("Starting presentation generation with automatic completion waiting")
    
    # Start the generation
    generation_result = await generate_presentation(
        input_text=input_text,
        theme_name=theme_name,
        layout_format=layout_format,
        additional_instructions=additional_instructions,
        export_as=export_as
    )
    
    # Check if generation started successfully
    if "error" in generation_result:
        logger.error("Failed to start presentation generation")
        return generation_result
    
    generation_id = generation_result.get("generationId")
    if not generation_id:
        logger.error("No generation ID returned from generation request")
        return {"error": "No generation ID returned from generation request"}
    
    logger.info(f"Generation started successfully with ID: {generation_id}")
    logger.info("Now waiting for completion...")
    
    # Wait for completion
    completion_result = await wait_for_presentation_completion(
        generation_id=generation_id,
        polling_interval=polling_interval,
        max_attempts=max_attempts
    )
    
    return completion_result


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
