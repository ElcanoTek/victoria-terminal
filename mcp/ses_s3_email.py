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
import re
from datetime import datetime, timezone
from email.header import decode_header
from email.message import Message
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import unquote, urlparse

import boto3
import httpx
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


# Common file extensions that indicate downloadable files
DOWNLOAD_EXTENSIONS = {
    # Documents
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".odt", ".ods", ".odp", ".rtf", ".txt",
    # Data files
    ".csv", ".json", ".xml", ".yaml", ".yml",
    # Archives
    ".zip", ".tar", ".gz", ".rar", ".7z", ".bz2",
    # Images
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg", ".webp",
    # Media
    ".mp3", ".mp4", ".wav", ".avi", ".mov", ".mkv",
    # Code/Dev
    ".py", ".js", ".ts", ".html", ".css", ".sql",
    # Other
    ".exe", ".dmg", ".pkg", ".deb", ".rpm", ".apk",
}


def extract_urls_from_text(text: str) -> List[str]:
    """Extract URLs from plain text using regex."""
    # URL pattern that captures most common URL formats
    url_pattern = r'https?://[^\s<>"\')\]}>]+'
    urls = re.findall(url_pattern, text)
    # Clean up trailing punctuation that might be captured
    cleaned = []
    for url in urls:
        url = url.rstrip('.,;:!?')
        if url:
            cleaned.append(url)
    return cleaned


def extract_urls_from_html(html: str) -> List[Dict[str, str]]:
    """Extract URLs from HTML anchor tags with their link text."""
    # Pattern to match <a> tags and extract href and text
    link_pattern = r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>([^<]*)</a>'
    matches = re.findall(link_pattern, html, re.IGNORECASE)

    links = []
    for href, text in matches:
        if href.startswith(('http://', 'https://')):
            links.append({
                "url": href,
                "text": text.strip() if text else "",
            })
    return links


def classify_url(url: str) -> Dict[str, Any]:
    """Classify a URL and determine if it's likely a download link."""
    parsed = urlparse(url)
    path = unquote(parsed.path)

    # Extract filename from URL path
    filename = Path(path).name if path else ""
    extension = Path(path).suffix.lower() if path else ""

    # Check if extension indicates a downloadable file
    is_download_likely = extension in DOWNLOAD_EXTENSIONS

    # Check for common download indicators in URL (includes API patterns)
    download_keywords = [
        'download', 'attachment', 'file', 'export', 'get',
        'report', 'generate', 'csv', 'xlsx', 'pdf',
        'api/download', 'api/export', 'api/report',
    ]
    has_download_keyword = any(kw in url.lower() for kw in download_keywords)

    # Check query parameters for download-related params
    query_lower = parsed.query.lower()
    download_params = ['format=csv', 'format=xlsx', 'format=pdf', 'type=csv',
                       'export=', 'download=', 'action=download', 'action=export']
    has_download_param = any(p in query_lower for p in download_params)

    return {
        "url": url,
        "domain": parsed.netloc,
        "filename": filename if filename else None,
        "extension": extension if extension else None,
        "is_download_likely": is_download_likely or has_download_keyword or has_download_param,
        "has_download_keyword": has_download_keyword,
        "has_download_param": has_download_param,
    }


def get_filename_from_response(response: httpx.Response, url: str) -> str:
    """Extract filename from HTTP response headers or URL."""
    # Try Content-Disposition header first
    content_disposition = response.headers.get("content-disposition", "")
    if content_disposition:
        # Try to extract filename from Content-Disposition
        filename_match = re.search(
            r'filename[*]?=["\']?(?:UTF-8\'\')?([^"\';\n]+)',
            content_disposition,
            re.IGNORECASE
        )
        if filename_match:
            return unquote(filename_match.group(1).strip())

    # Fall back to URL path
    parsed = urlparse(url)
    path = unquote(parsed.path)
    filename = Path(path).name

    if filename and '.' in filename:
        return filename

    # Generate a filename based on content type
    content_type = response.headers.get("content-type", "").lower()
    extension_map = {
        # Document types
        "application/pdf": ".pdf",
        "text/csv": ".csv",
        "application/csv": ".csv",
        "text/comma-separated-values": ".csv",
        "application/json": ".json",
        "application/xml": ".xml",
        "text/xml": ".xml",
        "text/plain": ".txt",
        # Microsoft Office
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
        "application/vnd.ms-excel": ".xls",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
        "application/msword": ".doc",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation": ".pptx",
        "application/vnd.ms-powerpoint": ".ppt",
        # Archives
        "application/zip": ".zip",
        "application/x-gzip": ".gz",
        "application/gzip": ".gz",
        "application/x-tar": ".tar",
        "application/x-rar-compressed": ".rar",
        # Images
        "image/png": ".png",
        "image/jpeg": ".jpg",
        "image/gif": ".gif",
        "image/svg+xml": ".svg",
        # Octet-stream often used for generic binary downloads
        "application/octet-stream": "",  # Will need better handling
    }

    for mime, ext in extension_map.items():
        if mime in content_type:
            if ext:
                return f"download_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
            else:
                # For octet-stream, try to guess from URL or just use .bin
                parsed = urlparse(url)
                url_ext = Path(unquote(parsed.path)).suffix.lower()
                if url_ext and url_ext in DOWNLOAD_EXTENSIONS:
                    return f"download_{datetime.now().strftime('%Y%m%d_%H%M%S')}{url_ext}"
                return f"download_{datetime.now().strftime('%Y%m%d_%H%M%S')}.bin"

    return f"download_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


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


