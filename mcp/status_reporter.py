#!/usr/bin/env python3
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

"""
Status Reporter MCP Server for Victoria Terminal.

This MCP server provides a ReportStatus tool that allows the LLM agent
to send structured status updates back to the All-Time Quarterback orchestrator.

The server is configured via environment variables:
- ORCHESTRATOR_URL: URL of the orchestrator's /status endpoint
- JOB_ID: Unique identifier for the current task/job

If these variables are not set, the MCP server will not be configured
(following the pattern of other optional MCP servers in Victoria Terminal).
"""

from __future__ import annotations

import logging
import os
import sys
from enum import Enum
from typing import Any, Dict, Optional

import httpx
from mcp.server.fastmcp import FastMCP

# Configure logging to stderr (not stdout for STDIO transport)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("status-reporter")

# Constants
USER_AGENT = "victoria-terminal/1.0"
DEFAULT_TIMEOUT = 30.0


class TaskStatus(str, Enum):
    """Valid status values for task reporting."""

    PENDING = "pending"
    ASSIGNED = "assigned"
    RUNNING = "running"
    ANALYZING = "analyzing"
    SUCCESS = "success"
    ERROR = "error"
    CANCELLED = "cancelled"


def get_orchestrator_url() -> Optional[str]:
    """Get the orchestrator URL from environment."""
    url = os.environ.get("ORCHESTRATOR_URL")
    if url:
        return url.rstrip("/")
    return None


def get_job_id() -> Optional[str]:
    """Get the current job ID from environment."""
    return os.environ.get("JOB_ID")


