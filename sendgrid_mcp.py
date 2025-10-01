#!/usr/bin/env python3
"""SendGrid MCP server implementation for Victoria Terminal."""

from __future__ import annotations

import logging
import os
import sys
from typing import Any, Mapping, MutableMapping, Sequence

import httpx
from mcp.server.fastmcp import FastMCP

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

mcp = FastMCP("sendgrid")

SENDGRID_BASE_URL = "https://api.sendgrid.com/v3"
DEFAULT_TIMEOUT = 30.0
DEFAULT_CONTENT_TYPE = "text/plain"


class SendGridConfigurationError(RuntimeError):
    """Raised when required SendGrid configuration is missing."""


def _get_api_key() -> str:
    api_key = os.environ.get("SENDGRID_API_KEY")
    if not api_key:
        message = "SENDGRID_API_KEY environment variable not set"
        logger.error(message)
        raise SendGridConfigurationError(message)
    return api_key


def _resolve_from_email(explicit_from: str | None = None) -> str:
    if explicit_from:
        return explicit_from

    env_from = os.environ.get("SENDGRID_FROM_EMAIL")
    if not env_from:
        message = (
            "From email address not provided. Pass `from_email` or set "
            "SENDGRID_FROM_EMAIL in the environment."
        )
        logger.error(message)
        raise SendGridConfigurationError(message)

    return env_from


async def _sendgrid_request(
    method: str,
    path: str,
    *,
    json: Mapping[str, Any] | None = None,
    params: Mapping[str, Any] | None = None,
    expected_status: Sequence[int] | None = None,
    parse_json: bool = True,
) -> MutableMapping[str, Any]:
    api_key = _get_api_key()
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "victoria-terminal-sendgrid-mcp/1.0",
    }

    expected = tuple(expected_status) if expected_status is not None else (200, 201, 202, 204)

    url = f"{SENDGRID_BASE_URL}{path}"
    logger.info("Calling SendGrid API: %s %s", method.upper(), url)

    try:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            response = await client.request(
                method=method.upper(),
                url=url,
                headers=headers,
                json=dict(json) if json is not None else None,
                params=dict(params) if params is not None else None,
            )
    except httpx.TimeoutException as exc:  # pragma: no cover - network timeout
        message = f"SendGrid request timed out after {DEFAULT_TIMEOUT}s: {exc}"
        logger.error(message)
        return {"error": message}
    except httpx.RequestError as exc:  # pragma: no cover - connection issue
        message = f"SendGrid request error: {exc}"
        logger.error(message)
        return {"error": message}

    status_code = response.status_code
    logger.info("SendGrid response status: %s", status_code)

    if status_code not in expected:
        error_detail: Any
        try:
            error_detail = response.json()
        except ValueError:
            error_detail = response.text
        message = f"SendGrid API error ({status_code}): {error_detail}"
        logger.error(message)
        return {"error": message, "status_code": status_code, "details": error_detail}

    payload: MutableMapping[str, Any] = {"status_code": status_code}
    message_id = response.headers.get("x-message-id")
    if message_id:
        payload["message_id"] = message_id

    if parse_json and response.content:
        try:
            payload["data"] = response.json()
        except ValueError:
            payload["raw"] = response.text

    return payload


def _normalize_recipients(addresses: Sequence[str] | None) -> list[dict[str, str]]:
    if not addresses:
        return []
    return [{"email": address} for address in addresses if address]


@mcp.tool()
async def send_email(
    to_email: str,
    subject: str,
    content: str,
    *,
    content_type: str = DEFAULT_CONTENT_TYPE,
    from_email: str | None = None,
    cc_emails: Sequence[str] | None = None,
    bcc_emails: Sequence[str] | None = None,
) -> MutableMapping[str, Any]:
    """Send a basic SendGrid email with optional CC and BCC recipients."""

    try:
        sender = _resolve_from_email(from_email)
    except SendGridConfigurationError as exc:
        return {"error": str(exc)}

    personalization: MutableMapping[str, Any] = {
        "to": [{"email": to_email}],
    }

    cc = _normalize_recipients(cc_emails)
    if cc:
        personalization["cc"] = cc

    bcc = _normalize_recipients(bcc_emails)
    if bcc:
        personalization["bcc"] = bcc

    payload: Mapping[str, Any] = {
        "personalizations": [personalization],
        "from": {"email": sender},
        "subject": subject,
        "content": [
            {
                "type": content_type or DEFAULT_CONTENT_TYPE,
                "value": content,
            }
        ],
    }

    result = await _sendgrid_request("POST", "/mail/send", json=payload, expected_status=(202,))
    if "error" in result:
        return result

    result["status"] = "queued"
    return result


@mcp.tool()
async def send_template_email(
    to_email: str,
    template_id: str,
    dynamic_template_data: Mapping[str, Any],
    *,
    from_email: str | None = None,
    subject: str | None = None,
) -> MutableMapping[str, Any]:
    """Send an email using a SendGrid dynamic template."""

    try:
        sender = _resolve_from_email(from_email)
    except SendGridConfigurationError as exc:
        return {"error": str(exc)}

    personalization: MutableMapping[str, Any] = {
        "to": [{"email": to_email}],
        "dynamic_template_data": dict(dynamic_template_data),
    }

    if subject:
        personalization["subject"] = subject

    payload: Mapping[str, Any] = {
        "personalizations": [personalization],
        "from": {"email": sender},
        "template_id": template_id,
    }

    result = await _sendgrid_request("POST", "/mail/send", json=payload, expected_status=(202,))
    if "error" in result:
        return result

    result["status"] = "queued"
    result["template_id"] = template_id
    return result


@mcp.tool()
async def validate_email_address(
    email_address: str,
    *,
    source: str = "Victoria Terminal",
) -> MutableMapping[str, Any]:
    """Validate an email address using the SendGrid email validation API."""

    payload = {
        "email": email_address,
        "source": source,
    }

    return await _sendgrid_request(
        "POST",
        "/validations/email",
        json=payload,
        expected_status=(200, 202),
    )


@mcp.tool()
async def get_suppression_status(email_address: str) -> MutableMapping[str, Any]:
    """Check if an email address is on any SendGrid suppression lists."""

    result = await _sendgrid_request(
        "GET",
        f"/asm/suppressions/{email_address}",
        expected_status=(200, 404),
    )

    if "error" in result and result.get("status_code") != 404:
        return result

    status_code = result.get("status_code")
    if status_code == 404:
        return {
            "suppressed": False,
            "status_code": status_code,
        }

    return {
        "suppressed": True,
        "status_code": status_code,
        "data": result.get("data"),
    }


if __name__ == "__main__":
    mcp.run()
