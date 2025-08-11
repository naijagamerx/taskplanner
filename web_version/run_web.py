#!/usr/bin/env python3
"""
Task Planner Web Version Launcher
Simple script to start the web application
"""

import os
import sys
import webbrowser
from threading import Timer

def open_browser():
    """Open browser after a short delay"""
    webbrowser.open('http://localhost:5000')

def main():
    print("🌐 Task Planner Web Version")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("❌ Error: Please run this script from the web_version directory")
        print("   Navigate to the web_version folder and try again.")
        return
    
    # Check if Flask is installed
    try:
        import flask
        print("✅ Flask is available")
    except ImportError:
        print("❌ Flask is not installed!")
        print("   Please install requirements: pip install -r requirements.txt")
        return
    
    # Check if desktop models are accessible
    try:
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from models.task import Task
        print("✅ Desktop models are accessible")
    except ImportError as e:
        print(f"⚠️  Warning: Desktop models not accessible: {e}")
        print("   Web version will run with limited functionality")
    
    print("\n🚀 Starting Task Planner Web Application...")
    print("📍 URL: http://localhost:5000")
    print("📊 Dashboard: http://localhost:5000/dashboard")
    print("🔌 API: http://localhost:5000/api/")
    print("\n💡 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Open browser after 2 seconds
    Timer(2.0, open_browser).start()
    
    # Import and run the Flask app
    from app import app
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()
