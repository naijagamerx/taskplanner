"""
Setup Task Planner for distribution to different computers
Handles database configuration and creates portable versions
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path

def create_portable_sqlite_version():
    """Create a portable version using SQLite"""
    print("📦 Creating portable SQLite version...")

    # Create portable directory
    portable_dir = "TaskPlanner_Portable"
    if os.path.exists(portable_dir):
        shutil.rmtree(portable_dir)

    os.makedirs(portable_dir)

    # Copy application files
    files_to_copy = [
        "main.py",
        "gui/",
        "models/",
        "database/",
        "config/",
        "services/",
        "assets/",
        "requirements.txt"
    ]

    for item in files_to_copy:
        if os.path.exists(item):
            if os.path.isdir(item):
                shutil.copytree(item, os.path.join(portable_dir, item))
            else:
                shutil.copy2(item, portable_dir)

    # Create SQLite configuration
    sqlite_config = {
        "type": "sqlite",
        "database": "data/task_planner.db"
    }

    config_dir = os.path.join(portable_dir, "config")
    with open(os.path.join(config_dir, "db_config.json"), "w", encoding='utf-8') as f:
        json.dump(sqlite_config, f, indent=2)

    # Create data directory
    os.makedirs(os.path.join(portable_dir, "data"), exist_ok=True)

    # Create startup script
    startup_script = """@echo off
echo Starting Task Planner (Portable SQLite Version)...
python main.py
pause"""

    with open(os.path.join(portable_dir, "start.bat"), "w", encoding='utf-8') as f:
        f.write(startup_script)

    # Create README
    readme_content = """# Task Planner - Portable Version

This is a portable version of Task Planner that uses SQLite database.

## Requirements
- Python 3.8 or higher
- All dependencies will be installed automatically

## How to Run
1. Double-click 'start.bat' (Windows)
2. Or run: python main.py

## Features
- No server setup required
- Database file travels with the application
- Perfect for single users
- Easy backup and sharing

## Database Location
Your tasks are stored in: data/task_planner.db

## Backup
Simply copy the entire folder to backup all your data.
"""

    with open(os.path.join(portable_dir, "README.txt"), "w", encoding='utf-8') as f:
        f.write(readme_content)

    print(f"✅ Portable version created in: {portable_dir}/")
    return portable_dir

def create_mysql_template():
    """Create MySQL configuration template"""
    print("🗄️ Creating MySQL configuration template...")

    mysql_dir = "TaskPlanner_MySQL"
    if os.path.exists(mysql_dir):
        shutil.rmtree(mysql_dir)

    os.makedirs(mysql_dir)

    # Copy application files (same as portable)
    files_to_copy = [
        "main.py",
        "gui/",
        "models/",
        "database/",
        "config/",
        "services/",
        "assets/",
        "requirements.txt"
    ]

    for item in files_to_copy:
        if os.path.exists(item):
            if os.path.isdir(item):
                shutil.copytree(item, os.path.join(mysql_dir, item))
            else:
                shutil.copy2(item, mysql_dir)

    # Create MySQL configuration template
    mysql_config_template = {
        "type": "mysql",
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "",
        "database": "task_planner",
        "charset": "utf8mb4",
        "autocommit": True
    }

    config_dir = os.path.join(mysql_dir, "config")
    with open(os.path.join(config_dir, "db_config_template.json"), "w", encoding='utf-8') as f:
        json.dump(mysql_config_template, f, indent=2)

    # Create setup script
    setup_script = """@echo off
echo Task Planner - MySQL Setup
echo.
echo This version requires MySQL server to be installed and running.
echo.
echo Setup Steps:
echo 1. Install MySQL server if not already installed
echo 2. Create database 'task_planner'
echo 3. Configure database settings in the application
echo.
echo Starting Task Planner...
python main.py
pause"""

    with open(os.path.join(mysql_dir, "setup_mysql.bat"), "w", encoding='utf-8') as f:
        f.write(setup_script)

    # Create MySQL README
    mysql_readme = """# Task Planner - MySQL Version

This version uses MySQL database for multi-user environments.

## Requirements
- Python 3.8 or higher
- MySQL Server 5.7 or higher
- Network access to MySQL server

## Setup Instructions

### 1. Install MySQL Server
- Download from: https://dev.mysql.com/downloads/mysql/
- Install and configure with root password

