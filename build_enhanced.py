#!/usr/bin/env python3
"""
Enhanced Build Script for Task Planner
Creates a robust, portable executable that works on different computers
"""

import os
import sys
import shutil
import subprocess
import json
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f" {text}")
    print("="*60)

def print_step(step, text):
    """Print formatted step"""
    print(f"\n[{step}] {text}")

def check_dependencies():
    """Check if all required dependencies are installed"""
    print_step("1", "Checking Dependencies")
    
    required_packages = [
        'pyinstaller',
        'mysql-connector-python',
        'customtkinter',
        'tkcalendar',
        'matplotlib',
        'pillow',
        'python-dateutil',
        'plyer',
        'pygame',
        'cryptography'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'mysql-connector-python':
                import mysql.connector
            elif package == 'customtkinter':
                import customtkinter
            elif package == 'tkcalendar':
                import tkcalendar
            elif package == 'matplotlib':
                import matplotlib
            elif package == 'pillow':
                import PIL
            elif package == 'python-dateutil':
                import dateutil
            elif package == 'plyer':
                import plyer
            elif package == 'pygame':
                import pygame
            elif package == 'cryptography':
                import cryptography
            elif package == 'pyinstaller':
                import PyInstaller
            
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install " + " ".join(missing_packages))
        return False
    
    print("✅ All dependencies available")
    return True

def clean_build_directories():
    """Clean previous build artifacts"""
    print_step("2", "Cleaning Build Directories")
    
    dirs_to_clean = ['build', 'dist/__pycache__']
    files_to_clean = ['dist/TaskPlanner_Enhanced.exe']
    
    for dir_path in dirs_to_clean:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
            print(f"🧹 Removed {dir_path}")
    
    for file_path in files_to_clean:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"🧹 Removed {file_path}")
    
    print("✅ Build directories cleaned")

def verify_required_files():
    """Verify all required files exist"""
    print_step("3", "Verifying Required Files")
    
    required_files = [
        'main.py',
        'TaskPlanner_Enhanced.spec',
        'assets/icons/app_icon.ico',
        'config/database_config.py',
        'database/schema_sqlite.sql',
        'settings.json'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n❌ Missing required files: {', '.join(missing_files)}")
        return False
    
    print("✅ All required files present")
    return True

def create_version_file():
    """Create version information file for Windows executable"""
    print_step("4", "Creating Version Information")
    
    version_content = '''# Version information for PyInstaller
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(2, 0, 0, 0),
    prodvers=(2, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'Task Planner Solutions'),
        StringStruct(u'FileDescription', u'Task Planner - Comprehensive Life Planning'),
        StringStruct(u'FileVersion', u'2.0.0.0'),
        StringStruct(u'InternalName', u'TaskPlanner'),
        StringStruct(u'LegalCopyright', u'Copyright (C) 2024 Task Planner Solutions'),
        StringStruct(u'OriginalFilename', u'TaskPlanner_Enhanced.exe'),
        StringStruct(u'ProductName', u'Task Planner Enhanced'),
        StringStruct(u'ProductVersion', u'2.0.0.0')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)'''
    
    with open('version_info.txt', 'w') as f:
        f.write(version_content)
    
    print("✅ Version information file created")

def build_executable():
    """Build the executable using PyInstaller"""
    print_step("5", "Building Executable")
    
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--clean',
        '--noconfirm',
        'TaskPlanner_Enhanced.spec'
    ]
    
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("✅ Build completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed with error code {e.returncode}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False

def verify_executable():
    """Verify the built executable exists and is functional"""
    print_step("6", "Verifying Executable")
    
    exe_path = 'dist/TaskPlanner_Enhanced.exe'
    
    if not os.path.exists(exe_path):
        print(f"❌ Executable not found: {exe_path}")
        return False
    
    # Check file size (should be reasonable)
    file_size = os.path.getsize(exe_path) / (1024 * 1024)  # MB
    print(f"📦 Executable size: {file_size:.1f} MB")
    
    if file_size < 10:
        print("⚠️  Warning: Executable seems too small, might be missing dependencies")
    elif file_size > 500:
        print("⚠️  Warning: Executable seems very large")
    else:
        print("✅ Executable size looks reasonable")
    
    print(f"✅ Executable created: {exe_path}")
    return True

def create_distribution_package():
    """Create a complete distribution package"""
    print_step("7", "Creating Distribution Package")
    
    # Create distribution directory
    dist_dir = Path("TaskPlanner_Distribution")
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    
    dist_dir.mkdir()
    
    # Copy executable
    shutil.copy2("dist/TaskPlanner_Enhanced.exe", dist_dir / "TaskPlanner_Enhanced.exe")
    
    # Create data directory with default database
    data_dir = dist_dir / "data"
    data_dir.mkdir()
    
    # Copy default settings
    if os.path.exists("settings.json"):
        shutil.copy2("settings.json", dist_dir / "settings.json")
    
    # Create README for distribution
    readme_content = """# Task Planner Enhanced - Distribution Package

## Installation Instructions

1. Extract all files to a folder on your computer
2. Run TaskPlanner_Enhanced.exe to start the application
3. The application will create its database and configuration files automatically

## System Requirements

- Windows 10 or later
- No additional software installation required
- All dependencies are included in the executable

## First Run

- The application will start with SQLite database by default
- You can configure MySQL database in Settings > Database if needed
- Sample categories and tasks are included for demonstration

## Support

For support and updates, please contact the development team.

Version: 2.0.0
Build Date: """ + str(datetime.now().strftime("%Y-%m-%d")) + """
"""
    
    with open(dist_dir / "README.txt", "w") as f:
        f.write(readme_content)
    
    print(f"✅ Distribution package created: {dist_dir}")
    return True

def main():
    """Main build process"""
    print_header("Task Planner Enhanced - Build Process")
    
    # Import datetime here to avoid issues during dependency check
    import datetime
    
    try:
        # Step 1: Check dependencies
        if not check_dependencies():
            print("\n❌ Build failed: Missing dependencies")
            return False
        
        # Step 2: Clean build directories
        clean_build_directories()
        
        # Step 3: Verify required files
        if not verify_required_files():
            print("\n❌ Build failed: Missing required files")
            return False
        
        # Step 4: Create version file
        create_version_file()
        
        # Step 5: Build executable
        if not build_executable():
            print("\n❌ Build failed: PyInstaller error")
            return False
        
        # Step 6: Verify executable
        if not verify_executable():
            print("\n❌ Build failed: Executable verification failed")
            return False
        
        # Step 7: Create distribution package
        if not create_distribution_package():
            print("\n⚠️  Warning: Distribution package creation failed")
        
        print_header("BUILD SUCCESSFUL!")
        print("✅ TaskPlanner_Enhanced.exe created successfully")
        print("✅ Ready for distribution to other computers")
        print("\nNext steps:")
        print("1. Test the executable on this computer")
        print("2. Copy to other computers for testing")
        print("3. Verify all features work correctly")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Build failed with unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