async def send_status_update(
    status: TaskStatus,
    message: Optional[str] = None,
    progress: Optional[float] = None,
    crush_session_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Send a status update to the orchestrator.

    Args:
        status: Current task status
        message: Optional status message
        progress: Optional progress percentage (0-100)
        crush_session_id: Optional Crush session ID for log linking

    Returns:
        Response from the orchestrator or error information
    """
    orchestrator_url = get_orchestrator_url()
    job_id = get_job_id()

    if not orchestrator_url:
        return {"error": "ORCHESTRATOR_URL not configured", "sent": False}

    if not job_id:
        return {"error": "JOB_ID not configured", "sent": False}

    payload = {
        "job_id": job_id,
        "status": status.value,
    }

    if message:
        payload["message"] = message
    if progress is not None:
        payload["progress"] = progress
    if crush_session_id:
        payload["crush_session_id"] = crush_session_id

    logger.info(f"Sending status update: {status.value}" + (f" - {message}" if message else ""))

    try:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            response = await client.post(
                f"{orchestrator_url}/status",
                json=payload,
                headers={
                    "User-Agent": USER_AGENT,
                    "Content-Type": "application/json",
                },
            )
            response.raise_for_status()
            result = response.json()
            logger.info("Status update sent successfully")
            return {"sent": True, "response": result}

    except httpx.TimeoutException as e:
        error_msg = f"Request timeout: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg, "sent": False}
    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP error: {e.response.status_code} - {e.response.text}"
        logger.error(error_msg)
        return {"error": error_msg, "sent": False}
    except httpx.RequestError as e:
        error_msg = f"Request error: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg, "sent": False}
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg, "sent": False}


@mcp.tool()
async def report_status(
    status: str,
    message: Optional[str] = None,
    progress: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Report the current task status to the All-Time Quarterback orchestrator.

    Use this tool to keep the orchestrator informed about task progress.
    Call this at key milestones during task execution.

    IMPORTANT: Always call this tool with status="success" when the task is
    complete, or status="error" if the task fails.

    Args:
        status: Current status. Must be one of:
            - "running": Task is actively being processed
            - "analyzing": Task is in analysis phase
            - "success": Task completed successfully
            - "error": Task failed with an error
        message: Optional human-readable status message describing what's happening
                 or the result/error details
        progress: Optional progress percentage (0-100) for long-running tasks

    Returns:
        Dictionary containing:
        - sent: Boolean indicating if the update was sent successfully
        - response: The orchestrator's response (if successful)
        - error: Error message (if failed)

    Examples:
        # Report that analysis has started
        report_status(status="analyzing", message="Analyzing sales data from Q4")

        # Report progress on a long task
        report_status(status="running", message="Processing files", progress=45.0)

        # Report successful completion
        report_status(status="success", message="Analysis complete. Found 3 key insights.")

        # Report an error
        report_status(status="error", message="Failed to connect to database")
    """
    # Validate status
    valid_statuses = {"running", "analyzing", "success", "error"}
    if status not in valid_statuses:
        return {
            "error": f"Invalid status '{status}'. Must be one of: {', '.join(valid_statuses)}",
            "sent": False,
        }

    # Map string to enum
    status_map = {
        "running": TaskStatus.RUNNING,
        "analyzing": TaskStatus.ANALYZING,
        "success": TaskStatus.SUCCESS,
        "error": TaskStatus.ERROR,
    }
    task_status = status_map[status]

    # Validate progress if provided
    if progress is not None:
        if not 0 <= progress <= 100:
            return {
                "error": "Progress must be between 0 and 100",
                "sent": False,
            }

    return await send_status_update(
        status=task_status,
        message=message,
        progress=progress,
    )


@mcp.tool()
async def report_started(message: Optional[str] = None) -> Dict[str, Any]:
    """
    Report that the task has started.

    This is a convenience wrapper around report_status for the common case
    of reporting task start.

    Args:
        message: Optional message describing what the task will do

    Returns:
        Dictionary with send status and any error information
    """
    return await send_status_update(
        status=TaskStatus.RUNNING,
        message=message or "Task started",
    )


@mcp.tool()
async def report_complete(
    message: Optional[str] = None,
    crush_session_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Report that the task has completed successfully.

    This is a convenience wrapper around report_status for the common case
    of reporting successful completion.

    IMPORTANT: Always call this (or report_status with status="success")
    when the task completes successfully.

    Args:
        message: Optional message describing the result or outcome
        crush_session_id: Optional Crush session ID for linking to logs

    Returns:
        Dictionary with send status and any error information
    """
    return await send_status_update(
        status=TaskStatus.SUCCESS,
        message=message or "Task completed successfully",
        crush_session_id=crush_session_id,
    )


@mcp.tool()
async def report_error(
    error_message: str,
    crush_session_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Report that the task has failed with an error.

    This is a convenience wrapper around report_status for the common case
    of reporting task failure.

    IMPORTANT: Always call this (or report_status with status="error")
    when the task fails.

    Args:
        error_message: Description of what went wrong
        crush_session_id: Optional Crush session ID for linking to logs

    Returns:
        Dictionary with send status and any error information
    """
    return await send_status_update(
        status=TaskStatus.ERROR,
        message=error_message,
        crush_session_id=crush_session_id,
    )


@mcp.tool()
async def get_job_info() -> Dict[str, Any]:
    """
    Get information about the current job/task.

    Returns the job ID and orchestrator URL if configured, or indicates
    that orchestration is not configured.

    Returns:
        Dictionary containing:
        - configured: Boolean indicating if orchestration is configured
        - job_id: The current job ID (if configured)
        - orchestrator_url: The orchestrator URL (if configured)
    """
    orchestrator_url = get_orchestrator_url()
    job_id = get_job_id()

    if orchestrator_url and job_id:
        return {
            "configured": True,
            "job_id": job_id,
            "orchestrator_url": orchestrator_url,
        }
    else:
        return {
            "configured": False,
            "message": "Orchestration not configured. Running in standalone mode.",
        }


if __name__ == "__main__":
    # Check if orchestration is configured
    orchestrator_url = get_orchestrator_url()
    job_id = get_job_id()

    if not orchestrator_url or not job_id:
        logger.warning(
            "Status Reporter MCP Server not starting: "
            "ORCHESTRATOR_URL and JOB_ID environment variables are required"
        )
        # Exit gracefully - this is expected when not running in orchestrated mode
        sys.exit(0)

    logger.info("Starting Status Reporter MCP Server")
    logger.info(f"Orchestrator URL: {orchestrator_url}")
    logger.info(f"Job ID: {job_id}")

    try:
        mcp.run(transport="stdio")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)
