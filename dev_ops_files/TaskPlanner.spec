# -*- mode: python ; coding: utf-8 -*-
# TaskPlanner Spec File - Updated for Countdown Notifications
# Includes all dependencies for persistent notification system

# Comprehensive hidden imports for all features
hiddenimports = [
    # Core Python modules
    'sqlite3', 'json', 'datetime', 'os', 'sys', 'threading', 'time',
    'pathlib', 'shutil', 'subprocess', 'traceback', 'logging', 'signal',
    'atexit', 'uuid', 'hashlib', 'base64', 'pickle', 'copy',

    # GUI frameworks
    'customtkinter', 'tkinter', 'tkinter.ttk', 'tkinter.messagebox',
    'tkinter.filedialog', 'tkinter.simpledialog', 'tkcalendar',

    # Database
    'mysql.connector', 'mysql.connector.cursor', 'mysql.connector.errors',
    'mysql.connector.pooling', 'mysql.connector.connection',

    # Graphics and visualization
    'PIL', 'PIL.Image', 'PIL.ImageTk', 'matplotlib', 'matplotlib.pyplot',
    'matplotlib.backends.backend_tkagg', 'matplotlib.figure',

    # Date/time
    'dateutil', 'dateutil.parser', 'dateutil.relativedelta',

    # Notifications - CRITICAL for countdown notifications
    'plyer', 'plyer.platforms', 'plyer.platforms.win', 'plyer.platforms.win.notification',
    'pygame', 'pygame.mixer', 'pygame.mixer.music',
    'win10toast', 'winsound',

    # Windows API - CRITICAL for compiled notifications
    'ctypes', 'ctypes.wintypes', 'winreg',
    'win32api', 'win32gui', 'win32con', 'pywin32',

    # Security and licensing
    'cryptography', 'cryptography.fernet', 'cryptography.hazmat',
    'cryptography.hazmat.primitives', 'cryptography.hazmat.backends',
    'cryptography.hazmat.primitives.kdf', 'cryptography.hazmat.primitives.hashes',

    # Enhanced features
    'services.theme_manager', 'services.keyboard_manager',
    'services.search_manager', 'services.template_manager',
    'services.font_manager', 'services.drag_drop_manager',
    'services.notification_service', 'services.analytics_manager',
    'services.notification_manager',

    # Models and database
    'models.task', 'models.category', 'models.goal', 'models.habit',
    'database.db_manager', 'database.settings_manager',

    # GUI components
    'gui.main_window', 'gui.task_manager', 'gui.calendar_view',
    'gui.settings', 'gui.analytics', 'gui.dialogs.task_dialog',
    'gui.dialogs.help_dialog', 'gui.auth.license_activation_window',

    # Authentication and licensing
    'auth.license_manager', 'auth.hardware_id',

    # Utilities
    'utils.file_migration', 'utils.backup_manager',

    # Configuration
    'config.window_config', 'config.database_config',
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        ('auth', 'auth'),
        ('config', 'config'),
        ('database', 'database'),
        ('gui', 'gui'),
        ('models', 'models'),
        ('services', 'services'),
        ('utils', 'utils'),
        ('data', 'data'),
        ('compiled_startup.py', '.'),
        ('startup_check.py', '.'),
        ('requirements.txt', '.'),
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
    name='TaskPlanner',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[
        # Exclude notification-related DLLs from UPX compression
        'pygame*.dll',
        'SDL*.dll',
        'plyer*.dll',
        'win32*.dll',
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
    # Additional options for notification system
    manifest=None,
    uac_admin=False,
    uac_uiaccess=False,
)
