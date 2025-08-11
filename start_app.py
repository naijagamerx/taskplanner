"""
Simple application starter for Task Planner
This script helps start the application with better error handling and visibility
"""

import sys
import os
import traceback

def check_dependencies():
    """Check if all required dependencies are available"""
    print("🔍 Checking dependencies...")
    
    required_modules = [
        ('mysql.connector', 'mysql-connector-python'),
        ('customtkinter', 'customtkinter'),
        ('tkcalendar', 'tkcalendar'),
        ('matplotlib', 'matplotlib'),
        ('PIL', 'Pillow')
    ]
    
    missing = []
    for module, package in required_modules:
        try:
            __import__(module)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing.append(package)
    
    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print("Install with: py -m pip install " + " ".join(missing))
        return False
    
    print("✅ All dependencies available!")
    return True

def test_database():
    """Test database connection"""
    print("\n🗄️  Testing database connection...")
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from database.db_manager import db_manager
        
        if db_manager.test_connection():
            print("✅ Database connection successful!")
            return True
        else:
            print("❌ Database connection failed!")
            print("💡 Make sure MySQL server is running")
            return False
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def start_application():
    """Start the Task Planner application"""
    print("\n🚀 Starting Task Planner application...")
    
    try:
        # Import and run the main application
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        print("📱 Initializing GUI components...")
        import tkinter as tk
        
        # Test basic tkinter
        print("🧪 Testing Tkinter...")
        root = tk.Tk()
        root.withdraw()  # Hide test window
        root.destroy()
        print("✅ Tkinter working!")
        
        # Import CustomTkinter
        print("🎨 Loading CustomTkinter...")
        import customtkinter as ctk
        print("✅ CustomTkinter loaded!")
        
        # Import the main application
        print("📋 Loading Task Planner...")
        from main import TaskPlannerApp
        
        print("🎯 Creating application instance...")
        app = TaskPlannerApp()
        
        print("🖥️  Starting application...")
        print("👀 Look for the Task Planner window on your screen!")
        print("📌 The window should appear with the title 'Task Planner - Comprehensive Life Planning'")
        
        # Run the application
        app.run()
        
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        print("\n🔍 Full error details:")
        traceback.print_exc()
        
        print("\n💡 Troubleshooting tips:")
        print("1. Make sure you're running this from the correct directory")
        print("2. Check that MySQL server is running")
        print("3. Verify all dependencies are installed")
        print("4. Try running: py -m pip install --upgrade customtkinter")

def main():
    """Main function"""
    print("=" * 60)
    print("🚀 Task Planner Application Starter")
    print("=" * 60)
    
    # Check current directory
    current_dir = os.getcwd()
    print(f"📁 Current directory: {current_dir}")
    
    if not os.path.exists('main.py'):
        print("❌ main.py not found in current directory!")
        print("Please navigate to the Task Planner directory first.")
        return
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install missing dependencies first.")
        return
    
    # Test database
    if not test_database():
        print("\n⚠️  Database connection failed, but you can still try to run the app.")
        try:
            continue_anyway = input("Continue anyway? (y/n): ").lower()
            if continue_anyway not in ['y', 'yes']:
                return
        except:
            return
    
    # Start application
    start_application()

if __name__ == "__main__":
    main()
