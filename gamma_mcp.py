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
from enum import Enum
from typing import Any, Dict, Optional, List

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
GAMMA_API_V1_BASE = "https://public-api.gamma.app/v1.0"
USER_AGENT = "victoria-terminal/1.0"
DEFAULT_TIMEOUT = 60.0  # Increased timeout for presentation generation

# Polling configuration
POLLING_INTERVAL = 30  # seconds
MAX_POLLING_ATTEMPTS = 10  # Maximum number of polling attempts (5 minutes total)

# Template IDs
WRAP_UP_PROTOCOL_TEMPLATE_ID = "g_vzunwtnstnq4oag"


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
    "8) Use styling (borders, shadows, padding) to group important insights, summaries, or recs; apply sparingly for emphasis."
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
    Generate a presentation using the Gamma API (legacy method with full control).

    NOTE: For most use cases, consider using the more specific functions:
    - generate_wrap_up_presentation(): For Campaign Wrap-Up Protocol presentations using templates
    - generate_standard_presentation(): For basic presentations with Elcano theme only

    This function provides full control over all generation parameters and is best used
    when you need custom instructions or specific configurations not covered by the
    specialized functions above.

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
async def generate_wrap_up_presentation(
    prompt: str,
    theme_id: Optional[str] = None,
    folder_ids: Optional[List[str]] = None,
    export_as: str = "pptx",
    image_model: Optional[str] = None,
    image_style: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate a Campaign Wrap-Up presentation using the predefined Gamma template.

    This function uses Gamma's template API (v1.0) to create presentations following the
    Campaign Wrap-Up Protocol structure. The template (g_vzunwtnstnq4oag) includes
    predefined pages and layouts optimized for campaign analysis reporting.

    Args:
        prompt: Text content, image URLs, and instructions for how to modify the template.
               Can include specific data to populate the template slides.
               Example: "Create a campaign wrap-up for Acme Corp's 2025 campaign.
                        Total Investment: $50,000, Total Conversions: 1,250,
                        Conversion Rate: 2.5%, Cost per Acquisition: $40.
                        Include this image for the title: https://example.com/logo.png"
        theme_id: Optional theme ID to override the template's default theme
        folder_ids: Optional list of folder IDs where the gamma should be stored
        export_as: Export format - "pdf" or "pptx" (default: pptx)
        image_model: Optional AI image model to use (e.g., "flux-1-pro", "imagen-4-pro")
        image_style: Optional style description for AI-generated images (e.g., "photorealistic")

    Returns:
        Dictionary containing the generation ID or error information
    """
    logger.info("Generating Campaign Wrap-Up presentation from template")

    url = f"{GAMMA_API_V1_BASE}/generations/from-template"
    payload = {
        "gammaId": WRAP_UP_PROTOCOL_TEMPLATE_ID,
        "prompt": prompt,
        "exportAs": export_as,
    }

    # Add optional parameters
    if theme_id:
        payload["themeId"] = theme_id
    if folder_ids:
        payload["folderIds"] = folder_ids

    # Add image options if specified
    if image_model or image_style:
        image_options = {}
        if image_model:
            image_options["model"] = image_model
        if image_style:
            image_options["style"] = image_style
        payload["imageOptions"] = image_options

    result = await make_gamma_request("POST", url, json=payload)

    if "error" not in result:
        logger.info("Wrap-Up presentation generation started successfully")

    return result


@mcp.tool()
async def generate_standard_presentation(
    input_text: str,
    layout_format: str = "16x9",
    export_as: str = "pptx",
) -> Dict[str, Any]:
    """
    Generate a standard presentation with the Elcano theme.

    This function creates basic presentations using only the Elcano theme,
    without the complex structure of the Campaign Wrap-Up Protocol. Use this
    for general presentation requests that don't require the wrap-up template.

    Args:
        input_text: The markdown content for the presentation
        layout_format: Layout format for the presentation. Options: "16x9" (Traditional), "4x3" (Tall), "fluid" (Default/Fluid). Default: "16x9"
        export_as: Export format (default: pptx)

    Returns:
        Dictionary containing the generation ID or error information
    """
    logger.info("Generating standard presentation with Elcano theme")

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
        "themeName": DEFAULT_THEME,
        "cardOptions": {
            "dimensions": layout_format
        },
        "additionalInstructions": "Use the Elcano theme with clean, professional styling. Keep formatting simple and readable.",
        "imageOptions": {
            "source": "noImages",
        },
        "exportAs": export_as,
    }

    result = await make_gamma_request("POST", url, json=payload)

    if "error" not in result:
        logger.info("Standard presentation generation started successfully")

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


@mcp.tool()
async def generate_and_wait_for_wrap_up_presentation(
    prompt: str,
    theme_id: Optional[str] = None,
    folder_ids: Optional[List[str]] = None,
    export_as: str = "pptx",
    image_model: Optional[str] = None,
    image_style: Optional[str] = None,
    polling_interval: int = POLLING_INTERVAL,
    max_attempts: int = MAX_POLLING_ATTEMPTS
) -> Dict[str, Any]:
    """
    Generate a Campaign Wrap-Up presentation from template and automatically wait for completion.

    This is a convenience function that combines generate_wrap_up_presentation and
    wait_for_presentation_completion into a single call. It will start the generation
    using the predefined Campaign Wrap-Up Protocol template and then automatically
    poll every 30 seconds until the presentation is ready.

    Args:
        prompt: Text content, image URLs, and instructions for how to modify the template
        theme_id: Optional theme ID to override the template's default theme
        folder_ids: Optional list of folder IDs where the gamma should be stored
        export_as: Export format - "pdf" or "pptx" (default: pptx)
        image_model: Optional AI image model to use (e.g., "flux-1-pro", "imagen-4-pro")
        image_style: Optional style description for AI-generated images
        polling_interval: Time in seconds between status checks (default: 30)
        max_attempts: Maximum number of polling attempts (default: 10)

    Returns:
        Dictionary containing the final generation result or error information
    """
    logger.info("Starting Campaign Wrap-Up presentation generation with automatic completion waiting")

    # Start the generation
    generation_result = await generate_wrap_up_presentation(
        prompt=prompt,
        theme_id=theme_id,
        folder_ids=folder_ids,
        export_as=export_as,
        image_model=image_model,
        image_style=image_style
    )

    # Check if generation started successfully
    if "error" in generation_result:
        logger.error("Failed to start wrap-up presentation generation")
        return generation_result

    generation_id = generation_result.get("generationId")
    if not generation_id:
        logger.error("No generation ID returned from generation request")
        return {"error": "No generation ID returned from generation request"}

    logger.info(f"Wrap-Up generation started successfully with ID: {generation_id}")
    logger.info("Now waiting for completion...")

    # Wait for completion
    completion_result = await wait_for_presentation_completion(
        generation_id=generation_id,
        polling_interval=polling_interval,
        max_attempts=max_attempts
    )

    return completion_result


@mcp.tool()
async def generate_and_wait_for_standard_presentation(
    input_text: str,
    layout_format: str = "16x9",
    export_as: str = "pptx",
    polling_interval: int = POLLING_INTERVAL,
    max_attempts: int = MAX_POLLING_ATTEMPTS
) -> Dict[str, Any]:
    """
    Generate a standard presentation with Elcano theme and automatically wait for completion.

    This is a convenience function that combines generate_standard_presentation and
    wait_for_presentation_completion into a single call. It will start the generation
    with simple Elcano theme styling and then automatically poll every 30 seconds
    until the presentation is ready.

    Args:
        input_text: The markdown content for the presentation
        layout_format: Layout format for the presentation. Options: "16x9" (Traditional), "4x3" (Tall), "fluid" (Default/Fluid). Default: "16x9"
        export_as: Export format (default: pptx)
        polling_interval: Time in seconds between status checks (default: 30)
        max_attempts: Maximum number of polling attempts (default: 10)

    Returns:
        Dictionary containing the final generation result or error information
    """
    logger.info("Starting standard presentation generation with automatic completion waiting")

    # Start the generation
    generation_result = await generate_standard_presentation(
        input_text=input_text,
        layout_format=layout_format,
        export_as=export_as
    )

    # Check if generation started successfully
    if "error" in generation_result:
        logger.error("Failed to start standard presentation generation")
        return generation_result

    generation_id = generation_result.get("generationId")
    if not generation_id:
        logger.error("No generation ID returned from generation request")
        return {"error": "No generation ID returned from generation request"}

    logger.info(f"Standard generation started successfully with ID: {generation_id}")
    logger.info("Now waiting for completion...")

    # Wait for completion
    completion_result = await wait_for_presentation_completion(
        generation_id=generation_id,
        polling_interval=polling_interval,
        max_attempts=max_attempts
    )

    return completion_result


# Chart Brief Generation Functionality

class ChartType(Enum):
    """Supported chart types for Gamma presentations."""
    BAR = "bar"
    COLUMN = "column"
    LINE = "line"
    PIE = "pie"
    DONUT = "donut"
    SCATTER = "scatter"
    BUBBLE = "bubble"
    HEATMAP = "heatmap"
    AREA = "area"


@mcp.tool()
async def generate_chart_brief(
    chart_type: str,
    title: str,
    data: List[Dict[str, Any]],
    x_axis_title: str = "",
    y_axis_title: str = "",
    key_insight: str = "",
    color_palette: str = "Elcano brand colors",
    sort_order: str = ""
) -> Dict[str, Any]:
    """
    Generate a structured chart brief for Gamma AI presentations.
    
    This tool creates professional chart briefs that follow the Chart Brief Template
    documented in VICTORIA.md, ensuring high-quality visualizations in presentations.
    
    Args:
        chart_type: Type of chart (bar, column, line, pie, donut, scatter, bubble, heatmap, area)
        title: Clear, descriptive title for the chart
        data: List of data dictionaries containing the chart data
        x_axis_title: Title for X-axis (optional)
        y_axis_title: Title for Y-axis (optional)
        key_insight: Main takeaway to highlight (optional)
        color_palette: Color palette to use (default: Elcano brand colors)
        sort_order: How to organize the data (optional)
        
    Returns:
        Dictionary containing the formatted chart brief and metadata
    """
    try:
        # Validate chart type
        try:
            chart_enum = ChartType(chart_type.lower())
        except ValueError:
            return {
                "error": f"Invalid chart type '{chart_type}'. Supported types: {[t.value for t in ChartType]}"
            }
        
        # Get chart-specific instructions
        chart_instructions = _get_chart_instructions(chart_enum)
        
        # Build the chart brief
        brief = f"""**Chart Brief:**
- **Chart Type**: {chart_instructions['type_name']}
- **Title**: "{title}"
"""
        
        if x_axis_title:
            brief += f"- **X-Axis Title**: \"{x_axis_title}\"\n"
        if y_axis_title:
            brief += f"- **Y-Axis Title**: \"{y_axis_title}\"\n"
            
        brief += f"- **Data Labels**: {chart_instructions['data_labels']}\n"
        
        if sort_order:
            brief += f"- **Sorting**: {sort_order}\n"
        elif chart_instructions['default_sort']:
            brief += f"- **Sorting**: {chart_instructions['default_sort']}\n"
            
        brief += f"- **Color Palette**: Use {color_palette}\n"
        brief += f"- **Purpose**: {chart_instructions['purpose']}\n"
        
        if key_insight:
            brief += f"- **Key Insight**: {key_insight}\n"
            
        # Add data table
        brief += "\n**Data:**\n"
        brief += _format_data_table(data)
        
        return {
            "chart_brief": brief,
            "chart_type": chart_instructions['type_name'],
            "data_points": len(data),
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Error generating chart brief: {str(e)}")
        return {"error": f"Failed to generate chart brief: {str(e)}"}


def _get_chart_instructions(chart_type: ChartType) -> Dict[str, str]:
    """Get chart-specific instructions based on chart type."""
    
    instructions = {
        ChartType.BAR: {
            "type_name": "Horizontal Bar Chart",
            "purpose": "Compare values across different categories",
            "data_labels": "Show values on bars, formatted appropriately",
            "default_sort": "Sort bars from highest to lowest for easy comparison"
        },
        ChartType.COLUMN: {
            "type_name": "Vertical Column Chart", 
            "purpose": "Compare values across different categories",
            "data_labels": "Show values on top of columns, formatted appropriately",
            "default_sort": "Sort columns from highest to lowest for easy comparison"
        },
        ChartType.LINE: {
            "type_name": "Line Chart",
            "purpose": "Show trends and changes over time",
            "data_labels": "Add markers for each data point to improve readability",
            "default_sort": "Sort by time/sequence in chronological order"
        },
        ChartType.PIE: {
            "type_name": "Pie Chart",
            "purpose": "Show proportions of each category as part of the whole",
            "data_labels": "Label each slice with category name and percentage",
            "default_sort": "Sort slices from largest to smallest, limit to 5 categories max"
        },
        ChartType.DONUT: {
            "type_name": "Donut Chart",
            "purpose": "Show proportions with emphasis on the total in the center",
            "data_labels": "Label each segment with category name and percentage",
            "default_sort": "Sort segments from largest to smallest, limit to 5 categories max"
        },
        ChartType.SCATTER: {
            "type_name": "Scatter Plot",
            "purpose": "Show relationships and correlations between two variables",
            "data_labels": "Label key data points, include trendline if correlation exists",
            "default_sort": None
        },
        ChartType.BUBBLE: {
            "type_name": "Bubble Chart",
            "purpose": "Show relationships between three variables using position and size",
            "data_labels": "Label significant bubbles, use size to represent third variable",
            "default_sort": None
        },
        ChartType.HEATMAP: {
            "type_name": "Heatmap",
            "purpose": "Show patterns and intensity across two categorical dimensions",
            "data_labels": "Use color intensity to represent values, include legend",
            "default_sort": "Arrange categories logically (e.g., time, alphabetical)"
        },
        ChartType.AREA: {
            "type_name": "Area Chart",
            "purpose": "Show cumulative totals and trends over time",
            "data_labels": "Label key points and show total values",
            "default_sort": "Sort by time/sequence in chronological order"
        }
    }
    
    return instructions.get(chart_type, {
        "type_name": "Chart",
        "purpose": "Visualize the data effectively",
        "data_labels": "Include appropriate labels",
        "default_sort": None
    })


def _format_data_table(data: List[Dict[str, Any]]) -> str:
    """Format data as a markdown table."""
    if not data:
        return "| No data provided |\n|---|\n"
        
    # Get headers from first row
    headers = list(data[0].keys())
    
    # Create table header
    table = "| " + " | ".join(headers) + " |\n"
    table += "|" + "|".join(["---"] * len(headers)) + "|\n"
    
    # Add data rows
    for row in data:
        values = [str(row.get(header, "")) for header in headers]
        table += "| " + " | ".join(values) + " |\n"
        
    return table


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
