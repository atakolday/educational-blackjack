#!/usr/bin/env python3
"""
Build script to create a standalone macOS app for the Blackjack game.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import PyInstaller
        print("✅ PyInstaller is installed")
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    try:
        import PIL
        print("✅ Pillow (PIL) is installed")
    except ImportError:
        print("❌ Pillow not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pillow"])


def create_spec_file():
    """Create a PyInstaller spec file for the app."""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['gui_main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/gui/assets/*', 'src/gui/assets/'),
        ('src/game/*.py', 'src/game/'),
        ('src/counting/*.py', 'src/counting/'),
        ('src/strategy/*.py', 'src/strategy/'),
        ('src/gui/components/*.py', 'src/gui/components/'),
        ('src/gui/*.py', 'src/gui/'),
        ('src/__init__.py', 'src/'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'numpy',
        'matplotlib',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Blackjack',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Blackjack',
)

app = BUNDLE(
    coll,
    name='Blackjack.app',
    icon='src/gui/assets/icon.icns' if os.path.exists('src/gui/assets/icon.icns') else None,
    bundle_identifier='com.blackjack.cardcounting',
    info_plist={
        'CFBundleName': 'Blackjack with Card Counting',
        'CFBundleDisplayName': 'Blackjack',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleExecutable': 'Blackjack',
        'CFBundleIdentifier': 'com.blackjack.cardcounting',
        'CFBundlePackageType': 'APPL',
        'CFBundleSignature': '????',
        'LSMinimumSystemVersion': '10.13.0',
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,
    },
)
'''
    
    with open('blackjack.spec', 'w') as f:
        f.write(spec_content)
    
    print("✅ Created blackjack.spec file")


def build_app():
    """Build the macOS app."""
    print("🔨 Building Blackjack app...")
    
    # Run PyInstaller
    result = subprocess.run([
        'pyinstaller',
        '--clean',
        '--windowed',
        '--name=Blackjack',
        '--distpath=dist',
        '--workpath=build',
        'blackjack.spec'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ App built successfully!")
        print(f"📱 App location: {os.path.abspath('dist/Blackjack.app')}")
    else:
        print("❌ Build failed!")
        print("Error output:")
        print(result.stderr)
        return False
    
    return True


def create_dmg():
    """Create a DMG file for easy distribution (optional)."""
    print("📦 Creating DMG file...")
    
    # Check if create-dmg is available
    try:
        subprocess.run(['create-dmg', '--version'], capture_output=True, check=True)
        
        # Create DMG
        subprocess.run([
            'create-dmg',
            '--volname', 'Blackjack',
            '--window-pos', '200', '120',
            '--window-size', '600', '400',
            '--icon-size', '100',
            '--icon', 'Blackjack.app', '175', '120',
            '--hide-extension', 'Blackjack.app',
            '--app-drop-link', '425', '120',
            'dist/Blackjack.dmg',
            'dist/Blackjack.app'
        ])
        
        print("✅ DMG created successfully!")
        print(f"📦 DMG location: {os.path.abspath('dist/Blackjack.dmg')}")
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  create-dmg not found. Skipping DMG creation.")
        print("   Install with: brew install create-dmg")


def main():
    """Main build process."""
    print("🚀 Starting Blackjack app build process...")
    print("=" * 50)
    
    # Check dependencies
    check_dependencies()
    print()
    
    # Create spec file
    create_spec_file()
    print()
    
    # Build the app
    if build_app():
        print()
        print("🎉 Build completed successfully!")
        print()
        print("📱 Your app is ready at: dist/Blackjack.app")
        print("   You can now double-click to run it!")
        print()
        
        # Try to create DMG
        create_dmg()
        
        print()
        print("🎯 Next steps:")
        print("1. Double-click 'dist/Blackjack.app' to test")
        print("2. Drag the app to your Applications folder")
        print("3. The app will appear in your Dock when running")
        
    else:
        print("❌ Build failed. Check the error messages above.")


if __name__ == "__main__":
    main() 