#!/usr/bin/env python3
"""Victoria Browser - A simple tool to open the ElcanoTek website."""

import webbrowser
from common import console

def main():
    """Opens the default web browser to the ElcanoTek website."""
    console.print("[cyan]ℹ️ Opening the ElcanoTek website in your default browser...")
    webbrowser.open("https://elcano.tek.com")

if __name__ == "__main__":
    main()
