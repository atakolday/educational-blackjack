#!/usr/bin/env python3
"""
Simple build script to create a standalone macOS app for the Blackjack game.
"""

import os
import sys
import subprocess


def main():
    """Build the Blackjack app using PyInstaller."""
    print("🚀 Building Blackjack app...")
    print("=" * 40)
    
    # Install PyInstaller if not present
    try:
        import PyInstaller
        print("✅ PyInstaller is installed")
    except ImportError:
        print("📦 Installing PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Build command
    cmd = [
        "pyinstaller",
        "--onefile",                    # Create a single executable
        "--windowed",                   # No console window
        "--name=Blackjack",             # App name
        "--icon=src/gui/assets/icon.icns" if os.path.exists("src/gui/assets/icon.icns") else "",
        "--add-data=src/gui/assets:src/gui/assets",  # Include assets
        "--hidden-import=tkinter",
        "--hidden-import=tkinter.ttk", 
        "--hidden-import=tkinter.messagebox",
        "--hidden-import=PIL",
        "--hidden-import=PIL.Image",
        "--hidden-import=PIL.ImageTk",
        "gui_main.py"
    ]
    
    # Remove empty icon argument if no icon file
    cmd = [arg for arg in cmd if arg]
    
    print("🔨 Running PyInstaller...")
    print(f"Command: {' '.join(cmd)}")
    print()
    
    # Run the build
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print()
        print("🎉 Build completed successfully!")
        print()
        print("📱 Your app is ready at: dist/Blackjack")
        print("   You can now double-click to run it!")
        print()
        print("🎯 Next steps:")
        print("1. Double-click 'dist/Blackjack' to test")
        print("2. The app will run without needing Python!")
        
    else:
        print("❌ Build failed. Check the error messages above.")


if __name__ == "__main__":
    main() 