#!/usr/bin/env python3
"""AWS SES + S3 Email Polling MCP Server for Victoria Terminal

This MCP server provides tools for Victoria to poll an S3 bucket for emails
that have been deposited by AWS SES. It allows the agent to:
- Check for new emails since the last check
- Get email details (subject, from, to, date, attachments)
- Download attachments (especially CSV files) for data analysis

Setup Requirements:
1. AWS SES configured to receive emails and save to S3
2. S3 bucket with emails stored in a prefix (e.g., emails/)
3. AWS credentials with S3 read access

Environment Variables:
- AWS_ACCESS_KEY_ID: AWS access key
- AWS_SECRET_ACCESS_KEY: AWS secret key
- AWS_REGION: AWS region (e.g., us-east-2)
- EMAIL_S3_BUCKET: S3 bucket name (e.g., victoria-email-inbox)
- EMAIL_S3_PREFIX: S3 prefix for emails (default: emails/)
- EMAIL_ATTACHMENT_DIR: Local directory for downloaded attachments
- EMAIL_LAST_CHECK_FILE: File to store last check timestamp
"""

import asyncio
import email
import logging
import os
from datetime import datetime, timezone
from email.header import decode_header
from email.message import Message
from pathlib import Path
from typing import Any, Dict, List, Optional

import boto3
from mcp.server.fastmcp import FastMCP

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# --- Configuration ---
S3_BUCKET = os.environ.get("EMAIL_S3_BUCKET", "victoria-email-inbox")
S3_PREFIX = os.environ.get("EMAIL_S3_PREFIX", "emails/")
ATTACHMENT_DOWNLOAD_DIR = os.environ.get(
    "EMAIL_ATTACHMENT_DIR",
    os.path.expanduser("~/Victoria/email_attachments")
)
LAST_CHECK_FILE = os.environ.get(
    "EMAIL_LAST_CHECK_FILE",
    os.path.expanduser("~/Victoria/email_last_checked.txt")
)
AWS_REGION = os.environ.get("AWS_REGION", "us-east-2")

# Ensure directories exist
Path(ATTACHMENT_DOWNLOAD_DIR).mkdir(parents=True, exist_ok=True)
Path(LAST_CHECK_FILE).parent.mkdir(parents=True, exist_ok=True)

# Initialize FastMCP
mcp = FastMCP("ses_s3_email")

# Initialize S3 client
s3_client = boto3.client("s3", region_name=AWS_REGION)


def decode_email_header(header_value: str) -> str:
    """Decode email header that may contain encoded words."""
    if not header_value:
        return ""
    decoded_parts = decode_header(header_value)
    result = []
    for part, charset in decoded_parts:
        if isinstance(part, bytes):
            result.append(part.decode(charset or "utf-8", errors="replace"))
        else:
            result.append(part)
    return "".join(result)


def get_last_checked_timestamp() -> datetime:
    """Reads the timestamp of the last successful email check."""
    if not os.path.exists(LAST_CHECK_FILE):
        # Default to a very old date if never checked
        return datetime(2000, 1, 1, tzinfo=timezone.utc)
    with open(LAST_CHECK_FILE, "r") as f:
        iso_ts = f.read().strip()
        if not iso_ts:
            return datetime(2000, 1, 1, tzinfo=timezone.utc)
        return datetime.fromisoformat(iso_ts)


def update_last_checked_timestamp(ts: Optional[datetime] = None):
    """Updates the timestamp to the current time or a specified time."""
    if ts is None:
        ts = datetime.now(timezone.utc)
    with open(LAST_CHECK_FILE, "w") as f:
        f.write(ts.isoformat())
    logger.info(f"Updated last checked timestamp to {ts.isoformat()}")


# --- MCP Tools ---

@mcp.tool()
async def check_inbox(since_last_check: bool = True) -> Dict[str, Any]:
    """Check the email inbox for messages.
    
    Args:
        since_last_check: If True, only return emails since last check.
                         If False, return all emails in the inbox.
    
    Returns:
        Dictionary with list of emails found.
    """
    last_checked = get_last_checked_timestamp() if since_last_check else datetime(2000, 1, 1, tzinfo=timezone.utc)
    logger.info(f"Checking inbox for emails since {last_checked.isoformat()}")
    
    emails_found = []
    max_last_modified = last_checked

    try:
        paginator = s3_client.get_paginator("list_objects_v2")
        pages = paginator.paginate(Bucket=S3_BUCKET, Prefix=S3_PREFIX)

        for page in pages:
            if "Contents" not in page:
                continue
            for obj in page["Contents"]:
                # Skip the prefix itself
                if obj["Key"] == S3_PREFIX:
                    continue
                    
                last_modified = obj["LastModified"]
                if last_modified > last_checked:
                    emails_found.append({
                        "s3_key": obj["Key"],
                        "size_bytes": obj["Size"],
                        "received_at": last_modified.isoformat(),
                    })
                    if last_modified > max_last_modified:
                        max_last_modified = last_modified

        # Sort by received date (newest first)
        emails_found.sort(key=lambda x: x["received_at"], reverse=True)

        # Update the timestamp
        if emails_found:
            update_last_checked_timestamp(max_last_modified)
        else:
            update_last_checked_timestamp()

        return {
            "status": "success",
            "new_email_count": len(emails_found),
            "checked_since": last_checked.isoformat(),
            "emails": emails_found,
        }

    except Exception as e:
        logger.error(f"Failed to check inbox: {e}")
        return {"status": "error", "error": str(e)}