@mcp.tool()
async def extract_download_links(
    s3_key: str,
    download_likely_only: bool = False,
) -> Dict[str, Any]:
    """Extract potential download links from an email body.

    This tool parses the email body (both plain text and HTML) to find URLs
    that may be download links. It classifies each URL based on file extension
    and download-related keywords.

    Args:
        s3_key: The S3 object key of the email file.
        download_likely_only: If True, only return links that appear to be downloads
                             (have file extensions or download keywords).

    Returns:
        Dictionary with list of found links and their classifications.
    """
    try:
        response = s3_client.get_object(Bucket=S3_BUCKET, Key=s3_key)
        raw_email = response["Body"].read()
        msg: Message = email.message_from_bytes(raw_email)

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

        all_links = []
        seen_urls = set()

        # Extract from HTML (includes link text)
        if body_html:
            html_links = extract_urls_from_html(body_html)
            for link in html_links:
                if link["url"] not in seen_urls:
                    seen_urls.add(link["url"])
                    classification = classify_url(link["url"])
                    classification["link_text"] = link["text"]
                    classification["source"] = "html"
                    all_links.append(classification)

        # Extract from plain text
        if body_plain:
            text_urls = extract_urls_from_text(body_plain)
            for url in text_urls:
                if url not in seen_urls:
                    seen_urls.add(url)
                    classification = classify_url(url)
                    classification["link_text"] = None
                    classification["source"] = "plain_text"
                    all_links.append(classification)

        # Also extract any URLs from HTML that weren't in anchor tags
        if body_html:
            text_urls = extract_urls_from_text(body_html)
            for url in text_urls:
                if url not in seen_urls:
                    seen_urls.add(url)
                    classification = classify_url(url)
                    classification["link_text"] = None
                    classification["source"] = "html_text"
                    all_links.append(classification)

        # Filter if requested
        if download_likely_only:
            all_links = [l for l in all_links if l["is_download_likely"]]

        # Sort by download likelihood
        all_links.sort(key=lambda x: x["is_download_likely"], reverse=True)

        return {
            "status": "success",
            "s3_key": s3_key,
            "subject": decode_email_header(msg.get("Subject", "")),
            "total_links_found": len(all_links),
            "download_likely_count": sum(1 for l in all_links if l["is_download_likely"]),
            "links": all_links,
        }

    except Exception as e:
        logger.error(f"Failed to extract links from email {s3_key}: {e}")
        return {"status": "error", "s3_key": s3_key, "error": str(e)}


