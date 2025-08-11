#!/usr/bin/env python3
"""
Create distribution package for Task Planner
"""

import os
import shutil
import zipfile
import platform
from datetime import datetime
from pathlib import Path

def create_distribution_package():
    """Create a complete distribution package"""
    
    print("📦 Creating Task Planner Distribution Package")
    print("=" * 50)
    
    # Get version and platform info
    version = "1.0.0"
    platform_name = platform.system().lower()
    timestamp = datetime.now().strftime("%Y%m%d")
    
    # Package name
    package_name = f"TaskPlanner-v{version}-{platform_name}-{timestamp}"
    package_dir = f"dist/{package_name}"
    
    # Create package directory
    os.makedirs(package_dir, exist_ok=True)
    print(f"📁 Created package directory: {package_dir}")
    
    # Copy executable
    if platform.system() == "Windows":
        exe_name = "TaskPlanner.exe"
    elif platform.system() == "Darwin":
        exe_name = "TaskPlanner.app"
    else:
        exe_name = "TaskPlanner"
    
    exe_source = f"dist/{exe_name}"
    exe_dest = f"{package_dir}/{exe_name}"
    
    if os.path.exists(exe_source):
        if os.path.isdir(exe_source):  # macOS .app bundle
            shutil.copytree(exe_source, exe_dest)
        else:  # Windows .exe or Linux binary
            shutil.copy2(exe_source, exe_dest)
        
        # Get file size
        if os.path.isdir(exe_dest):
            size = sum(f.stat().st_size for f in Path(exe_dest).rglob('*') if f.is_file())
        else:
            size = os.path.getsize(exe_dest)
        
        size_mb = size / (1024 * 1024)
        print(f"✅ Copied executable: {exe_name} ({size_mb:.1f} MB)")
    else:
        print(f"❌ Executable not found: {exe_source}")
        return False
    
    # Create README for distribution
    readme_content = f"""# Task Planner v{version}

## 🚀 Quick Start

### Windows Users:
1. Double-click `TaskPlanner.exe` to run the application
2. Follow the database setup wizard on first launch
3. Start organizing your tasks!

### macOS Users:
1. Drag `TaskPlanner.app` to your Applications folder
2. Double-click to launch
3. If you see a security warning, go to System Preferences > Security & Privacy and click "Open Anyway"
4. Follow the database setup wizard on first launch

## 🗄️ Database Setup

Task Planner supports two database options:

### Option 1: MySQL (Recommended for multiple users)
- Install MySQL Server from https://dev.mysql.com/downloads/
- Create a database named 'task_planner' (or let the app create it)
- Use the database setup dialog to configure connection

### Option 2: SQLite (Simple, single-user)
- No additional software required
- Creates a local database file
- Perfect for personal use

## ✨ Features

- ✅ **Task Management**: Create, edit, and organize tasks
- 📅 **Calendar Integration**: Schedule tasks with due dates
- 🏷️ **Categories & Priorities**: Organize with custom categories
- 📊 **Analytics & Reports**: Track productivity and progress
- 🔍 **Advanced Search**: Find tasks quickly with smart search
- 🎨 **Modern UI**: Clean, intuitive interface
- 💾 **Reliable Storage**: MySQL or SQLite database support

## 📋 System Requirements

### Windows:
- Windows 10 or later
- 4GB RAM minimum
- 100MB free disk space
- MySQL Server (optional, for MySQL database)

### macOS:
- macOS 10.14 (Mojave) or later
- 4GB RAM minimum
- 100MB free disk space
- MySQL Server (optional, for MySQL database)

## 🔧 Troubleshooting

### Application won't start:
1. Make sure you have the required system version
2. Check antivirus software (may need to whitelist the app)
3. Try running as administrator (Windows) or check security settings (macOS)

### Database connection issues:
1. Ensure MySQL server is running (if using MySQL)
2. Check database credentials in the setup dialog
3. Try SQLite option for simpler setup

### Performance issues:
1. Close other applications to free up memory
2. Check available disk space
3. Restart the application

## 📞 Support

For technical support or questions:
- Check the troubleshooting section above
- Review the database setup guide
- Contact the development team

## 📄 License

This software is provided as-is for personal and commercial use.

---

**Built with ❤️ using Python and CustomTkinter**
**Package created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}**
"""
    
    readme_path = f"{package_dir}/README.txt"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print(f"✅ Created: README.txt")
    
    # Create installation guide
    install_guide = f"""# Installation Guide - Task Planner v{version}

## 📥 Installation Steps

### Windows Installation:
1. **Download**: Extract the TaskPlanner package to a folder
2. **Run**: Double-click `TaskPlanner.exe`
3. **Setup**: Follow the database configuration wizard
4. **Optional**: Create a desktop shortcut for easy access

### macOS Installation:
1. **Download**: Extract the TaskPlanner package
2. **Install**: Drag `TaskPlanner.app` to your Applications folder
3. **Security**: If prompted, allow the app in System Preferences > Security & Privacy
4. **Run**: Launch from Applications or Launchpad
5. **Setup**: Follow the database configuration wizard

## 🗄️ Database Configuration

### First-Time Setup:
1. Launch Task Planner
2. The database setup dialog will appear automatically
3. Choose your preferred database type:
   - **MySQL**: For multi-user or production use
   - **SQLite**: For simple, single-user setup
4. Enter connection details and test the connection
5. Click "Save & Continue" to complete setup

### MySQL Setup:
1. **Install MySQL**: Download from https://dev.mysql.com/downloads/
2. **Create Database**: The app can create it automatically
3. **Configure Connection**:
   - Host: localhost (or your server address)
   - Port: 3306 (default)
   - Database: task_planner
   - Username: your MySQL username
   - Password: your MySQL password

### SQLite Setup:
1. **Choose SQLite** in the database type selection
2. **Database File**: Enter a filename (e.g., "my_tasks.db")
3. **Location**: The file will be created in the app directory
4. **No Server Required**: SQLite works without additional software

## 🚀 Getting Started

### After Installation:
1. **Create Categories**: Set up task categories (Work, Personal, etc.)
2. **Set Priorities**: Define priority levels (High, Medium, Low)
3. **Add Tasks**: Start creating your first tasks
4. **Explore Features**: Try the calendar, analytics, and search functions

### Tips for Success:
- Use descriptive task titles
- Set realistic due dates
- Organize with categories and priorities
- Review analytics to track progress
- Use search to find tasks quickly

## 🔄 Updates

To update Task Planner:
1. Download the latest version
2. Close the current application
3. Replace the old executable with the new one
4. Your database and settings will be preserved

## 🗑️ Uninstallation

### Windows:
1. Delete the TaskPlanner folder
2. Remove any desktop shortcuts
3. Database files will remain unless manually deleted

### macOS:
1. Drag TaskPlanner.app to Trash
2. Database files will remain unless manually deleted

---

**Need help? Check README.txt for troubleshooting tips**
"""
    
    install_path = f"{package_dir}/INSTALL.txt"
    with open(install_path, 'w', encoding='utf-8') as f:
        f.write(install_guide)
    print(f"✅ Created: INSTALL.txt")
    
    # Copy license if it exists
    if os.path.exists("LICENSE"):
        shutil.copy2("LICENSE", f"{package_dir}/LICENSE.txt")
        print(f"✅ Copied: LICENSE.txt")
    
    # Create ZIP package
    zip_name = f"dist/{package_name}.zip"
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, "dist")
                zipf.write(file_path, arc_name)
    
    zip_size = os.path.getsize(zip_name) / (1024 * 1024)
    print(f"✅ Created ZIP package: {zip_name} ({zip_size:.1f} MB)")
    
    print("\n" + "=" * 50)
    print("🎉 DISTRIBUTION PACKAGE CREATED SUCCESSFULLY!")
    print("=" * 50)
    print(f"📦 Package: {package_name}")
    print(f"📁 Folder: {package_dir}")
    print(f"🗜️ ZIP File: {zip_name}")
    print(f"💾 Total Size: {zip_size:.1f} MB")
    print("\n📋 Package Contents:")
    print(f"   • {exe_name} - Main application")
    print(f"   • README.txt - User guide and features")
    print(f"   • INSTALL.txt - Installation instructions")
    if os.path.exists(f"{package_dir}/LICENSE.txt"):
        print(f"   • LICENSE.txt - Software license")
    
    print(f"\n🚀 Ready for distribution!")
    print(f"   Share the ZIP file: {zip_name}")
    print(f"   Or share the folder: {package_dir}")
    
    return True

if __name__ == "__main__":
    try:
        create_distribution_package()
    except Exception as e:
        print(f"❌ Error creating distribution package: {e}")
        import traceback
        traceback.print_exc()
