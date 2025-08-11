# -*- mode: python ; coding: utf-8 -*-

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.abspath('.'))

# Define all data files and directories to include
datas = [
    ('assets', 'assets'),
    ('auth', 'auth'),
]

# Comprehensive hidden imports for admin dashboard
hiddenimports = [
    # Core Python modules
    'sqlite3', 'json', 'datetime', 'os', 'sys', 'threading', 'time',
    'pathlib', 'shutil', 'subprocess', 'traceback', 'logging',
    
    # GUI frameworks
    'customtkinter', 'tkinter', 'tkinter.ttk', 'tkinter.messagebox',
    'tkinter.filedialog', 'tkinter.simpledialog',
    
    # Security
    'cryptography', 'cryptography.fernet', 'cryptography.hazmat',
    'cryptography.hazmat.primitives', 'cryptography.hazmat.backends',
    
    # System
    'ctypes', 'ctypes.wintypes', 'winreg', 'uuid', 'hashlib',
]

a = Analysis(
    ['admin_dashboard.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter.test', 'test', 'unittest', 'pytest',
    ],
    noarchive=False,
    optimize=2,
)

# Remove duplicate files
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='TaskPlanner-Admin-v1.0.0',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='version_info.txt',
    icon='assets/icons/app_icon.ico',
)