@mcp.tool()
async def download_link_attachment(
    url: str,
    output_dir: Optional[str] = None,
    filename: Optional[str] = None,
    timeout_seconds: int = 120,
) -> Dict[str, Any]:
    """Download a file from a URL (typically a download link from an email).

    This tool downloads files from URLs found in email bodies. It handles
    redirects, extracts the filename from headers or URL, and saves the file
    locally.

    Args:
        url: The URL to download from.
        output_dir: Optional directory to save the file. Defaults to EMAIL_ATTACHMENT_DIR.
        filename: Optional filename to use. If not provided, extracted from response.
        timeout_seconds: Download timeout in seconds (default 120).

    Returns:
        Dictionary with the local file path and download details.
    """
    try:
        download_dir = output_dir or ATTACHMENT_DOWNLOAD_DIR
        Path(download_dir).mkdir(parents=True, exist_ok=True)

        # Validate URL
        parsed = urlparse(url)
        if parsed.scheme not in ('http', 'https'):
            return {
                "status": "error",
                "error": f"Invalid URL scheme: {parsed.scheme}. Only http/https supported.",
            }

        logger.info(f"Downloading from URL: {url}")

        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=httpx.Timeout(timeout_seconds),
        ) as client:
            response = await client.get(url)
            response.raise_for_status()

            # Determine filename
            if filename:
                final_filename = filename
            else:
                final_filename = get_filename_from_response(response, url)

            # Sanitize filename
            safe_filename = Path(final_filename).name
            if not safe_filename:
                safe_filename = f"download_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            output_path = Path(download_dir) / safe_filename

            # Prevent overwriting by adding a counter
            counter = 1
            stem, suffix = output_path.stem, output_path.suffix
            while output_path.exists():
                output_path = Path(download_dir) / f"{stem}_{counter}{suffix}"
                counter += 1

            # Write the file
            content = response.content
            with open(output_path, "wb") as f:
                f.write(content)

            logger.info(f"Downloaded link attachment: {output_path}")

            return {
                "status": "success",
                "url": url,
                "final_url": str(response.url),  # After redirects
                "filename": safe_filename,
                "saved_to": str(output_path),
                "size_bytes": len(content),
                "content_type": response.headers.get("content-type", "unknown"),
                "http_status": response.status_code,
            }

    except httpx.TimeoutException:
        logger.error(f"Download timeout for URL: {url}")
        return {
            "status": "error",
            "url": url,
            "error": f"Download timed out after {timeout_seconds} seconds",
        }
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error downloading {url}: {e}")
        return {
            "status": "error",
            "url": url,
            "error": f"HTTP error {e.response.status_code}: {e.response.reason_phrase}",
        }
    except Exception as e:
        logger.error(f"Failed to download from URL {url}: {e}")
        return {"status": "error", "url": url, "error": str(e)}


@mcp.tool()
async def download_all_link_attachments(
    s3_key: str,
    output_dir: Optional[str] = None,
    timeout_seconds: int = 120,
) -> Dict[str, Any]:
    """Download all likely download links from an email.

    This tool extracts all URLs from an email that appear to be download links
    (based on file extension or download keywords) and downloads them all.

    Args:
        s3_key: The S3 object key of the email file.
        output_dir: Optional directory to save files. Defaults to EMAIL_ATTACHMENT_DIR.
        timeout_seconds: Download timeout per file in seconds (default 120).

    Returns:
        Dictionary with list of downloaded files and any errors.
    """
    try:
        # First extract the download links
        links_result = await extract_download_links(s3_key, download_likely_only=True)

        if links_result["status"] != "success":
            return links_result

        if not links_result["links"]:
            return {
                "status": "success",
                "s3_key": s3_key,
                "message": "No download links found in email",
                "downloaded": [],
                "errors": [],
            }

        downloaded = []
        errors = []

        for link in links_result["links"]:
            result = await download_link_attachment(
                url=link["url"],
                output_dir=output_dir,
                timeout_seconds=timeout_seconds,
            )

            if result["status"] == "success":
                downloaded.append({
                    "url": link["url"],
                    "link_text": link.get("link_text"),
                    "saved_to": result["saved_to"],
                    "size_bytes": result["size_bytes"],
                    "content_type": result["content_type"],
                })
            else:
                errors.append({
                    "url": link["url"],
                    "link_text": link.get("link_text"),
                    "error": result["error"],
                })

        return {
            "status": "success",
            "s3_key": s3_key,
            "subject": links_result["subject"],
            "total_links_found": links_result["total_links_found"],
            "downloaded_count": len(downloaded),
            "error_count": len(errors),
            "downloaded": downloaded,
            "errors": errors,
            "download_directory": output_dir or ATTACHMENT_DOWNLOAD_DIR,
        }

    except Exception as e:
        logger.error(f"Failed to download link attachments from {s3_key}: {e}")
        return {"status": "error", "s3_key": s3_key, "error": str(e)}


if __name__ == "__main__":
    logger.info(f"Starting SES S3 Email MCP Server")
    logger.info(f"  Bucket: {S3_BUCKET}")
    logger.info(f"  Prefix: {S3_PREFIX}")
    logger.info(f"  Region: {AWS_REGION}")
    asyncio.run(mcp.run())
