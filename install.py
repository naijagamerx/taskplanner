#!/usr/bin/env python3
"""
Task Planner Installer
Installs dependencies and sets up the application
"""

import subprocess
import sys
import os

def install_dependencies():
    """Install required Python packages"""
    print("📦 Installing dependencies...")

    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_database():
    """Setup database based on configuration"""
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
    """Main installer function"""
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

    print("\n✅ Installation complete!")
    print("\n🚀 To start the application:")
    print("   python main.py")
    print("\n⚙️ To configure database:")
    print("   Go to Settings → Database → Configure Database")

    return True

if __name__ == "__main__":
    main()
