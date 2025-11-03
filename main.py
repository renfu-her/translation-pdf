#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Translator Launcher - Supports both GUI and CLI modes
"""

import sys
import argparse


def main():
    """Main launcher function."""
    parser = argparse.ArgumentParser(
        description="PDF Translator - Translate PDF to Traditional Chinese"
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Launch GUI interface (default if no arguments provided)"
    )
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Use command-line interface"
    )
    
    # Parse arguments to check if GUI should be used
    args, remaining_args = parser.parse_known_args()
    
    # If --gui is specified or no CLI arguments provided, launch GUI
    if args.gui or (not args.cli and len(remaining_args) == 0):
        try:
            from gui import main as gui_main
            gui_main()
        except ImportError as e:
            print("Error: GUI dependencies not installed.")
            print("Install PySide6 with: pip install PySide6")
            print("\nAlternatively, use command-line mode:")
            print("  python pdf_translator.py <input.pdf>")
            sys.exit(1)
    else:
        # Use CLI mode
        from pdf_translator import main as cli_main
        # Reconstruct sys.argv with remaining arguments
        sys.argv = [sys.argv[0]] + remaining_args
        cli_main()


if __name__ == "__main__":
    main()

