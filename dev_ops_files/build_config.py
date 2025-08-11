#!/usr/bin/env python3
"""
Build configuration for Task Planner application
Cross-platform executable generation
"""

import os
import sys
import platform

# Application metadata
APP_NAME = "TaskPlanner"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Comprehensive Life Planning Application"
APP_AUTHOR = "Task Planner Team"
APP_COPYRIGHT = "Copyright (c) 2025 Task Planner Team"

# Build paths
BUILD_DIR = "build"
DIST_DIR = "dist"
ASSETS_DIR = "assets"
ICONS_DIR = os.path.join(ASSETS_DIR, "icons")

# Platform detection
IS_WINDOWS = platform.system() == "Windows"
IS_MACOS = platform.system() == "Darwin"
IS_LINUX = platform.system() == "Linux"

# Icon files
WINDOWS_ICON = os.path.join(ICONS_DIR, "app_icon.ico")
MACOS_ICON = os.path.join(ICONS_DIR, "app_icon.icns")
LINUX_ICON = os.path.join(ICONS_DIR, "app_icon.png")

# PyInstaller configuration
PYINSTALLER_CONFIG = {
    "name": APP_NAME,
    "script": "main.py",
    "onefile": True,
    "windowed": True,  # No console window
    "clean": True,
    "noconfirm": True,
    "distpath": DIST_DIR,
    "workpath": BUILD_DIR,
    "specpath": ".",
}

# Platform-specific configurations
if IS_WINDOWS:
    PYINSTALLER_CONFIG.update({
        "icon": WINDOWS_ICON,
        "version_file": "version_info.txt",
        "add_data": [
            ("assets;assets"),
            ("auth;auth"),
            ("config;config"),
            ("database;database"),
            ("gui;gui"),
            ("models;models"),
            ("services;services"),
            ("utils;utils"),
            ("data;data"),
            ("compiled_startup.py;."),
            ("startup_check.py;."),
        ],
        "hidden_imports": [
            "mysql.connector",
            "customtkinter",
            "tkcalendar",
            "matplotlib",
            "PIL",
            "dateutil",
            "sqlite3",
            "tkinter",
            "tkinter.ttk",
            "plyer",
            "threading",
            "json",
            "datetime",
            "os",
            "sys",
        ],
        "exclude_modules": [
            "tkinter.test",
            "test",
            "unittest",
        ],
    })

elif IS_MACOS:
    PYINSTALLER_CONFIG.update({
        "icon": MACOS_ICON,
        "add_data": [
            ("assets:assets"),
            ("auth:auth"),
            ("config:config"),
            ("database:database"),
            ("gui:gui"),
            ("models:models"),
            ("services:services"),
            ("data:data"),
            ("compiled_startup.py:."),
            ("startup_check.py:."),
        ],
        "hidden_imports": [
            "mysql.connector",
            "customtkinter",
            "tkcalendar",
            "matplotlib",
            "PIL",
            "dateutil",
            "sqlite3",
            "tkinter",
            "tkinter.ttk",
            "plyer",
            "threading",
            "json",
            "datetime",
            "os",
            "sys",
        ],
        "exclude_modules": [
            "tkinter.test",
            "test",
            "unittest",
        ],
        "osx_bundle_identifier": f"com.taskplanner.{APP_NAME.lower()}",
    })

elif IS_LINUX:
    PYINSTALLER_CONFIG.update({
        "icon": LINUX_ICON,
        "add_data": [
            ("assets:assets"),
            ("auth:auth"),
            ("config:config"),
            ("database:database"),
            ("gui:gui"),
            ("models:models"),
            ("services:services"),
            ("data:data"),
            ("compiled_startup.py:."),
            ("startup_check.py:."),
        ],
        "hidden_imports": [
            "mysql.connector",
            "customtkinter",
            "tkcalendar",
            "matplotlib",
            "PIL",
            "dateutil",
            "sqlite3",
            "tkinter",
            "tkinter.ttk",
            "plyer",
            "threading",
            "json",
            "datetime",
            "os",
            "sys",
        ],
        "exclude_modules": [
            "tkinter.test",
            "test",
            "unittest",
        ],
    })

# Additional files to include
ADDITIONAL_FILES = [
    "README.md",
    "LICENSE",
    "requirements.txt",
]

# Directories to exclude from build
EXCLUDE_DIRS = [
    "__pycache__",
    ".git",
    ".vscode",
    "build",
    "dist",
    "*.egg-info",
    ".pytest_cache",
    "tests",
]

def get_platform_name():
    """Get platform-specific name for distribution"""
    system = platform.system().lower()
    machine = platform.machine().lower()

    if system == "windows":
        return f"windows-{machine}"
    elif system == "darwin":
        return f"macos-{machine}"
    elif system == "linux":
        return f"linux-{machine}"
    else:
        return f"{system}-{machine}"

def get_output_filename():
    """Get platform-specific output filename"""
    platform_name = get_platform_name()

    if IS_WINDOWS:
        return f"{APP_NAME}-v{APP_VERSION}-{platform_name}.exe"
    elif IS_MACOS:
        return f"{APP_NAME}-v{APP_VERSION}-{platform_name}.app"
    else:
        return f"{APP_NAME}-v{APP_VERSION}-{platform_name}"

# Build optimization settings
OPTIMIZATION_CONFIG = {
    "strip": True,  # Strip debug symbols
    "upx": False,   # UPX compression (set to True if UPX is installed)
    "console": False,  # Hide console window
    "debug": False,  # Disable debug mode
}
