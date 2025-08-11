"""
Setup script for Task Planner application
Creates executable using PyInstaller
"""

import os
import sys
import subprocess
from pathlib import Path

def create_executable():
    """Create executable using PyInstaller"""
    
    # PyInstaller command
    cmd = [
        'pyinstaller',
        '--onefile',                    # Create single executable file
        '--windowed',                   # Hide console window (for GUI apps)
        '--name=TaskPlanner',           # Executable name
        '--icon=icon.ico',              # Application icon (if available)
        '--add-data=database;database', # Include database folder
        '--add-data=gui;gui',           # Include GUI folder
        '--add-data=models;models',     # Include models folder
        '--add-data=config;config',     # Include config folder
        '--add-data=utils;utils',       # Include utils folder (if created)
        '--hidden-import=mysql.connector',
        '--hidden-import=customtkinter',
        '--hidden-import=tkcalendar',
        '--hidden-import=matplotlib',
        '--hidden-import=PIL',
        '--collect-all=customtkinter',
        '--collect-all=tkcalendar',
        'main.py'                       # Main script
    ]
    
    print("Creating executable with PyInstaller...")
    print("Command:", ' '.join(cmd))
    
    try:
        # Run PyInstaller
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("PyInstaller output:")
        print(result.stdout)
        
        if result.stderr:
            print("PyInstaller warnings/errors:")
            print(result.stderr)
        
        print("\n✅ Executable created successfully!")
        print("📁 Check the 'dist' folder for the executable file.")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creating executable: {e}")
        print("Output:", e.stdout)
        print("Error:", e.stderr)
        return False
    
    except FileNotFoundError:
        print("❌ PyInstaller not found. Please install it with: pip install pyinstaller")
        return False
    
    return True

def create_installer():
    """Create installer using NSIS (Windows) or other tools"""
    print("\n📦 Creating installer...")
    
    # This would require NSIS or other installer tools
    # For now, just provide instructions
    print("""
To create an installer:

Windows (NSIS):
1. Install NSIS (Nullsoft Scriptable Install System)
2. Create an NSIS script (.nsi file)
3. Compile the script to create an installer

macOS:
1. Use create-dmg or similar tools
2. Create a .dmg file with the application

Linux:
1. Create .deb package (Debian/Ubuntu)
2. Create .rpm package (Red Hat/Fedora)
3. Create AppImage for universal compatibility

For now, users can run the executable directly from the 'dist' folder.
    """)

def check_dependencies():
    """Check if all dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'mysql-connector-python',
        'customtkinter',
        'tkcalendar',
        'matplotlib',
        'Pillow',
        'python-dateutil',
        'pyinstaller'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - Missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Install them with: pip install " + " ".join(missing_packages))
        return False
    
    print("\n✅ All dependencies are installed!")
    return True

def create_icon():
    """Create application icon if it doesn't exist"""
    icon_path = "icon.ico"
    
    if not os.path.exists(icon_path):
        print(f"⚠️  Icon file '{icon_path}' not found.")
        print("Creating a simple icon placeholder...")
        
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Create a simple icon
            size = (64, 64)
            img = Image.new('RGBA', size, (52, 152, 219, 255))  # Blue background
            draw = ImageDraw.Draw(img)
            
            # Draw a simple task list icon
            draw.rectangle([10, 15, 54, 20], fill='white')
            draw.rectangle([10, 25, 54, 30], fill='white')
            draw.rectangle([10, 35, 54, 40], fill='white')
            draw.rectangle([10, 45, 54, 50], fill='white')
            
            # Add checkmarks
            draw.text((12, 12), "✓", fill='green', font_size=12)
            draw.text((12, 22), "✓", fill='green', font_size=12)
            draw.text((12, 32), "○", fill='gray', font_size=12)
            draw.text((12, 42), "○", fill='gray', font_size=12)
            
            img.save(icon_path, format='ICO')
            print(f"✅ Created icon: {icon_path}")
            
        except ImportError:
            print("⚠️  Pillow not available for icon creation. Using default icon.")
        except Exception as e:
            print(f"⚠️  Could not create icon: {e}")

def clean_build():
    """Clean previous build files"""
    print("🧹 Cleaning previous build files...")
    
    folders_to_clean = ['build', 'dist', '__pycache__']
    files_to_clean = ['*.spec']
    
    for folder in folders_to_clean:
        if os.path.exists(folder):
            import shutil
            shutil.rmtree(folder)
            print(f"🗑️  Removed {folder}")
    
    # Remove .spec files
    for spec_file in Path('.').glob('*.spec'):
        spec_file.unlink()
        print(f"🗑️  Removed {spec_file}")

def main():
    """Main setup function"""
    print("🚀 Task Planner - Build Setup")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists('main.py'):
        print("❌ Error: main.py not found. Please run this script from the project root directory.")
        return
    
    # Clean previous builds
    clean_build()
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install missing dependencies before building.")
        return
    
    # Create icon
    create_icon()
    
    # Create executable
    if create_executable():
        print("\n🎉 Build completed successfully!")
        
        # Show final instructions
        print("\n📋 Next Steps:")
        print("1. Test the executable in the 'dist' folder")
        print("2. Ensure MySQL server is running before using the app")
        print("3. The app will create the database automatically on first run")
        
        # Ask about installer
        try:
            create_inst = input("\n❓ Would you like instructions for creating an installer? (y/n): ")
            if create_inst.lower() in ['y', 'yes']:
                create_installer()
        except KeyboardInterrupt:
            print("\n👋 Build process completed.")
    
    else:
        print("\n❌ Build failed. Please check the errors above.")

if __name__ == "__main__":
    main()
