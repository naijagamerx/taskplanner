#!/usr/bin/env python3
"""
Quick build script for testing PyInstaller setup
"""

import subprocess
import sys
import os
import platform

def quick_build():
    """Quick build test"""
    print(f"🚀 Quick Build Test for {platform.system()}")
    print("=" * 50)
    
    # Basic PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name", "TaskPlanner",
        "--distpath", "dist",
        "--workpath", "build",
        "--clean",
        "--noconfirm",
        "main.py"
    ]
    
    # Add platform-specific options
    if platform.system() == "Windows":
        # Add Windows icon if it exists
        if os.path.exists("assets/icons/app_icon.ico"):
            cmd.extend(["--icon", "assets/icons/app_icon.ico"])
    elif platform.system() == "Darwin":  # macOS
        # Add macOS icon if it exists
        if os.path.exists("assets/icons/app_icon.icns"):
            cmd.extend(["--icon", "assets/icons/app_icon.icns"])
    
    print(f"Command: {' '.join(cmd)}")
    print("\n🔧 Building...")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Build completed successfully!")
        
        # Check if executable was created
        if platform.system() == "Windows":
            exe_path = "dist/TaskPlanner.exe"
        elif platform.system() == "Darwin":
            exe_path = "dist/TaskPlanner.app"
        else:
            exe_path = "dist/TaskPlanner"
        
        if os.path.exists(exe_path):
            size = os.path.getsize(exe_path) / (1024 * 1024)  # MB
            print(f"📦 Executable created: {exe_path}")
            print(f"📏 Size: {size:.1f} MB")
            return True
        else:
            print(f"❌ Executable not found: {exe_path}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed with error code {e.returncode}")
        print(f"Error output: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Build failed with error: {e}")
        return False

if __name__ == "__main__":
    success = quick_build()
    sys.exit(0 if success else 1)
