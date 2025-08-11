#!/usr/bin/env python3
"""
Alternative server runner for Task Planner Web
"""

import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("🔍 Starting Task Planner Web Server...")
print(f"📁 Working directory: {os.getcwd()}")
print(f"🐍 Python executable: {sys.executable}")

try:
    # Import and run the app
    print("📦 Importing application...")
    from app import app, db_manager
    
    print("🔗 Database status:", "✅ Connected" if db_manager else "❌ Not connected")
    
    print("🌐 Starting Flask development server...")
    print("📍 Access the application at:")
    print("   🏠 Home: http://localhost:8080")
    print("   📊 Dashboard: http://localhost:8080/dashboard") 
    print("   📅 Calendar: http://localhost:8080/calendar")
    print("   🔄 Recurring: http://localhost:8080/recurring")
    print("   ⚙️  Settings: http://localhost:8080/settings")
    print()
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    # Run on port 8080 instead of 5000
    app.run(debug=True, host='127.0.0.1', port=8080, threaded=True)
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure Flask is installed: pip install flask flask-cors")
except Exception as e:
    print(f"❌ Error starting server: {e}")
    import traceback
    traceback.print_exc()
