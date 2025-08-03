#!/usr/bin/env python3
"""
Blackjack Game with Card Counting and Statistical Strategy
GUI entry point.
"""

import sys
import tkinter as tk
from tkinter import ttk
from src.gui.main_window import BlackjackGUI


def main():
    """Main GUI entry point."""
    try:
        # Create and run the GUI
        app = BlackjackGUI(num_decks=6, min_bet=10, max_bet=1000)
        app.run()
    except Exception as e:
        print(f"Error starting GUI: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 