@mcp.tool()
async def get_email(s3_key: str) -> Dict[str, Any]:
    """Get details of a specific email from the inbox.
    
    Args:
        s3_key: The S3 object key of the email file.
    
    Returns:
        Dictionary with parsed email details including headers and attachment info.
    """
    try:
        response = s3_client.get_object(Bucket=S3_BUCKET, Key=s3_key)
        raw_email = response["Body"].read()
        msg: Message = email.message_from_bytes(raw_email)

        # Parse attachments
        attachments = []
        for part in msg.walk():
            if part.get_content_maintype() == "multipart":
                continue
            content_disposition = part.get("Content-Disposition", "")
            if "attachment" in content_disposition or part.get_filename():
                filename = part.get_filename()
                if filename:
                    filename = decode_email_header(filename)
                    payload = part.get_payload(decode=True)
                    attachments.append({
                        "filename": filename,
                        "content_type": part.get_content_type(),
                        "size_bytes": len(payload) if payload else 0,
                    })

        # Get email body
        body_plain = ""
        body_html = ""
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = part.get("Content-Disposition", "")
            
            if "attachment" not in content_disposition:
                if content_type == "text/plain":
                    payload = part.get_payload(decode=True)
                    if payload:
                        body_plain = payload.decode("utf-8", errors="replace")
                elif content_type == "text/html":
                    payload = part.get_payload(decode=True)
                    if payload:
                        body_html = payload.decode("utf-8", errors="replace")

        details = {
            "s3_key": s3_key,
            "subject": decode_email_header(msg.get("Subject", "")),
            "from": decode_email_header(msg.get("From", "")),
            "to": decode_email_header(msg.get("To", "")),
            "date": msg.get("Date", ""),
            "message_id": msg.get("Message-ID", ""),
            "body_preview": body_plain[:500] if body_plain else body_html[:500],
            "attachment_count": len(attachments),
            "attachments": attachments,
        }

        return {"status": "success", "email": details}

    except Exception as e:
        logger.error(f"Failed to get email {s3_key}: {e}")
        return {"status": "error", "s3_key": s3_key, "error": str(e)}


