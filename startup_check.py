#!/usr/bin/env python3
"""
Startup check for Task Planner
Ensures proper environment setup for distribution
"""

import os
import sys
from pathlib import Path

def ensure_data_directory():
    """Ensure data directory exists for SQLite database"""
    try:
        # Get the directory where the executable/script is located
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            app_dir = os.path.dirname(sys.executable)
        else:
            # Running as script
            app_dir = os.path.dirname(os.path.abspath(__file__))

        # Create data directory
        data_dir = os.path.join(app_dir, 'data')
        os.makedirs(data_dir, exist_ok=True)

        # Create config directory
        config_dir = os.path.join(app_dir, 'config')
        os.makedirs(config_dir, exist_ok=True)

        print(f"Data directory ready: {data_dir}")
        return True

    except Exception as e:
        print(f"Error creating data directory: {e}")
        return False

def check_dependencies():
    """Check if critical dependencies are available"""
    try:
        import customtkinter
        import mysql.connector
        import sqlite3
        import matplotlib
        print("All dependencies available")
        return True
    except ImportError as e:
        print(f"Missing dependency: {e}")
        return False

def setup_environment():
    """Setup environment for Task Planner"""
    print("Task Planner - Environment Setup")
    print("=" * 40)

    # Check dependencies
    if not check_dependencies():
        return False

    # Ensure directories exist
    if not ensure_data_directory():
        return False

    print("Environment setup complete")
    return True

if __name__ == "__main__":
    setup_environment()
