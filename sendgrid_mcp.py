#!/usr/bin/env python3
"""SendGrid MCP server implementation for Victoria Terminal."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
from typing import Any, Callable, Mapping, MutableMapping, Sequence

from mcp.server.fastmcp import FastMCP
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Content, Email, Mail, Personalization

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

mcp = FastMCP("sendgrid")
DEFAULT_CONTENT_TYPE = "text/plain"

_CLIENT: SendGridAPIClient | None = None


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


def _get_sendgrid_client() -> SendGridAPIClient:
    """Return a cached SendGrid API client instance."""

    global _CLIENT
    if _CLIENT is None:
        api_key = _get_api_key()
        _CLIENT = SendGridAPIClient(api_key)
    return _CLIENT


def _decode_response_body(body: Any) -> str:
    if body in (None, b"", ""):
        return ""
    if isinstance(body, bytes):
        return body.decode("utf-8", errors="replace")
    return str(body)


async def _sendgrid_request(
    operation: Callable[[SendGridAPIClient], Any],
    *,
    expected_status: Sequence[int] | None = None,
    parse_json: bool = True,
) -> MutableMapping[str, Any]:
    try:
        client = _get_sendgrid_client()
    except SendGridConfigurationError as exc:
        return {"error": str(exc)}

    expected = tuple(expected_status) if expected_status is not None else (200, 201, 202, 204)

    try:
        response = await asyncio.to_thread(operation, client)
    except Exception as exc:  # pragma: no cover - network/SDK error
        message = f"SendGrid request error: {exc}"
        logger.error(message)
        return {"error": message}

    status_code = getattr(response, "status_code", None)
    logger.info("SendGrid response status: %s", status_code)

    if status_code not in expected:
        body_text = _decode_response_body(getattr(response, "body", ""))
        details: Any
        if parse_json and body_text:
            try:
                details = json.loads(body_text)
            except json.JSONDecodeError:
                details = body_text
        else:
            details = body_text
        message = f"SendGrid API error ({status_code}): {details}"
        logger.error(message)
        return {"error": message, "status_code": status_code, "details": details}

    payload: MutableMapping[str, Any] = {"status_code": status_code}

    headers = getattr(response, "headers", {}) or {}
    try:
        header_items = headers.items()
    except AttributeError:
        header_items = []
    header_map = {str(key).lower(): str(value) for key, value in header_items}
    message_id = header_map.get("x-message-id")
    if message_id:
        payload["message_id"] = message_id

    body_text = _decode_response_body(getattr(response, "body", ""))
    if parse_json and body_text:
        try:
            payload["data"] = json.loads(body_text)
        except json.JSONDecodeError:
            payload["raw"] = body_text
    elif body_text:
        payload["raw"] = body_text

    return payload


def _normalize_recipients(addresses: Sequence[str] | None) -> list[Email]:
    if not addresses:
        return []
    return [Email(address) for address in addresses if address]


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

    mail = Mail(from_email=sender, subject=subject)
    mail.reply_to = Email("followup@victoria.elcanotek.com")

    personalization = Personalization()
    personalization.add_to(Email(to_email))

    for cc in _normalize_recipients(cc_emails):
        personalization.add_cc(cc)

    for bcc in _normalize_recipients(bcc_emails):
        personalization.add_bcc(bcc)

    mail.add_personalization(personalization)
    mail.add_content(Content(content_type or DEFAULT_CONTENT_TYPE, content))

    result = await _sendgrid_request(
        lambda client: client.send(mail),
        expected_status=(202,),
        parse_json=False,
    )
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

    mail = Mail(from_email=sender, to_emails=[to_email])
    mail.reply_to = Email("followup@victoria.elcanotek.com")
    mail.template_id = template_id
    mail.dynamic_template_data = dict(dynamic_template_data)

    if subject:
        mail.subject = subject

    result = await _sendgrid_request(
        lambda client: client.send(mail),
        expected_status=(202,),
        parse_json=False,
    )
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
        lambda client: client.client.validations.email.post(request_body=payload),
        expected_status=(200, 202),
    )


@mcp.tool()
async def get_suppression_status(email_address: str) -> MutableMapping[str, Any]:
    """Check if an email address is on any SendGrid suppression lists."""

    result = await _sendgrid_request(
        lambda client: client.client.asm.suppressions._(email_address).get(),
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
