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
from datetime import datetime
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
AVAILABLE_THEMES = {"Elcano"}

# Default presentation instructions for Campaign Wrap-Up Protocol
DEFAULT_ADDITIONAL_INSTRUCTIONS = (
    "Use the Elcano theme with the standard title and thank you slides. "
    "For Campaign Wrap-Up Protocol presentations, follow this specific 13-slide structure: "
    "1) Title Slide: Client and Elcano logos with the campaign year. "
    "2) AI-Powered Performance: A title and a brief description of the project. "
    "3) Meet Victoria: A brief introduction to the Victoria AI agent. "
    "4) Delivering Supply-side Performance: 'The Challenge' and 'The Results' sections. "
    "5) How We Did It: A diagram illustrating the workflow. "
    "6) Executive Summary: Four key metrics at top (Total Investment, Total Conversions, Conversion Rate, Cost per Acquisition), with Campaign Performance Highlights on the left and Strategic Recommendations on the right. "
    "7) Platform Performance Analysis: A table with platform metrics, a donut chart for conversion distribution, and key platform insights. "
    "8) Campaign Lifecycle Optimization: A line chart for CPA optimization and a section for optimization actions. "
    "9) Conversion Spike Analysis: A line chart for conversion spikes and a section for spike event details. "
    "10) Winning Inventory Combinations: A bar chart for conversions by site category and a section for content theme analysis. "
    "11) Key Learnings & Next Steps: 'Key Learnings' and 'Next Steps' sections. "
    "12) Thank You Slide: A simple 'Thank You' message with contact information. "
    "13) Appendix: An appendix slide. "
    "For all charts and data visualizations: "
    "1) Choose the most appropriate chart type for the data (bar charts for comparisons, line charts for trends, pie charts for proportions). "
    "2) Ensure all charts have clear, descriptive titles and properly labeled axes. "
    "3) Use consistent color schemes that align with the Elcano brand palette. "
    "4) Sort data logically (e.g., highest to lowest for bar charts). "
    "5) Include data labels where they enhance readability. "
    "6) For complex datasets, focus on the key insights and highlight the most important data points. "
    "7) Maintain professional formatting with adequate spacing and readable fonts."
)


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
    additional_instructions: str = DEFAULT_ADDITIONAL_INSTRUCTIONS,
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
    
    # Add standard Elcano title and thank you slides with dynamic year
    current_year = datetime.now().year
    title_slide = f"# Elcano\n## {current_year}"
    thank_you_slide = "---\n# Thank you\n## Elcano"
    
    # Combine title slide, user content, and thank you slide with proper slide separators
    full_input_text = f"{title_slide}\n\n---\n\n{input_text}\n\n{thank_you_slide}"
    
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
            "source": "noImages",
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
    additional_instructions: str = DEFAULT_ADDITIONAL_INSTRUCTIONS,
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
