# -*- mode: python ; coding: utf-8 -*-
# Admin Dashboard Spec File - For License Management
# Includes all dependencies for admin dashboard functionality

# Comprehensive hidden imports for admin dashboard
hiddenimports = [
    # Core Python modules
    'sqlite3', 'json', 'datetime', 'os', 'sys', 'threading', 'time',
    'pathlib', 'shutil', 'subprocess', 'traceback', 'logging',
    'uuid', 'hashlib', 'base64', 'pickle', 'copy',
    
    # GUI frameworks
    'customtkinter', 'tkinter', 'tkinter.ttk', 'tkinter.messagebox',
    'tkinter.filedialog', 'tkinter.simpledialog',
    
    # Security and licensing - CRITICAL for admin dashboard
    'cryptography', 'cryptography.fernet', 'cryptography.hazmat',
    'cryptography.hazmat.primitives', 'cryptography.hazmat.backends',
    'cryptography.hazmat.primitives.kdf', 'cryptography.hazmat.primitives.hashes',
    
    # Windows API
    'ctypes', 'ctypes.wintypes', 'winreg',
    
    # Authentication and licensing
    'auth.license_generator', 'auth.license_manager',
    
    # Configuration
    'config.database_config',
]

a = Analysis(
    ['admin_dashboard.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('auth', 'auth'),
        ('config', 'config'),
        ('assets', 'assets'),
        ('version_info.txt', '.'),
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter.test', 'test', 'unittest', 'pytest', 'nose'],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='AdminDashboard',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[
        # Exclude crypto-related DLLs from UPX compression
        'cryptography*.dll',
        'openssl*.dll',
    ],
    runtime_tmpdir=None,
    console=False,  # Set to True for debugging if needed
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='version_info.txt',
    icon=['assets\\icons\\app_icon.ico'],
    # Additional options for admin dashboard
    manifest=None,
    uac_admin=False,
    uac_uiaccess=False,
)