@mcp.tool()
async def download_attachment(
    s3_key: str,
    filename: str,
    output_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """Download a specific attachment from an email.
    
    Args:
        s3_key: The S3 object key of the email file.
        filename: The filename of the attachment to download.
        output_dir: Optional directory to save the file. Defaults to EMAIL_ATTACHMENT_DIR.
    
    Returns:
        Dictionary with the local file path of the downloaded attachment.
    """
    try:
        response = s3_client.get_object(Bucket=S3_BUCKET, Key=s3_key)
        raw_email = response["Body"].read()
        msg: Message = email.message_from_bytes(raw_email)

        download_dir = output_dir or ATTACHMENT_DOWNLOAD_DIR
        Path(download_dir).mkdir(parents=True, exist_ok=True)

        for part in msg.walk():
            if part.get_content_maintype() == "multipart":
                continue
            
            part_filename = part.get_filename()
            if part_filename:
                part_filename = decode_email_header(part_filename)
                
                if part_filename == filename:
                    # Found the attachment
                    payload = part.get_payload(decode=True)
                    
                    # Sanitize filename
                    safe_filename = Path(filename).name
                    output_path = Path(download_dir) / safe_filename

                    # Prevent overwriting by adding a counter
                    counter = 1
                    stem, suffix = output_path.stem, output_path.suffix
                    while output_path.exists():
                        output_path = Path(download_dir) / f"{stem}_{counter}{suffix}"
                        counter += 1

                    # Write the file
                    with open(output_path, "wb") as f:
                        f.write(payload)

                    logger.info(f"Downloaded attachment: {output_path}")
                    
                    return {
                        "status": "success",
                        "filename": filename,
                        "saved_to": str(output_path),
                        "size_bytes": len(payload),
                        "content_type": part.get_content_type(),
                    }

        return {
            "status": "error",
            "error": f"Attachment '{filename}' not found in email",
        }

    except Exception as e:
        logger.error(f"Failed to download attachment: {e}")
        return {"status": "error", "error": str(e)}


@mcp.tool()
async def download_all_csv_attachments(
    s3_key: Optional[str] = None,
    output_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """Download all CSV attachments from one email or all new emails.
    
    Args:
        s3_key: Optional S3 key of a specific email. If not provided,
               downloads CSVs from all emails received since last check.
        output_dir: Optional directory to save files. Defaults to EMAIL_ATTACHMENT_DIR.
    
    Returns:
        Dictionary with list of downloaded CSV files.
    """
    try:
        download_dir = output_dir or ATTACHMENT_DOWNLOAD_DIR
        Path(download_dir).mkdir(parents=True, exist_ok=True)
        
        downloaded_files = []
        
        # Get list of emails to process
        if s3_key:
            email_keys = [s3_key]
        else:
            # Get all new emails
            inbox_result = await check_inbox(since_last_check=False)
            if inbox_result["status"] != "success":
                return inbox_result
            email_keys = [e["s3_key"] for e in inbox_result["emails"]]

        for key in email_keys:
            response = s3_client.get_object(Bucket=S3_BUCKET, Key=key)
            raw_email = response["Body"].read()
            msg: Message = email.message_from_bytes(raw_email)
            
            email_subject = decode_email_header(msg.get("Subject", "unknown"))
            email_from = decode_email_header(msg.get("From", "unknown"))

            for part in msg.walk():
                if part.get_content_maintype() == "multipart":
                    continue
                
                filename = part.get_filename()
                if filename:
                    filename = decode_email_header(filename)
                    content_type = part.get_content_type()
                    
                    # Check if it's a CSV
                    is_csv = (
                        content_type == "text/csv" or
                        filename.lower().endswith(".csv")
                    )
                    
                    if is_csv:
                        payload = part.get_payload(decode=True)
                        
                        # Sanitize filename
                        safe_filename = Path(filename).name
                        output_path = Path(download_dir) / safe_filename

                        # Prevent overwriting
                        counter = 1
                        stem, suffix = output_path.stem, output_path.suffix
                        while output_path.exists():
                            output_path = Path(download_dir) / f"{stem}_{counter}{suffix}"
                            counter += 1

                        with open(output_path, "wb") as f:
                            f.write(payload)

                        downloaded_files.append({
                            "filename": filename,
                            "saved_to": str(output_path),
                            "size_bytes": len(payload),
                            "from_email": email_from,
                            "email_subject": email_subject,
                        })
                        
                        logger.info(f"Downloaded CSV: {output_path}")

        return {
            "status": "success",
            "emails_processed": len(email_keys),
            "csv_files_downloaded": len(downloaded_files),
            "files": downloaded_files,
            "download_directory": download_dir,
        }

    except Exception as e:
        logger.error(f"Failed to download CSV attachments: {e}")
        return {"status": "error", "error": str(e)}


@mcp.tool()
async def get_inbox_stats() -> Dict[str, Any]:
    """Get statistics about the email inbox.
    
    Returns:
        Dictionary with inbox statistics.
    """
    try:
        total_emails = 0
        total_size = 0
        oldest_email = None
        newest_email = None

        paginator = s3_client.get_paginator("list_objects_v2")
        pages = paginator.paginate(Bucket=S3_BUCKET, Prefix=S3_PREFIX)

        for page in pages:
            if "Contents" not in page:
                continue
            for obj in page["Contents"]:
                if obj["Key"] == S3_PREFIX:
                    continue
                total_emails += 1
                total_size += obj["Size"]
                
                if oldest_email is None or obj["LastModified"] < oldest_email:
                    oldest_email = obj["LastModified"]
                if newest_email is None or obj["LastModified"] > newest_email:
                    newest_email = obj["LastModified"]

        last_checked = get_last_checked_timestamp()

        return {
            "status": "success",
            "stats": {
                "total_emails": total_emails,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "oldest_email": oldest_email.isoformat() if oldest_email else None,
                "newest_email": newest_email.isoformat() if newest_email else None,
                "last_checked": last_checked.isoformat(),
                "s3_bucket": S3_BUCKET,
                "s3_prefix": S3_PREFIX,
            },
        }

    except Exception as e:
        logger.error(f"Failed to get inbox stats: {e}")
        return {"status": "error", "error": str(e)}


if __name__ == "__main__":
    logger.info(f"Starting SES S3 Email MCP Server")
    logger.info(f"  Bucket: {S3_BUCKET}")
    logger.info(f"  Prefix: {S3_PREFIX}")
    logger.info(f"  Region: {AWS_REGION}")
    asyncio.run(mcp.run())
