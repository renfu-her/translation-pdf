#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Translator - Build Script for Windows Executable
Run this script to build a standalone executable using PyInstaller
"""

import subprocess
import sys
import os

def check_pyinstaller():
    """Check if PyInstaller is installed."""
    try:
        import PyInstaller
        return True
    except ImportError:
        return False

def install_pyinstaller():
    """Install PyInstaller."""
    print("Installing PyInstaller...")
    result = subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], 
                          capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error installing PyInstaller: {result.stderr}")
        return False
    print("PyInstaller installed successfully!")
    return True

def build_executable():
    """Build the executable using PyInstaller."""
    print("=" * 50)
    print("PDF Translator - Building Windows Executable")
    print("=" * 50)
    print()
    
    # Check if PyInstaller is installed
    if not check_pyinstaller():
        print("PyInstaller not found. Installing...")
        if not install_pyinstaller():
            print("Failed to install PyInstaller!")
            return False
    
    # PyInstaller command
    # Option 1: Use spec file (recommended)
    cmd = [
        "pyinstaller",
        "PDFTranslator.spec"
    ]
    
    # Option 2: Use command line (uncomment to use instead)
    # cmd = [
    #     "pyinstaller",
    #     "--name=PDFTranslator",
    #     "--windowed",  # No console window for GUI app
    #     "--onefile",   # Single executable file
    #     "--hidden-import=PySide6.QtCore",
    #     "--hidden-import=PySide6.QtGui",
    #     "--hidden-import=PySide6.QtWidgets",
    #     "--hidden-import=pdf_translator",
    #     "--hidden-import=deep_translator",
    #     "--hidden-import=langdetect",
    #     "--hidden-import=fitz",
    #     "--collect-all=PySide6",  # Collect all PySide6 resources
    #     "--noconfirm",  # Overwrite output directory without confirmation
    #     "main.py"
    # ]
    
    print("Building executable...")
    print(f"Command: {' '.join(cmd)}")
    print()
    
    # Run PyInstaller
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print()
        print("=" * 50)
        print("Build completed successfully!")
        print("=" * 50)
        print()
        print("Executable location: dist\\PDFTranslator.exe")
        print()
        print("You can now distribute PDFTranslator.exe")
        return True
    else:
        print()
        print("Build failed!")
        return False

if __name__ == "__main__":
    success = build_executable()
    sys.exit(0 if success else 1)

