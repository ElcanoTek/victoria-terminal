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
# License Notes: 2026-01-02

"""Constants and configuration values for Victoria Terminal."""

from __future__ import annotations

from pathlib import Path

__version__ = "2025.9.9"

# File and directory names
VICTORIA_FILE = "VICTORIA.md"
PROTOCOLS_DIR = "protocols"
CONFIGS_DIR = "configs"
CRUSH_TEMPLATE = Path(CONFIGS_DIR) / "crush" / "crush.template.json"
CRUSH_LOCAL = Path(CONFIGS_DIR) / "crush" / "crush.local.json"
CRUSH_CONFIG_NAME = "crush.json"
VICTORIA_CONFIG_DIR = Path(".config") / "victoria"
ENV_FILENAME = ".env"
CRUSH_COMMAND = "crush"
SUPPORT_FILES: tuple[Path, ...] = (Path(VICTORIA_FILE),)

# License constants
LICENSE_ACCEPTANCE_KEY = "VICTORIA_LICENSE_ACCEPTED"
LICENSE_ACCEPTED_VALUES = {"yes", "true", "1", "accepted"}
LICENSE_NOTICE_TITLE = "Victoria Terminal License Agreement"
LICENSE_FILE_NAME = "LICENSE"
LICENSE_NOTICE_REMINDER = "You must accept these terms to continue. Type 'accept' to agree or 'decline' to exit."
LICENSE_ACCEPT_PROMPT = "Type 'accept' to agree or 'decline' to exit: "

# Telemetry configuration
TELEMETRY_URL = "https://webhook.site/b58b736e-2790-48ed-a24f-e0bb40dd3a92"

# Environment variable keys
REQUIRED_ENV_KEYS = ("OPENROUTER_API_KEY",)
BROWSERBASE_ENV_KEYS = ("BROWSERBASE_API_KEY", "BROWSERBASE_PROJECT_ID", "GEMINI_API_KEY")
GAMMA_ENV_KEY = "GAMMA_API_KEY"
SENDGRID_ENV_KEY = "SENDGRID_API_KEY"
EMAIL_ENV_KEYS = ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "EMAIL_S3_BUCKET")
SNOWFLAKE_ENV_KEYS = ("SNOWFLAKE_ACCOUNT", "SNOWFLAKE_USER", "SNOWFLAKE_PASSWORD")
BROWSEROS_ENV_KEY = "BROWSEROS_URL"
ORCHESTRATOR_ENV_KEYS = ("ORCHESTRATOR_URL", "JOB_ID", "NODE_API_KEY")

# UI Icons
ICONS = {
    "info": "ℹ️",
    "good": "✅",
    "warn": "⚠️",
    "bad": "❌",
    "rocket": "🚀",
    "wave": "🌊",
    "anchor": "⚓",
    "folder": "📁",
}

# ASCII Art
TERMINAL_PROMPT = ">_"

COMPACT_SHIP_ASCII_BASE = [
    "              |    |    |                ",
    "             )_)  )_)  )_)               ",
    "            )___))___))___)\\             ",
    "           )____)____)_____)\\\\           ",
    "         _____|____|____|____\\\\\\__       ",
    "---------\\                   /---------  ",
    "  ^^^^^ ^^^^^^^^^^^^^^^^^^^^^           ",
    "    ^^^^      ^^^^     ^^^    ^^        ",
    "         ^^^^      ^^^               ",
]

VICTORIA_TEXT = """
██╗   ██╗██╗ ██████╗████████╗ ██████╗ ██████╗ ██╗ █████╗
██║   ██║██║██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗██║██╔══██╗
██║   ██║██║██║        ██║   ██║   ██║██████╔╝██║███████║
╚██╗ ██╔╝██║██║        ██║   ██║   ██║██╔══██╗██║██╔══██║
 ╚████╔╝ ██║╚██████╗   ██║   ╚██████╔╝██║  ██║██║██║  ██║
  ╚═══╝  ╚═╝ ╚═════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝
"""

TIPS_BULLETS = [
    "• Put data files in the Victoria folder",
    '• Ask any question you like (e.g., "Hey Victoria, Analyze the top-performing sites")',
    "• Report bugs to the support channel or the GitHub repo",
]

TIPS_CHECKED = [
    "✅ Put data files in the Victoria folder",
    '✅ Ask any question you like (e.g., "Hey Victoria, Analyze the top-performing sites")',
    "✅ Report bugs to the support channel or the GitHub repo",
]
