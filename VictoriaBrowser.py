#!/usr/bin/env python3
"""Victoria Browser - A simple tool to open the ElcanoTek website."""

import webbrowser

from common import console, handle_error


def main():
    """Opens the default web browser to the ElcanoTek website."""
    console.print("[cyan]ℹ️ Opening the ElcanoTek website in your default browser...")
    webbrowser.open("https://www.elcanotek.com/")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        handle_error(e)
