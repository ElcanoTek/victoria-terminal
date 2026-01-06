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

This MCP server provides tools that allow the LLM agent to:
1. Send structured status updates back to the All-Time Quarterback orchestrator
2. Submit Crush session logs for the completed task

The server is configured via environment variables:
- ORCHESTRATOR_URL: URL of the orchestrator's /status endpoint
- JOB_ID: Unique identifier for the current task/job
- VICTORIA_HOME: Path to the Victoria home directory (for finding Crush logs)

If these variables are not set, the MCP server will not be configured
(following the pattern of other optional MCP servers in Victoria Terminal).
"""

from __future__ import annotations

import logging
import os
import sqlite3
import sys
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

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
CRUSH_DB_NAME = "crush.db"
CRUSH_DATA_DIR = ".crush"


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


def get_victoria_home() -> Path:
    """Get the Victoria home directory."""
    return Path(os.environ.get("VICTORIA_HOME", Path.home() / "Victoria"))


def get_crush_db_path() -> Optional[Path]:
    """Find the Crush database file."""
    victoria_home = get_victoria_home()
    
    # Check in Victoria home's .crush directory
    db_path = victoria_home / CRUSH_DATA_DIR / CRUSH_DB_NAME
    if db_path.exists():
        return db_path
    
    # Check in current working directory's .crush
    cwd_path = Path.cwd() / CRUSH_DATA_DIR / CRUSH_DB_NAME
    if cwd_path.exists():
        return cwd_path
    
    # Check in XDG data directory
    xdg_data = os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")
    xdg_path = Path(xdg_data) / "crush" / CRUSH_DB_NAME
    if xdg_path.exists():
        return xdg_path
    
    return None


def read_crush_sessions() -> List[Dict[str, Any]]:
    """Read all sessions from the Crush database."""
    db_path = get_crush_db_path()
    if not db_path:
        logger.warning("Crush database not found")
        return []
    
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get sessions (excluding child sessions)
        cursor.execute("""
            SELECT id, title, prompt_tokens, completion_tokens, cost, 
                   created_at, updated_at
            FROM sessions
            WHERE parent_session_id IS NULL
            ORDER BY updated_at DESC
        """)
        
        sessions = []
        for row in cursor.fetchall():
            session = {
                "id": row["id"],
                "title": row["title"],
                "prompt_tokens": row["prompt_tokens"],
                "completion_tokens": row["completion_tokens"],
                "cost": row["cost"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "messages": [],
            }
            
            # Get messages for this session
            cursor.execute("""
                SELECT id, role, parts, model, provider, created_at, finished_at
                FROM messages
                WHERE session_id = ?
                ORDER BY created_at ASC
            """, (row["id"],))
            
            for msg_row in cursor.fetchall():
                session["messages"].append({
                    "id": msg_row["id"],
                    "role": msg_row["role"],
                    "content": msg_row["parts"],
                    "model": msg_row["model"],
                    "provider": msg_row["provider"],
                    "created_at": msg_row["created_at"],
                    "finished_at": msg_row["finished_at"],
                })
            
            sessions.append(session)
        
        conn.close()
        return sessions
        
    except sqlite3.Error as e:
        logger.error(f"Error reading Crush database: {e}")
        return []


def get_latest_session() -> Optional[Dict[str, Any]]:
    """Get the most recent Crush session."""
    sessions = read_crush_sessions()
    return sessions[0] if sessions else None


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
    submit_logs: bool = True,
) -> Dict[str, Any]:
    """
    Report that the task has completed successfully.

    This is a convenience wrapper around report_status for the common case
    of reporting successful completion.

    IMPORTANT: Always call this (or report_status with status="success")
    when the task completes successfully.

    Args:
        message: Optional message describing the result or outcome
        submit_logs: Whether to also submit Crush logs (default: True)

    Returns:
        Dictionary with send status and any error information
    """
    result = {"status_sent": False, "logs_sent": False}
    
    # Get the latest session ID for linking
    session = get_latest_session()
    crush_session_id = session["id"] if session else None
    
    # Send status update
    status_result = await send_status_update(
        status=TaskStatus.SUCCESS,
        message=message or "Task completed successfully",
        crush_session_id=crush_session_id,
    )
    result["status_sent"] = status_result.get("sent", False)
    result["status_result"] = status_result
    
    # Submit logs if requested
    if submit_logs and session:
        logs_result = await submit_crush_logs()
        result["logs_sent"] = logs_result.get("sent", False)
        result["logs_result"] = logs_result
    
    return result


@mcp.tool()
async def report_error(
    error_message: str,
    submit_logs: bool = True,
) -> Dict[str, Any]:
    """
    Report that the task has failed with an error.

    This is a convenience wrapper around report_status for the common case
    of reporting task failure.

    IMPORTANT: Always call this (or report_status with status="error")
    when the task fails.

    Args:
        error_message: Description of what went wrong
        submit_logs: Whether to also submit Crush logs (default: True)

    Returns:
        Dictionary with send status and any error information
    """
    result = {"status_sent": False, "logs_sent": False}
    
    # Get the latest session ID for linking
    session = get_latest_session()
    crush_session_id = session["id"] if session else None
    
    # Send status update
    status_result = await send_status_update(
        status=TaskStatus.ERROR,
        message=error_message,
        crush_session_id=crush_session_id,
    )
    result["status_sent"] = status_result.get("sent", False)
    result["status_result"] = status_result
    
    # Submit logs if requested
    if submit_logs and session:
        logs_result = await submit_crush_logs()
        result["logs_sent"] = logs_result.get("sent", False)
        result["logs_result"] = logs_result
    
    return result


@mcp.tool()
async def submit_crush_logs(session_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Submit Crush session logs to the All-Time Quarterback orchestrator.

    This tool reads the conversation history from the local Crush database
    and uploads it to the orchestrator for viewing in the dashboard.

    Call this tool when the task is complete to preserve the full conversation
    history. It's automatically called by report_complete() and report_error().

    Args:
        session_id: Optional specific session ID to submit. If not provided,
                   submits the most recent session.

    Returns:
        Dictionary containing:
        - sent: Boolean indicating if logs were sent successfully
        - session_id: The session ID that was submitted
        - message_count: Number of messages in the session
        - error: Error message (if failed)

    Example:
        # Submit logs for the current session
        submit_crush_logs()

        # Submit logs for a specific session
        submit_crush_logs(session_id="abc123")
    """
    orchestrator_url = get_orchestrator_url()
    job_id = get_job_id()

    if not orchestrator_url:
        return {"error": "ORCHESTRATOR_URL not configured", "sent": False}

    if not job_id:
        return {"error": "JOB_ID not configured", "sent": False}

    # Get the session to submit
    if session_id:
        sessions = read_crush_sessions()
        session = next((s for s in sessions if s["id"] == session_id), None)
        if not session:
            return {"error": f"Session {session_id} not found", "sent": False}
    else:
        session = get_latest_session()
        if not session:
            return {"error": "No Crush sessions found", "sent": False}

    logger.info(f"Submitting logs for session {session['id']} with {len(session['messages'])} messages")

    payload = {
        "job_id": job_id,
        "session": session,
    }

    try:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            response = await client.post(
                f"{orchestrator_url}/logs",
                json=payload,
                headers={
                    "User-Agent": USER_AGENT,
                    "Content-Type": "application/json",
                },
            )
            response.raise_for_status()
            logger.info("Logs submitted successfully")
            return {
                "sent": True,
                "session_id": session["id"],
                "message_count": len(session["messages"]),
            }

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
        - crush_db_path: Path to the Crush database (if found)
        - session_count: Number of Crush sessions available
    """
    orchestrator_url = get_orchestrator_url()
    job_id = get_job_id()
    crush_db = get_crush_db_path()
    sessions = read_crush_sessions()

    if orchestrator_url and job_id:
        return {
            "configured": True,
            "job_id": job_id,
            "orchestrator_url": orchestrator_url,
            "crush_db_path": str(crush_db) if crush_db else None,
            "session_count": len(sessions),
        }
    else:
        return {
            "configured": False,
            "message": "Orchestration not configured. Running in standalone mode.",
            "crush_db_path": str(crush_db) if crush_db else None,
            "session_count": len(sessions),
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
    
    crush_db = get_crush_db_path()
    if crush_db:
        logger.info(f"Crush database: {crush_db}")
    else:
        logger.warning("Crush database not found - log submission will not work")

    try:
        mcp.run(transport="stdio")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)