### 2. Create Database
Run in MySQL:
```sql
CREATE DATABASE task_planner CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 3. Configure Application
1. Run: python main.py
2. Go to Settings → Database
3. Click "Configure Database"
4. Enter your MySQL connection details

### 4. Alternative: Environment Variables
Set these environment variables:
- DB_HOST=localhost
- DB_PORT=3306
- DB_USER=root
- DB_PASSWORD=your_password
- DB_NAME=task_planner

## Multi-User Setup
- Install MySQL on a server
- Configure all clients to connect to the server
- Each user can have their own tasks in the same database

## Backup
Use MySQL backup tools:
```bash
mysqldump -u root -p task_planner > backup.sql
```
"""

    with open(os.path.join(mysql_dir, "README_MySQL.txt"), "w", encoding='utf-8') as f:
        f.write(mysql_readme)

    print(f"✅ MySQL version created in: {mysql_dir}/")
    return mysql_dir

def create_installer_script():
    """Create installer script for dependencies"""
    print("📋 Creating installer script...")

    installer_content = """#!/usr/bin/env python3
\"\"\"
Task Planner Installer
Installs dependencies and sets up the application
\"\"\"

import subprocess
import sys
import os

def install_dependencies():
    \"\"\"Install required Python packages\"\"\"
    print("📦 Installing dependencies...")

    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_database():
    \"\"\"Setup database based on configuration\"\"\"
    print("🗄️ Setting up database...")

    try:
        # Import after dependencies are installed
        from database.db_manager import db_manager

        if db_manager.test_connection():
            print("✅ Database connection successful!")

            # Initialize database schema
            if db_manager.initialize_database():
                print("✅ Database schema initialized!")
                return True
            else:
                print("❌ Failed to initialize database schema")
                return False
        else:
            print("❌ Database connection failed")
            print("💡 Please configure database settings in the application")
            return False

    except Exception as e:
        print(f"❌ Database setup error: {e}")
        return False

def main():
    \"\"\"Main installer function\"\"\"
    print("=" * 50)
    print("🚀 TASK PLANNER INSTALLER")
    print("=" * 50)

    # Install dependencies
    if not install_dependencies():
        print("❌ Installation failed!")
        return False

    # Setup database
    if not setup_database():
        print("⚠️ Database setup incomplete - you can configure it later")

    print("\\n✅ Installation complete!")
    print("\\n🚀 To start the application:")
    print("   python main.py")
    print("\\n⚙️ To configure database:")
    print("   Go to Settings → Database → Configure Database")

    return True

if __name__ == "__main__":
    main()
"""

    with open("install.py", "w", encoding='utf-8') as f:
        f.write(installer_content)

    print("✅ Installer script created: install.py")

def create_distribution_guide():
    """Create distribution guide"""
    print("📖 Creating distribution guide...")

    guide_content = """# Task Planner - Distribution Guide

## Distribution Options

### 1. Portable SQLite Version (Recommended)
**Best for:** Single users, easy distribution, no server setup

**Folder:** TaskPlanner_Portable/
- ✅ No server required
- ✅ Database travels with app
- ✅ Easy backup and sharing
- ✅ Works offline

**How to distribute:**
1. Zip the TaskPlanner_Portable folder
2. Send to users
3. Users extract and run start.bat

### 2. MySQL Version
**Best for:** Multi-user environments, centralized data

**Folder:** TaskPlanner_MySQL/
- ✅ Multi-user support
- ✅ Centralized database
- ✅ Network sharing
- ❌ Requires MySQL server

**How to distribute:**
1. Set up MySQL server
2. Zip the TaskPlanner_MySQL folder
3. Send to users with MySQL connection details
4. Users run setup_mysql.bat

### 3. Executable Version
**Best for:** Users without Python

**Command:** python create_executable.py
- ✅ No Python required
- ✅ Single .exe file
- ✅ Professional distribution
- ❌ Larger file size

## Installation Instructions for Users

### Option A: Portable (SQLite)
1. Extract TaskPlanner_Portable.zip
2. Double-click start.bat
3. Application starts with local database

### Option B: MySQL
1. Extract TaskPlanner_MySQL.zip
2. Install MySQL server (if not available)
3. Run setup_mysql.bat
4. Configure database in Settings

### Option C: Executable
1. Download TaskPlanner.exe
2. Double-click to run
3. Configure database in Settings → Database

## Configuration Options

### Environment Variables
Set these for automatic configuration:

**SQLite:**
```
DB_SQLITE_PATH=data/task_planner.db
```

**MySQL:**
```
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=task_planner
```

### Configuration File
Create config/db_config.json:

**SQLite:**
```json
{
  "type": "sqlite",
  "database": "data/task_planner.db"
}
```

**MySQL:**
```json
{
  "type": "mysql",
  "host": "localhost",
  "port": 3306,
  "user": "root",
  "password": "",
  "database": "task_planner"
}
```

## Troubleshooting

### Common Issues
1. **Python not found:** Install Python 3.8+
2. **Dependencies missing:** Run install.py
3. **Database connection failed:** Check MySQL server
4. **Permission denied:** Run as administrator

### Support
- Check README files in each distribution folder
- Use Settings → Database → Test Connection
- Configure database through the GUI

## Security Notes
- Never include passwords in distributed files
- Use environment variables for sensitive data
- Consider using database user accounts with limited permissions
- Backup database regularly
"""

    with open("DISTRIBUTION_GUIDE.md", "w", encoding='utf-8') as f:
        f.write(guide_content)

    print("✅ Distribution guide created: DISTRIBUTION_GUIDE.md")

def main():
    """Create distribution packages"""
    print("=" * 60)
    print("📦 TASK PLANNER DISTRIBUTION SETUP")
    print("=" * 60)

    try:
        # Create portable SQLite version
        portable_dir = create_portable_sqlite_version()

        # Create MySQL template
        mysql_dir = create_mysql_template()

        # Create installer script
        create_installer_script()

        # Create distribution guide
        create_distribution_guide()

        print("\n" + "=" * 60)
        print("✅ DISTRIBUTION SETUP COMPLETE!")
        print("=" * 60)

        print("\n📦 Created distributions:")
        print(f"   📁 {portable_dir}/ - Portable SQLite version")
        print(f"   📁 {mysql_dir}/ - MySQL server version")
        print("   📄 install.py - Dependency installer")
        print("   📖 DISTRIBUTION_GUIDE.md - Complete guide")

        print("\n🚀 Next steps:")
        print("   1. Test both versions locally")
        print("   2. Create executable: python create_executable.py")
        print("   3. Zip folders for distribution")
        print("   4. Share with users along with instructions")

        print("\n💡 Recommendation:")
        print("   Use SQLite version for most users - it's simpler!")

    except Exception as e:
        print(f"❌ Error creating distributions: {e}")
        return False

    return True

if __name__ == "__main__":
    main()
