#!/usr/bin/env python3
"""Victoria Browser - A simple tool to open the ElcanoTek website."""

import webbrowser
import tkinter as tk
from tkinter import messagebox

def main():
    """Opens the default web browser to the ElcanoTek website."""
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    messagebox.showinfo("Victoria Browser", "Opening the ElcanoTek website in your default browser.")
    webbrowser.open("https://elcano.tek.com")
    root.destroy()

if __name__ == "__main__":
    main()
