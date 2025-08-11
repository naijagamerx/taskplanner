"""
Create executable for Task Planner with custom icon
Uses PyInstaller to create a standalone executable with the email icon
"""

import os
import sys
import subprocess
import shutil

def check_pyinstaller():
    """Check if PyInstaller is installed"""
    try:
        import PyInstaller
        return True
    except ImportError:
        return False

def install_pyinstaller():
    """Install PyInstaller"""
    print("📦 Installing PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        return True
    except subprocess.CalledProcessError:
        return False

def create_executable():
    """Create executable with custom icon"""
    print("🔨 Creating Task Planner executable...")
    
    # Paths
    main_script = "main.py"
    icon_path = os.path.join("assets", "icons", "favicon.ico")
    dist_dir = "dist"
    build_dir = "build"
    
    # Check if icon exists
    if not os.path.exists(icon_path):
        print(f"❌ Icon file not found: {icon_path}")
        return False
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",                    # Single executable file
        "--windowed",                   # No console window
        f"--icon={icon_path}",         # Custom icon
        "--name=TaskPlanner",          # Executable name
        "--add-data=assets;assets",    # Include assets folder
        "--add-data=config;config",    # Include config folder
        "--add-data=database;database", # Include database folder
        "--add-data=gui;gui",          # Include gui folder
        "--add-data=models;models",    # Include models folder
        "--add-data=services;services", # Include services folder
        main_script
    ]
    
    try:
        print("⚙️ Running PyInstaller...")
        print(f"Command: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Executable created successfully!")
            
            # Check if executable exists
            exe_path = os.path.join(dist_dir, "TaskPlanner.exe")
            if os.path.exists(exe_path):
                size_mb = os.path.getsize(exe_path) / (1024 * 1024)
                print(f"📁 Executable location: {exe_path}")
                print(f"📊 File size: {size_mb:.1f} MB")
                
                # Create a shortcut info
                print("\n🎯 Executable Features:")
                print("   ✅ Custom email icon in taskbar")
                print("   ✅ No console window")
                print("   ✅ Standalone - no Python required")
                print("   ✅ All assets included")
                print("   ✅ Ready for distribution")
                
                return True
            else:
                print("❌ Executable not found after build")
                return False
        else:
            print("❌ PyInstaller failed:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error creating executable: {e}")
        return False

def cleanup_build_files():
    """Clean up build files"""
    print("🧹 Cleaning up build files...")
    
    dirs_to_remove = ["build", "__pycache__"]
    files_to_remove = ["TaskPlanner.spec"]
    
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   🗑️ Removed {dir_name}/")
    
    for file_name in files_to_remove:
        if os.path.exists(file_name):
            os.remove(file_name)
            print(f"   🗑️ Removed {file_name}")

def main():
    """Create executable with icon"""
    print("=" * 60)
    print("🚀 TASK PLANNER EXECUTABLE BUILDER")
    print("=" * 60)
    
    # Check PyInstaller
    if not check_pyinstaller():
        print("📦 PyInstaller not found. Installing...")
        if not install_pyinstaller():
            print("❌ Failed to install PyInstaller")
            return False
        print("✅ PyInstaller installed successfully")
    else:
        print("✅ PyInstaller is available")
    
    # Check icon
    icon_path = os.path.join("assets", "icons", "favicon.ico")
    if not os.path.exists(icon_path):
        print("❌ Icon file not found. Run setup_app_icon.py first")
        return False
    print("✅ Icon file found")
    
    # Create executable
    success = create_executable()
    
    if success:
        print("\n🎉 BUILD SUCCESSFUL!")
        print("\n📋 What was created:")
        print("   • TaskPlanner.exe - Standalone executable")
        print("   • Custom email icon for taskbar")
        print("   • All dependencies included")
        print("   • No Python installation required")
        
        print("\n🚀 How to use:")
        print("   1. Find TaskPlanner.exe in dist/ folder")
        print("   2. Double-click to run")
        print("   3. Icon appears in taskbar")
        print("   4. Distribute to other computers")
        
        print("\n💡 Tips:")
        print("   • Move exe to desired location")
        print("   • Create desktop shortcut")
        print("   • Icon will show in taskbar and Alt+Tab")
        print("   • No need to install Python on target machines")
        
        # Ask about cleanup
        cleanup = input("\n🧹 Clean up build files? (y/n): ").lower().strip()
        if cleanup in ['y', 'yes']:
            cleanup_build_files()
            print("✅ Build files cleaned up")
        
    else:
        print("\n❌ BUILD FAILED!")
        print("Check error messages above")
    
    print("=" * 60)
    return success

if __name__ == "__main__":
    main()
