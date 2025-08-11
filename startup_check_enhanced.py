#!/usr/bin/env python3
"""
Enhanced Startup Check for Task Planner
Ensures all dependencies and configurations are ready before launching the main application
Enhanced for compiled executable compatibility
"""

import sys
import os
import traceback
from pathlib import Path

def print_startup_header():
    """Print startup header"""
    print("Task Planner - Environment Setup")
    print("=" * 40)

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print(f"❌ Python {sys.version_info.major}.{sys.version_info.minor} detected")
        print("❌ Python 3.8 or higher is required")
        return False

    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def check_dependencies():
    """Check if all required dependencies are available"""
    dependencies = [
        ('tkinter', 'GUI framework'),
        ('sqlite3', 'Database support'),
        ('json', 'Configuration files'),
        ('datetime', 'Date/time handling'),
        ('pathlib', 'File system operations'),
        ('logging', 'Application logging'),
        ('threading', 'Background operations'),
        ('queue', 'Thread communication'),
        ('os', 'Operating system interface'),
        ('sys', 'System interface'),
    ]

    optional_dependencies = [
        ('mysql.connector', 'MySQL database support'),
        ('customtkinter', 'Enhanced GUI'),
        ('tkcalendar', 'Calendar widget'),
        ('matplotlib', 'Analytics charts'),
        ('PIL', 'Image processing'),
        ('plyer', 'System notifications'),
        ('pygame', 'Sound notifications'),
        ('cryptography', 'Security features'),
    ]

    missing_required = []
    missing_optional = []

    # Check required dependencies
    for module, description in dependencies:
        try:
            __import__(module)
        except ImportError:
            missing_required.append((module, description))

    # Check optional dependencies
    for module, description in optional_dependencies:
        try:
            __import__(module)
        except ImportError:
            missing_optional.append((module, description))

    if missing_required:
        print("❌ Missing required dependencies:")
        for module, description in missing_required:
            print(f"   - {module}: {description}")
        return False

    if missing_optional:
        print("⚠️  Missing optional dependencies (reduced functionality):")
        for module, description in missing_optional:
            print(f"   - {module}: {description}")
        print("Enhanced features not available - using basic functionality")
    else:
        print("✅ All dependencies available")

    return True

def get_app_directory():
    """Get the application directory (works for both script and executable)"""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        return Path(sys.executable).parent
    else:
        # Running as script
        return Path(__file__).parent

def setup_data_directory():
    """Ensure data directory exists"""
    try:
        app_dir = get_app_directory()
        data_dir = app_dir / "data"
        data_dir.mkdir(exist_ok=True)

        print(f"✅ Data directory ready: {data_dir}")
        return True

    except Exception as e:
        print(f"❌ Failed to setup data directory: {e}")
        return False

def setup_config_directory():
    """Ensure config directory exists with required files"""
    try:
        app_dir = get_app_directory()
        config_dir = app_dir / "config"

        # Create config directory if it doesn't exist
        if not config_dir.exists():
            config_dir.mkdir(exist_ok=True)
            print(f"✅ Created config directory: {config_dir}")

        return True

    except Exception as e:
        print(f"❌ Failed to setup config directory: {e}")
        return False

def check_configuration():
    """Check and setup configuration files"""
    try:
        app_dir = get_app_directory()

        # Setup config directory
        if not setup_config_directory():
            return False

        # Check for settings file
        settings_path = app_dir / "settings.json"
        if not settings_path.exists():
            create_default_settings(settings_path)

        return True

    except Exception as e:
        print(f"❌ Configuration check failed: {e}")
        return False

def create_default_settings(settings_path):
    """Create default settings file"""
    try:
        import json

        default_settings = {
            "appearance": {
                "theme": "dark",
                "font_size": 12
            },
            "notifications": {
                "enabled": True,
                "sound_enabled": True,
                "reminder_minutes": 15,
                "repeat_interval": 60
            },
            "database": {
                "type": "sqlite",
                "auto_backup": True
            },
            "window": {
                "start_maximized": True,
                "center_on_start": True
            }
        }

        settings_path.parent.mkdir(exist_ok=True)
        with open(settings_path, 'w') as f:
            json.dump(default_settings, f, indent=2)

        print(f"✅ Created default settings: {settings_path}")

    except Exception as e:
        print(f"⚠️  Could not create default settings: {e}")

def check_executable_environment():
    """Check if running as executable and setup accordingly"""
    try:
        if getattr(sys, 'frozen', False):
            print("✅ Running as compiled executable")

            # Add executable directory to path for imports
            exe_dir = Path(sys.executable).parent
            if str(exe_dir) not in sys.path:
                sys.path.insert(0, str(exe_dir))

            # Set working directory to executable directory
            os.chdir(exe_dir)
            print(f"✅ Working directory: {exe_dir}")

        else:
            print("✅ Running as Python script")

        return True

    except Exception as e:
        print(f"❌ Environment setup failed: {e}")
        return False

def run_startup_check(silent=False):
    """Run complete startup check"""
    if not silent:
        print_startup_header()

    try:
        # Check executable environment
        if not check_executable_environment():
            return False

        # Check Python version (silent mode)
        if sys.version_info < (3, 8):
            if not silent:
                print(f"❌ Python {sys.version_info.major}.{sys.version_info.minor} detected")
                print("❌ Python 3.8 or higher is required")
            return False

        if not silent:
            print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

        # Check dependencies (silent mode for compiled executables)
        if getattr(sys, 'frozen', False):
            # For compiled executables, do minimal dependency checking
            essential_modules = ['tkinter', 'sqlite3', 'json', 'datetime']
            for module in essential_modules:
                try:
                    __import__(module)
                except ImportError:
                    if not silent:
                        print(f"❌ Missing essential module: {module}")
                    return False
        else:
            # For script mode, do full dependency check
            if not check_dependencies():
                return False

        # Setup data directory
        if not setup_data_directory():
            return False

        # Check configuration
        if not check_configuration():
            return False

        if not silent:
            print("Environment setup complete")
        return True

    except Exception as e:
        if not silent:
            print(f"❌ Startup check failed: {e}")
            traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_startup_check()
    if not success:
        print("\n❌ Startup check failed. Please resolve the issues above.")
        input("Press Enter to exit...")
        sys.exit(1)
    else:
        print("✅ Startup check completed successfully")
