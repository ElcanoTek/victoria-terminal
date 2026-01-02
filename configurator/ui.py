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

"""Rich terminal UI for Victoria Terminal."""

from __future__ import annotations

import sys
import time

from rich.align import Align
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

from .constants import (
    COMPACT_SHIP_ASCII_BASE,
    ICONS,
    LICENSE_ACCEPT_PROMPT,
    LICENSE_NOTICE_REMINDER,
    LICENSE_NOTICE_TITLE,
    TERMINAL_PROMPT,
    TIPS_BULLETS,
    TIPS_CHECKED,
    VICTORIA_TEXT,
)


class VictoriaUI:
    """Terminal UI for Victoria using Rich.

    Args:
        console: Rich Console instance.
        silent: If True, suppress informational output.
    """

    def __init__(self, console: Console | None = None, *, silent: bool = False) -> None:
        self.console = console or Console()
        self.silent = silent

    # ─────────────────────────────────────────────────────────────────────────
    # Simple message helpers
    # ─────────────────────────────────────────────────────────────────────────

    def info(self, message: str) -> None:  # pragma: no cover
        """Display an info message."""
        if self.silent:
            return
        self.console.print(f"[cyan]{ICONS['info']} {message}")

    def good(self, message: str) -> None:  # pragma: no cover
        """Display a success message."""
        if self.silent:
            return
        self.console.print(f"[green]{ICONS['good']} {message}")

    def warn(self, message: str) -> None:  # pragma: no cover
        """Display a warning message."""
        if self.silent:
            return
        self.console.print(f"[yellow]{ICONS['warn']} {message}")

    def err(self, message: str) -> None:  # pragma: no cover
        """Display an error message."""
        self.console.print(f"[red]{ICONS['bad']} {message}")

    def section(self, title: str) -> None:  # pragma: no cover
        """Display a section header."""
        if self.silent:
            return
        self.console.rule(f"[bold yellow]{title}")

    # ─────────────────────────────────────────────────────────────────────────
    # License UI
    # ─────────────────────────────────────────────────────────────────────────

    def display_license_notice(self) -> None:  # pragma: no cover
        """Display the license agreement notice."""
        from .license import get_license_text

        self.console.clear()
        title = Text(LICENSE_NOTICE_TITLE, style="bold bright_white")
        reminder = Text(LICENSE_NOTICE_REMINDER, style="bright_yellow")
        license_text = Text(get_license_text().rstrip(), style="bright_white")
        content = Group(
            Align.center(title),
            Text("\n"),
            license_text,
            Text("\n"),
            Align.left(reminder),
        )
        panel = Panel(content, border_style="bright_cyan", padding=(1, 2))
        self.console.print(panel)

    def prompt_license_response(self) -> str:  # pragma: no cover
        """Prompt user for license acceptance response."""
        try:
            return self.console.input(f"[cyan]{LICENSE_ACCEPT_PROMPT}[/cyan]").strip()
        except (KeyboardInterrupt, EOFError):
            self.handle_license_decline(cancelled=True)
            return ""

    def prompt_email(self) -> str:  # pragma: no cover
        """Prompt user for their email address."""
        return self.console.input(
            "[cyan]Enter your email address to complete license acceptance: [/cyan]"
        ).strip()

    def notify_invalid_response(self) -> None:  # pragma: no cover
        """Notify user of invalid license response."""
        if self.silent:
            return
        self.console.print("[yellow]Please respond with 'accept' or 'decline'.[/yellow]")

    def acknowledge_license_acceptance(self) -> None:  # pragma: no cover
        """Acknowledge that license was accepted."""
        if self.silent:
            return
        self.console.print("[green]License accepted. Continuing startup...[/green]")
        time.sleep(1.0)

    def handle_license_decline(self, *, cancelled: bool = False) -> None:  # pragma: no cover
        """Handle license decline or cancellation."""
        if cancelled:
            message = "Victoria launch cancelled before accepting the license."
        else:
            message = "Victoria Terminal requires license acceptance to continue. Exiting."
        self.console.print(f"[red]{message}[/red]")
        sys.exit(0)

    # ─────────────────────────────────────────────────────────────────────────
    # Banner and animation
    # ─────────────────────────────────────────────────────────────────────────

    def _ship_renderable(self, wave_offset: int = 0) -> Text:  # pragma: no cover
        """Build ship art with shifting waves."""
        lines = COMPACT_SHIP_ASCII_BASE.copy()
        for idx in (-3, -2, -1):
            if abs(idx) <= len(lines):
                padding = " " * (wave_offset % 6)
                line = lines[idx].strip()
                lines[idx] = f"{padding}{line}"
        return Text("\n".join(lines), style="bright_cyan")

    def _build_welcome_panel(self, wave_offset: int = 0) -> Panel:  # pragma: no cover
        """Build the welcome panel with optional wave animation."""
        prompt_text = Text(TERMINAL_PROMPT, style="bold bright_green")

        victoria_lines = VICTORIA_TEXT.strip().split("\n")
        victoria_text = Text()
        for i, line in enumerate(victoria_lines):
            color = "bright_magenta" if i % 2 == 0 else "magenta"
            victoria_text.append(line + "\n", style=f"bold {color}")

        subtitle = Text("AdTech Data Navigation Terminal", style="italic bright_white")

        content = Group(
            Align.left(prompt_text),
            Text("\n"),
            self._ship_renderable(wave_offset),
            Text("\n"),
            victoria_text,
            Text("\n"),
            Align.center(subtitle),
        )

        return Panel(
            Align.center(content),
            border_style="bright_cyan",
            padding=(1, 2),
            title="[bold bright_white]⚓ Victoria ⚓[/bold bright_white]",
            title_align="center",
            subtitle="[dim]Welcome[/dim]",
            subtitle_align="center",
        )

    def display_welcome(self) -> None:  # pragma: no cover
        """Display the welcome banner."""
        self.console.clear()
        self.console.print(self._build_welcome_panel(0))
        self.console.print()

    def animate_waves(self, duration: float = 1.8) -> None:  # pragma: no cover
        """Animate waves in the welcome banner."""
        start = time.time()
        offset = 0
        with Live(refresh_per_second=16, console=self.console, screen=False):
            while time.time() - start < duration:
                offset = (offset + 1) % 6
                self.console.clear()
                self.console.print(self._build_welcome_panel(offset))
                time.sleep(0.06)

    def _build_tips_panel(self, tips: list[str]) -> Panel:  # pragma: no cover
        """Build the tips panel with given tips."""
        title = Text("Victoria Terminal", style="bold bright_white")
        tips_text = Text()
        for tip in tips:
            tips_text.append(tip + "\n", style="bright_white")

        content = Group(
            Align.center(title),
            Text("\n"),
            Align.center(Text("TIPS", style="dim cyan")),
            Text("\n"),
            Align.center(tips_text),
        )

        return Panel(
            Align.center(content),
            border_style="bright_cyan",
            padding=(1, 2),
            title="[bold bright_white]⚓ Victoria Terminal ⚓[/bold bright_white]",
            title_align="center",
            subtitle="[dim]TIPS[/dim]",
            subtitle_align="center",
        )

    def display_tips(self, *, initial_bullets: bool = True) -> None:  # pragma: no cover
        """Display the tips screen."""
        self.console.clear()
        items = TIPS_BULLETS if initial_bullets else TIPS_CHECKED
        self.console.print(self._build_tips_panel(items))
        self.console.print()

    def animate_tips(self) -> None:  # pragma: no cover
        """Animate bullets transforming to checkmarks."""
        frames = []
        for i in range(1, len(TIPS_BULLETS) + 1):
            current = TIPS_CHECKED[:i] + TIPS_BULLETS[i:]
            frames.append(current)

        with Live(refresh_per_second=12, console=self.console, screen=False):
            for frame in frames:
                self.console.clear()
                self.console.print(self._build_tips_panel(frame))
                time.sleep(0.35)

    def spinner(self, message: str, duration: float = 1.8) -> None:  # pragma: no cover
        """Display a spinner with a message."""
        spinner_frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        start = time.time()
        idx = 0
        with Live(refresh_per_second=16, console=self.console, screen=False):
            while time.time() - start < duration:
                line = Text(
                    f"{spinner_frames[idx % len(spinner_frames)]} {message}",
                    style="cyan",
                )
                panel = Panel(Align.center(line), border_style="bright_cyan", padding=(1, 2))
                self.console.clear()
                self.console.print(panel)
                idx += 1
                time.sleep(0.07)

    def wait_for_enter(self, prompt: str) -> None:  # pragma: no cover
        """Wait for user to press Enter."""
        try:
            self.console.print(f"[cyan]{prompt}[/cyan]")
            input()
            self.console.clear()
        except (KeyboardInterrupt, EOFError):
            self.console.print("\n[yellow]Startup cancelled[/yellow]")
            sys.exit(0)

    def banner_sequence(self) -> None:  # pragma: no cover
        """Run the full intro banner sequence."""
        self.display_welcome()
        self.animate_waves(duration=1.8)
        self.wait_for_enter("Press Enter to continue...")
        self.display_tips(initial_bullets=True)
        self.animate_tips()
        self.wait_for_enter("Press Enter to continue...")

    def clear(self) -> None:  # pragma: no cover
        """Clear the console."""
        self.console.clear()


def check_rich_terminal() -> bool:
    """Check if Rich terminal rendering is available."""
    console = Console()
    return hasattr(console, "is_terminal") and console.is_terminal and sys.stdout.isatty()
