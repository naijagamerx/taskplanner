# -*- mode: python ; coding: utf-8 -*-

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.abspath('.'))

# Define all data files and directories to include
datas = [
    ('assets', 'assets'),
    ('auth', 'auth'),
    ('config', 'config'),
    ('database', 'database'),
    ('gui', 'gui'),
    ('models', 'models'),
    ('services', 'services'),
    ('utils', 'utils'),
    ('data', 'data'),
    ('embedded_config.py', '.'),
    ('compiled_startup.py', '.'),
    ('startup_check.py', '.'),
]

# Comprehensive hidden imports
hiddenimports = [
    # Core Python modules
    'sqlite3', 'json', 'datetime', 'os', 'sys', 'threading', 'time',
    'pathlib', 'shutil', 'subprocess', 'traceback', 'logging',
    
    # GUI frameworks
    'customtkinter', 'tkinter', 'tkinter.ttk', 'tkinter.messagebox',
    'tkinter.filedialog', 'tkinter.simpledialog', 'tkcalendar',
    
    # Database
    'mysql.connector', 'mysql.connector.cursor', 'mysql.connector.errors',
    
    # Graphics and visualization
    'PIL', 'PIL.Image', 'PIL.ImageTk', 'matplotlib', 'matplotlib.pyplot',
    'matplotlib.backends.backend_tkagg', 'matplotlib.figure',
    
    # Date/time
    'dateutil', 'dateutil.parser', 'dateutil.relativedelta',
    
    # Notifications
    'plyer', 'plyer.platforms.win.notification', 'pygame', 'pygame.mixer',
    'win10toast', 'pywin32', 'win32api', 'win32gui', 'win32con',
    
    # Security
    'cryptography', 'cryptography.fernet', 'cryptography.hazmat',
    'cryptography.hazmat.primitives', 'cryptography.hazmat.backends',
    
    # System
    'ctypes', 'ctypes.wintypes', 'winreg', 'uuid', 'hashlib',
    
    # Enhanced features
    'services.theme_manager', 'services.keyboard_manager', 
    'services.search_manager', 'services.template_manager',
    'services.font_manager', 'services.drag_drop_manager',
    'services.notification_service', 'services.analytics_manager',
]

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter.test', 'test', 'unittest', 'pytest',
        'numpy.tests', 'matplotlib.tests',
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
    name='TaskPlanner-v1.0.0',
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
